import json
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from build_conversation_curriculum import build as original
from build_conversation_robust import build
from build_conversation_contrasts import build as contrasts
from build_conversation_uncertainty import build as uncertainty
from build_conversation_identity import build as identity
from confere_ai.instruct import load_instructions
from evaluate_conversation_adoption import passes


class RobustCurriculumTests(unittest.TestCase):
    def test_adoption_requires_all_gates_without_relaxing_family_threshold(self):
        def result(correct):
            return {"samples": [dict(id=f"old-{i}", task="conversation_identity", exact_match=i<correct)
                                for i in range(415)]}
        regressions = [dict(exact_match=True) for _ in range(6)]
        self.assertTrue(passes(result(400), result(325), regressions))
        self.assertFalse(passes(result(330), result(325), regressions))
        self.assertFalse(passes(result(400), result(401), regressions))
        self.assertFalse(passes(result(400), result(325), regressions[:-1]))
        regressions[-1]["exact_match"] = False
        self.assertFalse(passes(result(400), result(325), regressions))

    def test_preserves_evaluation_and_prevents_conflicting_contexts(self):
        for builder in (build, contrasts, uncertainty, identity):
            rows = builder()
            self.assertEqual([r for r in original() if r["split"] != "train"],
                             [r for r in rows if r["split"] != "train"])
            with tempfile.TemporaryDirectory() as directory:
                path = Path(directory) / "examples.jsonl"
                path.write_text("".join(json.dumps(r, ensure_ascii=False)+"\n" for r in rows))
                checked, _ = load_instructions(path)
                self.assertEqual(len(checked), len(rows))
        repairs = [r for r in rows if r["id"].startswith("robust-") and r["prompt"] == "bugou?"]
        self.assertTrue(any(r["history"] == [] for r in repairs))
        self.assertTrue(any("Confere Confere Confere" in str(r["history"]) for r in repairs))
