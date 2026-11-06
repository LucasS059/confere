"""Amostra local da Wikipédia pt via API pública, sem baixar pesos de modelo."""

import argparse
import hashlib
import json
import unicodedata
import urllib.parse
import urllib.request
import urllib.error
import time
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path


SOURCE = "https://huggingface.co/datasets/wikimedia/wikipedia"
LICENSES = ["https://creativecommons.org/licenses/by-sa/3.0/", "https://www.gnu.org/licenses/fdl-1.3.html"]


def fetch(url, headers):
    for attempt in range(5):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=headers), timeout=30) as response:
                return response.read()
        except urllib.error.HTTPError as error:
            if error.code not in {429, 500, 502, 503, 504} or attempt == 4:
                raise
            delay = max(10 * (attempt + 1), float(error.headers.get("Retry-After", 0)))
            print(f"HTTP {error.code}; aguardando {delay:.0f}s antes de tentar novamente...", flush=True)
            time.sleep(delay)


def prepare_row(row, max_chars):
    text = unicodedata.normalize("NFC", row["text"]).replace("\r\n", "\n").strip()
    if len(text) < 500:
        return None
    if not row["url"].startswith("https://pt.wikipedia.org/wiki/"):
        raise ValueError("Origem inesperada para artigo em português.")
    normalized_hash = hashlib.sha256(" ".join(text.split()).encode()).hexdigest()
    bucket = int(hashlib.sha256(str(row["id"]).encode()).hexdigest(), 16) % 100
    split = "test" if bucket < 5 else "validation" if bucket < 10 else "train"
    return {
        "id": str(row["id"]), "title": row["title"], "url": row["url"], "split": split,
        "text": text[:max_chars], "original_chars": len(text), "truncated": len(text) > max_chars,
        "normalized_source_sha256": normalized_hash,
        "attribution": "Colaboradores da Wikipédia em português; autoria/histórico na URL do artigo.",
        "license_urls": LICENSES,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("output", type=Path)
    parser.add_argument("--rows", type=int, default=1000)
    parser.add_argument("--max-chars", type=int, default=8000)
    parser.add_argument("--resume-download", action="store_true", help="Reusar páginas locais de um download incompleto.")
    args = parser.parse_args()
    if not 100 <= args.rows <= 10000 or not 1000 <= args.max_chars <= 50000:
        parser.error("Use 100–10000 linhas e 1000–50000 caracteres por artigo.")
    if args.output.exists() and (not args.resume_download or (args.output / "manifest.json").exists()):
        parser.error("A saída já existe; escolha outra para preservar snapshots.")
    args.output.mkdir(parents=True, exist_ok=True)
    request_headers = {"User-Agent": "Confere-local-research/0.1"}
    if not (args.output / "SOURCE_CARD.md").exists():
        (args.output / "SOURCE_CARD.md").write_bytes(fetch(SOURCE + "/raw/main/README.md", request_headers))
    cache = args.output / "pages"
    cache.mkdir(exist_ok=True)
    rows, ids, hashes = [], set(), set()
    for offset in range(0, args.rows, 100):
        query = urllib.parse.urlencode({"dataset": "wikimedia/wikipedia", "config": "20231101.pt", "split": "train", "offset": offset, "length": min(100, args.rows - offset)})
        url = "https://datasets-server.huggingface.co/rows?" + query
        page = cache / f"{offset}-{min(100, args.rows - offset)}.json"
        if not page.exists():
            payload = fetch(url, request_headers)
            json.loads(payload)
            page.write_bytes(payload)
            time.sleep(.3)
        data = json.loads(page.read_bytes())
        if not data["rows"]:
            raise ValueError("API retornou uma página vazia inesperada.")
        for wrapped in data["rows"]:
            if wrapped.get("truncated_cells"):
                continue
            row = prepare_row(wrapped["row"], args.max_chars)
            if row is None or row["id"] in ids or row["normalized_source_sha256"] in hashes:
                continue
            ids.add(row["id"])
            hashes.add(row["normalized_source_sha256"])
            rows.append(row)
        print(f"Linhas consultadas: {offset + len(data['rows'])}; artigos aceitos: {len(rows)}", flush=True)
    target = args.output / "articles.jsonl"
    target.write_text("".join(json.dumps(row, ensure_ascii=False) + "\n" for row in rows), encoding="utf-8")
    manifest = {
        "schema_version": 1, "source": SOURCE, "config": "20231101.pt",
        "captured_utc": datetime.now(timezone.utc).isoformat(),
        "license_urls": LICENSES, "license_note": "Card da Wikimedia declara CC BY-SA 3.0 e GFDL; URLs e atribuição preservadas. Não redistribuir como conteúdo autoral do Confere.",
        "selection": "Prefixo da ordem do dataset; amostra limitada, não aleatória nem representativa de todo o português.",
        "rows_requested": args.rows, "documents": len(rows), "max_chars_per_article": args.max_chars,
        "splits": dict(Counter(row["split"] for row in rows)),
        "characters": sum(len(row["text"]) for row in rows),
        "snapshot_sha256": hashlib.sha256(target.read_bytes()).hexdigest(),
        "source_card_sha256": hashlib.sha256((args.output / "SOURCE_CARD.md").read_bytes()).hexdigest(),
        "split_policy": "SHA-256 do ID do artigo, 90/5/5; deduplicação exata normalizada antes dos splits. Sem deduplicação semântica.",
    }
    (args.output / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2))
    print(json.dumps(manifest, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
