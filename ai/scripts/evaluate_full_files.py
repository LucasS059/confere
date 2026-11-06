"""Piloto reproduzível da CLI com arquivos fictícios longos; sem treinamento."""
import argparse
import hashlib
import json
import subprocess
import sys
import time
from collections import defaultdict
from pathlib import Path
from xml.sax.saxutils import escape
from docx import Document
from reportlab.pdfgen.canvas import Canvas
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
from confere_ai.extract import extract_document


def fixtures(directory):
    directory.mkdir(parents=True)
    pdf=directory/"entrega-longa.pdf"
    canvas=Canvas(str(pdf))
    for page in range(1,7):
        canvas.setFont("Helvetica",9)
        for line in range(60):
            canvas.drawString(45,800-line*11,f"Equipe: registro {page}-{line}. A equipe registrou atividades e decisões da etapa atual.")
        if page==6:
            canvas.drawString(45,120,"O projeto inclui testes.")
            canvas.drawString(45,105,"O projeto inclui backup.")
        canvas.showPage()
    canvas.save()
    docx=directory/"entrega-tabelas.docx"
    document=Document();document.add_paragraph("O projeto não inclui backup.")
    table=document.add_table(rows=2,cols=2)
    table.cell(0,0).text="Item";table.cell(0,1).text="Registro"
    table.cell(1,0).text="Entrega";table.cell(1,1).text="O projeto inclui relatórios."
    document.add_paragraph("Equipe: documento fictício de integração.")
    document.save(docx)
    return [pdf,docx]


def audit_result(result,documents):
    quotes=0
    for requirement in result["requirements"]:
        spans=defaultdict(list)
        for call in requirement["calls"]:
            for source in call["sources"]:
                spans[source["document_id"],source["source_unit"]].append((source["char_start"],source["char_end"]))
        for i,doc in enumerate(documents,1):
            for unit in doc["units"]:
                if not unit["text"].strip(" |"):continue
                intervals=spans[f"doc:{i}",unit["id"]]
                assert intervals[0][0]==0 and intervals[-1][1]==len(unit["text"])
                assert all(a[1]==b[0] for a,b in zip(intervals,intervals[1:]))
        for evidence in requirement["evidence"]:
            document=documents[int(evidence["document_id"].split(":")[1])-1]
            unit=next(u for u in document["units"] if u["id"]==evidence["source_unit"])
            assert evidence["source_sha256"]==document["sha256"]
            assert evidence["quote"]==unit["text"][evidence["char_start"]:evidence["char_end"]]
            quotes+=1
    return dict(contiguous_text_coverage_verified=True,literal_quotes_verified=quotes,
                invalid_calls=sum(not (c["valid_format"] and c["reference_valid"]) for r in result["requirements"] for c in r["calls"]),
                expected_statuses=["atendido","evidencia_insuficiente","atendido"],
                expected_note="Rótulos por construção em três casos fictícios; sem revisão independente de semântica.")


