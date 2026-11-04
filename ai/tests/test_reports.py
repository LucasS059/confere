import json
import tempfile
import unittest
from pathlib import Path

from pypdf import PdfReader
from confere_ai.language_data import validate_expansion
from confere_ai.report import create_report


class ReportTests(unittest.TestCase):
    def test_long_context_report_exposes_failed_joint_gate(self):
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder)
            (root/"run.json").write_text(json.dumps(dict(parameters=100,device="cpu",dataset_fingerprint="abc",config=dict(block_size=1024))))
            (root/"summary.json").write_text(json.dumps(dict(start_step=0,final_step=1,elapsed_seconds=1)))
            (root/"metrics.jsonl").write_text(json.dumps(dict(step=1,train_loss=1.,validation_loss=1.)))
            docs=dict(correct=3,total=3,valid=3,references=3,families={"grounded_atendido":[3,3]})
            cohorts=dict(short_documents=docs,long_documents=docs,conversation=dict(correct=5,total=10,families={"conversation_memory":[5,10]}))
            pilot=dict(statuses=["evidencia_insuficiente"],audit=dict(invalid_calls=54,literal_quotes_verified=3))
            record=dict(policy="Política conjunta",note="Receitas compartilhadas",before=cohorts,after=cohorts,
                        pilot_before=pilot,pilot_after=pilot,gates=dict(conversation=False),failed_long_examples=[])
            (root/"long-document-evaluation.json").write_text(json.dumps(record))
            pdf=create_report(root,root/"report.pdf")
            text="\n".join(page.extract_text() for page in PdfReader(pdf).pages)
            self.assertIn("conversation: False",text)
            self.assertIn("conversation_memory: 5/10",text)
            self.assertIn("Teste reservado não consultado",text)

    def test_authored_conversation_manifest_is_not_reported_as_human_source(self):
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder)
            (root/"manifest.json").write_text(json.dumps(dict(source_sha256="authored")))
            (root/"run.json").write_text(json.dumps(dict(objective="conversation",data=str(root/"examples.jsonl"),parameters=100,device="cpu",dataset_fingerprint="abc",config=dict(block_size=1024),settings=dict(generation_budget=256))))
            (root/"summary.json").write_text(json.dumps(dict(start_step=0,final_step=1,elapsed_seconds=1)))
            (root/"metrics.jsonl").write_text(json.dumps(dict(step=1,train_loss=1.,validation_loss=1.)))
            pdf=create_report(root,root/"report.pdf")
            text="\n".join(p.extract_text() for p in PdfReader(pdf).pages)
            self.assertNotIn("Fonte humana:",text)

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
