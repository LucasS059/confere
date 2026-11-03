import json
import sys
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
from prepare_contextual_conversation import build_rows, contextual_rows
from prepare_document_lexical import paired_documents


class ContextualTests(unittest.TestCase):
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
