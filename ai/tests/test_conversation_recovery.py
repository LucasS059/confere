import json
import sys
import subprocess
import tempfile
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
from prepare_conversation_recovery import recovery_rows
from confere_ai.instruct import load_instructions
from evaluate_document_contrasts import matching_cohort, matching_validation_rows


class RecoveryTests(unittest.TestCase):
    def test_cached_reference_also_requires_initial_history_to_match(self):
        rows=[dict(split="validation",history=[["oi","olá"]],prompt="seu nome?",target="Confere")]
        changed=[dict(rows[0],history=[["outra pergunta","outra resposta"]])]
        self.assertFalse(matching_validation_rows(rows,changed))
        self.assertTrue(matching_validation_rows(rows,rows+[dict(split="train",prompt="novo")]))

    def test_cached_reference_requires_same_order_prompts_and_targets(self):
        rows=[dict(id="a",task="conversation_fixture",prompt="oi",expected="olá"),
              dict(id="b",task="grounded_atendido",prompt="requisito",expected="json")]
        left=dict(samples=rows)
        self.assertTrue(matching_cohort(left,dict(samples=[dict(r) for r in rows])))
        self.assertFalse(matching_cohort(left,dict(samples=list(reversed(rows)))))
        changed=[dict(r) for r in rows];changed[0]["expected"]="outra resposta"
        self.assertFalse(matching_cohort(left,dict(samples=changed)))

    def test_open_dialogue_does_not_overwrite_existing_diagnostic(self):
        with tempfile.TemporaryDirectory() as folder:
            path=Path(folder)/"open-dialogue.json";path.write_text("preservado")
            script=Path(__file__).resolve().parents[1]/"scripts/evaluate_open_dialogue.py"
            result=subprocess.run([sys.executable,str(script),folder],capture_output=True,text=True)
            self.assertNotEqual(result.returncode,0)
            self.assertIn("Diagnóstico existente",result.stderr)
            self.assertEqual(path.read_text(),"preservado")

    def test_new_rows_are_train_only_and_keep_generated_history_consistent(self):
        rows=recovery_rows()
        self.assertTrue(all(r["split"]=="train" and r["response_tokens"]==256 for r in rows))
        groups={}
        for row in rows:
            previous=groups.get(row["project_id"])
            if previous:
                self.assertEqual(row["history"],previous["history"]+[[previous["prompt"],previous["target"]]])
            groups[row["project_id"]]=row
        function=[r for r in rows if r["id"].startswith("recovery-function-")]
        self.assertTrue(any(r["history"] for r in function))
        self.assertTrue(all(r["target"]=="Sou um experimento para apoiar a conferência de projetos." for r in function))
        # O carregador precisa validar também as conversas completas, não só o schema.
        with tempfile.TemporaryDirectory() as folder:
            path=Path(folder)/"data.jsonl"
            validation=dict(function[0],id="unique-val",project_id="unique-val",split="validation",history=[],prompt="fixture reservada")
            path.write_text("".join(json.dumps(r,ensure_ascii=False)+"\n" for r in rows+[validation]))
            self.assertEqual(len(load_instructions(path)[0]),len(rows)+1)
