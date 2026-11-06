"""Interface de terminal; inferência local em worker, sem bloquear a navegação."""

from threading import Event
from time import monotonic

from rich.text import Text
from textual import work
from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import VerticalScroll
from textual.message import Message
from textual.widgets import Footer, Static, TextArea

from .chat import prepare_prompt


class Composer(TextArea):
    BINDINGS = [
        Binding("enter", "submit", "Enviar", priority=True),
        Binding("ctrl+j", "newline", "Nova linha", priority=True),
    ]

    def action_submit(self):
        self.app.action_submit()

    def action_newline(self):
        self.insert("\n")


class GenerationUpdate(Message):
    def __init__(self, text, tokens, done=False, error=None):
        super().__init__()
        self.text, self.tokens, self.done, self.error = text, tokens, done, error


class ConfereApp(App):
    TITLE = "Confere · laboratório local"
    CSS = """
    Screen { background: $background; }
    #heading { height: 3; padding: 1 2 0 2; color: $accent; text-style: bold; }
    #model { height: auto; max-height: 4; padding: 0 2; color: $text-muted; }
    #notice { height: auto; padding: 1 2; color: $warning; }
    #conversation { height: 1fr; padding: 0 2; scrollbar-gutter: stable; }
    .message { height: auto; margin-bottom: 1; padding: 1 2; border-left: thick $primary; background: $surface; }
    .user { border-left: thick $accent; }
    .system { border-left: thick $warning; color: $text-muted; }
    #status { height: 2; padding: 0 2; color: $text-muted; }
    #composer { height: 5; margin: 0 2; border: round $primary; }
    #composer:focus { border: round $accent; }
    Footer { margin-top: 1; }
    """
    BINDINGS = [
        Binding("ctrl+q", "quit", "Sair", priority=True),
        Binding("ctrl+l", "clear", "Limpar", priority=True),
        Binding("escape", "stop", "Parar geração", priority=True),
        Binding("f1", "help", "Ajuda", priority=True),
        Binding("pageup", "page_up", "", show=False, priority=True),
        Binding("pagedown", "page_down", "", show=False, priority=True),
    ]

    def __init__(self, tokenizer, stream, context_size, max_new_tokens,
                 objective="supervised", checkpoint="", device="cpu", parameters=0, step="?"):
        super().__init__()
        self.tokenizer, self.stream = tokenizer, stream
        self.context_size, self.max_new_tokens = context_size, max_new_tokens
        self.objective, self.checkpoint, self.device = objective, checkpoint, device
        self.parameters, self.step = parameters, step
        self.history = []
        self.busy = False
        self.stop_event = Event()
        self.started = 0.0
        self.tokens = 0
        self.context_tokens = 0
        self.pending = None

    def compose(self) -> ComposeResult:
        yield Static("CONFERE  /  laboratório local", id="heading")
        mode = "Continuação de texto" if self.objective == "causal_lm" else "Conversa experimental" if self.objective == "conversation" else "Piloto de instruções" if self.objective == "instruction" else "Experimental supervisionado"
        yield Static(Text(f"{mode} · {self.device.upper()} · {self.parameters / 1e6:.1f}M parâmetros · passo {self.step}\n"
                          f"{self.checkpoint}"), id="model")
        yield Static("Modelo experimental: pode inventar e repetir texto. Saídas sem validação.", id="notice")
        yield VerticalScroll(id="conversation")
        yield Static(f"Pronto · contexto {self.context_size} tokens · limite de geração {self.max_new_tokens}", id="status")
        yield Composer(id="composer", soft_wrap=True, show_line_numbers=False)
        yield Footer()

    def on_mount(self):
        self.theme = "textual-dark"
        self.query_one(Composer).focus()
        self.set_interval(0.1, self.update_progress)
        if self.objective=="causal_lm":
            hint="Digite o início de um texto para o modelo continuar. Ele ainda não foi treinado para conversar."
        elif self.objective=="conversation":
            hint="Conversa experimental com histórico curto; interpretação e memória ainda podem falhar."
        elif self.objective=="instruction":
            hint="Digite uma instrução curta. Saídas experimentais; conversa geral não validada."
        else:
            hint="Digite uma mensagem. Este checkpoint foi treinado com poucos exemplos documentais."
        self.add_message("Sessão", hint + "\nEnter envia · Ctrl+J insere uma linha · PgUp/PgDn rolam o histórico.", "system")

    def add_message(self, author, text, kind="model"):
        widget = Static(Text(f"{author}\n{text}"), classes=f"message {kind}")
        self.query_one("#conversation", VerticalScroll).mount(widget)
        self.call_after_refresh(self.query_one("#conversation", VerticalScroll).scroll_end, animate=False)
        return widget

    def action_submit(self):
        composer = self.query_one(Composer)
        message = composer.text
        command = message.strip()
        if not command:
            return
        if command in {"/sair", "/exit", "/quit"}:
            self.action_quit()
            return
        if command in {"/limpar", "/ajuda"}:
            composer.clear()
            self.action_clear() if command == "/limpar" else self.action_help()
            return
        if self.busy:
            self.notify("Aguarde a geração ou pressione Esc para interromper.")
            return
        if self.objective != "causal_lm":
            message = command
        try:
            ids, dropped = prepare_prompt(self.history, message, self.tokenizer,
                                          self.context_size, self.max_new_tokens, self.objective)
        except ValueError as error:
            self.add_message("Entrada recusada", str(error), "system")
            return
        if dropped:
            del self.history[:dropped]
            self.add_message("Contexto", f"{dropped} turno(s) antigo(s) saíram do contexto do modelo. Continuam visíveis aqui.", "system")
        self.add_message("Você", message, "user")
        self.pending = self.add_message("Modelo · gerando", "…")
        self.current_message = message
        self.busy, self.tokens, self.context_tokens = True, 0, len(ids)
        self.started = monotonic()
        self.stop_event.clear()
        composer.clear()
        self.update_progress()
        self.generate(ids)

    @work(thread=True, exit_on_error=False)
    def generate(self, ids):
        try:
            text, count = self.stream(ids, lambda text, count: self.post_message(GenerationUpdate(text, count)), self.stop_event)
            self.post_message(GenerationUpdate(text, count, done=True))
        except Exception as error:
            self.post_message(GenerationUpdate("", 0, done=True, error=str(error)))

    def on_generation_update(self, event):
        self.tokens = event.tokens
        if not event.done:
            conversation = self.query_one("#conversation", VerticalScroll)
            follow = conversation.is_vertical_scroll_end
            self.pending.update(Text(f"Modelo · gerando\n{event.text or '…'}"))
            if follow:
                self.call_after_refresh(conversation.scroll_end, animate=False)
            return
        elapsed = max(monotonic() - self.started, 0.001)
        stopped = self.stop_event.is_set()
        label = "Erro na geração" if event.error else "Modelo · interrompido" if stopped else "Modelo"
        self.pending.update(Text(f"{label} · {event.tokens} tokens · {elapsed:.1f}s\n"
                                 f"{event.error or event.text or '[sem texto gerado]'}"))
        if not stopped and not event.error:
            self.history.append((self.current_message, event.text))
        self.busy = False
        self.query_one("#status", Static).update(
            f"{'Erro' if event.error else 'Interrompido' if stopped else 'Concluído'} · {event.tokens} tokens · {elapsed:.1f}s · "
            f"{event.tokens / elapsed:.1f} tok/s · contexto {self.context_tokens}+{event.tokens}/{self.context_size}")
        self.query_one(Composer).focus()

    def update_progress(self):
        if self.busy:
            self.query_one("#status", Static).update(
                f"{'Interrompendo' if self.stop_event.is_set() else 'Gerando'} · {monotonic() - self.started:.1f}s · "
                f"{self.tokens}/{self.max_new_tokens} tokens · contexto {self.context_tokens}/{self.context_size}")

    def action_stop(self):
        if self.busy:
            self.stop_event.set()

    def action_clear(self):
        if self.busy:
            self.notify("Pressione Esc e aguarde a interrupção antes de limpar.")
            return
        self.history.clear()
        self.query_one("#conversation", VerticalScroll).remove_children()
        self.query_one("#status", Static).update("Histórico e contexto limpos · nada foi salvo em disco")

    def action_help(self):
        self.add_message("Atalhos", "Enter envia · Ctrl+J nova linha · Esc interrompe · Ctrl+L limpa · Ctrl+Q sai\n"
                         "PgUp/PgDn rolam. Selecione texto para copiar com o terminal (Shift+arraste, se necessário).\n"
                         "/limpar, /ajuda e /sair também funcionam. Histórico apenas nesta sessão.\n"
                         "Gerações interrompidas não entram no contexto das próximas mensagens.", "system")

    def action_page_up(self):
        self.query_one("#conversation", VerticalScroll).scroll_page_up()

    def action_page_down(self):
        self.query_one("#conversation", VerticalScroll).scroll_page_down()

    def action_quit(self):
        self.stop_event.set()
        self.exit()
