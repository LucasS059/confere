"""Mistura rastreável de templates e respostas humanas OpenAssistant curtas."""
import argparse
import gzip
import hashlib
import json
from collections import Counter
from pathlib import Path
import torch
from build_conversations import build
from confere_ai.tokenizer import ByteBPE
from confere_ai.training_data import encode_sample


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("output",type=Path)
    parser.add_argument("--source",type=Path,default=Path("ai/data/private/oasst1-pt"))
    parser.add_argument("--tokenizer-from",type=Path,default=Path("ai/runs/instruction-v2-refine-2026-11-02/best.pt"))
    parser.add_argument("--variant",choices=["initial","mixed"],default="initial")
    args=parser.parse_args()
    if args.output.exists(): parser.error("Saída deve ser nova.")
    source=args.source/"2023-04-12_oasst_ready.messages.jsonl.gz"
    messages={}
    with gzip.open(source,"rt") as f:
        for line in f:
            row=json.loads(line)
            if row["lang"]=="pt-BR": messages[row["message_id"]]=row
    def approved(row):
        labels=row.get("labels") or {}
        return (row.get("review_result") is True and not row.get("deleted") and not row.get("synthetic")
                and (row["role"]!="assistant" or (row.get("rank")==0 and labels.get("quality",{}).get("value",0)>=.6
                     and labels.get("fails_task",{}).get("value",0)==0)))
    if args.variant=="mixed":
        from build_conversation_mix import build as mixed
        rows=mixed()
    else: rows=build()
    counts=Counter()
    tokenizer=ByteBPE(torch.load(args.tokenizer_from,map_location="cpu",weights_only=True)["merges"])
    keys={json.dumps([r["history"],r["prompt"].strip().casefold()],ensure_ascii=False) for r in rows}
    revision=(args.source/"revision.txt").read_text().strip()
    for message in messages.values():
        if message["role"]!="assistant" or not approved(message): continue
        chain=[]; current=message; visited=set()
        while current is not None:
            if current["message_id"] in visited or not approved(current): break
            visited.add(current["message_id"]); chain.append(current)
            if current.get("parent_id") is None: break
            current=messages.get(current["parent_id"])
        chain.reverse()
        if not chain or chain[0].get("parent_id") is not None or len(chain)%2 or any(r["role"]!=("prompter" if i%2==0 else "assistant") for i,r in enumerate(chain)):
            counts["missing_or_unapproved_path"]+=1;continue
        tree=message["message_tree_id"]
        bucket=int(hashlib.sha256(tree.encode()).hexdigest(),16)%100
        split="test" if bucket<5 else "validation" if bucket<10 else "train"
        history=[[chain[i]["text"].strip(),chain[i+1]["text"].strip()] for i in range(0,len(chain)-2,2)]
        row={"id":"oasst-"+message["message_id"],"project_id":"oasst-tree-"+tree,"split":split,"task":"human_dialogue",
             "history":history,"turn_index":0,"prompt":chain[-2]["text"].strip(),"target":message["text"].strip(),
             "provenance":{"kind":"human_openassistant","source":"https://huggingface.co/datasets/OpenAssistant/oasst1",
                 "license":"Apache-2.0","revision":revision,"message_ids":[r["message_id"] for r in chain],
                 "note":"Resposta humana, rank 0, revisada na fonte; sem revisão humana local."}}
        key=json.dumps([history,row["prompt"].casefold()],ensure_ascii=False)
        if key in keys: counts["duplicate_context"]+=1;continue
        try: encode_sample(row,tokenizer,256)
        except ValueError: counts["context_or_answer_too_long"]+=1;continue
        keys.add(key);rows.append(row);counts["human_"+split]+=1
    for row in rows: encode_sample(row,tokenizer,256)
    args.output.mkdir(parents=True)
    target=args.output/"examples.jsonl"
    target.write_text("".join(json.dumps(r,ensure_ascii=False)+"\n" for r in rows))
    manifest={"source":"https://huggingface.co/datasets/OpenAssistant/oasst1","revision":revision,"license":"Apache-2.0",
              "source_sha256":hashlib.sha256(source.read_bytes()).hexdigest(),"source_pt_messages":len(messages),
              "filters":dict(counts),"splits":dict(Counter(r["split"] for r in rows)),
              "variant":args.variant,"dataset_sha256":hashlib.sha256(target.read_bytes()).hexdigest(),"note":"Respostas humanas longas foram excluídas; corpus não representativo. Árvores separadas antes da filtragem; sem deduplicação semântica."}
    (args.output/"manifest.json").write_text(json.dumps(manifest,ensure_ascii=False,indent=2))
    print(json.dumps(manifest,ensure_ascii=False,indent=2))


if __name__=="__main__": main()
