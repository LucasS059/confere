import json
import sys
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
from prepare_document_contrasts import documents, FORMS
from confere_ai.instruct import acceptance
from confere_ai.grounding import judge


class DocumentContrastTests(unittest.TestCase):
    def test_labels_have_correct_evidence_and_distractors(self):
        for row in documents():
            self.assertTrue(judge(row["target"],row)["exact_match"])
            self.assertEqual(len(row["units"]),4)
            target=json.loads(row["target"])
            if target["unit"]:
                text=next(u["text"] for u in row["units"] if u["id"]==target["unit"])
                feature=row["requirement"].removeprefix("O projeto deve incluir ").rstrip(".")
                positive,negative=FORMS[row["split"]][0]
                if row["split"]!="train":
                    self.assertEqual(text,(positive if target["status"]=="atendido" else negative).format(feature))

    def test_conversation_success_cannot_hide_document_failure(self):
        rows=[dict(task="conversation_fixture",exact_match=True),dict(task="grounded_atendido",exact_match=False,valid_format=True,reference_valid=True)]
        self.assertFalse(acceptance(dict(samples=rows))["passed"])
        rows[-1]["exact_match"]=True
        self.assertTrue(acceptance(dict(samples=rows))["passed"])
