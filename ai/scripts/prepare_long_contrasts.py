"""Pares de polaridade e fragmentos da CLI; só o split de treino é alterado."""
import argparse
import hashlib
import json
import random
from collections import Counter
from pathlib import Path

import torch
from confere_ai.grounding import prompt_for
from confere_ai.instruct import load_instructions
from confere_ai.project_review import batches_for, input_ids
from confere_ai.tokenizer import ByteBPE
from prepare_document_contrasts import TOPICS, FORMS
from prepare_document_lexical import LEXICAL
from prepare_long_documents import long_rows, STATUSES

MARKER="<frase-autoral>"
BACKGROUNDS=["A equipe organizou as atividades da semana.",
             "O grupo registrou a distribuição das tarefas na ata.",
             "A apresentação descreve a organização das reuniões.",
             "Os integrantes discutiram o andamento das atividades."]


def template_rows(units,feature,group,tokenizer,forms,profile):
    requirement=f"O projeto deve incluir {feature}."
    assert sum(u["text"].count(MARKER) for u in units)==1
    rows=[]
    for status,statement in zip(STATUSES,[forms[0].format(feature),forms[1].format(feature),f"A equipe discutiu {feature} durante uma reunião."]):
        source=[dict(id=u["id"],text=u["text"].replace(MARKER,statement)) for u in units]
        digest=hashlib.sha256(json.dumps(source,ensure_ascii=False).encode()).hexdigest()
        document=dict(name=group+".pdf",sha256=digest,units=source)
        for number,parts in enumerate(batches_for([document],requirement,tokenizer,1024)):
            aliases=[dict(id=f"page:{j+1}",text=part["text"]) for j,part in enumerate(parts)]
            match=next((u["id"] for u in aliases if statement in u["text"]),None) if status!="evidencia_insuficiente" else None
            local_status=status if match else "evidencia_insuficiente"
            rows.append(dict(id=f"{group}-{status}-{number}",project_id=group,split="train",
                             task="grounded_"+local_status,requirement=requirement,units=aliases,
                             document=document["name"],prompt=prompt_for(requirement,aliases),
                             target=json.dumps(dict(status=local_status,unit=match),ensure_ascii=False),
                             training_profile=profile,
                             provenance=dict(kind="synthetic_authored",note="Trecho fictício gerado pelo loteador da CLI. Polaridades pareadas; rótulo local por construção, sem revisão independente.")))
    return rows


def contrast_rows(tokenizer,count=360):
    rows=[];rng=random.Random(450)
    for i,base in enumerate(long_rows(tokenizer,"train",count)):
        feature=base["requirement"].removeprefix("O projeto deve incluir ").rstrip(".")
        options=[form.format(feature) for pair in FORMS["train"] for form in pair]+["O projeto inclui acessibilidade."]
        units=[dict(u,text=u["text"]) for u in base["units"]]
        for unit in units:
            for statement in options:
                if statement in unit["text"]:
                    unit["text"]=unit["text"].replace(statement,MARKER,1)
                    break
        rows.extend(template_rows(units,feature,f"longpair-train-{i}",tokenizer,rng.choice(LEXICAL),"minimal_pair"))
    for i in range(count//2):
        feature=rng.choice(TOPICS["train"])
        lines=[rng.choice(BACKGROUNDS)+f" Registro {rng.randrange(100000,999999)}." for _ in range(55+i%30)]
        lines.insert((0,len(lines)//2,len(lines))[i%3],MARKER)
        units=[dict(id="page:1",text="\n".join(lines)),
               dict(id="paragraph:1",text=f"Equipe do cenário {i}: apresentação e documentação de atividades."),
               dict(id="table:1:row:1",text="Etapa | Registro da reunião inicial.")]
        rows.extend(template_rows(units,feature,f"fragment-train-{i}",tokenizer,rng.choice(LEXICAL),"cli_fragment"))
    unique={}
    for row in rows:
        key=row["prompt"].strip().casefold()
        if key in unique and unique[key]["target"]!=row["target"]:raise ValueError("Fragmentos idênticos com alvos conflitantes.")
        unique.setdefault(key,row)
    return list(unique.values())


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument("output",type=Path)
    p.add_argument("--source",type=Path,required=True);p.add_argument("--checkpoint",type=Path,required=True)
    args=p.parse_args()
    if args.output.exists():p.error("Saída deve ser nova.")
    source,fingerprint=load_instructions(args.source)
    checkpoint=torch.load(args.checkpoint,map_location="cpu",weights_only=True)
    if checkpoint["config"]["block_size"]!=1024:raise ValueError("Currículo exige contexto 1024.")
    tokenizer=ByteBPE(checkpoint["merges"]);generated=contrast_rows(tokenizer)
    pools={s:[r for r in generated if r["task"]=="grounded_"+s] for s in STATUSES}
    per_status=min(600,min(map(len,pools.values())))
    selected=[]
    for pool in pools.values():random.Random(451).shuffle(pool);selected.extend(pool[:per_status])
    retained=[r for r in source if r["split"]!="train" or not r["task"].startswith("grounded_")]
    short=[r for r in source if r["split"]=="train" and r["task"].startswith("grounded_") and not r["id"].startswith("long-")]
    rows=retained+short+selected
    args.output.mkdir(parents=True);path=args.output/"examples.jsonl"
    path.write_text("".join(json.dumps(r,ensure_ascii=False)+"\n" for r in rows));load_instructions(path)
    assert [r for r in rows if r["split"]!="train"]==[r for r in source if r["split"]!="train"]
    lengths=[len(input_ids(r["requirement"],r["units"],tokenizer)) for r in selected]
    manifest=dict(source_sha256=fingerprint,dataset_sha256=hashlib.sha256(path.read_bytes()).hexdigest(),
                  checkpoint_sha256=hashlib.sha256(args.checkpoint.read_bytes()).hexdigest(),
                  generated=len(generated),selected_per_status=per_status,
                  profiles=dict(Counter(r["training_profile"] for r in selected)),
                  short_replay=len(short),conversation_replay=sum(r["split"]=="train" and "history" in r for r in retained),
                  input_tokens_min=min(lengths),input_tokens_max=max(lengths),
                  note="Somente treino alterado. Trechos positivos/negativos pareados, menções sem comprovação e fragmentos sem evidência. Seleção balanceada por status; nem todos os pares sobrevivem à seleção. Validação e teste idênticos ao snapshot anterior; receitas autorais não representam TCC real.")
    (args.output/"manifest.json").write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+"\n")
    print(json.dumps(manifest,ensure_ascii=False),flush=True)


if __name__=="__main__":main()
