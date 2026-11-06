import json
import sys
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
from diagnose_evidence_context import annotated_row


class EvidenceDiagnosticTests(unittest.TestCase):
    def test_oracle_preserves_alias_and_does_not_label_mention_as_support(self):
        pairs=[("atendido","O projeto inclui testes.")]
        units=[dict(id="page:1",text="Reunião sobre testes."),dict(id="page:3",text="Ata. O projeto inclui testes. Encerramento.")]
        row,oracle=annotated_row("Testes",units,pairs)
        self.assertEqual(json.loads(row["target"]),dict(status="atendido",unit="page:3"))
        self.assertEqual(oracle[1],dict(id="page:3",text="O projeto inclui testes."))
        row,_=annotated_row("Testes",units[:1],pairs)
        self.assertEqual(json.loads(row["target"]),dict(status="evidencia_insuficiente",unit=None))

    def test_multiple_hits_require_specific_annotation(self):
        with self.assertRaises(ValueError):
            annotated_row("Testes",[dict(id="page:1",text="Presente. Ausente.")],[("atendido","Presente."),("nao_atendido","Ausente.")])
