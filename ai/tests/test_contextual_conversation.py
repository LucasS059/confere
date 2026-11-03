import json
import sys
import unittest
import torch
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
from prepare_contextual_conversation import build_rows, contextual_rows
from prepare_document_lexical import paired_documents
from confere_ai.instruct import training_indices


class ContextualTests(unittest.TestCase):
    def test_explicit_document_mixture_uses_separate_homogeneous_batches(self):
        generator=torch.Generator().manual_seed(42)
        batches=[training_indices(4,[],[0,1],3,0,generator,documents=[2,3],document_fraction=.4) for _ in range(100)]
        self.assertTrue(any(all(i in {2,3} for i in batch) for batch in batches))
        self.assertTrue(any(all(i in {0,1} for i in batch) for batch in batches))
        self.assertTrue(all(set(batch)<={0,1} or set(batch)<={2,3} for batch in batches))

    def test_counterbalanced_mood_positions_and_name_corrections(self):
        rows=contextual_rows(self.fixture(),True)
        groups={}
        for row in rows:
            if row["project_id"].startswith("balanced-contextual-"):groups.setdefault(row["project_id"],[]).append(row)
        positions={next(i for i,r in enumerate(group) if r["task"]=="conversation_context_mood") for group in groups.values()}
        self.assertIn(0,positions)
        self.assertGreaterEqual(max(positions),6)
        for group in list(groups.values())[:10]:
            memory=[r for r in group if r["task"]=="conversation_context_memory"]
            first=memory[0]["target"].removeprefix("Prazer, ").removesuffix(".")
            second=memory[2]["target"].removeprefix("Prazer, ").removesuffix(".")
            self.assertEqual(memory[1]["target"],f"Seu nome é {first}.")
            self.assertEqual(memory[3]["target"],f"Seu nome é {second}.")

    def fixture(self):
        return [dict(id="train",project_id="train",split="train",task="conversation_fixture",history=[])]

    def test_name_recall_tracks_correction_and_history(self):
        rows=[r for r in contextual_rows(self.fixture()) if r["project_id"]=="contextual-0"]
        first=rows[0]["target"].removeprefix("Prazer, ").removesuffix(".")
        second=rows[5]["target"].removeprefix("Prazer, ").removesuffix(".")
        self.assertNotEqual(first,second)
        self.assertEqual(rows[1]["target"],f"Seu nome é {first}.")
        self.assertEqual(rows[6]["target"],f"Seu nome é {second}.")
        for before,after in zip(rows,rows[1:]):
            self.assertEqual(after["history"],before["history"]+[[before["prompt"],before["target"]]])

    def test_reserved_documents_are_not_added_twice(self):
        documents=paired_documents()
        reserved=[r for r in documents if r["split"]!="train"]
        source=self.fixture()+reserved
        before=json.dumps(source,ensure_ascii=False)
        rows,_,_=build_rows(source)
        self.assertEqual([r for r in rows if r["split"]!="train"],reserved)
        self.assertEqual(len({r["id"] for r in rows}),len(rows))
        self.assertEqual(json.dumps(source,ensure_ascii=False),before)
