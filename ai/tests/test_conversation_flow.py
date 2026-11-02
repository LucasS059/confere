import json
from pathlib import Path
import sys
import subprocess
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]/"scripts"))
from build_conversation_flow import build
from build_conversation_identity import build as legacy
from build_conversation_flow_expanded import build as expanded
from confere_ai.instruct import load_instructions
from evaluate_conversation_flow import conversation_metrics, flow_passes
from prepare_dialogue_restarts import restart_rows


class ConversationFlowTests(unittest.TestCase):
    def test_restart_contrasts_include_post_farewell_context_without_changing_base(self):
        row=dict(id="flow-train-fixture",project_id="fixture",split="train",prompt="olá",target="Olá! Sou o Confere.",history=[])
        original=json.dumps(row,sort_keys=True)
        extra=restart_rows([row],count=20)
        self.assertEqual(json.dumps(row,sort_keys=True),original)
        self.assertTrue(all(r["split"]=="train" for r in extra))
        self.assertTrue(any("Podemos conversar quando você quiser" in str(r["history"]) and r["target"]=="Olá! Sou o Confere." for r in extra))
        by_context={}
        for r in extra:by_context.setdefault(json.dumps(r["history"]),set()).add(r["target"])
        self.assertTrue(any({"Olá! Sou o Confere.","Tudo bem. Podemos conversar quando você quiser."}<=targets for targets in by_context.values()))

    def test_capture_replay_preserves_existing_evidence(self):
        with tempfile.TemporaryDirectory() as directory:
            output=Path(directory)/"evidence.json"
            output.write_text("evidência anterior")
            command=[sys.executable,str(Path(__file__).resolve().parents[1]/"scripts/evaluate_flow_captures.py"),"missing.pt",str(output)]
            result=subprocess.run(command,capture_output=True,text=True)
            self.assertNotEqual(result.returncode,0)
            self.assertIn("Saída já existe",result.stderr)
            self.assertEqual(output.read_text(),"evidência anterior")

    def test_whole_conversation_gate_rejects_distributed_failures_and_drops(self):
        samples=[dict(project_id=str(i//8),task="conversation_flow_state",exact_match=True,dropped_turns=0) for i in range(32)]
        def result(): return dict(correct=sum(r["exact_match"] for r in samples),total=len(samples),samples=samples)
        self.assertTrue(flow_passes(result()))
        for i in (0,8,16):samples[i]["exact_match"]=False
        self.assertEqual(conversation_metrics(result())["complete"],1)
        self.assertFalse(flow_passes(result()))
        for row in samples:row["exact_match"]=True
        samples[0]["dropped_turns"]=1
        self.assertFalse(flow_passes(result()))

    def test_scenarios_preserve_legacy_and_keep_state_corrections(self):
        rows = build()
        self.assertEqual([r for r in rows if not r["id"].startswith("flow-")], legacy())
        flows = [r for r in rows if r["id"].startswith("flow-")]
        groups = {}
        for row in flows:
            groups.setdefault(row["project_id"], []).append(row)
        self.assertTrue(all(len(group)==8 for group in groups.values()))
        corrected = [r for r in flows if r["task"]=="conversation_flow_state" and r["target"]=="Você disse que ainda não tem um projeto."]
        self.assertTrue(corrected)
        self.assertTrue(all("ainda não tem um projeto" in r["history"][-1][1] for r in corrected))
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory)/"examples.jsonl"
            path.write_text("".join(json.dumps(r,ensure_ascii=False)+"\n" for r in rows))
            loaded, _ = load_instructions(path)
            self.assertEqual(len(loaded), len(rows))

    def test_expansion_freezes_all_evaluation_rows(self):
        rows=expanded()
        self.assertEqual([r for r in rows if r["split"]!="train"], [r for r in build() if r["split"]!="train"])
        with tempfile.TemporaryDirectory() as directory:
            path=Path(directory)/"expanded.jsonl"
            path.write_text("".join(json.dumps(r,ensure_ascii=False)+"\n" for r in rows))
            loaded,_=load_instructions(path)
            self.assertEqual(len(loaded),len(rows))
