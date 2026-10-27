"""Cria cópia pesquisável e páginas de revisão, preservando o PDF original."""

import argparse
import hashlib
import io
import json
import platform
import shutil
import subprocess
from pathlib import Path

from pypdf import PdfReader, PdfWriter
from reportlab.pdfgen.canvas import Canvas


def make_searchable(source: Path, destination: Path, pages: list) -> None:
    reader = PdfReader(source)
    if len(pages) != len(reader.pages):
        raise ValueError("Quantidade de páginas do OCR difere do original.")
    writer = PdfWriter()
    for number, (page, result) in enumerate(zip(reader.pages, pages), 1):
        if result["number"] != number:
            raise ValueError("Ordem das páginas do OCR inválida.")
        # shortcut: PDFs rotacionados/cortados precisam de transformação antes do overlay.
        if page.rotation or page.mediabox != page.cropbox or float(page.mediabox.left) or float(page.mediabox.bottom):
            raise ValueError("Este protótipo exige páginas sem rotação ou recorte.")
        width, height = float(page.mediabox.width), float(page.mediabox.height)
        overlay = io.BytesIO()
        canvas = Canvas(overlay, pagesize=(width, height))
        for line in result["lines"]:
            text = canvas.beginText(line["x"] * width, line["y"] * height)
            text.setFont("Helvetica", max(1, line["height"] * height * 0.8))
            text.setTextRenderMode(3)  # Texto invisível; a página original continua visível.
            text.textLine(line["text"])
            canvas.drawText(text)
        canvas.showPage()
        canvas.save()
        target_page = writer.add_page(page)
        target_page.merge_page(PdfReader(overlay).pages[0])
        target_page.compress_content_streams()
    writer.write(destination)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path)
    parser.add_argument("output", type=Path, help="Diretório novo; não sobrescreve execuções")
    args = parser.parse_args()
    if platform.system() != "Darwin" or not shutil.which("swift"):
        parser.error("Este OCR usa Apple Vision e requer macOS com Swift instalado.")
    if args.source.suffix.lower() != ".pdf" or not args.source.is_file():
        parser.error("Forneça um PDF existente.")
    if args.output.exists():
        parser.error("O diretório de saída já existe; escolha outro para preservar os dados.")
    source = args.source.resolve()
    reader = PdfReader(source)
    if reader.is_encrypted:
        parser.error("PDF protegido não é suportado.")
    args.output.mkdir(parents=True)
    result = subprocess.run(
        ["swift", str(Path(__file__).with_name("ocr_macos.swift")), str(source), str(args.output)],
        check=True, stdout=subprocess.PIPE, timeout=600,
    )
    pages = json.loads(result.stdout)
    (args.output / "ocr.json").write_text(json.dumps({
        "schema_version": 1,
        "source_sha256": hashlib.sha256(source.read_bytes()).hexdigest(),
        "engine": "Apple Vision VNRecognizeTextRequest accurate pt-BR en-US",
        "os": platform.mac_ver()[0],
        "note": "Confiança de reconhecimento não é confiança de conformidade; revisão visual necessária.",
        "pages": pages,
    }, ensure_ascii=False, indent=2), encoding="utf-8")
    make_searchable(source, args.output / "searchable.pdf", pages)
    (args.output / "text.txt").write_text("\n\n".join(
        f"--- Página PDF {page['number']} ---\n" + "\n".join(line["text"] for line in page["lines"])
        for page in pages
    ), encoding="utf-8")
    print(f"OCR concluído: {len(pages)} páginas em {args.output}")


if __name__ == "__main__":
    main()
