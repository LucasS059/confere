"""Gera uma resposta experimental com um checkpoint local criado pelo treino."""

import argparse
import json
from pathlib import Path

import torch
from jsonschema import Draft202012Validator

from .model import GPT, GPTConfig
from .tokenizer import ByteBPE
from .train import choose_device
from .training_data import load_authored


def inspect_response(text):
    try:
        parsed = json.loads(text)
    except json.JSONDecodeError:
        return False, False
    contract = json.loads(Path(__file__).with_name("example.schema.json").read_text())
    schema = {"$defs": contract["$defs"], **contract["properties"]["expected"]}
    return True, Draft202012Validator(schema).is_valid(parsed)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("checkpoint", type=Path)
    parser.add_argument("--data", type=Path, default=Path("ai/data/authored/examples.jsonl"))
    parser.add_argument("--id", required=True)
    parser.add_argument("--max-new-tokens", type=int, default=256)
    parser.add_argument("--device", choices=["auto", "cpu", "mps"], default="auto")
    args = parser.parse_args()
    checkpoint = torch.load(args.checkpoint, map_location="cpu", weights_only=True)
    samples, fingerprint = load_authored(args.data)
    if fingerprint != checkpoint["dataset_fingerprint"]:
        parser.error("Dados diferentes dos registrados no checkpoint.")
    sample = next((item for item in samples if item["id"] == args.id and item["split"] != "test"), None)
    if sample is None or args.max_new_tokens <= 0:
        parser.error("Selecione um ID de treino/validação e uma quantidade positiva de tokens.")
    device = choose_device(args.device)
    tokenizer = ByteBPE(checkpoint["merges"])
    model = GPT(GPTConfig(**checkpoint["config"])).to(device)
    model.load_state_dict(checkpoint["model"])
    model.eval()
    prefix = [tokenizer.BOS] + tokenizer.encode(sample["prompt"]) + [tokenizer.SEP]
    generated = model.generate(torch.tensor([prefix], device=device), args.max_new_tokens, tokenizer.EOS)
    text = tokenizer.decode(generated[0, len(prefix):].tolist())
    valid_json, valid_schema = inspect_response(text)
    print(json.dumps({"id": sample["id"], "split": sample["split"], "step": checkpoint["step"], "text": text, "valid_json": valid_json, "valid_response_schema": valid_schema, "warning": "Sintaxe e formato não comprovam status correto nem evidências verdadeiras."}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
