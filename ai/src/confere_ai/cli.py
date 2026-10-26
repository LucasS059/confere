import argparse
import json
import sys
from pathlib import Path

from .dataset import validate_dataset
from .extract import extract_document


def main() -> int:
    parser = argparse.ArgumentParser(description="Preparação local dos dados do Confere")
    commands = parser.add_subparsers(dest="command", required=True)
    extract = commands.add_parser("extract", help="Extrair PDF/DOCX para JSON no stdout")
    extract.add_argument("file", type=Path)
    validate = commands.add_parser("validate", help="Validar JSONL e evidências nos documentos")
    validate.add_argument("file", type=Path)
    args = parser.parse_args()
    try:
        result = extract_document(args.file) if args.command == "extract" else validate_dataset(args.file)
    except Exception as error:
        print(f"Erro: {error}", file=sys.stderr)
        return 1
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
