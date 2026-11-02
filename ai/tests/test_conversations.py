import importlib.util
import tempfile
import json
import unittest
from pathlib import Path
from types import SimpleNamespace

from confere_ai.tokenizer import ByteBPE
from confere_ai.chat import prepare_prompt
from confere_ai.training_data import encode_sample
try:
    import torch
    from confere_ai.instruct import load_instructions, score
except ImportError:
    torch=None


@unittest.skipIf(torch is None,"Dependências de treino ausentes")
class ConversationTests(unittest.TestCase):
    def test_native_evaluation_keeps_long_history_and_explicit_response_budget(self):
        tokenizer=ByteBPE();calls=[]
        class Fake:
            config=SimpleNamespace(block_size=1024)
            def generate(self,ids,budget,eos):
                calls.append((ids[0].tolist(),budget))
                return torch.cat([ids,torch.tensor([tokenizer.encode("ok")+[eos]])],dim=1)
        history=[["pergunta "*25,"resposta "*25]]
        row=dict(id="native",project_id="native",turn_index=0,history=history,prompt="lembra?",target="ok",task="conversation_test")
        result=score(Fake(),tokenizer,[row],"cpu",context_limit=1024,response_tokens=256)
        expected,dropped=prepare_prompt(history,"lembra?",tokenizer,1024,256,"conversation")
        self.assertEqual(calls,[(expected,256)])
        self.assertEqual(dropped,0)
        self.assertEqual(result["samples"][0]["history_used"],history)
        self.assertEqual(result["correct"],1)

    def test_training_matches_runtime_history_and_masks_all_prior_answers(self):
        tokenizer=ByteBPE()
        row={"id":"case","prompt":"meu nome?","target":"Ana", "history":[["sou Ana","Olá Ana"]]}
        ids,labels=encode_sample(row,tokenizer,256)
        prefix,dropped=prepare_prompt(row["history"],row["prompt"],tokenizer,256,64,"conversation")
        self.assertEqual(dropped,0)
        self.assertEqual(ids[:len(prefix)],prefix)
        self.assertTrue(all(v==-100 for v in labels[:len(prefix)-1]))
        self.assertEqual(labels[len(prefix)-1:],tokenizer.encode("Ana")+[tokenizer.EOS])
        row["history"]=[["x"*180,"y"*50]]
        with self.assertRaises(ValueError): encode_sample(row,tokenizer,256)

    def test_scoring_feeds_generated_answers_instead_of_reference_history(self):
        tokenizer=ByteBPE();calls=[]
        class Fake:
            config=SimpleNamespace(block_size=256)
            def generate(self,ids,*args):
                calls.append(ids[0].tolist())
                return torch.cat([ids,torch.tensor([tokenizer.encode("erro")+[tokenizer.EOS]])],dim=1)
        rows=[{"id":"a","project_id":"c","turn_index":0,"history":[],"prompt":"oi","target":"certo","task":"conversation_test"},
              {"id":"b","project_id":"c","turn_index":1,"history":[["oi","certo"]],"prompt":"e agora?","target":"sim","task":"conversation_test"}]
        result=score(Fake(),tokenizer,rows,"cpu")
        expected,_=prepare_prompt([("oi","erro")],"e agora?",tokenizer,256,64,"conversation")
        self.assertEqual(calls[1],expected)
        self.assertEqual(result["samples"][1]["history_used"],[["oi","erro"]])
        self.assertEqual(result["correct"],0)

    def test_synthetic_conversation_splits_and_sequence_are_validated(self):
        spec=importlib.util.spec_from_file_location("build_conversations",Path(__file__).resolve().parents[1]/"scripts/build_conversations.py")
        module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
        rows=module.build()
        with tempfile.TemporaryDirectory() as folder:
            p=Path(folder)/"rows.jsonl"
            p.write_text("\n".join(json.dumps(r) for r in rows))
            loaded,_=load_instructions(p)
            self.assertEqual(len(loaded),1187)
            rows[1]["history"]=[["outro","contexto"]]
            p.write_text("\n".join(json.dumps(r) for r in rows))
            with self.assertRaises(ValueError): load_instructions(p)

    def test_mixed_conversations_have_disjoint_names_and_no_cross_split_prefixes(self):
        import sys
        scripts=str(Path(__file__).resolve().parents[1]/"scripts")
        sys.path.insert(0,scripts)
        try:
            from build_conversation_mix import build
            rows=build()
        finally: sys.path.remove(scripts)
        with tempfile.TemporaryDirectory() as folder:
            p=Path(folder)/"rows.jsonl";p.write_text("\n".join(json.dumps(r) for r in rows))
            loaded,_=load_instructions(p)
            self.assertEqual(len(loaded),8741)

    def test_social_conversations_offer_a_next_step_after_uncertainty(self):
        import sys
        scripts=str(Path(__file__).resolve().parents[1]/"scripts")
        sys.path.insert(0,scripts)
        try:
            from build_social_conversations import build
            rows=build()
        finally: sys.path.remove(scripts)
        with tempfile.TemporaryDirectory() as folder:
            p=Path(folder)/"rows.jsonl";p.write_text("\n".join(json.dumps(r) for r in rows))
            loaded,_=load_instructions(p)
            self.assertEqual(len(loaded),11741)
            cases=[r for r in loaded if r["id"].startswith("social-")]
            self.assertTrue(any("Fico feliz" in r["target"] for r in cases))
            self.assertTrue(any("Qual é o tema?" in r["target"] for r in cases))
            self.assertEqual(sum(r["split"]=="validation" for r in cases),120)
            self.assertTrue(any(r["turn_index"]==0 and r["history"] for r in cases))
            self.assertTrue(any(r["turn_index"]==0 and "conferência de projetos" in r["target"] for r in cases))
