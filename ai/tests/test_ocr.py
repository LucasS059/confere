"""Teste do overlay sem depender da instalação do Apple Vision no CI."""

import importlib.util
import tempfile
import unittest
from pathlib import Path

from pypdf import PdfReader, PdfWriter


spec = importlib.util.spec_from_file_location(
    "ocr_pdf", Path(__file__).resolve().parents[1] / "scripts/ocr_pdf.py"
)
ocr = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ocr)


class OCRTests(unittest.TestCase):
    def test_searchable_copy_preserves_original_and_pages(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source, target = root / "original.pdf", root / "searchable.pdf"
            writer = PdfWriter()
            writer.add_blank_page(width=600, height=800)
            writer.write(source)
            original = source.read_bytes()
            ocr.make_searchable(source, target, [{
                "number": 1,
                "lines": [{"text": "Evidência de autenticação", "x": 0.1, "y": 0.8, "height": 0.02}],
            }])
            self.assertEqual(source.read_bytes(), original)
            result = PdfReader(target)
            self.assertEqual(len(result.pages), 1)
            self.assertEqual(float(result.pages[0].mediabox.width), 600)
            self.assertIn("Evidência de autenticação", result.pages[0].extract_text())
            operations = result.pages[0].get_contents().operations
            self.assertTrue(any(operator == b"Tr" and operands == [3] for operands, operator in operations))

    def test_page_count_mismatch_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "original.pdf"
            writer = PdfWriter()
            writer.add_blank_page(width=600, height=800)
            writer.write(source)
            with self.assertRaisesRegex(ValueError, "Quantidade"):
                ocr.make_searchable(source, Path(directory) / "target.pdf", [])

    def test_page_without_recognized_text_is_preserved(self):
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "original.pdf"
            target = Path(directory) / "searchable.pdf"
            writer = PdfWriter()
            writer.add_blank_page(width=600, height=800)
            writer.write(source)
            ocr.make_searchable(source, target, [{"number": 1, "lines": []}])
            result = PdfReader(target)
            self.assertEqual(len(result.pages), 1)
            self.assertEqual(result.pages[0].extract_text(), "")

    def test_rotated_pages_are_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "original.pdf"
            writer = PdfWriter()
            writer.add_blank_page(width=600, height=800).rotate(90)
            writer.write(source)
            with self.assertRaisesRegex(ValueError, "rotação"):
                ocr.make_searchable(source, Path(directory) / "target.pdf", [{"number": 1, "lines": []}])
