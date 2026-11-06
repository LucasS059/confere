import contextlib
import io
import unittest
from unittest.mock import patch

from confere_ai.chat import chat_loop, prepare_prompt
from confere_ai.tokenizer import ByteBPE


class ChatTests(unittest.TestCase):
    def test_context_drops_whole_old_turns_and_keeps_current_message(self):
        tokenizer = ByteBPE()
        history = [("antiga", "resposta"), ("nova", "sim")]
        ids, dropped = prepare_prompt(history, "oi", tokenizer, 24, 10)
        self.assertEqual(dropped, 1)
        self.assertEqual(ids, [256, *tokenizer.encode("nova"), 258, *tokenizer.encode("sim"), 257, 256, *tokenizer.encode("oi"), 258])
        self.assertEqual(len(history), 2)

    def test_oversized_message_is_rejected_without_truncating(self):
        with self.assertRaisesRegex(ValueError, "Mensagem longa"):
            prepare_prompt([], "a" * 50, ByteBPE(), 32, 10)

    def test_loop_uses_history_and_clear_does_not_send_commands_to_model(self):
        prompts = []
        def respond(ids):
            prompts.append(ids)
            return "resposta"
        with patch("builtins.input", side_effect=["", "oi", "mais", "/ajuda", "/limpar", "oi", "/sair"]), contextlib.redirect_stdout(io.StringIO()) as output:
            chat_loop(ByteBPE(), respond, 1024, 32)
        self.assertEqual(len(prompts), 3)
        self.assertEqual(prompts[0], prompts[2])
        self.assertGreater(len(prompts[1]), len(prompts[0]))
        self.assertIn("Histórico limpo", output.getvalue())
        self.assertIn("Conversa encerrada", output.getvalue())

    def test_eof_and_interrupt_exit_cleanly(self):
        for exception in (EOFError, KeyboardInterrupt):
            with patch("builtins.input", side_effect=exception), contextlib.redirect_stdout(io.StringIO()) as output:
                chat_loop(ByteBPE(), lambda _: "", 1024, 32)
            self.assertIn("Conversa encerrada", output.getvalue())
