"""Prova documental controlada; teste reservado somente após validação."""
import argparse
import json
from pathlib import Path
import torch
from confere_ai.instruct import acceptance, load_instructions, score
from confere_ai.report import create_report
from evaluate_conversation_flow import load_model
from evaluate_informal_dialogues import capture, PROMPTS


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("run_dir", type=Path)
    args = parser.parse_args(); root = args.run_dir
    output = root / "document-transfer.json"
    if output.exists(): parser.error("Avaliação existente; não consultar o teste novamente.")
    info = json.loads((root / "run.json").read_text())
    rows, fingerprint = load_instructions(Path(info["data"]))
    if fingerprint != info["dataset_fingerprint"]: raise ValueError("Corpus alterado.")
    torch.set_num_threads(4)
    validation = [r for r in rows if r["split"] == "validation" and r["task"].startswith("grounded_")]
    model, tokenizer, step = load_model(root / "best.pt")
    result = dict(checkpoint=str(root / "best.pt"), step=step,
                  validation=score(model, tokenizer, validation, "mps"), test=None,
                  conversation_after=capture(model, tokenizer, PROMPTS), adopted=False,
                  scope="Documentos fictícios curtos e templates já explorados anteriormente; sem TCC real, sem validação independente de semântica. Não substitui o modelo de conversa.")
    if acceptance(result["validation"])["passed"]:
        result["test"] = score(model, tokenizer, [r for r in rows if r["split"] == "test" and r["task"].startswith("grounded_")], "mps")
    del model
    model, tokenizer, _ = load_model(info["baseline_checkpoint"])
    result["conversation_before"] = capture(model, tokenizer, PROMPTS)
    del model
    output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps({k: {"correct": result[k]["correct"], "total": result[k]["total"]} if result[k] else None for k in ("validation", "test")}), flush=True)
    print(create_report(root))


if __name__ == "__main__": main()
