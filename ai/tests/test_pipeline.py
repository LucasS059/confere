import copy
import json
import tempfile
import unittest
from pathlib import Path

from docx import Document
from jsonschema import ValidationError
from pypdf import PdfWriter
from reportlab.pdfgen.canvas import Canvas

from confere_ai.dataset import validate_dataset
from confere_ai.extract import extract_document


class PipelineTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        canvas = Canvas(str(self.root / "brief.pdf"))
        canvas.drawString(50, 750, "O projeto deve exigir autenticação.")
        canvas.showPage()
        canvas.drawString(50, 750, "A evidência deve indicar a localização.")
        canvas.save()
        document = Document()
        document.add_paragraph("Somente usuários autenticados podem acessar.")
        table = document.add_table(rows=1, cols=2)
        table.cell(0, 0).text = "Testes"
        table.cell(0, 1).text = "duas semanas"
        document.add_paragraph("Fim do relatório.")
        document.save(self.root / "submission.docx")
        self.row = {
            "schema_version": 1,
            "id": "example-1",
            "project_id": "project-1",
            "split": "train",
            "provenance": {"kind": "authored", "usage_rights": "Fixture de teste", "reviewed_by": "Teste", "derived_from": None},
            "documents": ["brief.pdf", "submission.docx"],
            "requirement": {"id": "R1", "text": "O projeto deve exigir autenticação.", "source": {"document": "brief.pdf", "unit": "page:1", "quote": "O projeto deve exigir autenticação."}},
            "expected": {"status": "atendido", "evidence": [{"document": "submission.docx", "unit": "paragraph:1", "quote": "Somente usuários autenticados podem acessar."}], "justification": "O acesso exige autenticação."},
        }

    def validate(self, *rows):
        target = self.root / "examples.jsonl"
        target.write_text("\n".join(json.dumps(row, ensure_ascii=False) for row in rows))
        return validate_dataset(target)

    def test_pdf_preserves_pages_accents_and_hash(self):
        result = extract_document(self.root / "brief.pdf")
        self.assertEqual([unit["id"] for unit in result["units"]], ["page:1", "page:2"])
        self.assertIn("autenticação", result["units"][0]["text"])
        self.assertIn("localização", result["units"][1]["text"])
        self.assertEqual(len(result["sha256"]), 64)

    def test_docx_preserves_table_and_paragraph_order(self):
        result = extract_document(self.root / "submission.docx")
        self.assertEqual([unit["id"] for unit in result["units"]], ["paragraph:1", "table:1:row:1", "paragraph:2"])
        self.assertEqual(result["units"][1]["text"], "Testes | duas semanas")

    def test_empty_pdf_is_flagged(self):
        writer = PdfWriter()
        writer.add_blank_page(width=100, height=100)
        writer.write(self.root / "empty.pdf")
        result = extract_document(self.root / "empty.pdf")
        self.assertEqual(result["units"][0]["text"], "")
        self.assertTrue(any("OCR" in warning for warning in result["warnings"]))

    def test_encrypted_pdf_is_rejected(self):
        writer = PdfWriter()
        writer.add_blank_page(width=100, height=100)
        writer.encrypt("secret")
        writer.write(self.root / "encrypted.pdf")
        with self.assertRaisesRegex(ValueError, "sem senha"):
            extract_document(self.root / "encrypted.pdf")

    def test_legacy_word_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "DOCX"):
            extract_document(self.root / "legacy.doc")

    def test_valid_dataset(self):
        result = self.validate(self.row)
        self.assertEqual(result["examples"], 1)
        self.assertEqual(result["documents"], 2)

    def test_invented_quote_is_rejected(self):
        self.row["expected"]["evidence"][0]["quote"] = "Texto inexistente"
        with self.assertRaisesRegex(ValueError, "Citação ausente"):
            self.validate(self.row)

    def test_wrong_location_is_rejected(self):
        self.row["expected"]["evidence"][0]["unit"] = "paragraph:2"
        with self.assertRaisesRegex(ValueError, "Citação ausente"):
            self.validate(self.row)

    def test_requirement_must_match_its_source(self):
        self.row["requirement"]["text"] = "O projeto deve funcionar sem autenticação."
        with self.assertRaisesRegex(ValueError, "Texto do requisito"):
            self.validate(self.row)

    def test_unrecognized_status_is_rejected(self):
        self.row["expected"]["status"] = "aprovado_com_certeza"
        with self.assertRaises(ValidationError):
            self.validate(self.row)

    def test_conclusive_status_requires_evidence(self):
        self.row["expected"]["evidence"] = []
        with self.assertRaises(ValidationError):
            self.validate(self.row)

    def test_project_leakage_is_rejected(self):
        other = copy.deepcopy(self.row)
        other.update(id="example-2", split="test")
        with self.assertRaisesRegex(ValueError, "Projeto em mais de um split"):
            self.validate(self.row, other)

    def test_identical_file_leakage_is_rejected(self):
        other = copy.deepcopy(self.row)
        other.update(id="example-2", project_id="other-project", split="test")
        with self.assertRaisesRegex(ValueError, "Arquivo idêntico"):
            self.validate(self.row, other)

    def test_duplicate_example_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "ID duplicado"):
            self.validate(self.row, self.row)

    def test_path_outside_dataset_is_rejected(self):
        self.row["documents"].append("../outside.pdf")
        with self.assertRaisesRegex(ValueError, "fora do diretório"):
            self.validate(self.row)

    def test_empty_quote_is_rejected(self):
        self.row["expected"]["evidence"][0]["quote"] = "   "
        with self.assertRaisesRegex(ValueError, "Citação ausente"):
            self.validate(self.row)

    def test_undeclared_evidence_document_is_rejected(self):
        self.row["expected"]["evidence"][0]["document"] = "unknown.pdf"
        with self.assertRaisesRegex(ValueError, "Documento não declarado"):
            self.validate(self.row)

    def test_checked_in_authored_dataset(self):
        result = validate_dataset(Path(__file__).resolve().parents[1] / "data/authored/examples.jsonl")
        self.assertEqual(result["projects"], 3)
        self.assertEqual(result["splits"], {"train": 6, "validation": 3, "test": 3})
        self.assertEqual(set(result["statuses"]), {"atendido", "nao_atendido", "evidencia_insuficiente"})


if __name__ == "__main__":
    unittest.main()
