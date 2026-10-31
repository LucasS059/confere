"""Piloto SFT de tarefas curtas, inicializado exclusivamente do nosso GPT local."""
import argparse
import hashlib
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

from .model import GPT, GPTConfig
from .tokenizer import ByteBPE
from .training_data import encode_sample
from .train import batch, choose_device, evaluate, save_checkpoint
from .report import create_report, save_samples
from .grounding import judge, prompt_for


def load_instructions(path):
    rows = [json.loads(line) for line in path.read_text().splitlines() if line.strip()]
    projects, prompts, ids, contexts, conversations = {}, set(), set(), {}, {}
    for row in rows:
        human=row["provenance"]["kind"]=="human_openassistant"
        if human and (row["provenance"].get("source")!="https://huggingface.co/datasets/OpenAssistant/oasst1" or row["provenance"].get("license")!="Apache-2.0" or not row["provenance"].get("revision")):
            raise ValueError("Proveniência humana não rastreável.")
        if row["split"] not in {"train", "validation", "test"} or row["provenance"]["kind"] not in {"synthetic_authored","human_openassistant"}:
            raise ValueError("Split ou proveniência inválida.")
        conversational = "history" in row
        if conversational:
            if not isinstance(row["history"],list) or any(not isinstance(p,list) or len(p)!=2 or any(not isinstance(t,str) for t in p) for p in row["history"]):
                raise ValueError("Histórico inválido.")
            key=json.dumps([row["history"],row["prompt"].strip().casefold()],ensure_ascii=False)
            value=(row["split"],row["target"])
            if contexts.setdefault(key,value)!=value: raise ValueError("Contexto duplicado entre splits ou alvos conflitantes.")
            previous=conversations.get(row["project_id"])
            if not human and ((previous is None and row["turn_index"]!=0) or (previous is not None and (row["turn_index"]!=previous["turn_index"]+1 or row["history"]!=previous["history"]+[[previous["prompt"],previous["target"]]]))):
                raise ValueError("Sequência de conversa inconsistente.")
            if not human: conversations[row["project_id"]]=row
        if not row["prompt"].strip() or not row["target"].strip() or (not conversational and row["prompt"].strip().casefold() in prompts) or row["id"] in ids:
            raise ValueError("Texto vazio ou exemplos duplicados.")
        prompts.add(row["prompt"].strip().casefold()); ids.add(row["id"])
        if projects.setdefault(row["project_id"], row["split"]) != row["split"]:
            raise ValueError("Projeto atravessando splits.")
        if row["task"].startswith("grounded_"):
            if (row["prompt"] != prompt_for(row["requirement"], row["units"])
                or len({u["id"] for u in row["units"]}) != len(row["units"])
                or row["task"] != "grounded_" + json.loads(row["target"])["status"]
                or not judge(row["target"], row)["exact_match"]):
                raise ValueError("Alvo documental ou referência inválida.")
    if not all(any(row["split"] == split for row in rows) for split in ("train", "validation")):
        raise ValueError("Treino e validação são obrigatórios.")
    return rows, hashlib.sha256(path.read_bytes()).hexdigest()


def score(model, tokenizer, rows, device):
    from .chat import prepare_prompt
    outputs, histories = [], {}
    for row in rows:
        trace={}
        if "history" in row:
            if row["turn_index"]==0: histories[row["project_id"]]=[tuple(p) for p in row["history"]]
            history=histories[row["project_id"]]
            ids,dropped=prepare_prompt(history,row["prompt"],tokenizer,model.config.block_size,64,"conversation")
            trace={"history_used":[list(p) for p in history[dropped:]],"dropped_turns":dropped,"project_id":row["project_id"],"turn_index":row["turn_index"]}
        else:
            ids = [tokenizer.BOS] + tokenizer.encode(row["prompt"]) + [tokenizer.SEP]
        generated = model.generate(torch.tensor([ids], device=device), min(64, model.config.block_size-len(ids)), tokenizer.EOS)
        answer = tokenizer.decode(generated[0, len(ids):].tolist())
        if "history" in row: history.append((row["prompt"],answer))
        judged = judge(answer, row) if row["task"].startswith("grounded_") else {"exact_match": answer.strip() == row["target"].strip()}
        outputs.append({"id": row["id"], "task": row["task"], "prompt": row["prompt"], "expected": row["target"], "actual": answer, **trace, **judged})
    criterion = ("Conversas com histórico gerado pelo modelo após o contexto inicial: igualdade exata após strip, greedy, 64 tokens. Não é qualidade geral."
                 if any("history" in r for r in rows) else "Casos documentais: JSON estrito e status/unidade corretos; replay: igualdade exata após strip. Greedy, até 64 tokens. Templates, não documentos reais."
                 if any(r["task"].startswith("grounded_") for r in rows) else
                 "Igualdade exata após strip; greedy, até 64 tokens. Validação de templates, não conversa geral.")
    return {"correct": sum(row["exact_match"] for row in outputs), "total": len(outputs), "samples": outputs, "criterion": criterion}


