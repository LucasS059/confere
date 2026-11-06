"""Ablação diagnóstica do piloto conhecido; nenhum treino ou promoção."""
import argparse
import hashlib
import json
from pathlib import Path
from xml.sax.saxutils import escape
import torch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from confere_ai.extract import extract_document
from confere_ai.grounding import judge, prompt_for
from confere_ai.project_review import input_ids
from evaluate_conversation_flow import load_model
from evaluate_long_documents import PILOT_SUPPORT


def annotated_row(requirement,units,pairs):
    hits=[(u["id"],status,phrase) for u in units for status,phrase in pairs if phrase in u["text"]]
    if len(hits)>1:raise ValueError("Lote com múltiplas evidências exige anotação específica.")
    target=dict(status=hits[0][1] if hits else "evidencia_insuficiente",unit=hits[0][0] if hits else None)
    oracle=[dict(id=u["id"],text=hits[0][2] if hits and u["id"]==hits[0][0] else "Registro da reunião da equipe.") for u in units]
    return dict(requirement=requirement,units=units,document="piloto",target=json.dumps(target,ensure_ascii=False)),oracle


def summarize(samples):
    relevant=[r for r in samples if json.loads(r["expected"])["unit"] is not None]
    return dict(correct=sum(r["exact_match"] for r in samples),total=len(samples),
                status_correct=sum(r["status_correct"] for r in samples),
                relevant_correct=sum(r["exact_match"] for r in relevant),relevant_total=len(relevant))


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument("--pilot",type=Path,required=True)
    p.add_argument("--checkpoint",type=Path,required=True);p.add_argument("--files",type=Path,nargs="+",required=True)
    p.add_argument("--output",type=Path,required=True);p.add_argument("--report",type=Path,required=True)
    a=p.parse_args()
    if a.output.exists() or a.report.exists():p.error("Use saídas novas.")
    pilot=json.loads(a.pilot.read_text());docs=[extract_document(path) for path in a.files]
    if [d["sha256"] for d in docs]!=[d["sha256"] for d in pilot["sources"]]:raise ValueError("Fontes alteradas.")
    digest=hashlib.sha256(a.checkpoint.read_bytes()).hexdigest()
    if digest!=pilot["model"]["sha256"]:raise ValueError("Checkpoint difere do piloto em cache.")
    torch.set_num_threads(4);model,tokenizer,step=load_model(a.checkpoint)
    samples={"full_cached":[],"oracle_short":[]};annotations=[];conflicts=[]
    for item,pairs in zip(pilot["requirements"],PILOT_SUPPORT):
        for call in item["calls"]:
            units=[]
            for source in call["sources"]:
                document=docs[int(source["document_id"].split(":")[1])-1]
                unit=next(u for u in document["units"] if u["id"]==source["source_unit"])
                units.append(dict(id=source["alias"],text=unit["text"][source["char_start"]:source["char_end"]]))
            identity=f'{item["id"]}-batch-{call["batch"]}'
            try:row,oracle=annotated_row(item["requirement"],units,pairs)
            except ValueError:
                conflicts.append(dict(id=identity,requirement=item["requirement"],units=units,
                                      raw=call["raw_model_output"],reason="Mais de uma evidência no lote; contrato de status/unit único não expressa todas. Fora do acerto local, preservado para revisão."))
                continue
            annotations.append(dict(id=identity,**row,oracle_units=oracle))
            for condition,context in (("full_cached",units),("oracle_short",oracle)):
                ids=input_ids(row["requirement"],context,tokenizer)
                if len(ids)+64>model.config.block_size:raise ValueError("Contexto excedido.")
                if condition=="full_cached":raw=call["raw_model_output"]
                else:
                    output=model.generate(torch.tensor([ids],device="mps"),64,tokenizer.EOS)
                    raw=tokenizer.decode(output[0,len(ids):].tolist())
                judged=judge(raw,dict(row,units=context))
                samples[condition].append(dict(id=identity,expected=row["target"],actual=raw,**judged))
    assert len(annotations)+len(conflicts)==sum(len(r["calls"]) for r in pilot["requirements"])
    result=dict(checkpoint_sha256=digest,step=step,pilot_sha256=hashlib.sha256(a.pilot.read_bytes()).hexdigest(),
                metrics={k:summarize(v) for k,v in samples.items()},samples=samples,annotations=annotations,conflicts=conflicts,
                note="Piloto fictício já conhecido. Oracle usa rótulo autoral para fornecer a frase correta, preservando aliases e requisito; remove outros conteúdos. Não é busca implementada, avaliação cega ou melhoria dos pesos. Full reutiliza saídas brutas após verificar hashes.",training=False,test_used=False,adopted=False)
    a.output.parent.mkdir(parents=True,exist_ok=True)
    with a.output.open("x") as f:json.dump(result,f,ensure_ascii=False,indent=2)
    styles=getSampleStyleSheet();story=[]
    def paragraph(text,style="BodyText"):
        story.extend([Paragraph(escape(text),styles[style]),Spacer(1,10)])
    paragraph("CONFERE | Diagnóstico de evidências","Title")
    paragraph("05/11/2026 - inferência local em MPS, sem treinamento.")
    paragraph(result["note"])
    paragraph("Métricas locais por lote","Heading2")
    paragraph(f'{len(conflicts)} lote(s) com múltiplas evidências foram separados e preservados no JSON, fora do denominador local. Não foram tratados como acertos ou descartados da análise do arquivo.')
    for name,m in result["metrics"].items():
        paragraph(f'{name}: status/unidade {m["correct"]}/{m["total"]}; só status {m["status_correct"]}/{m["total"]}; lotes com evidência {m["relevant_correct"]}/{m["relevant_total"]}.')
    paragraph("A maioria dos lotes não contém evidência. O agregado deve ser lido junto com os lotes relevantes. O oracle é um controle artificial com acesso à resposta anotada; qualquer ganho não pode ser atribuído a uma busca automática nem usado para promover o modelo.")
    if conflicts:paragraph("Limitação de representação: o contrato atual devolve um único status e uma única unidade por lote. Ele não consegue listar simultaneamente evidências opostas dentro do mesmo lote; a consolidação entre lotes não resolve essa omissão por si só. É necessário tratar esse caso no contrato/pipeline antes de exigir detecção completa de contradições.")
    paragraph("As anotações por frase literal só valem para este piloto autoral. Não avaliam TCCs reais, conteúdo visual, conversa aberta ou o teste reservado. Nenhum modelo foi alterado e o app não foi integrado.")
    paragraph("Checkpoint SHA-256: "+digest)
    paragraph("JSON com fontes reconstruídas, anotações, respostas e resultados: "+str(a.output))
    a.report.parent.mkdir(parents=True,exist_ok=True)
    SimpleDocTemplate(str(a.report)).build(story)
    print(json.dumps(result["metrics"]),flush=True)


if __name__=="__main__":main()
