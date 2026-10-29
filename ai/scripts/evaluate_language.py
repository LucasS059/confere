"""Compare checkpoints locais na validação completa, sem consultar o teste."""

import argparse
import json
from pathlib import Path

import torch

from confere_ai.language_data import language_windows, load_corpus, validate_expansion
from confere_ai.model import GPT, GPTConfig
from confere_ai.tokenizer import ByteBPE
from confere_ai.train import choose_device, evaluate


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("checkpoints", nargs="+", type=Path)
    parser.add_argument("--data", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--device", choices=["auto", "cpu", "mps"], default="auto")
    parser.add_argument("--validation-transfer", action="store_true", help="Comparar na validação de um corpus ampliado, após verificar splits.")
    parser.add_argument("--previous-data", type=Path)
    args = parser.parse_args()
    if args.output.exists():
        parser.error("Saída já existe; preserve os resultados anteriores.")
    torch.set_num_threads(4)
    rows, fingerprint = load_corpus(args.data)
    previous_fingerprint = None
    if args.validation_transfer:
        if not args.previous_data:
            parser.error("Transferência exige --previous-data para conferir os splits.")
        previous, previous_fingerprint = load_corpus(args.previous_data)
        validate_expansion(previous, rows)
    device = choose_device(args.device)
    results, reference = [], None
    for path in args.checkpoints:
        checkpoint = torch.load(path, map_location="cpu", weights_only=True)
        if checkpoint["dataset_fingerprint"] not in {fingerprint, previous_fingerprint} or checkpoint["settings"].get("objective") != "causal_lm":
            parser.error("Checkpoint incompatível com os dados/objetivo.")
        signature = (checkpoint["config"], checkpoint["merges"])
        if reference is not None and signature != reference:
            parser.error("Comparação exige mesma rede, tokenizer e janelas.")
        reference = signature
        tokenizer = ByteBPE(checkpoint["merges"])
        model = GPT(GPTConfig(**checkpoint["config"])).to(device)
        model.load_state_dict(checkpoint["model"])
        model.eval()
        windows = language_windows(rows, tokenizer, model.config.block_size, "validation")
        loss = evaluate(model, windows, device)
        samples = []
        for prefix in ("A ciência é ", "Um projeto de software deve ", "O Brasil é ",
                       "Para verificar um requisito, é necessário ", "Qual é o seu nome?"):
            ids = [tokenizer.BOS] + tokenizer.encode(prefix)
            generated = model.generate(torch.tensor([ids], device=device), 96, tokenizer.EOS)
            samples.append({"prefix": prefix, "continuation": tokenizer.decode(generated[0, len(ids):].tolist())})
        result = {"checkpoint": str(path), "step": checkpoint["step"], "training_dataset_fingerprint": checkpoint["dataset_fingerprint"], "validation_loss": loss,
                  "validation_windows": len(windows), "validation_tokens": sum(len(y) for _, y in windows),
                  "samples": samples}
        results.append(result)
        print(json.dumps({key: value for key, value in result.items() if key != "samples"}), flush=True)
        del model, checkpoint
    args.output.write_text(json.dumps({"dataset_fingerprint": fingerprint, "test_examples_used": 0,
        "note": "Perda de próximo token; não mede diálogo ou acurácia factual. Geração greedy idêntica entre variantes.",
        "results": results}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
