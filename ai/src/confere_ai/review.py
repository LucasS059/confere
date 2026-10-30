"""Conferência experimental de um contexto PDF/DOCX curto, sem truncamento."""
import argparse
import json
from pathlib import Path
import torch
from .extract import extract_document
from .grounding import prompt_for, resolve
from .model import GPT, GPTConfig
from .tokenizer import ByteBPE
from .train import choose_device


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("document", type=Path)
    parser.add_argument("--requirement", required=True)
    parser.add_argument("--unit", action="append", help="Unidade exata, como page:2; repita para selecionar várias.")
    parser.add_argument("--checkpoint", type=Path, default=Path("ai/runs/grounding-pilot-2026-11-02/best.pt"))
    parser.add_argument("--device", choices=["auto", "cpu", "mps"], default="auto")
    args = parser.parse_args()
    try:
        if not args.requirement.strip(): raise ValueError("Informe um requisito não vazio.")
        document = extract_document(args.document)
        units = document["units"]
        if args.unit:
            available = {u["id"] for u in units}
            if set(args.unit)-available: raise ValueError("Uma unidade selecionada não existe no documento.")
            units = [u for u in units if u["id"] in args.unit]
        if not any(u["text"].strip() for u in units): raise ValueError("Contexto sem texto utilizável.")
        checkpoint = torch.load(args.checkpoint, map_location="cpu", weights_only=True)
        if checkpoint["settings"].get("objective") != "document_grounding": raise ValueError("Use um checkpoint de conferência documental.")
        tokenizer = ByteBPE(checkpoint["merges"])
        ids = [tokenizer.BOS]+tokenizer.encode(prompt_for(args.requirement, units))+[tokenizer.SEP]
        config = GPTConfig(**checkpoint["config"])
        if len(ids)+64 > config.block_size:
            raise ValueError("Documento/trecho excede o contexto experimental. Selecione unidades menores; nada foi truncado ou avaliado parcialmente em silêncio.")
        device = choose_device(args.device)
        model = GPT(config).to(device)
        model.load_state_dict(checkpoint["model"]); model.eval()
        generated = model.generate(torch.tensor([ids], device=device), 64, tokenizer.EOS)
        raw = tokenizer.decode(generated[0,len(ids):].tolist())
        result = resolve(raw, document["name"], units)
        print(json.dumps({"source_sha256": document["sha256"], "selected_units": [u["id"] for u in units], "warnings": document["warnings"],
                          "coverage": "selected_units_only" if args.unit else "all_extracted_text",
                          "scope_note": "Resultado restrito ao contexto selecionado; referência válida não garante interpretação correta.",
                          "model_step": checkpoint["step"], "raw_model_output": raw, **result}, ensure_ascii=False, indent=2))
    except (ValueError, OSError, RuntimeError, KeyError) as error:
        parser.exit(1, f"Falha na conferência: {error}\n")


if __name__ == "__main__": main()
