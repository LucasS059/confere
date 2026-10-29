import hashlib
import contextlib
import importlib.util
import io
import json
import random
import tempfile
import unittest
from unittest.mock import patch
from pathlib import Path

from confere_ai.chat import chat_loop, prepare_prompt
from confere_ai.language_data import fit_language_tokenizer, language_windows, load_corpus
from confere_ai.tokenizer import ByteBPE


spec = importlib.util.spec_from_file_location("prepare_portuguese", Path(__file__).resolve().parents[1] / "scripts/prepare_portuguese.py")
prepare = importlib.util.module_from_spec(spec)
spec.loader.exec_module(prepare)


class LanguageTests(unittest.TestCase):
    def test_download_retries_rate_limit_without_replacing_results(self):
        error = prepare.urllib.error.HTTPError("https://example.test", 429, "rate limit", {"Retry-After": "12"}, None)
        response = io.BytesIO(b'{"rows": []}')
        with patch.object(prepare.urllib.request, "urlopen", side_effect=[error, response]) as request, patch.object(prepare.time, "sleep") as sleep, contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(prepare.fetch("https://example.test", {}), b'{"rows": []}')
        self.assertEqual(request.call_count, 2)
        sleep.assert_called_once_with(12.)

    def test_fast_bpe_matches_original_algorithm(self):
        tokenizer = ByteBPE.train(["ação e informação: ababab aaaaaa Português. " * 20], 310)
        rng = random.Random(42)
        texts = ["", "aaaaaa", "abababab", "ação", "🌍 東京"]
        texts += ["".join(rng.choice("aab ação e Português: ") for _ in range(100)) for _ in range(100)]
        for text in texts:
            expected = list(text.encode("utf-8"))
            for token, pair in enumerate(tokenizer.merges, 260):
                expected = tokenizer.merge(expected, pair, token)
            self.assertEqual(tokenizer.encode(text), expected)
            self.assertEqual(tokenizer.decode(expected), text)

    def test_tokenizer_fits_training_documents_only(self):
        rows = [{"split": "train", "text": "abcabc " * 50}, {"split": "validation", "text": "ZZZZZZ" * 1000}, {"split": "test", "text": "YYYYYY" * 1000}]
        actual = fit_language_tokenizer(rows, 280, 1000, 42)
        expected = ByteBPE.train([rows[0]["text"][:600]], 280)
        self.assertEqual(actual.merges, expected.merges)

    def test_windows_never_cross_document_boundaries(self):
        rows = [{"text": "abcde", "split": "train"}, {"text": "vwxyz", "split": "train"}, {"text": "secret", "split": "test"}]
        windows = language_windows(rows, ByteBPE(), 3, "train")
        self.assertEqual(windows, [([256, 97, 98], [97, 98, 99]), ([99, 100, 101], [100, 101, 257]), ([256, 118, 119], [118, 119, 120]), ([120, 121, 122], [121, 122, 257])])

    def test_language_prompt_does_not_inject_supervised_separator(self):
        ids, dropped = prepare_prompt([], "A ciência é", ByteBPE(), 256, 64, "causal_lm")
        self.assertEqual(ids, [256] + ByteBPE().encode("A ciência é"))
        self.assertNotIn(ByteBPE.SEP, ids)

    def test_language_interface_preserves_trailing_spaces_in_prefix(self):
        prompts = []
        with patch("builtins.input", side_effect=["A ciência é ", "/sair"]), contextlib.redirect_stdout(io.StringIO()):
            chat_loop(ByteBPE(), lambda ids: prompts.append(ids) or "continuação", 256, 64, "causal_lm")
        self.assertEqual(ByteBPE().decode(prompts[0]), "A ciência é ")

    def test_public_row_keeps_attribution_and_stable_split(self):
        row = {"id": "123", "title": "Teste", "url": "https://pt.wikipedia.org/wiki/Teste", "text": "Informação em português. " * 100}
        first = prepare.prepare_row(row, 1000)
        second = prepare.prepare_row(row, 2000)
        self.assertEqual(first["split"], second["split"])
        self.assertEqual(first["normalized_source_sha256"], second["normalized_source_sha256"])
        self.assertEqual(len(first["text"]), 1000)
        self.assertTrue(first["truncated"])
        self.assertTrue(first["license_urls"])
        self.assertTrue(first["attribution"])

    def test_loader_checks_snapshot_and_cross_split_duplicates(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "articles.jsonl"
            rows = [{"id": "a", "split": "train", "text": "igual", "license_urls": ["license"], "attribution": "autores"}, {"id": "b", "split": "validation", "text": "igual", "license_urls": ["license"], "attribution": "autores"}]
            path.write_text("\n".join(json.dumps(row) for row in rows))
            manifest = path.with_name("manifest.json")
            manifest.write_text(json.dumps({"snapshot_sha256": hashlib.sha256(path.read_bytes()).hexdigest()}))
            with self.assertRaisesRegex(ValueError, "atravessando splits"):
                load_corpus(path)
            path.write_text("alterado")
            with self.assertRaisesRegex(ValueError, "hash"):
                load_corpus(path)
