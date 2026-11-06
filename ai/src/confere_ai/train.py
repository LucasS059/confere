"""Experimento supervisionado do zero. Execute python -m confere_ai.train --help."""

import argparse
import json
import math
import platform
import resource
import time
from dataclasses import asdict
from pathlib import Path

import torch
from torch.nn import functional as F

from .model import GPT, GPTConfig
from .tokenizer import ByteBPE
from .training_data import encode_sample, load_authored


def batch(examples, indices, device):
    selected = [examples[index] for index in indices]
    length = max(len(ids) for ids, _ in selected)
    x = torch.full((len(selected), length), ByteBPE.PAD, dtype=torch.long)
    y = torch.full_like(x, -100)
    for index, (ids, labels) in enumerate(selected):
        x[index, :len(ids)] = torch.tensor(ids)
        y[index, :len(labels)] = torch.tensor(labels)
    return x.to(device), y.to(device)


@torch.no_grad()
def evaluate(model, examples, device):
    model.eval()
    total_loss, total_tokens = 0.0, 0
    for index in range(len(examples)):
        x, y = batch(examples, [index], device)
        total_loss += F.cross_entropy(model(x).flatten(0, 1), y.flatten(), ignore_index=-100, reduction="sum").item()
        total_tokens += (y != -100).sum().item()
    return total_loss / total_tokens if total_tokens else None


def choose_device(name):
    if name == "auto":
        return "mps" if torch.backends.mps.is_available() else "cpu"
    if name == "mps" and not torch.backends.mps.is_available():
        raise ValueError("MPS indisponível; escolha CPU explicitamente.")
    return name


def save_checkpoint(path, model, optimizer, tokenizer, generator, step, fingerprint, settings):
    temporary = path.with_suffix(".tmp")
    torch.save({
        "format_version": 1, "config": asdict(model.config),
        "model": {name: tensor.detach().cpu() for name, tensor in model.state_dict().items()},
        "optimizer": optimizer.state_dict(), "merges": tokenizer.merges,
        "generator_state": generator.get_state(), "torch_rng_state": torch.get_rng_state(),
        "step": step, "dataset_fingerprint": fingerprint, "settings": settings,
    }, temporary)
    temporary.replace(path)


