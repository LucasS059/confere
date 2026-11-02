"""Avalia diálogos inteiros no contexto nativo e retém o teste até a seleção."""
import argparse
import json
import random
from pathlib import Path
import torch
from confere_ai.instruct import acceptance, load_instructions, score
from confere_ai.model import GPT, GPTConfig
from confere_ai.report import create_report
from confere_ai.tokenizer import ByteBPE
from confere_ai.training_data import encode_sample
from confere_ai.train import evaluate as evaluate_loss
from evaluate_conversation_regressions import evaluate as regressions


def conversation_metrics(result):
    groups = {}
    for row in result["samples"]:
        groups.setdefault(row["project_id"], []).append(row)
    return dict(correct=result["correct"], total=result["total"],
                complete=sum(all(r["exact_match"] for r in rows) for rows in groups.values()),
                conversations=len(groups), dropped_turns=sum(r["dropped_turns"] for r in result["samples"]),
                families=acceptance(result)["counts"])


def flow_passes(result):
    metrics = conversation_metrics(result)
    return (metrics["conversations"]>0 and metrics["complete"]/metrics["conversations"]>=.5
            and metrics["dropped_turns"]==0 and acceptance(result)["passed"])


def load_model(path):
    checkpoint = torch.load(path, map_location="cpu", weights_only=True)
    model = GPT(GPTConfig(**checkpoint["config"])).to("mps")
    model.load_state_dict(checkpoint["model"])
    return model.eval(), ByteBPE(checkpoint["merges"]), checkpoint["step"]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("run_dir", type=Path)
    args = parser.parse_args()
    root = args.run_dir
    output = root/"flow-evaluation.json"
    if output.exists(): parser.error("Avaliação já existe; preserve o teste e a seleção.")
    torch.set_num_threads(4)
    info = json.loads((root/"run.json").read_text())
    rows, fingerprint = load_instructions(Path(info["data"]))
    if fingerprint != info["dataset_fingerprint"]: raise ValueError("Corpus alterado.")
    validation = [r for r in rows if r["split"]=="validation" and r["id"].startswith("flow-")]
    legacy = [r for r in rows if r["split"]=="validation" and not r["id"].startswith("flow-") and r["task"]!="human_dialogue"]
    reference, tokenizer, _ = load_model(info["baseline_checkpoint"])
    public_validation=[]
    reserved_path=Path(info["data"]).parent/"reserved-public.jsonl"
    if reserved_path.exists():
        train_contexts={json.dumps([r["history"],r["prompt"].strip().casefold()],ensure_ascii=False) for r in rows if r["task"]=="public_dialogue"}
        available=[json.loads(line) for line in reserved_path.read_text().splitlines() if line.strip()]
        random.Random(731).shuffle(available)
        groups=set()
        for row in available:
            key=json.dumps([row["history"],row["prompt"].strip().casefold()],ensure_ascii=False)
            if row["split"]=="validation" and key not in train_contexts and row["project_id"] not in groups:
                public_validation.append(row);groups.add(row["project_id"])
                if len(public_validation)==64:break
    public_encoded=[encode_sample(r,tokenizer,1024) for r in public_validation]
    baseline_flow = score(reference, tokenizer, validation, "mps", context_limit=1024, response_tokens=256)
    baseline_legacy = score(reference, tokenizer, legacy, "mps", context_limit=256)
    baseline_public_loss=evaluate_loss(reference,public_encoded,"mps") if public_encoded else None
    del reference
    result = dict(policy="Primeiro candidato best/last que passe validação: >=80% por família nova, >=50% conversas completas, zero truncamento, 6/6 regressões, retenção legada sem queda e >=80% por família legada. Teste final uma vez após seleção, com os mesmos limites por família e conversa.",
                  baseline_flow=baseline_flow, baseline_legacy=baseline_legacy, candidates=[], test=None, adopted=False,
                  public_validation_ids=[r["id"] for r in public_validation],baseline_public_loss=baseline_public_loss)
    selected = None
    for name in ("best", "last"):
        path = root/(name+".pt")
        model, tokenizer, step = load_model(path)
        flow = score(model, tokenizer, validation, "mps", context_limit=1024, response_tokens=256)
        retained = score(model, tokenizer, legacy, "mps", context_limit=256)
        known = regressions(path)
        passed = (flow_passes(flow) and retained["correct"]>=baseline_legacy["correct"]
                  and acceptance(retained)["passed"] and all(r["exact_match"] for r in known))
        candidate = dict(checkpoint=str(path), step=step, flow=flow, legacy=retained,
                         known=known, passed=passed, metrics=conversation_metrics(flow),
                         public_validation_loss=evaluate_loss(model,public_encoded,"mps") if public_encoded else None)
        result["candidates"].append(candidate)
        if passed and selected is None: selected=candidate
        del model
    if selected:
        model, tokenizer, _ = load_model(selected["checkpoint"])
        test_rows = [r for r in rows if r["split"]=="test" and r["id"].startswith("flow-")]
        result["test"] = score(model, tokenizer, test_rows, "mps", context_limit=1024, response_tokens=256)
        result["adopted"] = flow_passes(result["test"])
        del model
    result["selected_checkpoint"] = selected["checkpoint"] if selected else None
    output.write_text(json.dumps(result, ensure_ascii=False, indent=2)+"\n")
    report_path=root/"instruction-evaluation.json"
    report=json.loads(report_path.read_text())
    report["adoption_decision"]=("Aprovado em diálogos autorais de validação e teste reservado; conversa aberta ainda não validada." if result["adopted"] else "Reprovado na avaliação ampliada de diálogos; padrão da TUI preservado.")
    report_path.write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n")
    print(json.dumps(dict(adopted=result["adopted"], baseline=conversation_metrics(baseline_flow),
                         candidates=[dict(step=c["step"],metrics=c["metrics"],legacy=c["legacy"]["correct"],passed=c["passed"]) for c in result["candidates"]],
                         test=conversation_metrics(result["test"]) if result["test"] else None),ensure_ascii=False),flush=True)
    print(create_report(root))


if __name__=="__main__": main()
