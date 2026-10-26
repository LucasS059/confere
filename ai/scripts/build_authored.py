"""Gera fixtures de integração autorais; não gera rótulos com um modelo."""

import json
from pathlib import Path
from xml.sax.saxutils import escape

from docx import Document
from docx.shared import Cm, Pt, RGBColor
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer

from confere_ai.dataset import normalize, validate_dataset
from confere_ai.extract import extract_document


ROOT = Path(__file__).resolve().parents[1] / "data" / "authored"


def find_reference(name: str, quote: str) -> dict:
    for unit in extract_document(ROOT / name)["units"]:
        if normalize(quote) in normalize(unit["text"]):
            return {"document": name, "unit": unit["id"], "quote": quote}
    raise ValueError(f"Texto esperado ausente em {name}: {quote}")


def build() -> dict:
    projects = json.loads((ROOT / "projects.json").read_text())
    output = ROOT / "documents"
    output.mkdir(parents=True, exist_ok=True)
    examples = []
    styles = getSampleStyleSheet()
    for project in projects:
        brief_name = f"documents/{project['id']}-enunciado.pdf"
        story = [Paragraph(escape(project["title"]), styles["Title"]), Spacer(1, 12)]
        story.append(Paragraph("Requisitos da entrega", styles["Heading2"]))
        for requirement in project["requirements"]:
            story.append(Paragraph(escape(f"{requirement['id']} - {requirement['text']}"), styles["BodyText"]))
            story.append(Spacer(1, 8))
        SimpleDocTemplate(str(ROOT / brief_name), pagesize=A4, title=project["title"], author="Confere", invariant=1).build(story)
        for submission in project["submissions"]:
            name = f"documents/{project['id']}-{submission['id']}.docx"
            document = Document()
            document.core_properties.author = "Confere"
            document.core_properties.title = project["title"]
            section = document.sections[0]
            section.page_width, section.page_height = Cm(21), Cm(29.7)
            section.top_margin = section.bottom_margin = Cm(2)
            for style_name in ("Normal", "Title", "Heading 1"):
                document.styles[style_name].font.name = "Arial"
                document.styles[style_name].font.color.rgb = RGBColor(0, 0, 0)
            document.styles["Normal"].font.size = Pt(11)
            document.add_heading(project["title"], 0)
            for heading, text in submission["sections"]:
                document.add_heading(heading, 1)
                document.add_paragraph(text)
            if submission.get("table"):
                document.add_heading("Cronograma", 1)
                table = document.add_table(rows=0, cols=2)
                table.style = "Table Grid"
                for values in submission["table"]:
                    for cell, value in zip(table.add_row().cells, values):
                        cell.text = value
            document.save(ROOT / name)
            for label in submission["labels"]:
                requirement = next(item for item in project["requirements"] if item["id"] == label["requirement"])
                parent = submission.get("derived_from")
                examples.append({
                    "schema_version": 1,
                    "id": f"{project['id']}-{submission['id']}-{requirement['id']}",
                    "project_id": project["id"],
                    "split": project["split"],
                    "provenance": {
                        "kind": "controlled_variant" if parent else "authored",
                        "usage_rights": "Conteúdo fictício autoral criado para os experimentos do Confere.",
                        "reviewed_by": "revisão de consistência dos exemplos autorais; sem avaliação do professor",
                        "derived_from": f"documents/{project['id']}-{parent}.docx" if parent else None,
                    },
                    "documents": [brief_name, name],
                    "requirement": {"id": requirement["id"], "text": requirement["text"], "source": find_reference(brief_name, requirement["text"])},
                    "expected": {"status": label["status"], "evidence": [find_reference(name, label["quote"])], "justification": label["justification"]},
                })
    target = ROOT / "examples.jsonl"
    target.write_text("".join(json.dumps(row, ensure_ascii=False) + "\n" for row in examples), encoding="utf-8")
    return validate_dataset(target)


if __name__ == "__main__":
    print(json.dumps(build(), ensure_ascii=False, indent=2))
