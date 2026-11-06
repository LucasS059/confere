"""Amplia formas de conversa sem alterar os grupos reservados existentes."""
import argparse
import hashlib
import json
import random
import shutil
from collections import Counter
from pathlib import Path
from confere_ai.instruct import load_instructions
from build_conversation_flow import build
from prepare_document_lexical import paired_documents, balanced_replay

FORMS={
    "hello":["e aí, bora trocar ideia","fala Confere, tudo certo?"],
    "identity":["como q vc se chama?","qual era teu nome, hein?"],
    "well":["tô bem sim, valeu","comigo tá tranquilo"],
    "absent":["tô sem projeto por enquanto","não comecei projeto nenhum"],
    "insist":["eu falei q tô sem projeto","não insista em projeto, pfv"],
    "switch":["deixa isso pra lá, muda o papo","quero falar de outra coisa agora"],
    "topic":["vamos bater papo sobre {}","tô afim de conversar sobre {}"],
    "recall":["qual assunto a gente tá conversando?","qual tema eu tinha escolhido?"],
    "have":["já tenho projeto agora","mudou: tô com um projeto"],
    "state":["como tá a situação do meu projeto?","o que eu falei do projeto?"],
    "correct":["falei errado: tô sem projeto","na real eu ainda não tenho projeto"],
    "repair":["pera, não foi isso q eu quis dizer","ce entendeu errado"],
    "close":["vou nessa, flw","chega por hoje, até logo"]}

FUNCTIONS=["pra que vc foi criado?","pode me dizer oq voce faz?","descreve sua função, pfv",
           "o que tu consegue fazer?","me explica pra que serve esse assistente?","conta pra mim qual é sua função"]


def recovery_rows():
    generated=[r for r in build(FORMS) if r["split"]=="train" and r["id"].startswith("flow-")]
    rows=[dict(r,id="recovery-"+r["id"],project_id="recovery-"+r["project_id"],response_tokens=256) for r in generated]
    rng=random.Random(317)
    contexts=[r["history"][-3:] for r in rows]
    for i in range(2400):
        history=rng.choice(contexts)
        group=f"recovery-function-{i}"
        rows.append(dict(id=group,project_id=group,split="train",task="conversation_capability",
                         history=history,turn_index=0,prompt=rng.choice(FUNCTIONS),
                         target="Sou um experimento para apoiar a conferência de projetos.",response_tokens=256,
                         provenance=dict(kind="synthetic_authored",note="Função em contextos variados; sem revisão humana. Somente treino.")))
    return rows


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument("output",type=Path)
    p.add_argument("--source",type=Path,required=True);args=p.parse_args()
    if args.output.exists():p.error("Saída deve ser nova.")
    source,fingerprint=load_instructions(args.source)
    replay=balanced_replay(source,600)
    reserved=[r for r in source if r["split"]!="train" and r["task"].startswith("conversation_")]
    public=[r for r in source if r["split"]=="train" and r["task"] in ("human_dialogue","public_dialogue")]
    rows=paired_documents()+replay+reserved+public
    contexts={json.dumps([r.get("history",[]),r["prompt"].strip().casefold()],ensure_ascii=False):(r["split"],r["target"]) for r in rows}
    added=0
    for row in recovery_rows():
        key=json.dumps([row["history"],row["prompt"].strip().casefold()],ensure_ascii=False)
        if key in contexts and contexts[key]!=(row["split"],row["target"]):
            # Descartar só um turno quebraria a sequência inteira.
            raise ValueError("Novo diálogo colidiu com um alvo ou grupo reservado.")
        contexts[key]=(row["split"],row["target"]);rows.append(row);added+=1
    args.output.mkdir(parents=True);path=args.output/"examples.jsonl"
    path.write_text("".join(json.dumps(r,ensure_ascii=False)+"\n" for r in rows));load_instructions(path)
    manifest=json.loads((args.source.parent/"manifest.json").read_text())
    manifest.update(variant="conversation-recovery",source_sha256=fingerprint,
                    dataset_sha256=hashlib.sha256(path.read_bytes()).hexdigest(),
                    splits=dict(Counter(r["split"] for r in rows)),replay_train=len(replay),
                    recovery_added=added,external_train=len(public),
                    public_train=sum(r["task"]=="public_dialogue" for r in public),
                    human_train=sum(r["task"]=="human_dialogue" for r in public),document_train=6000,
                    note="Validação/teste autorais congelados; validação repetidamente consultada. Fontes públicas somente em treino; sem pesos externos.")
    manifest["upstream_filters"]=manifest.pop("filters",{})
    manifest["filters"]={"human_train":manifest["human_train"],"human_validation":0,"human_test":0}
    if (args.source.parent/"reserved-public.jsonl").exists():
        shutil.copyfile(args.source.parent/"reserved-public.jsonl",args.output/"reserved-public.jsonl")
    (args.output/"manifest.json").write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+"\n")
    print(json.dumps({k:manifest[k] for k in ("dataset_sha256","splits","replay_train","recovery_added","public_train","document_train")},ensure_ascii=False))


if __name__=="__main__":main()
