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


def document_passes(docs, minimum):
    return (docs["total"]>0 and docs["valid"]==docs["references"]==docs["total"]
            and bool(docs["families"]) and all(c/t>=minimum for c,t in docs["families"].values()))


def matching_cohort(left,right):
    fields=("id","task","prompt","expected")
    return [[r[k] for k in fields] for r in left["samples"]]==[[r[k] for k in fields] for r in right["samples"]]


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument("run_dir",type=Path)
    parser.add_argument("--perfect-documents",action="store_true",help="Exigir 100% por status antes de consultar o teste.")
    parser.add_argument("--baseline-evaluation-run",type=Path,help="Reutilizar referência já medida, somente com coorte e janelas idênticas.")
    args=parser.parse_args();root=args.run_dir;output=root/"contrast-evaluation.json"
    if output.exists():parser.error("Avaliação existente; preserve o teste.")
    evaluation=json.loads((root/"instruction-evaluation.json").read_text())
    reference_checkpoint=None
    if args.baseline_evaluation_run:
        previous=json.loads((args.baseline_evaluation_run/"instruction-evaluation.json").read_text())
        previous_info=json.loads((args.baseline_evaluation_run/"run.json").read_text())
        info=json.loads((root/"run.json").read_text())
        if (not matching_cohort(evaluation["selected"],previous["baseline"])
            or any(info[k]!=previous_info[k] for k in ("paired_evaluation_context","paired_evaluation_response_tokens"))):
            raise ValueError("Referência em cache não corresponde à coorte ou janela pareada.")
        evaluation["baseline"]=previous["baseline"]
        reference_checkpoint=previous_info["baseline_checkpoint"]
    before=metrics(evaluation["baseline"],"conversation_")
    after=metrics(evaluation["selected"],"conversation_")
    docs=metrics(evaluation["selected"],"grounded_")
    doc_pass=document_passes(docs,1 if args.perfect_documents else .9)
    conversation_pass=(after["correct"]>=before["correct"] and all(c/t>=.8 and c>=before["families"][name][0]
                           for name,(c,t) in after["families"].items()))
    result=dict(policy="Comparação pareada 1024/64. Documentos: >=90% em cada status, 100% formato/referências. Conversa: >=80% por família, sem queda por família ou no total ante o modelo informal. Teste somente se ambos passarem. Diagnóstico nativo 1024/256 não é teste independente.",
                before=before,after=after,documents=docs,document_pass=doc_pass,
                conversation_pass=conversation_pass,test=None,adopted=False)
    if args.perfect_documents:result["policy"]=result["policy"].replace(">=90% em cada status","100% em cada status")
    if reference_checkpoint:
        result["policy"]+=" Referência fixa reutilizada após conferir coorte e janelas: "+reference_checkpoint+". A loss e a comparação geral do treino usam a origem imediata; os critérios suplementares usam esta referência fixa."
        result["reference_checkpoint"]=reference_checkpoint
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