def acceptance(result):
    conversational=[r for r in result["samples"] if r["task"].startswith("conversation_")]
    if conversational:
        tasks={}
        for row in conversational:
            pair=tasks.setdefault(row["task"],[0,0]);pair[0]+=row["exact_match"];pair[1]+=1
        return {"passed":all(c/t>=.8 for c,t in tasks.values()),"counts":tasks,
                "description":"Conversas sintéticas: ao menos 80% em cada família, com histórico gerado pelo modelo.","scope":"Não valida conversa aberta."}
    grounded = [r for r in result["samples"] if r["task"].startswith("grounded_")]
    if grounded:
        return {"passed": all(r["valid_format"] and r["reference_valid"] for r in grounded) and sum(r["exact_match"] for r in grounded)/len(grounded) >= .9,
                "description":"Piloto documental: 100% de formato/referências válidos e ao menos 90% de status e unidade corretos em conjunto.",
                "scope":"Templates sintéticos; não comprova confiabilidade geral."}
    critical = {task: [0, 0] for task in ("copy", "field", "missing", "insufficient_context")}
    for row in result["samples"]:
        if row["task"] in critical:
            critical[row["task"]][0] += row["exact_match"]
            critical[row["task"]][1] += 1
    passed = all(total > 0 and correct / total >= .8 for correct, total in critical.values())
    return {"passed": passed, "minimum_per_critical_task": .8, "counts": critical,
            "scope": "Critério exploratório para o piloto; não comprova confiabilidade geral."}


