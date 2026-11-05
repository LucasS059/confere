"""Treino autoral de localização de evidência; avaliação anterior congelada."""
import argparse
import hashlib
import json
import random
from pathlib import Path
from collections import Counter
import torch
from confere_ai.instruct import load_instructions
from confere_ai.tokenizer import ByteBPE
from prepare_long_contrasts import template_rows, MARKER, BACKGROUNDS
from prepare_document_contrasts import TOPICS
from prepare_document_lexical import LEXICAL


def position_rows(tokenizer,count=120):
    rng=random.Random(510);rows=[]
    for i in range(count):
        feature=rng.choice(TOPICS["train"]);forms=rng.choice(LEXICAL)
        # Mesma evidência em cada posição; o identificador deve acompanhar a fonte.
        for position in range(4):
            texts=[(rng.choice(BACKGROUNDS)+f" Registro {i}-{j}. ")*(1+i%4) for j in range(3)]
            texts.insert(position,f"Registro {i}. "+MARKER)
            units=[dict(id=f"paragraph:{j+1}",text=t) for j,t in enumerate(texts)]
            rows.extend(template_rows(units,feature,f"evidence-train-{i}-{position}",tokenizer,forms,"evidence_position"))
    return rows


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument("output",type=Path)
    p.add_argument("--source",type=Path,required=True);p.add_argument("--checkpoint",type=Path,required=True)
    a=p.parse_args()
    if a.output.exists():p.error("Saída deve ser nova.")
    source,fingerprint=load_instructions(a.source)
    checkpoint=torch.load(a.checkpoint,map_location="cpu",weights_only=True)
    generated=position_rows(ByteBPE(checkpoint["merges"]))
    seen={r["prompt"].strip().casefold() for r in source};new=[]
    for row in generated:
        key=row["prompt"].strip().casefold()
        if key not in seen:new.append(row);seen.add(key)
    a.output.mkdir(parents=True);path=a.output/"examples.jsonl"
    path.write_text("".join(json.dumps(r,ensure_ascii=False)+"\n" for r in source+new))
    rows,_=load_instructions(path)
    assert [r for r in rows if r["split"]!="train"]==[r for r in source if r["split"]!="train"]
    manifest=dict(source_sha256=fingerprint,dataset_sha256=hashlib.sha256(path.read_bytes()).hexdigest(),
                  added=len(new),statuses=dict(Counter(r["task"] for r in new)),
                  note="Somente treino aumentado; avaliação idêntica. Templates autorais de localização, não TCCs reais.")
    (a.output/"manifest.json").write_text(json.dumps(manifest,ensure_ascii=False,indent=2))
    print(json.dumps(manifest),flush=True)


if __name__=="__main__":main()
