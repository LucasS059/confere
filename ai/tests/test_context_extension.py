import unittest
try:
    import torch
    from confere_ai.model import GPT,GPTConfig
except ImportError:
    torch=None


@unittest.skipIf(torch is None,"Dependências de treino ausentes")
class ContextExtensionTests(unittest.TestCase):
    def test_long_answer_budget_is_explicit_and_old_budget_stays_strict(self):
        from confere_ai.training_data import encode_sample
        from confere_ai.tokenizer import ByteBPE
        row={"id":"long","history":[],"prompt":"oi","target":"resposta "*12}
        with self.assertRaises(ValueError):encode_sample(row,ByteBPE(),1024)
        row["response_tokens"]=256
        ids,labels=encode_sample(row,ByteBPE(),1024)
        self.assertEqual(len(ids),len(labels));self.assertLessEqual(len(ids),1024)

    def test_human_batches_are_homogeneous_and_sampling_is_reproducible(self):
        from confere_ai.instruct import training_indices
        generators=[torch.Generator().manual_seed(42) for _ in range(2)]
        sequences=[[training_indices(8,[0,1],[2,3,4,5,6,7],4,.25,g) for _ in range(30)] for g in generators]
        self.assertEqual(sequences[0],sequences[1])
        for batch in sequences[0]:self.assertTrue(all(i<2 for i in batch) or all(i>=2 for i in batch))
        expected=torch.randint(8,(4,),generator=torch.Generator().manual_seed(42)).tolist()
        self.assertEqual(training_indices(8,[],[],4,0,torch.Generator().manual_seed(42)),expected)
    def test_extension_preserves_all_existing_positions_and_short_logits(self):
        torch.manual_seed(42)
        old=GPT(GPTConfig(280,16,32,2,4)).eval()
        checkpoint={"config":vars(old.config),"model":old.state_dict()}
        new=GPT(GPTConfig(280,32,32,2,4)).eval()
        with self.assertRaises(ValueError): new.load_local_checkpoint(checkpoint)
        new.load_local_checkpoint(checkpoint,extend_context=True)
        torch.testing.assert_close(new.position_embedding.weight[:16],old.position_embedding.weight,rtol=0,atol=0)
        ids=torch.tensor([[1,2,3,4]])
        with torch.no_grad():torch.testing.assert_close(new(ids),old(ids),rtol=0,atol=1e-6)
        self.assertTrue(torch.isfinite(new(torch.ones((1,32),dtype=torch.long))).all())
        self.assertEqual(checkpoint["model"]["position_embedding.weight"].shape[0],16)

    def test_shrinking_and_architecture_changes_are_rejected(self):
        old=GPT(GPTConfig(280,16,32,2,4))
        checkpoint={"config":vars(old.config),"model":old.state_dict()}
        for config in (GPTConfig(280,8,32,2,4),GPTConfig(281,32,32,2,4)):
            with self.assertRaises(ValueError):GPT(config).load_local_checkpoint(checkpoint,extend_context=True)