def pdf_report(path,result,audit,elapsed):
    path.parent.mkdir(parents=True,exist_ok=True)
    styles=getSampleStyleSheet();story=[]
    def p(text,style="BodyText"):
        story.append(Paragraph(escape(str(text)),styles[style]));story.append(Spacer(1,7))
    p("CONFERE | Piloto de arquivos completos","Title")
    p("Integração local PDF/DOCX - 04/11/2026","Heading2")
    p("Esta execução não treinou pesos. O piloto exercita a extração, divisão por contexto, inferência real e consolidação de propostas, mantendo os resultados brutos no JSON.")
    p("Modelo: "+result["model"]["checkpoint"]+f'; passo {result["model"]["step"]}; {result["model"]["device"]}; contexto {result["model"]["context_size"]}; saída {result["model"]["response_tokens"]} tokens.')
    p(f'Tempo da CLI com extração e carregamento: {elapsed:.1f} segundos.')
    p("Fontes fictícias: PDF de seis páginas com texto longo e DOCX com parágrafos e tabela. Requisitos informados manualmente. A extração não interpreta imagens nem toda a estrutura visual.")
    rows=[["Requisito","Proposta do modelo","Lotes / caracteres","Rótulo autoral"]]
    for item,expected in zip(result["requirements"],audit["expected_statuses"]):
        coverage=item["coverage"]
        rows.append([item["requirement"],item["status"],f'{coverage["batches"]} / {coverage["processed_characters"]}',expected])
    table=Table([[Paragraph(escape(str(v)),styles["BodyText"]) for v in row] for row in rows],colWidths=[175,110,100,110])
    table.setStyle(TableStyle([("VALIGN",(0,0),(-1,-1),"TOP"),("BACKGROUND",(0,0),(-1,0),colors.HexColor("#EDF3F7")),("GRID",(0,0),(-1,-1),.3,colors.grey)]))
    story.append(table);story.append(Spacer(1,12))
    p(f'Auditoria mecânica: intervalos contíguos de todo o texto extraído conferidos por requisito; {audit["literal_quotes_verified"]} citações verificadas literalmente contra suas unidades de origem.')
    p(audit["expected_note"])
    p(f'Resultado: {audit["invalid_calls"]} consultas inválidas; os três requisitos ficaram inconclusivos. As três referências retornadas apontam para o registro da equipe, sem sustentar testes, backup ou relatórios. A cobertura mecânica passou, mas este piloto reprovou a interpretação documental. O rótulo inconclusivo do backup coincide com o esperado sem detectar a contradição existente.')
    p("Todas as propostas exigem revisão humana. Formato ou referência válidos não comprovam suporte semântico. Respostas contraditórias, unidades sem texto ou saídas inválidas impedem uma conclusão no consolidado. O checkpoint continua experimental.")
    story.append(PageBreak())
    p("Evidências e limites", "Heading2")
    for item in result["requirements"]:
        p(item["id"]+": "+item["requirement"],"Heading3")
        p(f'Conflito detectado: {item["conflicting_evidence"]}; saídas estruturalmente válidas: {item["model_outputs_valid"]}.')
        for evidence in item["evidence"][:1]:
            quote=evidence["quote"]
            p(f'Fonte: {evidence["document"]} / {evidence["source_unit"]}; caracteres {evidence["char_start"]}:{evidence["char_end"]}.')
            p("Citação: "+quote[:200]+(" [exibição abreviada; íntegra no JSON]" if len(quote)>200 else ""))
    p("Rastreabilidade: arquivos de entrada, hashes, intervalos, aliases locais, respostas brutas e cobertura constam no JSON. Não houve avaliação com TCC real, integração ao simulador ou aprovação de conversa aberta.")
    SimpleDocTemplate(str(path),pagesize=(595.28,841.89),rightMargin=45,leftMargin=45,topMargin=35,bottomMargin=35).build(story)


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--directory",type=Path,required=True);p.add_argument("--output",type=Path,required=True)
    p.add_argument("--report",type=Path,required=True);p.add_argument("--checkpoint",type=Path,required=True)
    args=p.parse_args();audit_path=args.output.with_suffix(".audit.json")
    if any(path.exists() for path in (args.directory,args.output,args.report,audit_path)):p.error("Use caminhos novos; evidências existentes são preservadas.")
    paths=fixtures(args.directory);documents=[extract_document(path) for path in paths]
    args.output.parent.mkdir(parents=True,exist_ok=True)
    command=[sys.executable,"-m","confere_ai.cli","review-project",*[str(path) for path in paths],"--checkpoint",str(args.checkpoint),"--device","mps","--output",str(args.output)]
    for requirement in ("O projeto deve incluir testes.","O projeto deve incluir backup.","O projeto deve incluir relatórios."):
        command.extend(["--requirement",requirement])
    started=time.perf_counter();subprocess.run(command,check=True);elapsed=time.perf_counter()-started
    result=json.loads(args.output.read_text());audit=audit_result(result,documents)
    audit.update(elapsed_seconds=elapsed,result_sha256=hashlib.sha256(args.output.read_bytes()).hexdigest())
    audit_path.write_text(json.dumps(audit,ensure_ascii=False,indent=2)+"\n")
    pdf_report(args.report,result,audit,elapsed)
    print(json.dumps(dict(audit=audit,statuses=[r["status"] for r in result["requirements"]],batches=[r["coverage"]["batches"] for r in result["requirements"]]),ensure_ascii=False),flush=True)


if __name__=="__main__":main()
