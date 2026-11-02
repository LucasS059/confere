"""Decide adoção com critérios fixos, sem relaxá-los após olhar resultados."""
import argparse
import json
from pathlib import Path
import torch
from confere_ai.instruct import acceptance, load_instructions, score
from confere_ai.model import GPT, GPTConfig
from confere_ai.report import create_report
from confere_ai.tokenizer import ByteBPE
from evaluate_conversation_regressions import evaluate


def cohorts(result):
    return {name+"_"+metric: sum(r["exact_match"] if metric == "correct" else 1
            for r in result["samples"] if r["id"].startswith("curriculum-") == new)
            for name, new in (("old", False), ("new", True)) for metric in ("correct", "total")}


def passes(result, baseline, regressions):
    old, previous = cohorts(result), cohorts(baseline)
    return (acceptance(result)["passed"] and len(regressions) == 6
            and all(r["exact_match"] for r in regressions)
            and old["old_total"] == previous["old_total"] == 415
            and old["old_correct"] >= previous["old_correct"])


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("run_dir", type=Path)
    args = parser.parse_args()
    torch.set_num_threads(4)
    root = args.run_dir
    report_path = root / "instruction-evaluation.json"
    original = root / "loss-selected-evaluation.json"
    if original.exists():
        parser.error("A avaliação de adoção já existe; preserve a seleção anterior.")
    original.write_bytes(report_path.read_bytes())
    report = json.loads(original.read_text())
    info = json.loads((root / "run.json").read_text())
    rows, fingerprint = load_instructions(Path(info["data"]))
    if fingerprint != info["dataset_fingerprint"]:
        raise ValueError("Corpus mudou após o treino.")
    validation = [r for r in rows if r["split"] == "validation" and r["task"] != "human_dialogue"]
    candidates = []
    for name in ("best", "last"):
        checkpoint_path = root / (name+".pt")
        regressions = evaluate(checkpoint_path)
        if name == "best":
            result, step = report["selected"], report["selected_step"]
        else:
            checkpoint = torch.load(checkpoint_path, map_location="cpu", weights_only=True)
            tokenizer = ByteBPE(checkpoint["merges"])
            model = GPT(GPTConfig(**checkpoint["config"])).to("mps")
            model.load_state_dict(checkpoint["model"])
            model.eval()
            result, step = score(model, tokenizer, validation, "mps", context_limit=256), checkpoint["step"]
            del model
        candidates.append(dict(checkpoint=str(checkpoint_path), step=step,
                               result=result, regressions=regressions,
                               passed=passes(result, report["baseline"], regressions)))
    selected = next((c for c in candidates if c["passed"]), candidates[0])
    gate = {phase: cohorts(result) for phase, result in
            (("baseline", report["baseline"]), ("selected", selected["result"]))}
    gate.update(known_regressions_correct=sum(r["exact_match"] for r in selected["regressions"]),
                final_regressions_correct=sum(r["exact_match"] for r in candidates[1]["regressions"]),
                passed=selected["passed"])
    report.update(selected=selected["result"], selected_step=selected["step"],
                  selected_checkpoint=selected["checkpoint"], acceptance=acceptance(selected["result"]),
                  curriculum_gate=gate,
                  selection_policy="Melhor por loss primeiro; final somente se passar todos os critérios fixos. Ambos avaliados na mesma validação; não é teste cego.",
                  adoption_decision=("Aprovado somente no currículo controlado; conversa aberta não validada."
                                     if selected["passed"] else "Reprovado; padrão da TUI preservado. Pelo menos um critério fixo falhou."))
    for name, value in (("adoption-candidates.json", candidates),
                        ("instruction-evaluation.json", report),
                        ("interactive-regressions.json", selected["regressions"])):
        (root/name).write_text(json.dumps(value, ensure_ascii=False, indent=2)+"\n")
    print(json.dumps(dict(gate=gate, selected=selected["checkpoint"],
                         families=report["acceptance"]), ensure_ascii=False))
    print(create_report(root))


if __name__ == "__main__":
    main()
