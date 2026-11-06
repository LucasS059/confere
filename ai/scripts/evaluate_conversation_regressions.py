"""Reproduz falhas conhecidas sem respostas programadas na inferência."""
import argparse
import json
from pathlib import Path

import torch
from confere_ai.chat import prepare_prompt
from confere_ai.model import GPT, GPTConfig
from confere_ai.tokenizer import ByteBPE


CASES = [
    ("ola", "Olá! Sou o Confere."),
    ("vc esta bem?", "Estou pronto para ajudar. E você?"),
    ("qual seu nome? diga 3 vezes", "Confere Confere Confere"),
    ("fala pfv", "Confere Confere Confere"),
    ("bugou?", "Entendi errado. Pode reformular o pedido?"),
    ("nada ue", "Tudo bem. Podemos conversar quando você quiser."),
]


def evaluate(checkpoint_path, device="mps"):
    checkpoint = torch.load(checkpoint_path, map_location="cpu", weights_only=True)
    tokenizer = ByteBPE(checkpoint["merges"])
    model = GPT(GPTConfig(**checkpoint["config"])).to(device)
    model.load_state_dict(checkpoint["model"])
    model.eval()
    budget = checkpoint["settings"].get("generation_budget", 64)
    history, outputs = [], []
    for prompt, expected in CASES:
        ids, dropped = prepare_prompt(history, prompt, tokenizer, model.config.block_size, budget, "conversation")
        generated = model.generate(torch.tensor([ids], device=device), budget, tokenizer.EOS)
        answer = tokenizer.decode(generated[0, len(ids):].tolist())
        outputs.append(dict(prompt=prompt, answer=answer, expected=expected,
                            exact_match=answer.strip() == expected, dropped_turns=dropped))
        history = history[dropped:] + [(prompt, answer)]
    return outputs


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("checkpoint", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    torch.set_num_threads(4)
    results = evaluate(args.checkpoint)
    args.output.write_text(json.dumps(results, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps(results, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
