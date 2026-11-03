"""Variações autorais de português informal, aplicadas aos dados de treino."""
import argparse
import hashlib
import json
import random
import re
import shutil
import unicodedata
from collections import Counter
from pathlib import Path
import torch
from confere_ai.instruct import load_instructions
from confere_ai.tokenizer import ByteBPE
from confere_ai.training_data import encode_sample

REPLACEMENTS=[(r"\bpor favor\b",["pfv","pf"]),(r"\bo que\b",["oq","o q","q"]),
              (r"\bvocês\b",["vcs"]),(r"\bvocê\b",["vc","cê","ce","voce"]),
              (r"\bpor que\b",["pq","porq"]),(r"\bporque\b",["pq"]),
              (r"\bnão\b",["n","nao","num"]),(r"\btambém\b",["tb","tbm"]),
              (r"\bestou\b",["to","tô"]),(r"\bestá\b",["ta","tá"]),
              (r"\bobrigado\b",["obg","vlw"]),(r"\bmesmo\b",["msm"])]


def informalize(text,rng):
    for pattern,forms in REPLACEMENTS:
        text=re.sub(pattern,lambda match:rng.choice(forms),text,flags=re.IGNORECASE)
    if rng.random()<.5:text="".join(c for c in unicodedata.normalize("NFD",text) if not unicodedata.combining(c))
    return text


TARGETS={"hello":"Olá! Sou o Confere.","identity":"Sou o Confere.",
         "function":"Sou um experimento para apoiar a conferência de projetos.",
         "scope":"Projetos acadêmicos com requisitos e documentos. A análise de arquivos completos ainda não está validada.",
         "praise":"Valeu! Se quiser, podemos continuar.",
         "negation":"Sem problema. Podemos conversar sem um projeto."}
BANKS={
"train":{
"hello":["oi, bora conversar","e ai confere, blz?","opa, td certo?"],
"identity":["qm é vc?","como c chama?","qual teu nome?","qual seu nome msm?"],
"function":["e oq vc faz?","oq vc faz","q q vc faz?","pra q vc serve?","o que tu faz?","oq ce faz?"],
"scope":["que tipo de projetos?","q tipo de projetos?","tipo quais?","ok, que tipo de projetos?","q projetos vc confere?","e quais projetos?"],
"praise":["boa muleke","boa mlk","daora","vlw","tmj","show de bola"],
"negation":["n tenho projeto","to sem projeto","num tenho projeto","nao tenho projeto n"]},
"validation":{
"hello":["e aí, vamos papear?","opa, vamos trocar ideia?"],
"identity":["me diz qm vc é?","como q c se chama?"],
"function":["o q tu faz aí?","me conta oq ce faz?"],
"scope":["e q tipos de projetos seriam?","quais projetos c consegue conferir?"],
"praise":["boa demais mlk","vlw pela explicacao"],
"negation":["to sem nenhum projeto agr","n tenho um projeto ainda n"]},
"test":{
"hello":["oi, td tranquilo por aí?"],"identity":["qual q eh teu nome msm?"],
"function":["e oq c faz msm?"],"scope":["blz, mas q tipo de projeto vc confere?"],
"praise":["daora demais, vlw ai"],"negation":["por enquanto to sem projeto, blz?"]}}


def extra_rows(rows,augment_count=30000,train_conversations=2400):
    rng=random.Random(13031)
    result=[]
    contexts={json.dumps([r["history"],r["prompt"].strip().casefold()],ensure_ascii=False):(r["split"],r["target"]) for r in rows}
    def add(split,turns,seed,group):
        history=[list(pair) for pair in seed];proposed=[]
        for i,(task,prompt,target) in enumerate(turns):
            key=json.dumps([history,prompt.strip().casefold()],ensure_ascii=False)
            if key in contexts and contexts[key]!=(split,target):return False
            proposed.append((key,dict(id=f"{group}-{i}",project_id=group,split=split,task="conversation_slang_"+task,
                history=[list(pair) for pair in history],turn_index=i,prompt=prompt,target=target,response_tokens=256,
                provenance=dict(kind="synthetic_authored",note="Português informal autoral. Casos relatados incluídos no treino; avaliação por formulações separadas."))))
            history=history+[[prompt,target]]
        for key,row in proposed:contexts[key]=(split,row["target"]);result.append(row)
        return True
    train=[r for r in rows if r["split"]=="train" and r["provenance"]["kind"]=="synthetic_authored" and "memory" not in r["task"]]
    for i in range(augment_count if train else 0):
        row=rng.choice(train);prompt=informalize(row["prompt"],rng)
        if prompt==row["prompt"]:continue
        history=[[informalize(q,rng) if rng.random()<.5 else q,a] for q,a in row["history"]]
        add("train",[("augmentation",prompt,row["target"])],history,f"slang-augment-train-{i}")
    orders=[list(TARGETS),["function","scope","identity","hello","praise","negation"],["negation","hello","function","scope","identity","praise"]]
    for split,count in (("train",train_conversations),("validation",24),("test",24)):
        local=random.Random({"train":13032,"validation":13033,"test":13034}[split])
        for i in range(count):
            order=orders[i%len(orders)]
            turns=[(task,local.choice(BANKS[split][task]),TARGETS[task]) for task in order]
            if not add(split,turns,[],f"slang-dialogue-{split}-{i}"):raise ValueError("Conflito de contexto no novo currículo.")
    return result


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("output",type=Path);parser.add_argument("--base",type=Path,required=True)
    parser.add_argument("--tokenizer-from",type=Path,required=True);args=parser.parse_args()
    if args.output.exists():parser.error("Saída deve ser nova.")
    rows,base_hash=load_instructions(args.base)
    added=extra_rows(rows)
    tokenizer=ByteBPE(torch.load(args.tokenizer_from,map_location="cpu",weights_only=True)["merges"])
    for row in added:encode_sample(row,tokenizer,1024)
    rows.extend(added);args.output.mkdir(parents=True)
    target=args.output/"examples.jsonl";target.write_text("".join(json.dumps(r,ensure_ascii=False)+"\n" for r in rows))
    load_instructions(target)
    shutil.copyfile(args.base.parent/"reserved-public.jsonl",args.output/"reserved-public.jsonl")
    manifest=json.loads((args.base.parent/"manifest.json").read_text())
    manifest.update(variant="informal",base_sha256=base_hash,informal_added=len(added),splits=dict(Counter(r["split"] for r in rows)),dataset_sha256=hashlib.sha256(target.read_bytes()).hexdigest())
    (args.output/"manifest.json").write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+"\n")
    print(json.dumps(manifest,ensure_ascii=False),flush=True)


if __name__=="__main__":main()
