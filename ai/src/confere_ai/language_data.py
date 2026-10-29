"""Preparação causal: separação por documento antes de criar janelas."""

import hashlib
import json
import random
from pathlib import Path

from .tokenizer import ByteBPE


def load_corpus(path):
    path = Path(path)
    manifest = json.loads(path.with_name("manifest.json").read_text())
    fingerprint = hashlib.sha256(path.read_bytes()).hexdigest()
    if fingerprint != manifest["snapshot_sha256"]:
        raise ValueError("O corpus não corresponde ao hash do manifesto.")
    rows = [json.loads(line) for line in path.read_text().splitlines() if line.strip()]
    ids, text_splits = set(), {}
    for row in rows:
        if row["id"] in ids or row["split"] not in {"train", "validation", "test"}:
            raise ValueError("IDs duplicados ou split inválido.")
        ids.add(row["id"])
        if not row["text"].strip() or not row.get("license_urls") or not row.get("attribution"):
            raise ValueError("Texto vazio ou atribuição/licença ausente.")
        digest = hashlib.sha256(" ".join(row["text"].split()).encode()).hexdigest()
        if text_splits.setdefault(digest, row["split"]) != row["split"]:
            raise ValueError("Conteúdo idêntico atravessando splits.")
    if not all(any(row["split"] == split for row in rows) for split in ("train", "validation")):
        raise ValueError("Pré-treino requer documentos de treino e validação.")
    return rows, fingerprint


def fit_language_tokenizer(rows, vocab_size, max_chars, seed):
    documents = [row for row in rows if row["split"] == "train"]
    random.Random(seed).shuffle(documents)
    pieces, remaining = [], max_chars
    for row in documents:
        # Amostra distribuída por artigos; o BPE didático não percorre o corpus todo.
        text = row["text"][:min(600, remaining)]
        pieces.append(text)
        remaining -= len(text)
        if remaining <= 0:
            break
    return ByteBPE.train(pieces, vocab_size)


def validate_expansion(previous, current):
    indexed = {row["id"]: row for row in current}
    text_splits = {}
    for row in previous + current:
        digest = hashlib.sha256(" ".join(row["text"].split()).encode()).hexdigest()
        if text_splits.setdefault(digest, row["split"]) != row["split"]:
            raise ValueError("Expansão move conteúdo entre splits.")
    for old in previous:
        new = indexed.get(old["id"])
        if new is None or new["split"] != old["split"] or new["text"] != old["text"]:
            raise ValueError("Expansão exige preservar artigos anteriores, textos e splits.")


def language_windows(rows, tokenizer, block_size, split):
    result = []
    for row in rows:
        if row["split"] != split:
            continue
        sequence = [tokenizer.BOS] + tokenizer.encode(row["text"]) + [tokenizer.EOS]
        for start in range(0, len(sequence) - 1, block_size):
            window = sequence[start:start + block_size + 1]
            if len(window) > 1:
                result.append((window[:-1], window[1:]))
    return result
