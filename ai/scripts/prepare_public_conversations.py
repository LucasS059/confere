"""Mistura experimento autoral e diálogos públicos gerados por modelos, sem pesos externos."""
import argparse
import hashlib
import json
import random
from collections import Counter
from pathlib import Path
import torch
from confere_ai.instruct import load_instructions
from confere_ai.tokenizer import ByteBPE
from confere_ai.training_data import encode_sample

SOURCE="https://huggingface.co/datasets/nicholasKluge/instruct-aira-dataset-v3"
REVISION="1ca52371453cc9e52b650ba4314f2ca0a69f58ba"
SHA="fc43d5033a3f00740eb595cceeb633562b0d593d8a8eff42117fda52825c162a"


def public_paths(conversation, identifier):
    if len(conversation)%2 or any(m["role"]!=("user" if i%2==0 else "assistant") or not m["content"].strip() for i,m in enumerate(conversation)):
        return []
    digest=hashlib.sha256(json.dumps(conversation,ensure_ascii=False,sort_keys=True).encode()).hexdigest()
    bucket=int(digest,16)%100
    split="test" if bucket<5 else "validation" if bucket<10 else "train"
    return [dict(id=f"aira-{identifier}-{i}",project_id="aira-"+digest,split=split,task="public_dialogue",
                 history=[[conversation[j]["content"].strip(),conversation[j+1]["content"].strip()] for j in range(0,i-1,2)],
                 prompt=conversation[i-1]["content"].strip(),target=conversation[i]["content"].strip(),turn_index=0,response_tokens=256,
                 provenance=dict(kind="public_model_generated",source=SOURCE,revision=REVISION,license="Apache-2.0",
                                 conversation_id=identifier,assistant_index=i,note="Resposta gerada por modelo; sem anotação humana segundo o card. Sem revisão humana local.")) for i in range(1,len(conversation),2)]


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("output",type=Path)
    parser.add_argument("--base",type=Path,required=True)
    parser.add_argument("--source",type=Path,default=Path("ai/data/private/aira-v3-pt"))
    parser.add_argument("--tokenizer-from",type=Path,required=True)
    args=parser.parse_args()
    if args.output.exists():parser.error("Saída deve ser nova.")
    import pyarrow.parquet as pq
    source=args.source/"portuguese.parquet"
    if hashlib.sha256(source.read_bytes()).hexdigest()!=SHA or (args.source/"revision.txt").read_text().strip()!=REVISION:
        parser.error("Fonte não corresponde ao snapshot revisado.")
    rows,base_hash=load_instructions(args.base)
    tokenizer=ByteBPE(torch.load(args.tokenizer_from,map_location="cpu",weights_only=True)["merges"])
    counts=Counter();reserved=[];seen_conversations=set()
    contexts={json.dumps([r["history"],r["prompt"].strip().casefold()],ensure_ascii=False):(r["split"],r["target"]) for r in rows}
    def add(row):
        key=json.dumps([row["history"],row["prompt"].strip().casefold()],ensure_ascii=False)
        if key in contexts:counts["duplicate_context"]+=1;return False
        try:encode_sample(row,tokenizer,1024)
        except ValueError:counts["context_or_response_excluded"]+=1;return False
        contexts[key]=(row["split"],row["target"])
        rows.append(row);return True
    # Reforce retenção com cópias explícitas dos exemplos autorais legados.
    replay=[r for r in rows if r["split"]=="train" and r["provenance"]["kind"]=="synthetic_authored" and not r["id"].startswith("flow-")]
    rows.extend(dict(r,id="replay-"+r["id"],project_id="replay-"+r["project_id"]) for r in replay)
    counts["legacy_replay_rows"]=len(replay)
    rng=random.Random(11519)
    histories=[r["history"] for r in rows if r["split"]=="train" and r["id"].startswith("flow-")]
    known=[["ola","Olá! Sou o Confere."],["como vai?","Estou pronto para ajudar. E você?"],["vou bem tambem, obrigado","Que bom! Sobre o que você quer conversar?"],["qual seu nome mesmo?","Sou o Confere."]]
    for i in range(5000):
        history=known if i%5==0 else rng.choice(histories)
        prompt,target=rng.choice([
            (q,"Olá! Sou o Confere.") for q in ["oi, vamos bater papo","oi de novo","olá, novamente","voltei, olá","bom dia outra vez","oi, mais uma vez","oi"]]
            +[(q,"Posso ter entendido errado. Pode me dizer o que devo corrigir?") for q in ["ue","vc é burro?","acho que você bugou"]]
            +[(q,"Não entendi. Pode escrever uma mensagem mais completa?") for q in ["a","hm","?","..."]])
        group=f"flow-context-train-{i}"
        row=dict(id=group+"-0",project_id=group,split="train",task="conversation_flow_repair",history=history,turn_index=0,
                 prompt=prompt,target=target,response_tokens=256,provenance=dict(kind="synthetic_authored",note="Retomada e reparo em posições variadas; casos conhecidos incluídos, sem revisão humana."))
        if add(row):counts["context_variants_added"]+=1
    for batch in pq.ParquetFile(source).iter_batches(batch_size=128):
        for item in batch.to_pylist():
            paths=public_paths(item["conversations"],item["conversation_id"])
            if not paths:counts["invalid_conversation"]+=1;continue
            if paths[0]["project_id"] in seen_conversations:counts["duplicate_conversation"]+=1;continue
            seen_conversations.add(paths[0]["project_id"])
            for row in paths:
                # Identidades de outros assistentes não são a persona deste projeto.
                if any(name in row["target"].casefold() for name in ("chatgpt","openai","aira","laion")):
                    counts["other_assistant_identity"]+=1;continue
                try:encode_sample(row,tokenizer,1024)
                except ValueError:counts["public_too_long"]+=1;continue
                if row["split"]!="train":reserved.append(row);counts["reserved_"+row["split"]]+=1;continue
                if add(row):counts["public_train_added"]+=1
    args.output.mkdir(parents=True)
    target=args.output/"examples.jsonl"
    target.write_text("".join(json.dumps(r,ensure_ascii=False)+"\n" for r in rows))
    load_instructions(target)
    (args.output/"reserved-public.jsonl").write_text("".join(json.dumps(r,ensure_ascii=False)+"\n" for r in reserved))
    manifest=json.loads((args.base.parent/"manifest.json").read_text())
    manifest.update(variant="flow-public",base_sha256=base_hash,dataset_sha256=hashlib.sha256(target.read_bytes()).hexdigest(),splits=dict(Counter(r["split"] for r in rows)),
                    additional_source=dict(source=SOURCE,revision=REVISION,license="Apache-2.0",sha256=SHA,kind="public_model_generated",counts=dict(counts),note="Somente treino público é mesclado; demais caminhos reservados separadamente. Filtros automáticos, sem revisão humana de qualidade."))
    (args.output/"manifest.json").write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+"\n")
    print(json.dumps(manifest,ensure_ascii=False),flush=True)


if __name__=="__main__":main()
