"""Variações lexicais de treino e replay estratificado; avaliação congelada."""
import argparse
import hashlib
import json
import random
from collections import defaultdict, Counter
from pathlib import Path
from confere_ai.instruct import load_instructions
from prepare_document_contrasts import documents, FORMS

LEXICAL=FORMS["train"]+[
    ("O documento registra presença de {}.","O documento registra ausência de {}."),
    ("A equipe confirmou a existência de {}.","A equipe confirmou a inexistência de {}."),
    ("Há suporte para {}.","Falta suporte para {}."),
    ("A especificação prevê {}.","A especificação exclui {}."),
    ("O relatório indica presença de {}.","O relatório indica ausência de {}.")]


def balanced_replay(source, per_family=300):
    groups=defaultdict(list)
    for row in source:
        if row["split"]=="train" and row["task"].startswith("conversation_"):
            groups[row["project_id"]].append(row)
    by_task=defaultdict(list)
    for name,rows in groups.items():
        for task in {r["task"] for r in rows}:by_task[task].append(name)
    rng=random.Random(315);selected=set();result=[];counts=Counter()
    for task in sorted(by_task):
        names=by_task[task];rng.shuffle(names)
        for name in names:
            if counts[task]>=per_family:break
            if name in selected:continue
            selected.add(name);result.extend(groups[name]);counts.update(r["task"] for r in groups[name])
    return result


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument("output",type=Path)
    p.add_argument("--conversations",type=Path,required=True);args=p.parse_args()
    if args.output.exists():p.error("Saída deve ser nova.")
    source,fingerprint=load_instructions(args.conversations)
    replay=balanced_replay(source)
    reserved=[r for r in source if r["split"]!="train" and r["task"].startswith("conversation_")]
    rows=documents(LEXICAL)+replay+reserved
    args.output.mkdir(parents=True);target=args.output/"examples.jsonl"
    target.write_text("".join(json.dumps(r,ensure_ascii=False)+"\n" for r in rows));load_instructions(target)
    manifest=dict(source_sha256=fingerprint,dataset_sha256=hashlib.sha256(target.read_bytes()).hexdigest(),
                  replay_train=len(replay),replay_families=dict(Counter(r["task"] for r in replay)),
                  document_train=3000,note="Somente treino expandido; validação/teste congelados, validação já consultada em iterações. Teste não usado para ajustar.")
    (args.output/"manifest.json").write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+"\n")
    print(json.dumps(manifest,ensure_ascii=False))


if __name__=="__main__":main()
