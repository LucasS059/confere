import json
from pathlib import Path
import random
import sys
import tempfile
import unittest

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
from prepare_informal_dialogues import extra_rows, informalize
from confere_ai.instruct import load_instructions
from evaluate_informal_dialogues import cohorts, passes


class InformalDialogueTests(unittest.TestCase):
    def test_retention_cohorts_exclude_new_informal_rows(self):
        rows=[dict(id=name,split="validation",task=task) for name,task in (
            ("old", "conversation_identity"), ("flow-1", "conversation_flow_state"),
            ("slang-dialogue-validation-1", "conversation_slang_function"),
            ("human", "human_dialogue"))]
        self.assertEqual({k:len(v) for k,v in cohorts(rows).items()},dict(informal=1,flow=1,legacy=1))

    def test_informal_success_does_not_override_legacy_regression(self):
        samples=[dict(project_id=str(i//6),task="conversation_fixture",exact_match=True,dropped_turns=0) for i in range(24)]
        controlled=dict(correct=24,total=24,samples=samples)
        legacy=dict(correct=513,total=535,samples=samples)
        result=dict(informal=controlled,flow=controlled,legacy=legacy)
        self.assertFalse(passes(result,result))
        legacy["correct"]=514
        self.assertTrue(passes(result,result))

    def test_name_memory_is_not_rewritten(self):
        base=[dict(id="name",project_id="name",split="train",task="conversation_memory",history=[],turn_index=0,
                   prompt="Meu nome é José.",target="Prazer, José.",provenance=dict(kind="synthetic_authored"))]
        self.assertFalse(any(r["id"].startswith("slang-augment") for r in extra_rows(base,augment_count=10,train_conversations=0)))

    def test_abbreviations_keep_whole_word_boundaries(self):
        text=informalize("Você também sabe o que fazer, por favor? Não estou bem.",random.Random(4))
        self.assertNotIn("Você",text)
        self.assertNotIn("por favor",text)
        self.assertEqual(informalize("avocado",random.Random(4)),"avocado")

    def test_splits_targets_and_conversations_remain_consistent(self):
        base=[dict(id="base",project_id="base",split="train",task="conversation_function",history=[],turn_index=0,
                   prompt="O que você faz?",target="Sou um experimento para apoiar a conferência de projetos.",response_tokens=256,provenance=dict(kind="synthetic_authored"))]
        before=json.dumps(base)
        rows=base+extra_rows(base,augment_count=20,train_conversations=30)
        self.assertEqual(json.dumps(base),before)
        augmented=[r for r in rows if r["id"].startswith("slang-augment")]
        self.assertTrue(augmented)
        self.assertTrue(all(r["split"]=="train" and r["target"]==base[0]["target"] for r in augmented))
        with tempfile.TemporaryDirectory() as directory:
            path=Path(directory)/"examples.jsonl"
            path.write_text("".join(json.dumps(r,ensure_ascii=False)+"\n" for r in rows))
            self.assertEqual(len(load_instructions(path)[0]),len(rows))
        validation=[r for r in rows if r["split"]=="validation"]
        alternate=extra_rows(base,augment_count=10,train_conversations=10)
        self.assertEqual(validation,[r for r in alternate if r["split"]=="validation"])
