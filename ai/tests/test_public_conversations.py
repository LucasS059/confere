import json
from pathlib import Path
import sys
import tempfile
import unittest
import torch

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
from prepare_public_conversations import public_paths
from confere_ai.instruct import load_instructions, training_indices


class PublicConversationTests(unittest.TestCase):
    def test_provenance_history_and_split_follow_content_not_identifier(self):
        chat=[dict(role="user",content="Oi"),dict(role="assistant",content="Olá"),dict(role="user",content="Como vai?"),dict(role="assistant",content="Tudo bem.")]
        paths=public_paths(chat,"one")
        other=public_paths(chat,"two")
        self.assertEqual(paths[0]["project_id"],other[0]["project_id"])
        self.assertEqual(paths[0]["split"],other[0]["split"])
        self.assertEqual(paths[1]["history"],[["Oi","Olá"]])
        self.assertEqual(paths[0]["provenance"]["kind"],"public_model_generated")
        self.assertEqual(public_paths(chat[:-1],"odd"),[])
        chat[1]["role"]="user"
        self.assertEqual(public_paths(chat,"bad"),[])

    def test_loader_rejects_unrecognized_public_source(self):
        public=public_paths([dict(role="user",content="Oi"),dict(role="assistant",content="Olá")],"fixture")[0]
        rows=[dict(id="fixture-"+split,project_id="fixture-"+split,split=split,task="conversation_fixture",history=[],turn_index=0,prompt="prompt-"+split,target="alvo",provenance=dict(kind="synthetic_authored")) for split in ("train","validation")]+[public]
        with tempfile.TemporaryDirectory() as directory:
            path=Path(directory)/"rows.jsonl"
            def write():path.write_text("".join(json.dumps(r)+"\n" for r in rows))
            write();self.assertEqual(len(load_instructions(path)[0]),3)
            public["provenance"]["source"]="https://example.com/unverified"
            write()
            with self.assertRaises(ValueError):load_instructions(path)

    def test_three_sampling_pools_stay_homogeneous(self):
        generator=torch.Generator().manual_seed(42)
        batches=[training_indices(3,[0],[2],4,.2,generator,[1],.3) for _ in range(100)]
        self.assertEqual({batch[0] for batch in batches},{0,1,2})
        self.assertTrue(all(len(set(batch))==1 for batch in batches))
