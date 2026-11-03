import json
import sys
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
from prepare_document_contrasts import documents, FORMS
from confere_ai.instruct import acceptance
from confere_ai.grounding import judge
from prepare_document_lexical import LEXICAL, balanced_replay
from evaluate_document_contrasts import document_passes


class DocumentContrastTests(unittest.TestCase):
    def test_perfection_rejects_one_wrong_answer_or_reference(self):
        result=dict(total=100,valid=100,references=100,families=dict(grounded_atendido=[99,100]))
        self.assertTrue(document_passes(result,.9))
        self.assertFalse(document_passes(result,1))
        result["families"]["grounded_atendido"][0]=100
        self.assertTrue(document_passes(result,1))
        result["references"]=99
        self.assertFalse(document_passes(result,1))

    def test_lexical_expansion_freezes_reserved_rows(self):
        self.assertEqual([r for r in documents() if r["split"]!="train"],
                         [r for r in documents(LEXICAL) if r["split"]!="train"])
        self.assertTrue(any("ausência" in r["prompt"] for r in documents(LEXICAL) if r["split"]=="train"))

    def test_balancing_preserves_groups_and_excludes_reserved(self):
        rows=[dict(project_id=str(i//2),task="conversation_"+str(i//4),split="train",turn_index=i%2) for i in range(8)]
        rows.append(dict(project_id="reserved",task="conversation_2",split="test",turn_index=0))
        result=balanced_replay(rows,1)
        self.assertEqual(len(result),4)
        self.assertTrue(all(r["split"]=="train" for r in result))
        self.assertEqual(sorted(r["turn_index"] for r in result),[0,0,1,1])

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
