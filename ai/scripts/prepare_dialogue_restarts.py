"""Contrasta retomada, encerramento e mensagens incompletas no mesmo contexto."""
import argparse
import hashlib
import json
import random
import shutil
from collections import Counter
from pathlib import Path
import torch
from confere_ai.instruct import load_instructions
from confere_ai.tokenizer import ByteBPE
from confere_ai.training_data import encode_sample


def restart_rows(rows, count=4000):
    rng=random.Random(11729)
    pool=[r for r in rows if r["split"]=="train" and (r["id"].startswith("flow-train-") or r["id"].startswith("flow-expanded-train-"))]
    if not pool:raise ValueError("Não há diálogos autorais de treino.")
    contexts={json.dumps([r["history"],r["prompt"].strip().casefold()],ensure_ascii=False):(r["split"],r["target"]) for r in rows}
    result=[]
    def add(prompt,target,history):
        key=json.dumps([history,prompt.strip().casefold()],ensure_ascii=False)
        if key in contexts and contexts[key]!=("train",target):return
        contexts[key]=("train",target)
        group=f"restart-train-{len(result)}"
        result.append(dict(id=group+"-0",project_id=group,split="train",task="conversation_flow_restart",history=history,
                           turn_index=0,prompt=prompt,target=target,response_tokens=256,
                           provenance=dict(kind="synthetic_authored",note="Intenções contrastadas no mesmo histórico, inclusive após encerramento; sem revisão humana.")))
    for _ in range(count):
        row=rng.choice(pool)
        history=row["history"]+[[row["prompt"],row["target"]]]
        if rng.random()<.5:
            history=history+[["vou sair, até mais","Tudo bem. Podemos conversar quando você quiser."]]
        hello=rng.choice(["oi","olá","e aí","opa","bom dia"])
        suffix=rng.choice(["voltei","estou de volta","vamos conversar","bora conversar","bora bater papo","outra vez","mais uma vez","novamente","de novo por aqui"])
        add(f"{hello}, {suffix}","Olá! Sou o Confere.",history)
        add(rng.choice(["tchau","paramos por enquanto","até mais","vamos encerrar por agora","agora podemos parar","não preciso de ajuda agora"]),"Tudo bem. Podemos conversar quando você quiser.",history)
        add(rng.choice(["a","hm","?","não entendi"]),"Não entendi. Pode escrever uma mensagem mais completa?",history)
        add("obrigado o que","Eu apenas cumprimentei você.",history+[["oi","Olá! Sou o Confere."]])
        add("obrigado o que","Eu me confundi. Você apenas me cumprimentou.",history+[["oi","Obrigado!"]])
    return result


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("output",type=Path)
    parser.add_argument("--base",type=Path,required=True)
    parser.add_argument("--tokenizer-from",type=Path,required=True)
    args=parser.parse_args()
    if args.output.exists():parser.error("Saída deve ser nova.")
    rows,base_hash=load_instructions(args.base)
    extra=restart_rows(rows)
    tokenizer=ByteBPE(torch.load(args.tokenizer_from,map_location="cpu",weights_only=True)["merges"])
    for row in extra:encode_sample(row,tokenizer,1024)
    rows.extend(extra)
    args.output.mkdir(parents=True)
    target=args.output/"examples.jsonl"
    target.write_text("".join(json.dumps(r,ensure_ascii=False)+"\n" for r in rows))
    load_instructions(target)
    shutil.copyfile(args.base.parent/"reserved-public.jsonl",args.output/"reserved-public.jsonl")
    manifest=json.loads((args.base.parent/"manifest.json").read_text())
    manifest.update(variant="flow-restarts",base_sha256=base_hash,restart_rows=len(extra),splits=dict(Counter(r["split"] for r in rows)),dataset_sha256=hashlib.sha256(target.read_bytes()).hexdigest())
    (args.output/"manifest.json").write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+"\n")
    print(json.dumps(manifest,ensure_ascii=False),flush=True)


if __name__=="__main__":main()
