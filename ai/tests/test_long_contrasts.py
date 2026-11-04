import json
import sys
import unittest
from pathlib import Path

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
from prepare_long_contrasts import template_rows, contrast_rows, MARKER
from confere_ai.grounding import judge
from confere_ai.project_review import input_ids
from confere_ai.tokenizer import ByteBPE


class LongContrastTests(unittest.TestCase):
    def test_polarity_changes_label_but_mention_is_not_evidence(self):
        rows=template_rows([dict(id="paragraph:9",text="Registro único. "+MARKER)],"testes","pair",ByteBPE([]),
                           ("Há suporte para {}.","Falta suporte para {}."),"minimal_pair")
        self.assertEqual([json.loads(r["target"])["status"] for r in rows],["atendido","nao_atendido","evidencia_insuficiente"])
        self.assertIn("discutiu testes",rows[-1]["prompt"])
        self.assertEqual(json.loads(rows[-1]["target"])["unit"],None)
        self.assertEqual({r["project_id"] for r in rows},{"pair"})

    def test_cli_chunks_have_valid_local_targets_and_no_silent_overflow(self):
        tokenizer=ByteBPE([])
        rows=contrast_rows(tokenizer,12)
        self.assertEqual(len({r["prompt"] for r in rows}),len(rows))
        self.assertTrue(all(r["split"]=="train" for r in rows))
        self.assertEqual({r["training_profile"] for r in rows},{"minimal_pair","cli_fragment"})
        for row in rows:
            self.assertLessEqual(len(input_ids(row["requirement"],row["units"],tokenizer))+64,1024)
            self.assertTrue(judge(row["target"],row)["exact_match"])
            self.assertNotIn(MARKER,row["prompt"])
        self.assertTrue(any(r["training_profile"]=="cli_fragment" and json.loads(r["target"])["unit"] is None for r in rows))
