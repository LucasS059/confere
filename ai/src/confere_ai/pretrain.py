"""Pré-treino de linguagem do zero em um snapshot local de português."""

import argparse
import json
import math
import platform
import resource
import time
from collections import Counter
from dataclasses import asdict
from pathlib import Path

import torch
from torch.nn import functional as F

from .language_data import fit_language_tokenizer, language_windows, load_corpus, validate_expansion
from .model import GPT, GPTConfig
from .tokenizer import ByteBPE
from .train import batch, choose_device, evaluate, save_checkpoint


def run(args):
    if min(args.steps, args.batch_size, args.block_size, args.eval_every, args.eval_blocks, args.tokenizer_chars) <= 0 or not math.isfinite(args.learning_rate) or args.learning_rate <= 0 or not math.isfinite(args.max_seconds) or args.max_seconds <= 0:
        raise ValueError("Limites, passos e learning rate devem ser positivos e finitos.")
    if args.run_dir.exists():
        raise ValueError("A pasta de execução já existe.")
    init_from=getattr(args,"init_from",None)
    if args.resume and init_from: raise ValueError("Use resume ou init-from, não ambos.")
    preparation_started = time.perf_counter()
    torch.set_num_threads(4)
    torch.manual_seed(args.seed)
    device = choose_device(args.device)
    rows, fingerprint = load_corpus(args.data)
    settings = {key: getattr(args, key) for key in ("seed", "batch_size", "learning_rate", "block_size", "vocab_size", "tokenizer_chars", "eval_blocks")}
    settings["objective"] = "causal_lm"
    source_path=args.resume or init_from
    checkpoint = torch.load(source_path, map_location="cpu", weights_only=True) if source_path else None
    previous_fingerprint = None
    if checkpoint:
        if checkpoint["settings"].get("objective")!="causal_lm":
            raise ValueError("A base deve vir do nosso pré-treino de linguagem.")
        if not init_from and checkpoint["settings"] != settings:
            raise ValueError("Retomada exige as mesmas configurações.")
        if checkpoint["dataset_fingerprint"] != fingerprint:
            previous_data = getattr(args, "previous_data", None)
            if not previous_data:
                raise ValueError("Novos dados exigem --previous-data para validar expansão.")
            previous, previous_fingerprint = load_corpus(previous_data)
            if previous_fingerprint != checkpoint["dataset_fingerprint"]:
                raise ValueError("Corpus anterior não corresponde ao checkpoint.")
            validate_expansion(previous, rows)
        tokenizer = ByteBPE(checkpoint["merges"])
        if init_from and args.vocab_size!=tokenizer.vocab_size: raise ValueError("Inicialização preserva o vocabulário do checkpoint.")
    else:
        print("Treinando BPE somente na amostra de artigos de treino...", flush=True)
        tokenizer = fit_language_tokenizer(rows, args.vocab_size, args.tokenizer_chars, args.seed)
    print("Tokenizando treino e validação; artigos de teste ficam fora...", flush=True)
    train_examples = language_windows(rows, tokenizer, args.block_size, "train")
    validation_examples = language_windows(rows, tokenizer, args.block_size, "validation")
    if not train_examples or not validation_examples:
        raise ValueError("Não há janelas suficientes para treino e validação.")
    evaluation_generator = torch.Generator().manual_seed(args.seed + 1)
    def subset(examples):
        indices = torch.randperm(len(examples), generator=evaluation_generator).tolist()[:args.eval_blocks]
        return [examples[index] for index in indices]
    train_eval, validation_eval = subset(train_examples), subset(validation_examples)
    config = GPTConfig(tokenizer.vocab_size, args.block_size, 384, 6, 6)
    model = GPT(config).to(device)
    optimizer = torch.optim.AdamW(model.parameters(), lr=args.learning_rate, weight_decay=0.01)
    generator = torch.Generator().manual_seed(args.seed)
    start_step = 0
    if checkpoint:
        model.load_local_checkpoint(checkpoint,extend_context=bool(init_from))
        if not init_from:
            optimizer.load_state_dict(checkpoint["optimizer"])
            generator.set_state(checkpoint["generator_state"])
            torch.set_rng_state(checkpoint["torch_rng_state"])
            start_step = checkpoint["step"]
            if args.steps <= start_step:
                raise ValueError("Total de passos deve superar o checkpoint.")
    args.run_dir.mkdir(parents=True)
    info = {"objective": "causal_lm", "initialization": "local_checkpoint_new_optimizer" if init_from else "local_checkpoint" if checkpoint else "random_from_scratch", "resume_from": str(source_path) if source_path else None,
            "source_step":checkpoint["step"] if checkpoint else None,"source_context":checkpoint["config"]["block_size"] if checkpoint else None,
            "context_note":"Posições antigas preservadas; novas posições aleatórias, aprendidas nesta rodada. Otimizador reiniciado." if init_from else None,
            "config": asdict(config), "parameters": sum(p.numel() for p in model.parameters()),
            "data": str(args.data), "dataset_fingerprint": fingerprint, "settings": settings,
            "previous_dataset_fingerprint": previous_fingerprint,
            "document_splits": dict(Counter(row["split"] for row in rows)),
            "train_ids": [row["id"] for row in rows if row["split"] == "train"],
            "validation_ids": [row["id"] for row in rows if row["split"] == "validation"],
            "test_examples_used": 0, "train_windows": len(train_examples), "validation_windows": len(validation_examples),
            "train_tokens": sum(len(ids) for ids, _ in train_examples), "evaluation_windows_per_split": [len(train_eval), len(validation_eval)],
            "preparation_seconds": time.perf_counter() - preparation_started, "device": device,
            "torch": str(torch.__version__), "python": platform.python_version(),
            "note": "Métricas em amostras fixas de janelas; não são acurácia, diálogo nem avaliação de TCC."}
    (args.run_dir / "run.json").write_text(json.dumps(info, ensure_ascii=False, indent=2))
    (args.run_dir / "tokenizer.json").write_text(json.dumps({"merges": tokenizer.merges}))
    started, best_loss = time.perf_counter(), float("inf")
    metrics, processed, observed_memory = [], 0, 0

    def record(step):
        nonlocal best_loss
        item = {"step": step, "train_loss": evaluate(model, train_eval, device), "validation_loss": evaluate(model, validation_eval, device), "elapsed_seconds": time.perf_counter() - started}
        metrics.append(item)
        with (args.run_dir / "metrics.jsonl").open("a") as handle:
            handle.write(json.dumps(item) + "\n")
        print(json.dumps(item), flush=True)
        save_checkpoint(args.run_dir / "last.pt", model, optimizer, tokenizer, generator, step, fingerprint, settings)
        if item["validation_loss"] < best_loss:
            best_loss = item["validation_loss"]
            save_checkpoint(args.run_dir / "best.pt", model, optimizer, tokenizer, generator, step, fingerprint, settings)

    record(start_step)
    for step in range(start_step + 1, args.steps + 1):
        model.train()
        indices = torch.randint(len(train_examples), (args.batch_size,), generator=generator).tolist()
        x, y = batch(train_examples, indices, device)
        optimizer.zero_grad(set_to_none=True)
        loss = F.cross_entropy(model(x).flatten(0, 1), y.flatten(), ignore_index=-100)
        if not torch.isfinite(loss).item():
            raise ValueError("Loss não finita; último checkpoint preservado.")
        loss.backward()
        torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0, error_if_nonfinite=True)
        optimizer.step()
        processed += (y != -100).sum().item()
        if device == "mps":
            observed_memory = max(observed_memory, torch.mps.current_allocated_memory())
        timed_out = time.perf_counter() - started >= args.max_seconds
        if step % args.eval_every == 0 or step == args.steps or timed_out:
            record(step)
        if timed_out:
            break
    summary = {"start_step": start_step, "final_step": step, "stop_reason": "time_limit" if timed_out else "steps", "elapsed_seconds": time.perf_counter() - started,
               "tokens_processed": processed, "best_validation_loss_in_this_run": best_loss,
               "mps_allocated_bytes_max_observed": observed_memory if device == "mps" else None,
               "process_peak_rss_bytes": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss * (1 if platform.system() == "Darwin" else 1024),
               "initial": metrics[0], "final": metrics[-1]}
    (args.run_dir / "summary.json").write_text(json.dumps(summary, indent=2))
    from .report import create_report, save_samples
    prompts = ["A ciência é ", "Um projeto de software deve ", "O Brasil é "]
    save_samples(args.run_dir, model, tokenizer, device,
                 [(text, [tokenizer.BOS] + tokenizer.encode(text)) for text in prompts])
    print(f"Relatório PDF: {create_report(args.run_dir)}", flush=True)
    return summary


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data", type=Path, required=True)
    parser.add_argument("--run-dir", type=Path, required=True)
    initialization=parser.add_mutually_exclusive_group()
    initialization.add_argument("--resume", type=Path)
    initialization.add_argument("--init-from",type=Path,help="Inicializar pesos locais e novo otimizador; permite ampliar contexto.")
    parser.add_argument("--previous-data", type=Path, help="Corpus original exigido para expandir dados ao retomar.")
    parser.add_argument("--steps", type=int, default=2000)
    parser.add_argument("--max-seconds", type=float, default=180)
    parser.add_argument("--batch-size", type=int, default=8)
    parser.add_argument("--block-size", type=int, default=256)
    parser.add_argument("--vocab-size", type=int, default=1024)
    parser.add_argument("--tokenizer-chars", type=int, default=128000)
    parser.add_argument("--eval-every", type=int, default=200)
    parser.add_argument("--eval-blocks", type=int, default=32)
    parser.add_argument("--learning-rate", type=float, default=0.0003)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--device", choices=["auto", "cpu", "mps"], default="auto")
    args = parser.parse_args()
    try:
        run(args)
    except (ValueError, OSError) as error:
        parser.exit(1, f"Erro: {error}\n")


if __name__ == "__main__":
    main()
