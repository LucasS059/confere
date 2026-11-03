"""Diagnóstico exploratório do último checkpoint, sem seleção nem teste."""
import argparse
import json
from pathlib import Path
import torch
from confere_ai.instruct import load_instructions, score
from confere_ai.report import create_report
from evaluate_conversation_flow import load_model
from evaluate_document_contrasts import metrics


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument("run_dir",type=Path)
    root=p.parse_args().run_dir;output=root/"last-document-diagnostic.json"
    if output.exists():p.error("Diagnóstico existente.")
    info=json.loads((root/"run.json").read_text());rows,fingerprint=load_instructions(Path(info["data"]))
    if fingerprint!=info["dataset_fingerprint"]:raise ValueError("Corpus alterado.")
    torch.set_num_threads(4);model,tokenizer,step=load_model(root/"last.pt")
    result=score(model,tokenizer,[r for r in rows if r["split"]=="validation" and r["task"].startswith("grounded_")],"mps")
    record=dict(step=step,metrics=metrics(result,"grounded_"),result=result,test_used=False)
    output.write_text(json.dumps(record,ensure_ascii=False,indent=2)+"\n")
    print(json.dumps(record["metrics"],ensure_ascii=False),flush=True);print(create_report(root))


if __name__=="__main__":main()
