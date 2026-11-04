"""Extração local com referências estáveis dentro de uma versão do arquivo."""

import hashlib
from io import BytesIO
from pathlib import Path
from zipfile import ZipFile

from docx import Document
from docx.table import Table
from pypdf import PdfReader


def extract_document(path: Path) -> dict:
    path = Path(path)
    suffix = path.suffix.lower()
    if suffix not in {".pdf", ".docx"}:
        raise ValueError("Formato não suportado. Use PDF ou DOCX; converta DOC antes.")
    limit = 50 * 1024 * 1024
    with path.open("rb") as file:
        payload = file.read(limit+1)
    if len(payload) > limit:
        raise ValueError("Arquivo excede o limite inicial de 50 MiB.")

    units = []
    warnings = []
    if suffix == ".pdf":
        reader = PdfReader(BytesIO(payload))
        if reader.is_encrypted:
            raise ValueError("PDF protegido: forneça uma cópia sem senha.")
        for number, page in enumerate(reader.pages, 1):
            text = (page.extract_text() or "").strip()
            units.append({"id": f"page:{number}", "text": text})
            if not text:
                warnings.append(f"page:{number}: sem texto; verificar página em branco ou necessidade de OCR")
        warnings.append("Imagens e a estrutura das tabelas do PDF não são interpretadas nesta etapa.")
    else:
        with ZipFile(BytesIO(payload)) as archive:
            if sum(item.file_size for item in archive.infolist()) > 100 * 1024 * 1024:
                raise ValueError("DOCX excede o limite inicial de 100 MiB descompactado.")
        document = Document(BytesIO(payload))
        paragraph_number = table_number = 0
        for block in document.iter_inner_content():
            if isinstance(block, Table):
                table_number += 1
                for row_number, row in enumerate(block.rows, 1):
                    text = " | ".join(cell.text.strip() for cell in row.cells)
                    units.append({"id": f"table:{table_number}:row:{row_number}", "text": text})
            else:
                paragraph_number += 1
                if block.text.strip():
                    units.append({"id": f"paragraph:{paragraph_number}", "text": block.text.strip()})
        warnings.append("Somente corpo e tabelas de primeiro nível; imagens, caixas de texto, revisões, cabeçalhos e rodapés não são interpretados.")
    if not any(unit["text"].strip(" |") for unit in units):
        warnings.append("Nenhum conteúdo textual extraído; não usar para concluir conformidade.")
    return {
        "schema_version": 1,
        "name": path.name,
        "sha256": hashlib.sha256(payload).hexdigest(),
        "format": suffix[1:],
        "units": units,
        "warnings": warnings,
    }
