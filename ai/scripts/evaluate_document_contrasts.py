"""Separa objetivos da comparação pareada e mantém teste fora da seleção."""
import argparse
import json
from pathlib import Path
import torch
from confere_ai.instruct import acceptance, load_instructions, score
from confere_ai.report import create_report
from evaluate_conversation_flow import load_model
from evaluate_informal_dialogues import capture, PROMPTS


def metrics(result, prefix):
    rows=[r for r in result["samples"] if r["task"].startswith(prefix)]
    families={}
    for r in rows:
        pair=families.setdefault(r["task"],[0,0]);pair[0]+=r["exact_match"];pair[1]+=1
    return dict(correct=sum(r["exact_match"] for r in rows),total=len(rows),families=families,
                valid=sum(r.get("valid_format",False) for r in rows),
                references=sum(r.get("reference_valid",False) for r in rows))


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument("run_dir",type=Path)
    root=parser.parse_args().run_dir;output=root/"contrast-evaluation.json"
    if output.exists():parser.error("Avaliação existente; preserve o teste.")
    evaluation=json.loads((root/"instruction-evaluation.json").read_text())
    before=metrics(evaluation["baseline"],"conversation_")
    after=metrics(evaluation["selected"],"conversation_")
    docs=metrics(evaluation["selected"],"grounded_")
    doc_pass=(docs["total"]>0 and docs["valid"]==docs["references"]==docs["total"]
              and all(c/t>=.9 for c,t in docs["families"].values()))
    conversation_pass=(after["correct"]>=before["correct"] and all(c/t>=.8 and c>=before["families"][name][0]
                           for name,(c,t) in after["families"].items()))
    result=dict(policy="Comparação pareada 1024/64. Documentos: >=90% em cada status, 100% formato/referências. Conversa: >=80% por família, sem queda por família ou no total ante o modelo informal. Teste somente se ambos passarem. Diagnóstico nativo 1024/256 não é teste independente.",
                before=before,after=after,documents=docs,document_pass=doc_pass,
                conversation_pass=conversation_pass,test=None,adopted=False)
    torch.set_num_threads(4)
    model,tokenizer,step=load_model(root/"best.pt")
    result["step"]=step;result["captures"]=capture(model,tokenizer,PROMPTS)
    if doc_pass and conversation_pass:
        info=json.loads((root/"run.json").read_text());rows,fingerprint=load_instructions(Path(info["data"]))
        if fingerprint!=info["dataset_fingerprint"]:raise ValueError("Corpus alterado.")
        result["test"]=score(model,tokenizer,[r for r in rows if r["split"]=="test"],"mps",context_limit=1024)
        result["test_acceptance"]=acceptance(result["test"])
    output.write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n")
    print(json.dumps({k:v for k,v in result.items() if k not in {"captures","test"}},ensure_ascii=False),flush=True)
    print(create_report(root))


if __name__=="__main__":main()