def run(args):
    if args.run_dir.exists() or args.steps <= 0 or args.batch_size <= 0 or args.eval_every <= 0 or not math.isfinite(args.learning_rate) or args.learning_rate <= 0:
        raise ValueError("Saída deve ser nova; passos, batch e taxa devem ser positivos.")
    torch.set_num_threads(4); torch.manual_seed(42)
    device = choose_device(args.device)
    rows, fingerprint = load_instructions(args.data)
    train = [row for row in rows if row["split"] == "train"]
    validation = [row for row in rows if row["split"] == "validation"]
    source = torch.load(args.init_from, map_location="cpu", weights_only=True)
    if source["settings"].get("objective") not in {"causal_lm", "instruction", "document_grounding", "conversation"}:
        raise ValueError("Inicialização exige checkpoint local de linguagem ou instruções.")
    tokenizer = ByteBPE(source["merges"])
    model = GPT(GPTConfig(**source["config"])).to(device)
    model.load_state_dict(source["model"]); model.eval()
    encoded_train = [encode_sample(row, tokenizer, model.config.block_size) for row in train]
    encoded_val = [encode_sample(row, tokenizer, model.config.block_size) for row in validation]
    train_eval = encoded_train[:128] if len(encoded_train) > 128 else encoded_train
    comparison = getattr(args, "compare_with", None)
    if comparison:
        previous = torch.load(comparison, map_location="cpu", weights_only=True)
        if previous["config"] != source["config"] or previous["merges"] != source["merges"]:
            raise ValueError("Comparação exige arquitetura e tokenizer iguais.")
        model.load_state_dict(previous["model"])
    baseline = score(model, tokenizer, validation, device)
    model.load_state_dict(source["model"])
    args.run_dir.mkdir(parents=True)
    objective = "conversation" if any("history" in r for r in rows) else "document_grounding" if any(r["task"].startswith("grounded_") for r in rows) else "instruction"
    settings = {"objective": objective, "seed": 42, "batch_size": args.batch_size, "learning_rate": args.learning_rate}
    info = {"objective": objective, "initialization": "local_checkpoint_new_optimizer", "resume_from": str(args.init_from),
            "base_step": source["step"], "source_objective": source["settings"]["objective"], "config": asdict(model.config), "parameters": sum(p.numel() for p in model.parameters()),
            "baseline_checkpoint": str(comparison or args.init_from), "train_evaluation_examples": len(train_eval),
            "data": str(args.data), "dataset_fingerprint": fingerprint, "settings": settings,
            "document_splits": dict(Counter(row["split"] for row in rows)), "train_ids": [r["id"] for r in train],
            "validation_ids": [r["id"] for r in validation], "test_examples_used": 0,
            "device": device, "torch": str(torch.__version__), "python": platform.python_version()}
    (args.run_dir/"run.json").write_text(json.dumps(info, ensure_ascii=False, indent=2))
    optimizer = torch.optim.AdamW(model.parameters(), lr=args.learning_rate, weight_decay=.01)
    generator = torch.Generator().manual_seed(42)
    started, best, processed, memory = time.perf_counter(), float("inf"), 0, 0
    metrics = []
    def record(step):
        nonlocal best
        item = {"step": step, "train_loss": evaluate(model, train_eval, device), "validation_loss": evaluate(model, encoded_val, device), "elapsed_seconds": time.perf_counter()-started}
        metrics.append(item)
        with (args.run_dir/"metrics.jsonl").open("a") as f: f.write(json.dumps(item)+"\n")
        print(json.dumps(item), flush=True)
        save_checkpoint(args.run_dir/"last.pt", model, optimizer, tokenizer, generator, step, fingerprint, settings)
        if item["validation_loss"] < best:
            best = item["validation_loss"]
            save_checkpoint(args.run_dir/"best.pt", model, optimizer, tokenizer, generator, step, fingerprint, settings)
    record(0)
    for step in range(1, args.steps+1):
        model.train()
        x,y = batch(encoded_train, torch.randint(len(train), (args.batch_size,), generator=generator).tolist(), device)
        optimizer.zero_grad(set_to_none=True)
        loss = F.cross_entropy(model(x).flatten(0,1), y.flatten(), ignore_index=-100)
        if not torch.isfinite(loss).item(): raise ValueError("Loss não finita; checkpoint anterior preservado.")
        loss.backward(); torch.nn.utils.clip_grad_norm_(model.parameters(), 1., error_if_nonfinite=True); optimizer.step()
        processed += (y != -100).sum().item()
        if device == "mps": memory = max(memory, torch.mps.current_allocated_memory())
        if step % args.eval_every == 0 or step == args.steps: record(step)
    summary = {"start_step": 0, "final_step": args.steps, "elapsed_seconds": time.perf_counter()-started,
               "tokens_processed": processed, "initial": metrics[0], "final": metrics[-1],
               "mps_allocated_bytes_max_observed": memory, "process_peak_rss_bytes": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss*(1 if platform.system()=="Darwin" else 1024)}
    (args.run_dir/"summary.json").write_text(json.dumps(summary, indent=2))
    selected = torch.load(args.run_dir/"best.pt", map_location="cpu", weights_only=True)
    model.load_state_dict(selected["model"]); model.eval()
    result = {"baseline": baseline, "selected": score(model, tokenizer, validation, device), "selected_step": selected["step"], "test_examples_used": 0}
    result["acceptance"] = acceptance(result["selected"])
    (args.run_dir/"instruction-evaluation.json").write_text(json.dumps(result, ensure_ascii=False, indent=2))
    if objective=="conversation":
        samples=[{"prompt":r["prompt"],"continuation":r["actual"]} for r in result["selected"]["samples"][:3]]
        (args.run_dir/"report-samples.json").write_text(json.dumps(samples,ensure_ascii=False,indent=2))
    else:
        save_samples(args.run_dir, model, tokenizer, device, [(row["prompt"], [tokenizer.BOS]+tokenizer.encode(row["prompt"])+[tokenizer.SEP]) for row in validation[:3]])
    print(f"Relatório: {create_report(args.run_dir)}", flush=True)
    print(f'Acertos exatos: {baseline["correct"]}/{baseline["total"]} -> {result["selected"]["correct"]}/{result["selected"]["total"]}', flush=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data", type=Path, default=Path("ai/data/authored/instructions.jsonl"))
    parser.add_argument("--init-from", type=Path, required=True)
    parser.add_argument("--compare-with", type=Path, help="Checkpoint local anterior avaliado nos mesmos pedidos novos.")
    parser.add_argument("--run-dir", type=Path, required=True)
    parser.add_argument("--steps", type=int, default=2000)
    parser.add_argument("--batch-size", type=int, default=8)
    parser.add_argument("--learning-rate", type=float, default=.0001)
    parser.add_argument("--eval-every", type=int, default=200)
    parser.add_argument("--device", choices=["auto", "mps", "cpu"], default="auto")
    args = parser.parse_args()
    try: run(args)
    except (ValueError, OSError) as error: parser.exit(1, f"Erro: {error}\n")


if __name__ == "__main__": main()
