import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


class DocumentTransferTests(unittest.TestCase):
    def test_existing_evidence_blocks_repeated_reserved_test(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            evidence = root / "document-transfer.json"
            evidence.write_text("evidência preservada")
            script = Path(__file__).resolve().parents[1] / "scripts/evaluate_document_transfer.py"
            result = subprocess.run([sys.executable, str(script), str(root)], capture_output=True, text=True)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("não consultar o teste novamente", result.stderr)
            self.assertEqual(evidence.read_text(), "evidência preservada")
