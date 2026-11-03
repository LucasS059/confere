"""Afirmação/negação com distratores e replay de conversas completas de treino."""
import argparse
import hashlib
import json
import random
from collections import defaultdict
from pathlib import Path
from confere_ai.grounding import prompt_for
from confere_ai.instruct import load_instructions

FORMS={
    "train":[("O projeto inclui {}.","O projeto não inclui {}."),
             ("A entrega apresenta {}.","A entrega não apresenta {}."),
             ("O escopo contempla {}.","Não existe suporte para {}.")],
    "validation":[("Foi confirmada a presença de {}.","Foi confirmada a ausência de {}.")],
    "test":[("Há evidência explícita de {}.","Há indicação explícita de ausência de {}.")]}
TOPICS={"train":["testes","backup","cronograma","orçamento","cadastro","login"],
        "validation":["monitoramento","relatórios","busca"],
        "test":["auditoria","importação","exportação"]}


def documents():
    rows=[]
    for split,count in (("train",3000),("validation",180),("test",90)):
        rng=random.Random({"train":311,"validation":312,"test":313}[split])
        for i in range(count):
            feature=rng.choice(TOPICS[split]);status=("atendido","nao_atendido","evidencia_insuficiente")[i%3]
            pos,neg=rng.choice(FORMS[split])
            texts=[f"Equipe: {rng.randint(100000,999999)}.","Tema: biblioteca.","O projeto inclui acessibilidade."]
            texts.append(pos.format(feature) if status=="atendido" else neg.format(feature)
                         if status=="nao_atendido" else "A equipe documentou a reunião inicial.")
            rng.shuffle(texts)
            units=[dict(id=f"page:{j+1}",text=t) for j,t in enumerate(texts)]
            unit=next((u["id"] for u in units if feature in u["text"]),None)
            requirement=f"O projeto deve incluir {feature}."
            rows.append(dict(id=f"contrast-{split}-{i}",project_id=f"contrast-{split}-{i}",split=split,
                             task="grounded_"+status,requirement=requirement,units=units,document=f"fiction-{split}-{i}.pdf",
                             prompt=prompt_for(requirement,units),target=json.dumps(dict(status=status,unit=unit),ensure_ascii=False),
                             provenance=dict(kind="synthetic_authored",note="Documento fictício; rótulo por construção. Sem revisão humana.")))
    return rows


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("output",type=Path);parser.add_argument("--conversations",type=Path,required=True)
    args=parser.parse_args()
    if args.output.exists():parser.error("Saída deve ser nova.")
    source,fingerprint=load_instructions(args.conversations)
    groups=defaultdict(list)
    for row in source:
        if row["task"].startswith("conversation_") and row["split"]=="train":groups[row["project_id"]].append(row)
    names=list(groups);random.Random(314).shuffle(names)
    replay=[]
    for name in names:
        replay.extend(groups[name])
        if len(replay)>=3000:break
    # Todos os turnos dos grupos escolhidos são mantidos, com orçamento nativo.
    reserved=[r for r in source if r["split"]!="train" and r["task"].startswith("conversation_")]
    rows=documents()+replay+reserved
    args.output.mkdir(parents=True)
    path=args.output/"examples.jsonl"
    path.write_text("".join(json.dumps(r,ensure_ascii=False)+"\n" for r in rows))
    load_instructions(path)
    manifest=dict(source_sha256=fingerprint,dataset_sha256=hashlib.sha256(path.read_bytes()).hexdigest(),
                  replay_train=len(replay),document_train=3000,document_validation=180,document_test=90,
                  note="Redação antiga de validação vira treino conhecido; novas redações reservadas não são benchmark independente de semântica.")
    (args.output/"manifest.json").write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+"\n")
    print(json.dumps(manifest))


if __name__=="__main__":main()
