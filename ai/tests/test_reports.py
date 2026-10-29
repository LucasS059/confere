import json
import tempfile
import unittest
from pathlib import Path

from pypdf import PdfReader
from confere_ai.language_data import validate_expansion
from confere_ai.report import create_report


class ReportTests(unittest.TestCase):
    def test_report_preserves_metrics_and_marks_missing_samples(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            info = {"parameters": 100, "model_config": {}, "device": "cpu", "dataset_fingerprint": "abc"}
            summary = {"start_step": 0, "final_step": 1, "elapsed_seconds": 1}
            metrics = [{"step": 0, "train_loss": 5., "validation_loss": 6.},
                       {"step": 1, "train_loss": 3., "validation_loss": 4.}]
            (root / "run.json").write_text(json.dumps(info))
            (root / "summary.json").write_text(json.dumps(summary))
            (root / "metrics.jsonl").write_text("\n".join(json.dumps(row) for row in metrics))
            pdf = create_report(root, root / "report.pdf")
            reader = PdfReader(pdf)
            text = "\n".join(page.extract_text() for page in reader.pages)
            self.assertEqual(len(reader.pages), 2)
            self.assertIn("6.0000 / 4.0000", text)
            self.assertIn("Não há amostras", text)
            self.assertIn("abc", text)

    def test_expansion_preserves_old_data_and_prevents_split_leakage(self):
        old = [{"id": "1", "text": "texto original", "split": "train"}]
        validate_expansion(old, old + [{"id": "2", "text": "novo", "split": "validation"}])
        for new in ([], [{"id": "1", "text": "alterado", "split": "train"}],
                    [{"id": "1", "text": "texto original", "split": "validation"}],
                    old + [{"id": "2", "text": "texto  original", "split": "validation"}]):
            with self.assertRaises(ValueError):
                validate_expansion(old, new)
