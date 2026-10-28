import argparse
import contextlib
import io
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from confere_ai.tokenizer import ByteBPE

try:
    import torch
except ImportError:
    torch = None


class TokenizerTests(unittest.TestCase):
    def test_utf8_roundtrip_including_unseen_text(self):
        tokenizer = ByteBPE.train(["conferência documental " * 10], 280)
        text = "Requisito: ação, evidência, 東京 e 🏀."
        self.assertEqual(tokenizer.decode(tokenizer.encode(text)), text)
        self.assertEqual(ByteBPE(tokenizer.merges).encode(text), tokenizer.encode(text))
        self.assertTrue(all(token < 256 or token >= 260 for token in tokenizer.encode(text)))

    def test_repeated_patterns_are_compressed(self):
        text = "documento documento documento"
        tokenizer = ByteBPE.train([text], 280)
        self.assertLess(len(tokenizer.encode(text)), len(text.encode()))


@unittest.skipIf(torch is None, "Instale ai[train] para os testes da rede")
class TrainingTests(unittest.TestCase):
    def test_generation_stream_and_stop_match_generated_tokens(self):
        from confere_ai.model import GPT, GPTConfig
        model = GPT(GPTConfig(16, 8, 16, 1, 2)).eval()
        prompt = torch.tensor([[1, 2]])
        streamed = []
        generated = model.generate(prompt, 5, -1, on_token=streamed.append,
                                   should_stop=lambda: len(streamed) == 2)
        self.assertEqual(streamed, generated[0, 2:].tolist())
        self.assertEqual(len(streamed), 2)
        empty = model.generate(prompt, 5, -1, should_stop=lambda: True)
        torch.testing.assert_close(empty, prompt)

    def test_causal_attention_does_not_see_future_tokens(self):
        from confere_ai.model import GPT, GPTConfig
        torch.manual_seed(42)
        model = GPT(GPTConfig(280, 8, 32, 2, 4)).eval()
        first = torch.tensor([[1, 2, 3, 4, 5]])
        second = torch.tensor([[1, 2, 3, 9, 10]])
        with torch.no_grad():
            a, b = model(first), model(second)
        torch.testing.assert_close(a[:, :3], b[:, :3], rtol=0, atol=1e-6)
        self.assertFalse(torch.allclose(a[:, 3:], b[:, 3:]))

    def test_prompt_is_masked_and_answer_includes_eos(self):
        from confere_ai.training_data import encode_sample
        tokenizer = ByteBPE()
        ids, labels = encode_sample({"id": "sample", "prompt": "pergunta", "target": "sim"}, tokenizer, 64)
        prefix_length = 1 + len(tokenizer.encode("pergunta")) + 1
        self.assertEqual(labels[:prefix_length - 1], [-100] * (prefix_length - 1))
        self.assertEqual(labels[prefix_length - 1:], tokenizer.encode("sim") + [tokenizer.EOS])
        self.assertEqual(ids[0], tokenizer.BOS)

    def test_context_overflow_is_explicit(self):
        from confere_ai.training_data import encode_sample
        with self.assertRaisesRegex(ValueError, "excedem"):
            encode_sample({"id": "x", "prompt": "abc", "target": "def"}, ByteBPE(), 3)

    def test_real_candidate_is_rejected_before_loading_documents(self):
        from confere_ai.training_data import load_authored
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "data.jsonl"
            path.write_text(json.dumps({"provenance": {"kind": "real"}}))
            with self.assertRaisesRegex(ValueError, "somente dados autorais"):
                load_authored(path)

    def test_json_syntax_does_not_imply_a_valid_response(self):
        from confere_ai.sample import inspect_response
        self.assertEqual(inspect_response('{"document": "paragraph:do"}'), (True, False))
        self.assertEqual(inspect_response('resposta quebrada'), (False, False))
        self.assertEqual(inspect_response(json.dumps({"status": "evidencia_insuficiente", "evidence": [], "justification": "Faltam dados."})), (True, True))

    def test_checkpoint_resume_matches_uninterrupted_training(self):
        from confere_ai.train import run
        from confere_ai.training_data import load_authored
        data = Path(__file__).resolve().parents[1] / "data/authored/examples.jsonl"
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            def args(name, steps, resume=None):
                return argparse.Namespace(data=data, run_dir=root/name, steps=steps, resume=resume, preset="smoke", device="cpu", seed=42, batch_size=1, learning_rate=0.0003, eval_every=1, vocab_size=512, block_size=1024)
            with contextlib.redirect_stdout(io.StringIO()), patch("confere_ai.report.REPORTS", root / "reports"):
                run(args("full", 2))
                run(args("part", 1))
                run(args("resumed", 2, root/"part/last.pt"))
            full = torch.load(root/"full/last.pt", weights_only=True)
            resumed = torch.load(root/"resumed/last.pt", weights_only=True)
            for name in full["model"]:
                torch.testing.assert_close(full["model"][name], resumed["model"][name], rtol=0, atol=0)
            samples, _ = load_authored(data)
            train = [sample for sample in samples if sample["split"] == "train"]
            expected = ByteBPE.train([text for sample in train for text in (sample["prompt"], sample["target"])], 512)
            self.assertEqual(full["merges"], expected.merges)
            info = json.loads((root/"full/run.json").read_text())
            self.assertEqual(info["test_examples_used"], 0)
            self.assertTrue(set(info["train_ids"]).isdisjoint(info["validation_ids"]))
            with self.assertRaisesRegex(ValueError, "pasta da execução"):
                run(args("full", 3))
            invalid = args("invalid", 3, root/"part/last.pt")
            invalid.seed = 99
            with self.assertRaisesRegex(ValueError, "mesmos dados"):
                run(invalid)
