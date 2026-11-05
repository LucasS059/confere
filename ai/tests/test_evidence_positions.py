import json
import sys
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
from prepare_evidence_positions import position_rows
from confere_ai.tokenizer import ByteBPE
from confere_ai.grounding import judge
from confere_ai.project_review import input_ids


class EvidencePositionTests(unittest.TestCase):
    def test_targets_follow_evidence_across_positions_and_fit(self):
        tokenizer=ByteBPE([]);rows=position_rows(tokenizer,4)
        self.assertEqual({json.loads(r["target"])["unit"] for r in rows},{None,"page:1","page:2","page:3","page:4"})
        for row in rows:
            self.assertTrue(judge(row["target"],row)["exact_match"])
            self.assertLessEqual(len(input_ids(row["requirement"],row["units"],tokenizer))+64,1024)
            self.assertEqual(row["split"],"train")
