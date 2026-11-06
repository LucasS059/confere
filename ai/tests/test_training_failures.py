import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch
import torch
from confere_ai.report import record_failure


class TrainingFailureTests(unittest.TestCase):
    def test_failure_report_preserves_checkpoint_and_marks_unknown_counters(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory)
            (root/"run.json").write_text("{}")
            metrics=[dict(step=0,elapsed_seconds=1,train_loss=2,validation_loss=2),dict(step=7,elapsed_seconds=12,train_loss=1,validation_loss=1)]
            (root/"metrics.jsonl").write_text("".join(json.dumps(r)+"\n" for r in metrics))
            torch.save(dict(step=7,model=dict(weight=torch.tensor([3.]))),root/"last.pt")
            checkpoint=(root/"last.pt").read_bytes()
            with patch("confere_ai.report.create_report",return_value=root/"report.pdf"):
                self.assertEqual(record_failure(root,RuntimeError("MPS memory")),root/"report.pdf")
            self.assertEqual((root/"last.pt").read_bytes(),checkpoint)
            summary=json.loads((root/"summary.json").read_text())
            self.assertEqual(summary["final_step"],7)
            self.assertEqual(summary["measurement_scope"],"until_last_checkpoint_only")
            self.assertNotIn("tokens_processed",summary)
            self.assertEqual(json.loads((root/"failure.json").read_text())["last_checkpoint_step"],7)
            with self.assertRaises(ValueError):record_failure(root,RuntimeError("again"))

    def test_reusing_completed_directory_does_not_mark_it_as_failed(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory)
            (root/"run.json").write_text("preservado")
            result=subprocess.run([sys.executable,"-m","confere_ai.instruct","--run-dir",str(root),"--init-from","missing.pt"],capture_output=True,text=True)
            self.assertNotEqual(result.returncode,0)
            self.assertEqual((root/"run.json").read_text(),"preservado")
            self.assertFalse((root/"failure.json").exists())
