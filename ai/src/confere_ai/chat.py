"""Conversa experimental no terminal com um checkpoint local do Confere."""

import argparse
import pickle
import sys
from pathlib import Path

from .tokenizer import ByteBPE


DEFAULT_CHECKPOINT = Path("ai/runs/conversation-mixed-2026-11-02/best.pt")


def prepare_prompt(history, message, tokenizer, context_size, max_new_tokens, objective="supervised"):
    if objective == "causal_lm":
        current = [tokenizer.BOS] + tokenizer.encode(message)
    else:
        current = [tokenizer.BOS] + tokenizer.encode(message) + [tokenizer.SEP]
    if len(current) + max_new_tokens > context_size:
        raise ValueError("Mensagem longa demais para o contexto. Encurte o texto ou reduza --max-new-tokens.")
    turns = [([tokenizer.BOS] + tokenizer.encode(question + answer) + [tokenizer.EOS])
             if objective == "causal_lm" else
             ([tokenizer.BOS] + tokenizer.encode(question) + [tokenizer.SEP]
              + tokenizer.encode(answer) + [tokenizer.EOS])
             for question, answer in history]
    dropped = 0
    while sum(map(len, turns)) + len(current) + max_new_tokens > context_size:
        turns.pop(0)
        dropped += 1
    return [token for turn in turns for token in turn] + current, dropped


def chat_loop(tokenizer, respond, context_size, max_new_tokens, objective="supervised"):
    history = []
    print("Confere — interface local experimental")
    if objective == "causal_lm":
        print("Modo continuação de texto: modelo-base de português, ainda sem treino de diálogo.")
        print("Digite o início de um texto; a saída é uma continuação, não uma resposta validada.")
    elif objective == "instruction":
        print("Piloto de instruções curtas: dados sintéticos, sem validação de conversa geral.")
    elif objective == "conversation":
        print("Conversa experimental com histórico curto. Capacidade geral ainda não validada.")
    else:
        print("Este modelo foi treinado em poucos exemplos documentais, não em diálogo geral.")
    print("Comandos: /sair, /limpar, /ajuda. Histórico apenas nesta sessão.\n")
    try:
        while True:
            message = input("Você: ")
            command = message.strip()
            if not command:
                continue
            if command in {"/sair", "/exit", "/quit"}:
                break
            if command == "/ajuda":
                print("/sair encerra; /limpar apaga o contexto da sessão. Digite uma mensagem para gerar uma resposta.\n")
                continue
            if command == "/limpar":
                history.clear()
                print("Histórico limpo.\n")
                continue
            if objective != "causal_lm":
                message = command
            try:
                ids, dropped = prepare_prompt(history, message, tokenizer, context_size, max_new_tokens, objective)
                if dropped:
                    print(f"[Contexto cheio: {dropped} turno(s) antigo(s) descartado(s).]")
                answer = respond(ids)
            except (ValueError, RuntimeError) as error:
                print(f"Erro: {error}\n")
                continue
            if dropped:
                del history[:dropped]
            history.append((message, answer))
            print(f"Modelo: {answer if answer.strip() else '[sem texto gerado]'}\n")
    except (EOFError, KeyboardInterrupt):
        print()
    print("Conversa encerrada.")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("checkpoint", nargs="?", type=Path, default=DEFAULT_CHECKPOINT)
    parser.add_argument("--device", choices=["auto", "cpu", "mps"], default="auto")
    parser.add_argument("--max-new-tokens", type=int)
    parser.add_argument("--plain", action="store_true", help="Usar a interface simples, sem TUI.")
    args = parser.parse_args()
    if not args.checkpoint.is_file():
        parser.exit(1, f"Checkpoint não encontrado: {args.checkpoint}\nExecute na raiz do repositório ou informe o caminho do last.pt.\n")
    if args.max_new_tokens is not None and args.max_new_tokens <= 0:
        parser.error("--max-new-tokens deve ser positivo.")
    try:
        import torch
        from .model import GPT, GPTConfig
        from .train import choose_device

        device = choose_device(args.device)
        print(f"Carregando {args.checkpoint} ({device})...", flush=True)
        checkpoint = torch.load(args.checkpoint, map_location="cpu", weights_only=True)
        tokenizer = ByteBPE(checkpoint["merges"])
        model = GPT(GPTConfig(**checkpoint["config"])).to(device)
        model.load_state_dict(checkpoint["model"])
        model.eval()
        objective = checkpoint.get("settings", {}).get("objective", "supervised")
        if args.max_new_tokens is None:
            args.max_new_tokens = 64 if objective == "conversation" else min(256, model.config.block_size // 2)
        if args.max_new_tokens + 2 >= model.config.block_size:
            raise ValueError("Reserve menos tokens de resposta que o tamanho do contexto.")
    except ImportError:
        parser.exit(1, "Instale as dependências: ai/.venv/bin/python -m pip install -r ai/requirements-train.lock\n")
    except (ValueError, RuntimeError, OSError, KeyError, TypeError, EOFError, pickle.UnpicklingError) as error:
        parser.exit(1, f"Falha ao carregar o modelo: {error}\n")

    def respond(ids):
        generated = model.generate(torch.tensor([ids], device=device), args.max_new_tokens, tokenizer.EOS)
        return tokenizer.decode(generated[0, len(ids):].tolist())

    if args.plain or not (sys.stdin.isatty() and sys.stdout.isatty()):
        chat_loop(tokenizer, respond, model.config.block_size, args.max_new_tokens, objective)
        return

    try:
        from .tui import ConfereApp
    except ImportError:
        parser.exit(1, "Instale a TUI: ai/.venv/bin/python -m pip install -r ai/requirements-train.lock\nOu use --plain.\n")

    def stream(ids, update, stop):
        tokens = []
        def on_token(token):
            tokens.append(token)
            update(tokenizer.decode(tokens), len(tokens))
        model.generate(torch.tensor([ids], device=device), args.max_new_tokens,
                       tokenizer.EOS, on_token=on_token, should_stop=stop.is_set)
        return tokenizer.decode(tokens), len(tokens)

    ConfereApp(tokenizer, stream, model.config.block_size, args.max_new_tokens,
               objective, str(args.checkpoint), str(device),
               sum(p.numel() for p in model.parameters()), checkpoint.get("step", "?")).run()


if __name__ == "__main__":
    main()
