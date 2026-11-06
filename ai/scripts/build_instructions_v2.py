"""Dados sintéticos mais diversos; não reutiliza projetos da primeira versão."""
import json
import random
from pathlib import Path


def build():
    rng = random.Random(7321)
    rows, used = [], set()
    templates = {
        "train": [
            ["Copie exatamente: {text}", "Repita só este trecho: {text}", "Devolva o texto sem modificar: {text}"],
            ["Qual é o código? Responda só o código.\n{text}", "Leia o texto e retorne apenas o código: {text}", "Extraia o campo Código, sem explicação.\n{text}"],
            ["Há data no texto? Responda SIM ou NÃO.\n{text}", "O texto contém uma data? Só SIM ou NÃO.\n{text}"],
            ["Qual é o prazo? Se não houver, diga Não informado.\n{text}", "Retorne apenas o prazo, ou Não informado. se ausente.\n{text}"]],
        "validation": [["Reproduza fielmente a frase a seguir: {text}"], ["Informe exclusivamente o identificador do campo Código: {text}"], ["Verifique se uma data está presente; use SIM ou NÃO.\n{text}"], ["Leia o prazo informado; caso falte, devolva Não informado.\n{text}"]],
        "test": [["Escreva uma cópia literal: {text}"], ["Preciso somente do valor de Código: {text}"], ["Responda se existe data com SIM ou NÃO.\n{text}"], ["Mostre apenas o prazo ou Não informado. quando não constar.\n{text}"]]
    }
    for split, count in (("train", 1000), ("validation", 40), ("test", 40)):
        for project in range(count):
            number = str(rng.randint(10 ** (length := rng.choice([2,3,4,5])) , 10 ** (length+1)-1))
            while number in used:
                number = str(rng.randint(100, 999999))
            used.add(number)
            code = rng.choice(["P", "TCC-", "A", "REQ-"]) + number
            days = str(rng.randint(1, 365)) + rng.choice([" dias", " semanas", " meses"])
            theme = rng.choice(["biblioteca", "horta", "estoque", "oficina", "escola", "agenda"])
            text = f"O projeto {number} trata de {theme}."
            fields = [f"Autor: Equipe {number}.", f"Código: {code}.", f"Tema: {theme}."]
            rng.shuffle(fields)
            date = f"Projeto {number}. Data: {rng.randint(1,28):02d}/{rng.randint(1,12):02d}/2026." if project % 2 else f"Projeto {number}. Tema: {theme}."
            deadline = f"Projeto {number}. Prazo: {days}." if project % 2 else f"Projeto {number}. Autor: Equipe {number}."
            for task_id, (task, context, target) in enumerate(zip(("copy","field","presence","missing"),
                        (text, " ".join(fields), date, deadline), (text, code, "SIM" if project%2 else "NÃO", days if project%2 else "Não informado."))):
                rows.append({"id": f"v2-{split}-{project}-{task}", "project_id": f"v2-project-{number}", "split": split, "task": task,
                    "prompt": rng.choice(templates[split][task_id]).format(text=context), "target": target,
                    "provenance": {"kind":"synthetic_authored", "note":"Templates do assistente; alvos construídos dos campos; sem revisão humana."}})
    conversations = {
        "train": [(q,"Olá! Sou o Confere.") for q in ["oi", "oii", "oiii", "oiiii", "olá", "ola", "ola!", "oi!", "bom dia", "boa tarde", "boa noite", "olá, tudo bem?"]] + [(q,"Sou o Confere.") for q in ["qual seu nome?", "qual é seu nome?", "qual é o seu nome?", "quem é você?", "como você se chama?", "me diga seu nome", "qual o nome do modelo?"]] + [(q,"Sim. Minhas respostas precisam ser verificadas.") for q in ["você pode errar?", "você erra?", "você pode cometer erros?", "suas respostas podem estar erradas?", "você inventa informações?"]],
        "validation": [("e aí, olá!","Olá! Sou o Confere."), ("diga como você é chamado","Sou o Confere."), ("há risco de você dar uma resposta errada?","Sim. Minhas respostas precisam ser verificadas.")],
        "test": [("ei, oi!","Olá! Sou o Confere."), ("como devo te chamar?","Sou o Confere.")]}
    for split, items in conversations.items():
        for i,(prompt,target) in enumerate(items):
            rows.append({"id":f"v2-{split}-dialog-{i}", "project_id":f"v2-dialog-{split}", "split":split, "task":"dialogue", "prompt":prompt, "target":target, "provenance":{"kind":"synthetic_authored"}})
    unknown = {
        "train":["qual a nota do meu projeto?", "quem avaliou meu trabalho?", "qual é meu nome?", "qual será a nota da apresentação?", "o professor aprovou?", "o projeto foi entregue?", "que dia será minha banca?", "qual foi o parecer do professor?", "qual a senha do sistema?", "onde está meu arquivo?", "você leu meu PDF?", "consegue avaliar meu TCC sem anexos?", "qual o orçamento do projeto?", "quem é meu orientador?", "qual a data da minha entrega?", "qual a versão do documento?", "o meu projeto está correto?", "resuma meu arquivo", "quais erros há no meu projeto?", "eu vou passar na apresentação?"],
        "validation":["qual nota o professor deu ao meu TCC?", "qual é o nome do orientador do meu trabalho?", "qual foi a conclusão da minha banca?", "o que está escrito no PDF que não enviei?", "minha entrega atende todos os requisitos?"],
        "test":["como o professor pontuou minha apresentação?", "qual foi a avaliação do meu orientador?"]}
    for split, items in unknown.items():
        for i,prompt in enumerate(items):
            rows.append({"id":f"v2-{split}-unknown-{i}", "project_id":f"v2-unknown-{split}", "split":split, "task":"insufficient_context", "prompt":prompt, "target":"Não tenho informação suficiente para responder.", "provenance":{"kind":"synthetic_authored"}})
    return rows


if __name__ == "__main__":
    path = Path("ai/data/authored/instructions-v2.jsonl")
    path.write_text("".join(json.dumps(row, ensure_ascii=False)+"\n" for row in build()))
    print(path, len(build()), "exemplos")
