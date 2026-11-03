"""Validação exploratória da conversa do final, sem consultar teste."""
import argparse
import json
from pathlib import Path
import torch
from confere_ai.instruct import load_instructions, score
from confere_ai.report import create_report
from evaluate_conversation_flow import load_model
from evaluate_document_contrasts import metrics
from evaluate_informal_dialogues import capture, PROMPTS


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument("run_dir",type=Path)
    root=p.parse_args().run_dir;output=root/"final-conversation-validation.json"
    if output.exists():p.error("Validação existente.")
    info=json.loads((root/"run.json").read_text());rows,fingerprint=load_instructions(Path(info["data"]))
    if fingerprint!=info["dataset_fingerprint"]:raise ValueError("Corpus alterado.")
    torch.set_num_threads(4);model,tokenizer,step=load_model(root/"last.pt")
    result=score(model,tokenizer,[r for r in rows if r["split"]=="validation" and r["task"].startswith("conversation_")],"mps",context_limit=1024)
    record=dict(checkpoint=str(root/"last.pt"),step=step,metrics=metrics(result,"conversation_"),result=result,
                captures=capture(model,tokenizer,PROMPTS),test_used=False,
                note="Exploratório após detectar 180/180 documentos no final. Não muda seleção por loss nem libera teste reservado.")
    output.write_text(json.dumps(record,ensure_ascii=False,indent=2)+"\n")
    print(json.dumps(record["metrics"],ensure_ascii=False),flush=True);print(create_report(root))


if __name__=="__main__":main()
