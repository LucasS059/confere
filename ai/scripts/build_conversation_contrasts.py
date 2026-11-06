"""Contrasta intenções próximas somente no treino; avaliação permanece congelada."""
import json
from build_conversation_robust import build as robust


def build():
    rows = robust()
    contexts = {json.dumps([r["history"], r["prompt"].strip().casefold()], ensure_ascii=False):
                (r["split"], r["target"]) for r in rows}
    seeds = [[], [["oi", "Olá! Sou o Confere."]],
             [["o que vc faz?", "Sou um experimento para apoiar a conferência de projetos."]],
             [["como você se chama?", "Sou o Confere."]],
             [["vc esta bem?", "Estou pronto para ajudar. E você?"]],
             [["qual o prazo?", "15 dias"]]]
    def add(task, prompt, target, history):
        key = json.dumps([history, prompt.strip().casefold()], ensure_ascii=False)
        if key in contexts and contexts[key] != ("train", target):
            return
        contexts[key] = ("train", target)
        group = f"contrasts-train-{len(rows)}"
        rows.append(dict(id=group+"-0", project_id=group, split="train", task="conversation_"+task,
                         history=history, turn_index=0, prompt=prompt, target=target,
                         provenance=dict(kind="synthetic_authored", note="Contraste de intenções autoral; sem revisão humana. Validação congelada.")))
    added_start = len(rows)
    banks = [
        ("capability", "Sou um experimento para apoiar a conferência de projetos.",
         ["o que posso fazer com sua ajuda?", "que coisas você faz?", "para quê você serve?", "quais são suas funções?", "o que podemos fazer juntos?", "que tipo de ajuda você oferece?", "me conta o que você consegue fazer", "o que eu poderia fazer com você?", "você ajuda com o quê?"]),
        ("social", "Obrigado! Fico feliz em ajudar.",
         ["curti a sua proposta", "adorei entender sua função", "que bom contar com seu apoio", "sua ideia é legal", "gostei da sua função", "que bom que posso contar contigo", "curti muito essa proposta", "adorei saber disso", "sua função parece legal", "obrigado por explicar sua função"]),
        ("clarify", "O que você gostaria que eu fizesse?",
         ["gentilmente, me ajude", "uma ajudinha, por gentileza", "por gentileza, preciso de ajuda", "pode fazer algo por mim?", "poderia me ajudar um pouco?", "preciso de auxílio", "consegue me dar uma mão?", "me dê uma força, por gentileza"]),
        ("clarify", "Diga qual é o projeto e o que você quer verificar.",
         ["não sei o que informar", "não sei quais informações passar", "o que preciso te informar?", "não entendi o que preciso informar", "quais dados você precisa?"]),
    ]
    for task, target, prompts in banks:
        for prompt in prompts:
            for seed in seeds:
                add(task, prompt, target, seed)
    # Reforce a diferença entre contar nomes e repetir literalmente a última resposta.
    for n in range(1, 6):
        name = " ".join(["Confere"]*n)
        for seed in seeds:
            for form in ("Quero que fale seu nome {} vezes.", "Gostaria de ouvir seu nome {} vezes.",
                         "Mostre seu nome {} vezes.", "Apresente seu nome {} vezes, por favor."):
                prompt = form.format(n)
                add("composed", prompt, name, seed)
                for again in ("repita o que você falou", "pode falar aquilo de novo?", "diga novamente o que acabou de falar"):
                    add("composed", again, name, seed+[[prompt, name]])
    contrasts = rows[added_start:]
    for _ in range(11):
        for row in contrasts:
            add(row["task"].removeprefix("conversation_"), row["prompt"], row["target"], row["history"])
    return rows