def run(args):
    if args.steps <= 0 or args.batch_size <= 0 or args.eval_every <= 0 or not math.isfinite(args.learning_rate) or args.learning_rate <= 0:
        raise ValueError("Passos, batch, intervalo e learning rate devem ser positivos.")
    if args.run_dir.exists():
        raise ValueError("A pasta da execução já existe; use outra para preservar resultados.")
    torch.set_num_threads(4)
    torch.manual_seed(args.seed)
    device = choose_device(args.device)
    samples, fingerprint = load_authored(args.data)
    train_samples = [sample for sample in samples if sample["split"] == "train"]
    validation_samples = [sample for sample in samples if sample["split"] == "validation"]
    generator = torch.Generator().manual_seed(args.seed)
    settings = {"seed": args.seed, "batch_size": args.batch_size, "learning_rate": args.learning_rate, "preset": args.preset, "vocab_size": args.vocab_size, "block_size": args.block_size}
    checkpoint = torch.load(args.resume, map_location="cpu", weights_only=True) if args.resume else None
    if checkpoint:
        if checkpoint["dataset_fingerprint"] != fingerprint or checkpoint["settings"] != settings:
            raise ValueError("Retomada exige os mesmos dados e configurações da execução original.")
        tokenizer = ByteBPE(checkpoint["merges"])
        config = GPTConfig(**checkpoint["config"])
    else:
        tokenizer = ByteBPE.train([text for sample in train_samples for text in (sample["prompt"], sample["target"])], args.vocab_size)
        dimensions = {"smoke": (128, 2, 4), "small": (384, 6, 6)}[args.preset]
        config = GPTConfig(tokenizer.vocab_size, args.block_size, *dimensions)
    train_examples = [encode_sample(sample, tokenizer, config.block_size) for sample in train_samples]
    validation_examples = [encode_sample(sample, tokenizer, config.block_size) for sample in validation_samples]
    model = GPT(config).to(device)
    optimizer = torch.optim.AdamW(model.parameters(), lr=args.learning_rate, weight_decay=0.01)
    start_step = 0
    if checkpoint:
        model.load_state_dict(checkpoint["model"])
        optimizer.load_state_dict(checkpoint["optimizer"])
        generator.set_state(checkpoint["generator_state"])
        torch.set_rng_state(checkpoint["torch_rng_state"])
        start_step = checkpoint["step"]
        if args.steps <= start_step:
            raise ValueError("--steps é o total desejado e precisa superar o passo salvo.")
    args.run_dir.mkdir(parents=True)
    (args.run_dir / "tokenizer.json").write_text(json.dumps({"format_version": 1, "merges": tokenizer.merges}))
    info = {
        "initialization": "local_checkpoint" if checkpoint else "random_from_scratch",
        "resume_from": str(args.resume) if args.resume else None,
        "model_config": asdict(config), "settings": settings,
        "parameters": sum(parameter.numel() for parameter in model.parameters()),
        "dataset_fingerprint": fingerprint, "data": str(args.data),
        "train_ids": [sample["id"] for sample in train_samples],
        "validation_ids": [sample["id"] for sample in validation_samples],
        "test_examples_used": 0, "device": device, "torch": torch.__version__,
        "python": platform.python_version(), "platform": platform.platform(),
        "max_train_sequence": max(len(ids) for ids, _ in train_examples),
        "max_validation_sequence": max((len(ids) for ids, _ in validation_examples), default=0),
        "warning": "Corpus mínimo autoral; loss não mede qualidade de conferência nem generalização.",
    }
    (args.run_dir / "run.json").write_text(json.dumps(info, ensure_ascii=False, indent=2))
    started = time.perf_counter()
    token_count, observed_memory = 0, 0
    metrics = []

    def record(step):
        measurement = {"step": step, "train_loss": evaluate(model, train_examples, device), "validation_loss": evaluate(model, validation_examples, device), "elapsed_seconds": time.perf_counter() - started}
        metrics.append(measurement)
        with (args.run_dir / "metrics.jsonl").open("a") as handle:
            handle.write(json.dumps(measurement) + "\n")
        print(json.dumps(measurement), flush=True)

    record(start_step)
    for step in range(start_step + 1, args.steps + 1):
        model.train()
        indices = torch.randint(len(train_examples), (args.batch_size,), generator=generator).tolist()
        x, y = batch(train_examples, indices, device)
        optimizer.zero_grad(set_to_none=True)
        loss = F.cross_entropy(model(x).flatten(0, 1), y.flatten(), ignore_index=-100)
        if not torch.isfinite(loss).item():
            raise ValueError("Loss não finita; interrompido sem substituir o último checkpoint.")
        loss.backward()
        torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0, error_if_nonfinite=True)
        optimizer.step()
        token_count += (y != -100).sum().item()
        if device == "mps":
            observed_memory = max(observed_memory, torch.mps.current_allocated_memory())
        if step % args.eval_every == 0 or step == args.steps:
            record(step)
            save_checkpoint(args.run_dir / "last.pt", model, optimizer, tokenizer, generator, step, fingerprint, settings)
    elapsed = time.perf_counter() - started
    summary = {"start_step": start_step, "final_step": args.steps, "elapsed_seconds": elapsed, "supervised_tokens_processed": token_count, "supervised_tokens_per_second_including_evaluation": token_count / elapsed, "mps_allocated_bytes_max_observed_after_step": observed_memory if device == "mps" else None, "process_peak_rss_bytes": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss * (1 if platform.system() == "Darwin" else 1024), "initial": metrics[0], "final": metrics[-1]}
    (args.run_dir / "summary.json").write_text(json.dumps(summary, indent=2))
    from .report import create_report, save_samples
    prompts = []
    for sample in validation_samples[:3]:
        ids = [tokenizer.BOS] + tokenizer.encode(sample["prompt"]) + [tokenizer.SEP]
        prompts.append((sample["id"] + " | validação", ids))
    save_samples(args.run_dir, model, tokenizer, device, prompts)
    print(f"Relatório PDF: {create_report(args.run_dir)}", flush=True)
    return summary


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data", type=Path, default=Path("ai/data/authored/examples.jsonl"))
    parser.add_argument("--run-dir", type=Path, required=True)
    parser.add_argument("--resume", type=Path)
    parser.add_argument("--preset", choices=["smoke", "small"], default="smoke")
    parser.add_argument("--device", choices=["auto", "cpu", "mps"], default="auto")
    parser.add_argument("--steps", type=int, default=100)
    parser.add_argument("--batch-size", type=int, default=2)
    parser.add_argument("--eval-every", type=int, default=25)
    parser.add_argument("--learning-rate", type=float, default=0.0003)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--vocab-size", type=int, default=512)
    parser.add_argument("--block-size", type=int, default=1024)
    args = parser.parse_args()
    try:
        run(args)
    except (ValueError, OSError) as error:
        parser.exit(1, f"Erro: {error}\n")


if __name__ == "__main__":
    main()
