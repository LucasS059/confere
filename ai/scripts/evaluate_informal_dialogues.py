"""Validação informal com histórico gerado e retenção das avaliações anteriores."""
import argparse
import json
from pathlib import Path
import torch
from confere_ai.instruct import acceptance, load_instructions, score
from confere_ai.report import create_report
from evaluate_conversation_flow import conversation_metrics, flow_passes, load_model
from evaluate_flow_captures import PROMPTS as OLD_PROMPTS
from confere_ai.chat import prepare_prompt

PROMPTS = ["oi", "qual seu nome? diga 3 vezes", "boa muleke", "?", "qual seu nome mesmo?",
           "e oq vc faz?", "e o que voce faz?", "que tipo de projetos?",
           "ok, que tipo de projetos?", "quer ser meu amigo?"]


def cohorts(rows):
    validation = [r for r in rows if r["split"] == "validation"]
    return {
        "informal": [r for r in validation if r["id"].startswith("slang-dialogue-")],
        "flow": [r for r in validation if r["id"].startswith("flow-")],
        "legacy": [r for r in validation if not r["id"].startswith(("flow-", "slang-"))
                   and r["task"] not in ("human_dialogue", "public_dialogue")],
    }


def passes(results, baseline):
    return (flow_passes(results["informal"]) and flow_passes(results["flow"])
            and results["legacy"]["correct"] >= max(514, baseline["legacy"]["correct"])
            and acceptance(results["legacy"])["passed"])


def capture(model, tokenizer, prompts):
    history = []; records = []
    for prompt in prompts:
        ids, dropped = prepare_prompt(history, prompt, tokenizer, 1024, 256, "conversation")
        output = model.generate(torch.tensor([ids], device="mps"), 256, tokenizer.EOS)
        answer = tokenizer.decode(output[0, len(ids):].tolist())
        records.append(dict(prompt=prompt, answer=answer, dropped_turns=dropped))
        history = history[dropped:] + [(prompt, answer)]
    return records


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("run_dir", type=Path)
    args = parser.parse_args(); root = args.run_dir
    output = root / "informal-evaluation.json"
    if output.exists(): parser.error("Avaliação já existe; preserve a seleção e o teste.")
    torch.set_num_threads(4)
    info = json.loads((root / "run.json").read_text())
    rows, fingerprint = load_instructions(Path(info["data"]))
    if fingerprint != info["dataset_fingerprint"]: raise ValueError("Corpus alterado.")
    groups = cohorts(rows)
    if {k: len(v) for k, v in groups.items()} != dict(informal=144, flow=192, legacy=535):
        raise ValueError("Coortes diferentes do protocolo registrado.")
    def evaluate(path):
        model, tokenizer, step = load_model(path)
        results = {key: score(model, tokenizer, group, "mps",
                              context_limit=256 if key == "legacy" else 1024,
                              response_tokens=64 if key == "legacy" else 256)
                   for key, group in groups.items()}
        return model, tokenizer, step, results
    reference, tokenizer, _, baseline = evaluate(info["baseline_checkpoint"])
    del reference
    result = dict(policy="Validação: >=80% por família e >=50% diálogos completos nas coortes informal e fluxo anterior, zero descarte; legado >=514/535 e sem queda ante referência, >=80% por família. Teste informal reservado somente após seleção. Casos conhecidos são diagnóstico, não teste cego.",
                  baseline=baseline, candidates=[], selected_checkpoint=None, test=None, approved=False)
    result["cohorts"] = {key: dict(rows=len(group), unique_prompts=len({r["prompt"] for r in group}),
                                  unique_reference_contexts=len({json.dumps([r["history"],r["prompt"]],ensure_ascii=False) for r in group}))
                         for key, group in groups.items()}
    selected = None
    for name in ("best", "last"):
        path = root / (name + ".pt")
        model, tokenizer, step, results = evaluate(path)
        candidate = dict(checkpoint=str(path), step=step, results=results,
                         passed=passes(results, baseline), captures=capture(model, tokenizer, PROMPTS),
                         previous_captures=capture(model, tokenizer, OLD_PROMPTS))
        result["candidates"].append(candidate)
        if candidate["passed"] and selected is None: selected = candidate
        print(json.dumps(dict(checkpoint=str(path), step=step, passed=candidate["passed"],
                              metrics={k: conversation_metrics(v) for k, v in results.items()}), ensure_ascii=False), flush=True)
        del model
    if selected:
        result["selected_checkpoint"] = selected["checkpoint"]
        model, tokenizer, _ = load_model(selected["checkpoint"])
        test_rows = [r for r in rows if r["split"] == "test" and r["id"].startswith("slang-dialogue-")]
        result["test"] = score(model, tokenizer, test_rows, "mps", context_limit=1024, response_tokens=256)
        result["approved"] = flow_passes(result["test"])
        del model
    output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n")
    evaluation_path = root / "instruction-evaluation.json"
    evaluation = json.loads(evaluation_path.read_text())
    evaluation["adoption_decision"] = ("Aprovado no protocolo informal autoral; conversa aberta ainda não validada."
                                       if result["approved"] else "Critérios ampliados não atingidos; checkpoint experimental e padrão da TUI preservado.")
    evaluation_path.write_text(json.dumps(evaluation, ensure_ascii=False, indent=2) + "\n")
    print(create_report(root), flush=True)


if __name__ == "__main__": main()
