import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

try:
    from confere_ai.instruct import load_instructions, acceptance
except ImportError:
    load_instructions = None

spec = importlib.util.spec_from_file_location("build_instructions", Path(__file__).resolve().parents[1]/"scripts/build_instructions.py")
builder = importlib.util.module_from_spec(spec)
spec.loader.exec_module(builder)


@unittest.skipIf(load_instructions is None, "Instale as dependências de treino")
class InstructionTests(unittest.TestCase):
    def test_grounded_fixture_has_separate_projects_and_valid_targets(self):
        spec3 = importlib.util.spec_from_file_location("build_grounding", Path(__file__).resolve().parents[1]/"scripts/build_grounding.py")
        module = importlib.util.module_from_spec(spec3)
        spec3.loader.exec_module(module)
        rows, _ = self.load_rows(module.build())
        self.assertEqual(len(rows), 1704)
        self.assertEqual(sum(r["task"].startswith("grounded_") and r["split"]=="validation" for r in rows), 90)
        bad = next(r for r in rows if r["task"] == "grounded_atendido")
        bad["prompt"] += " Resposta inventada"
        with self.assertRaises(ValueError): self.load_rows(rows)

    def test_acceptance_requires_every_critical_task_not_just_total(self):
        result = {"samples": [{"task": task, "exact_match": True} for task in ("copy", "field", "missing", "insufficient_context")]}
        self.assertTrue(acceptance(result)["passed"])
        result["samples"][0]["exact_match"] = False
        self.assertFalse(acceptance(result)["passed"])
        self.assertFalse(acceptance({"samples": []})["passed"])

    def test_v2_data_is_disjoint_and_has_new_held_out_formats(self):
        spec2 = importlib.util.spec_from_file_location("build_v2", Path(__file__).resolve().parents[1]/"scripts/build_instructions_v2.py")
        module = importlib.util.module_from_spec(spec2)
        spec2.loader.exec_module(module)
        rows, _ = self.load_rows(module.build())
        self.assertEqual(rows, module.build())
        self.assertEqual(len(rows), 4376)
        self.assertEqual(sum(row["split"] == "validation" for row in rows), 168)
        self.assertTrue(any(row["task"] == "insufficient_context" for row in rows))

    def load_rows(self, rows):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder)/"data.jsonl"
            path.write_text("\n".join(json.dumps(row) for row in rows))
            return load_instructions(path)

    def test_generated_data_is_deterministic_and_project_disjoint(self):
        rows, digest = self.load_rows(builder.build())
        self.assertEqual(builder.build(), builder.build())
        self.assertEqual(len(digest), 64)
        self.assertEqual({row["split"] for row in rows}, {"train", "validation", "test"})
        self.assertEqual(sum(row["split"] == "train" for row in rows), 167)

    def test_duplicate_prompts_and_project_leakage_are_rejected(self):
        rows = builder.build()
        duplicate = dict(rows[0], id="different")
        with self.assertRaises(ValueError): self.load_rows(rows+[duplicate])
        leakage = dict(rows[0], id="leak", split="validation", prompt="outro pedido")
        with self.assertRaises(ValueError): self.load_rows(rows+[leakage])

    def test_unknown_sources_and_missing_validation_are_rejected(self):
        rows = builder.build()
        rows[0]["provenance"] = {"kind": "real"}
        with self.assertRaises(ValueError): self.load_rows(rows)
        with self.assertRaises(ValueError): self.load_rows([r for r in builder.build() if r["split"] == "train"])
