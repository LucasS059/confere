import asyncio
import threading
import unittest

from confere_ai.tokenizer import ByteBPE

try:
    from confere_ai.tui import Composer, ConfereApp
except ImportError:
    ConfereApp = None


@unittest.skipIf(ConfereApp is None, "Textual não instalado")
class TUITests(unittest.IsolatedAsyncioTestCase):
    async def test_send_literal_text_clear_and_multiline(self):
        prompts = []
        def stream(ids, update, stop):
            prompts.append(ids)
            update("[bold]texto[/bold]", 3)
            return "[bold]texto[/bold]", 3
        app = ConfereApp(ByteBPE(), stream, 256, 32, "causal_lm")
        async with app.run_test(size=(80, 30)) as pilot:
            composer = app.query_one(Composer)
            composer.load_text("A ciência é ")
            await pilot.press("enter")
            await app.workers.wait_for_complete()
            await pilot.pause()
            self.assertFalse(app.busy)
            self.assertEqual(app.history, [("A ciência é ", "[bold]texto[/bold]")])
            self.assertEqual(prompts[0], [256] + ByteBPE().encode("A ciência é "))
            self.assertIn("[bold]texto[/bold]", app.pending.render().plain)
            await pilot.press("ctrl+j")
            self.assertEqual(composer.text, "\n")
            await pilot.press("ctrl+l")
            await pilot.pause()
            self.assertEqual(app.history, [])
            self.assertEqual(len(app.query(".message")), 0)

    async def test_cancel_keeps_ui_responsive_and_excludes_partial_answer(self):
        started = threading.Event()
        def stream(ids, update, stop):
            update("parcial", 1)
            started.set()
            stop.wait(3)
            return "parcial", 1
        app = ConfereApp(ByteBPE(), stream, 256, 32)
        async with app.run_test(size=(60, 24)) as pilot:
            app.query_one(Composer).load_text("oi")
            await pilot.press("enter")
            await asyncio.to_thread(started.wait, 2)
            await pilot.press("f1", "escape")
            await app.workers.wait_for_complete()
            await pilot.pause()
            self.assertFalse(app.busy)
            self.assertEqual(app.history, [])
            self.assertIn("interrompido", app.pending.render().plain)

    async def test_error_and_context_overflow_leave_app_usable(self):
        def stream(ids, update, stop):
            raise RuntimeError("falha simulada")
        app = ConfereApp(ByteBPE(), stream, 64, 16)
        async with app.run_test(size=(80, 28)) as pilot:
            composer = app.query_one(Composer)
            composer.load_text("x" * 100)
            await pilot.press("enter")
            self.assertFalse(app.busy)
            self.assertEqual(composer.text, "x" * 100)
            composer.load_text("oi")
            await pilot.press("enter")
            await app.workers.wait_for_complete()
            await pilot.pause()
            self.assertFalse(app.busy)
            self.assertIn("falha simulada", app.pending.render().plain)
            self.assertEqual(app.history, [])


if __name__ == "__main__":
    unittest.main()
