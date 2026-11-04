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
    review = commands.add_parser("review-project", help="Conferência experimental de todo o texto de PDFs/DOCX")
    review.add_argument("files", nargs="+", type=Path)
    review.add_argument("--requirement", action="append", required=True)
    review.add_argument("--checkpoint", type=Path, required=True)
    review.add_argument("--device", choices=["auto", "cpu", "mps"], default="auto")
    review.add_argument("--output", type=Path, help="Salvar JSON novo; rejeita sobrescrita")
    args = parser.parse_args()
    try:
        if args.command == "review-project":
            if args.output and args.output.exists():raise ValueError("O arquivo de saída já existe.")
            if args.output and not args.output.parent.is_dir():raise ValueError("O diretório de saída não existe.")
            from .project_review import review_files
            result = review_files(args.files,args.requirement,args.checkpoint,args.device)
            if args.output:
                with args.output.open("x",encoding="utf-8") as file:
                    json.dump(result,file,ensure_ascii=False,indent=2)
                print(str(args.output))
                return 0
        else:
            result = extract_document(args.file) if args.command == "extract" else validate_dataset(args.file)
    except Exception as error:
        print(f"Erro: {error}", file=sys.stderr)
        return 1
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
