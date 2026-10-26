"""Valida estrutura, referências e separação por projeto e arquivo."""

import json
from collections import Counter
from pathlib import Path

from jsonschema import Draft202012Validator

from .extract import extract_document


def normalize(text: str) -> str:
    return " ".join(text.split())


def validate_dataset(path: Path) -> dict:
    path = Path(path).resolve()
    root = path.parent
    schema = json.loads(Path(__file__).with_name("example.schema.json").read_text())
    validator = Draft202012Validator(schema)
    ids = set()
    project_splits = {}
    file_splits = {}
    extracted = {}
    splits = Counter()
    statuses = Counter()
    rows = [json.loads(line) for line in path.read_text().splitlines() if line.strip()]
    if not rows:
        raise ValueError("Conjunto de dados vazio.")
    for row in rows:
        validator.validate(row)
        if row["id"] in ids:
            raise ValueError(f"ID duplicado: {row['id']}")
        ids.add(row["id"])
        split = row["split"]
        project_id = row["project_id"]
        if project_splits.setdefault(project_id, split) != split:
            raise ValueError(f"Projeto em mais de um split: {project_id}")
        if row["provenance"]["kind"] == "controlled_variant" and not row["provenance"]["derived_from"]:
            raise ValueError("Variação controlada precisa identificar derived_from.")
        for name in row["documents"]:
            document_path = (root / name).resolve()
            if not document_path.is_relative_to(root):
                raise ValueError(f"Documento fora do diretório do conjunto: {name}")
            if name not in extracted:
                extracted[name] = extract_document(document_path)
            digest = extracted[name]["sha256"]
            if file_splits.setdefault(digest, split) != split:
                raise ValueError(f"Arquivo idêntico em mais de um split: {name}")
        references = [row["requirement"]["source"], *row["expected"]["evidence"]]
        if normalize(row["requirement"]["text"]) not in normalize(row["requirement"]["source"]["quote"]):
            raise ValueError("Texto do requisito ausente na citação do enunciado.")
        for ref in references:
            if ref["document"] not in row["documents"]:
                raise ValueError(f"Documento não declarado: {ref['document']}")
            units = {unit["id"]: unit["text"] for unit in extracted[ref["document"]]["units"]}
            quote = normalize(ref["quote"])
            if not quote or quote not in normalize(units.get(ref["unit"], "")):
                raise ValueError(f"Citação ausente em {ref['document']} / {ref['unit']}")
        splits[split] += 1
        statuses[row["expected"]["status"]] += 1
    return {"examples": len(rows), "projects": len(project_splits), "documents": len(extracted), "splits": dict(splits), "statuses": dict(statuses)}
