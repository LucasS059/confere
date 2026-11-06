"""Fixtures sintéticas de instrução; templates do assistente, sem rótulos humanos."""
import json
from pathlib import Path


def build():
    rows = []
    phrases = {"train": ("Copie exatamente: {text}", "Qual é o código? Responda só o código.\nTexto: {text}", "O texto informa a data? Responda SIM ou NÃO.\nTexto: {text}", "Qual é o prazo? Se faltar, responda Não informado.\nTexto: {text}"),
               "validation": ("Repita sem alterar: {text}", "Extraia apenas o código deste texto: {text}", "Existe uma data neste texto? Responda SIM ou NÃO.\n{text}", "Extraia o prazo deste texto; se ausente, responda Não informado.\n{text}"),
               "test": ("Retorne só esta frase: {text}", "Leia e devolva só o código: {text}", "Há uma data? Retorne SIM ou NÃO.\n{text}", "Informe o prazo ou responda Não informado.\n{text}")}
    for split, start, count in (("train", 1, 40), ("validation", 101, 8), ("test", 201, 8)):
        for i in range(start, start + count):
            texts = (f"O projeto {i} usa testes.", f"Código: P{i}. Autor: Equipe {i}.",
                     f"Projeto {i}. Data: 10/05/2026." if i % 2 else f"Projeto {i}. Autor: Equipe {i}.",
                     f"Projeto {i}. Prazo: 15 dias." if i % 2 else f"Projeto {i}. Tema: biblioteca.")
            targets = (texts[0], f"P{i}", "SIM" if i % 2 else "NÃO", "15 dias" if i % 2 else "Não informado.")
            for task, text, target, template in zip(("copy", "field", "presence", "missing"), texts, targets, phrases[split]):
                rows.append({"id": f"{split}-{i}-{task}", "project_id": f"project-{i}", "split": split,
                    "task": task, "prompt": template.format(text=text), "target": target,
                    "provenance": {"kind": "synthetic_authored", "note": "Templates e respostas construídos pelo assistente; não são entregas reais nem revisão humana."}})
    conversations = {"train": [("oi", "Olá! Sou o Confere."), ("olá", "Olá! Sou o Confere."), ("bom dia", "Olá! Sou o Confere."), ("qual seu nome?", "Sou o Confere."), ("quem é você?", "Sou o Confere."), ("você pode errar?", "Sim. Minhas respostas precisam ser verificadas."), ("você sabe tudo?", "Não. Posso errar ou não ter informação suficiente.")],
        "validation": [("oiii", "Olá! Sou o Confere."), ("qual é o seu nome?", "Sou o Confere."), ("você também pode cometer erros?", "Sim. Minhas respostas precisam ser verificadas.")],
        "test": [("olá, tudo bem?", "Olá! Sou o Confere."), ("como você se chama?", "Sou o Confere.")]}
    for split, items in conversations.items():
        for i, (prompt, target) in enumerate(items):
            rows.append({"id": f"{split}-dialog-{i}", "project_id": f"dialog-{split}", "split": split,
                "task": "dialogue", "prompt": prompt, "target": target,
                "provenance": {"kind": "synthetic_authored", "note": "Template do assistente, sem validação humana."}})
    return rows


if __name__ == "__main__":
    path = Path("ai/data/authored/instructions.jsonl")
    path.write_text("".join(json.dumps(row, ensure_ascii=False) + "\n" for row in build()))
    print(path)
