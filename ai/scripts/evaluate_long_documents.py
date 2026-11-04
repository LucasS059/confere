"""Avaliação conjunta do selecionado por loss, sem abrir o teste reservado."""
import argparse
import hashlib
import json
from pathlib import Path

from confere_ai.extract import extract_document
from confere_ai.instruct import load_instructions
from confere_ai.project_review import review_files
from confere_ai.report import create_report
from evaluate_document_contrasts import metrics, document_passes, matching_cohort
from evaluate_full_files import audit_result

PILOT_SUPPORT=[[("atendido","O projeto inclui testes.")],
               [("atendido","O projeto inclui backup."),("nao_atendido","O projeto não inclui backup.")],
               [("atendido","O projeto inclui relatórios.")]]


def supported_citations(result):
    return sum(any(e["model_status"]==status and phrase in e["quote"] for status,phrase in pairs)
               for row,pairs in zip(result["requirements"],PILOT_SUPPORT) for e in row["evidence"])


def cohorts(result):
    return {name:metrics(dict(samples=[r for r in result["samples"] if predicate(r)]),prefix)
            for name,prefix,predicate in (
                ("conversation","conversation_",lambda r:r["task"].startswith("conversation_")),
                ("short_documents","grounded_",lambda r:r["task"].startswith("grounded_") and not r["id"].startswith("long-")),
                ("long_documents","grounded_",lambda r:r["id"].startswith("long-")))}


def gates(before,after):
    old,new=before["conversation"],after["conversation"]
    return dict(short_documents=document_passes(after["short_documents"],1),
                long_documents=document_passes(after["long_documents"],.9),
                conversation=(new["total"]>0 and new["correct"]>=old["correct"]
                              and new["families"].keys()==old["families"].keys()
                              and all(t==old["families"][name][1] and c/t>=.8 and c>=old["families"][name][0]
                                      for name,(c,t) in new["families"].items())))


def full_file_gate(result,audit):
    # Oráculo restrito às frases autorais do piloto conhecido, sem julgar texto livre.
    if ([r["status"] for r in result["requirements"]]!=audit["expected_statuses"]
        or not result["requirements"][1]["conflicting_evidence"] or audit["invalid_calls"]):return False
    for row,pairs in zip(result["requirements"],PILOT_SUPPORT):
        evidence=row["evidence"]
        if not all(any(e["model_status"]==status and phrase in e["quote"] for e in evidence) for status,phrase in pairs):return False
        if any(not any(e["model_status"]==status and phrase in e["quote"] for status,phrase in pairs) for e in evidence):return False
    return True


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument("run_dir",type=Path)
    p.add_argument("--pilot",type=Path,required=True);p.add_argument("--files",type=Path,nargs="+",required=True)
    args=p.parse_args();root=args.run_dir;output=root/"long-document-evaluation.json"
    raw_path=root/"full-file-validation.json"
    if output.exists() or raw_path.exists():p.error("Avaliação existente; preserve as evidências.")
    info=json.loads((root/"run.json").read_text());rows,fingerprint=load_instructions(Path(info["data"]))
    if fingerprint!=info["dataset_fingerprint"]:raise ValueError("Corpus alterado.")
    evaluation=json.loads((root/"instruction-evaluation.json").read_text())
    if not matching_cohort(evaluation["baseline"],evaluation["selected"]):raise ValueError("Coortes diferentes.")
    before,after=cohorts(evaluation["baseline"]),cohorts(evaluation["selected"])
    checks=gates(before,after)
    pilot=json.loads(args.pilot.read_text());documents=[extract_document(path) for path in args.files]
    if [d["sha256"] for d in documents]!=[d["sha256"] for d in pilot["sources"]]:raise ValueError("Arquivos diferem do piloto anterior.")
    if hashlib.sha256(Path(info["baseline_checkpoint"]).read_bytes()).hexdigest()!=pilot["model"]["sha256"]:
        raise ValueError("Referência do piloto difere da comparação do treino.")
    full=review_files(args.files,[r["requirement"] for r in pilot["requirements"]],root/"best.pt","mps")
    with raw_path.open("x") as f:json.dump(full,f,ensure_ascii=False,indent=2)
    audit=audit_result(full,documents)
    checks["full_files"]=full_file_gate(full,audit)
    record=dict(policy="Selecionado por menor loss. Documentos curtos: 100% por status. Longos: >=90% por status. Ambos: 100% formato/referências. Conversa: >=80% por família, sem queda por família ou agregado ante a origem, janela 1024/64. Piloto completo: todos os rótulos, conflito do backup, citações com as frases autorais corretas e zero saída inválida. Nenhuma promoção automática ou abertura do teste neste experimento.",
                selected_step=evaluation["selected_step"],before=before,after=after,gates=checks,
                provenance=dict(dataset_sha256=fingerprint,checkpoint_sha256=full["model"]["sha256"],
                                baseline_checkpoint_sha256=pilot["model"]["sha256"],
                                pilot_source_sha256=[d["sha256"] for d in documents]),
                passed=all(checks.values()),adopted=False,test_used=False,
                pilot_before=dict(statuses=[r["status"] for r in pilot["requirements"]],audit=audit_result(pilot,documents),
                                  supported_citations=supported_citations(pilot)),
                pilot_after=dict(statuses=[r["status"] for r in full["requirements"]],audit=audit,
                                 supported_citations=supported_citations(full),
                                 conflicting_evidence=[r["conflicting_evidence"] for r in full["requirements"]]),
                failed_long_examples=[r for r in evaluation["selected"]["samples"] if r["id"].startswith("long-") and not r["exact_match"]][:3],
                note="Validação autoral, receitas compartilhadas. Piloto completo já conhecido pelo diagnóstico, fora do gradiente mas não independente. Citação literal não prova suporte semântico. Checkpoint e padrão da TUI preservados separadamente.")
    with output.open("x") as f:json.dump(record,f,ensure_ascii=False,indent=2)
    print(json.dumps({k:v for k,v in record.items() if k not in {"failed_long_examples"}},ensure_ascii=False),flush=True)
    print(create_report(root),flush=True)


if __name__=="__main__":main()
