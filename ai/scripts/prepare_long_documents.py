"""Currículo autoral de trechos longos, com replay e avaliação anterior intacta."""
import argparse
import hashlib
import json
import random
from collections import Counter
from pathlib import Path

import torch
from confere_ai.grounding import prompt_for
from confere_ai.instruct import load_instructions
from confere_ai.project_review import input_ids, RESPONSE_TOKENS
from confere_ai.tokenizer import ByteBPE
from prepare_document_contrasts import TOPICS, FORMS

STATUSES=("atendido","nao_atendido","evidencia_insuficiente")
FILLERS={
    "train":["A equipe registrou atividades e decisões da etapa atual.",
             "O grupo discutiu responsabilidades durante a reunião.",
             "A apresentação descreve o tema e a organização do trabalho."],
    "validation":["Os integrantes atualizaram o registro de acompanhamento semanal.",
                  "O encontro encerrou com a distribuição das próximas atividades."]}


def long_rows(tokenizer, split, count):
    rng=random.Random(440 if split=="train" else 441)
    rows=[]
    for i in range(count):
        status=STATUSES[i%3];n=1+(i//3)%4;slot=(i//12)%3
        feature=rng.choice(TOPICS[split]);requirement=f"O projeto deve incluir {feature}."
        group=f"long-{split}-{i}";position=rng.randrange(n)
        forms=FORMS[split];positive,negative=rng.choice(forms)
        statement=(positive if status=="atendido" else negative).format(feature) if status!="evidencia_insuficiente" else "O projeto inclui acessibilidade."
        filler=rng.choice(FILLERS[split])+f" Registro {group}. "
        budget=(384,704,950)[(i//36)%3]

        def units_for(repeats):
            units=[]
            for j in range(n):
                lines=[filler]*repeats
                if j==position:lines.insert((0,len(lines)//2,len(lines))[slot],statement)
                units.append(dict(id=f"page:{j+1}",text=f"Registro {group}-{j}. "+" ".join(lines)))
            return units

        low,high,best=0,32,0
        while low<=high:
            middle=(low+high)//2
            if len(input_ids(requirement,units_for(middle),tokenizer))<=budget:
                best=middle;low=middle+1
            else:high=middle-1
        units=units_for(best)
        assert len(input_ids(requirement,units,tokenizer))+RESPONSE_TOKENS<=1024
        rows.append(dict(id=group,project_id=group,split=split,task="grounded_"+status,
                         requirement=requirement,units=units,document=group+".pdf",
                         prompt=prompt_for(requirement,units),
                         target=json.dumps(dict(status=status,unit=None if status=="evidencia_insuficiente" else f"page:{position+1}"),ensure_ascii=False),
                         provenance=dict(kind="synthetic_authored",note="Trecho fictício longo; rótulo por construção. Sem revisão independente.")))
    return rows


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("output",type=Path);p.add_argument("--source",type=Path,required=True)
    p.add_argument("--checkpoint",type=Path,required=True);args=p.parse_args()
    if args.output.exists():p.error("Saída deve ser nova.")
    source,fingerprint=load_instructions(args.source)
    checkpoint=torch.load(args.checkpoint,map_location="cpu",weights_only=True)
    if checkpoint["config"]["block_size"]!=1024:raise ValueError("Este currículo exige contexto 1024.")
    tokenizer=ByteBPE(checkpoint["merges"])
    # Replay curto estratificado, sem alterar validação/teste ou os turnos de conversa.
    by_status={s:[r for r in source if r["split"]=="train" and r["task"]=="grounded_"+s] for s in STATUSES}
    short=[]
    for pool in by_status.values():
        random.Random(442).shuffle(pool);short.extend(pool[:200])
    retained=[r for r in source if r["split"]!="train" or not r["task"].startswith("grounded_")]
    new=long_rows(tokenizer,"train",1440)+long_rows(tokenizer,"validation",144)
    rows=retained+short+new
    args.output.mkdir(parents=True);path=args.output/"examples.jsonl"
    path.write_text("".join(json.dumps(r,ensure_ascii=False)+"\n" for r in rows))
    load_instructions(path)
    lengths=[len(input_ids(r["requirement"],r["units"],tokenizer)) for r in new]
    manifest=dict(source_sha256=fingerprint,dataset_sha256=hashlib.sha256(path.read_bytes()).hexdigest(),
                  checkpoint_sha256=hashlib.sha256(args.checkpoint.read_bytes()).hexdigest(),
                  counts=dict(Counter(r["split"]+":"+r["task"] for r in rows)),
                  long_input_tokens_min=min(lengths),long_input_tokens_max=max(lengths),
                  note="Novos trechos longos autorais, tópicos e redações separados por split; receitas compartilhadas. Avaliação antiga preservada. Teste não consultado para ajuste.")
    (args.output/"manifest.json").write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+"\n")
    print(json.dumps(manifest,ensure_ascii=False),flush=True)


if __name__=="__main__":main()
