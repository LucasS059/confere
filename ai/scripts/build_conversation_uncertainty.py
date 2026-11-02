"""Recupera falta de informação e reparo após históricos mais longos, só no treino."""
import json
import random
from build_conversation_contrasts import build as contrasts


def build():
    rows = contrasts()
    rng = random.Random(9209)
    contexts = {json.dumps([r["history"], r["prompt"].strip().casefold()], ensure_ascii=False):
                (r["split"], r["target"]) for r in rows}
    def add(task, prompt, target, history):
        key = json.dumps([history, prompt.strip().casefold()], ensure_ascii=False)
        if key in contexts and contexts[key] != ("train", target):
            return
        contexts[key] = ("train", target)
        group = f"uncertainty-train-{len(rows)}"
        rows.append(dict(id=group+"-0", project_id=group, split="train", task="conversation_"+task,
                         history=history, turn_index=0, prompt=prompt, target=target,
                         provenance=dict(kind="synthetic_authored", note="Regressões conhecidas e incerteza autorais; sem revisão humana. Avaliação congelada.")))
    seeds = [[], [["oi", "Olá! Sou o Confere."]],
             [["qual seu nome?", "Sou o Confere."]],
             [["me ajuda", "O que você gostaria que eu fizesse?"]],
             [["não sei ainda", "Sem problema. Podemos falar de objetivos, requisitos ou evidências."]],
             [["O que é teste?", "Uma verificação do comportamento do sistema."]]]
    questions = ["quanto tirei na apresentação?", "qual foi minha nota na apresentação?",
                 "quanto valeu minha última apresentação?", "que nota recebi pelo trabalho?",
                 "qual foi o resultado da minha avaliação?", "quem avalia meu projeto?",
                 "quem vai ser meu avaliador?", "qual professor vai avaliar minha entrega?",
                 "quem estará na banca do meu trabalho?", "quem será o responsável pela avaliação?",
                 "qual é a nota que o professor me deu?", "qual é o nome de quem avalia meu trabalho?"]
    for _ in range(24):
        for prompt in questions:
            for seed in seeds:
                add("insufficient", prompt, "Não tenho informação suficiente para responder.", seed)
    for _ in range(300):
        n = rng.randint(1, 5)
        name = " ".join(["Confere"]*n)
        history = list(rng.choice(seeds))
        for task, prompt, target in [
            ("wellbeing", "ola", "Olá! Sou o Confere."),
            ("wellbeing", "vc esta bem?", "Estou pronto para ajudar. E você?"),
            ("composed", f"qual seu nome? diga {n} vezes", name),
            ("composed", "fala pfv", name),
            ("misunderstanding", "bugou?", "Entendi errado. Pode reformular o pedido?"),
            ("closure", "nada ue", "Tudo bem. Podemos conversar quando você quiser.")]:
            add(task, prompt, target, history)
            history = history + [[prompt, target]]
    return rows
