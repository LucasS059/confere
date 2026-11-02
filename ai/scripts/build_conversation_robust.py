"""Varia o histórico de treino; preserva integralmente validação e teste."""
import json
import random
from build_conversation_curriculum import build as curriculum


def build():
    rows = curriculum()
    rng = random.Random(9103)
    contexts = {json.dumps([r["history"], r["prompt"].strip().casefold()], ensure_ascii=False):
                (r["split"], r["target"]) for r in rows}
    train = [r for r in rows if r["split"] == "train"]
    seeds = [[], [["oi", "Olá! Sou o Confere."]],
             [["qual seu nome? diga 3 vezes", "Confere Confere Confere"]],
             [["vc esta bem?", "Estou pronto para ajudar. E você?"]],
             [["qual o prazo?", "15 dias"]],
             [["o que vc faz?", "felificação do comportamento do sistema."]]]

    def add(task, prompt, target, history):
        key = json.dumps([history, prompt.strip().casefold()], ensure_ascii=False)
        if key in contexts and contexts[key] != ("train", target):
            return
        contexts[key] = ("train", target)
        group = f"robust-train-{len(rows)}"
        rows.append(dict(id=group+"-0", project_id=group, split="train", task=task,
                         history=history, turn_index=0, prompt=prompt, target=target,
                         provenance=dict(kind="synthetic_authored",
                                         note="Variação autoral do histórico; sem revisão humana. Validação congelada.")))

    # Preserve o contexto relevante dos exemplos dependentes de memória.
    for _ in range(10000):
        row = rng.choice(train)
        add(row["task"], row["prompt"], row["target"], rng.choice(seeds) + row["history"])

    banks = [
        ("wellbeing", "Estou pronto para ajudar. E você?",
         ["vc esta bem?", "como estão as coisas com você?", "como você anda?", "como vai você?", "tudo certo contigo?", "como está indo hoje?", "tudo bem contigo?"]),
        ("misunderstanding", "Entendi errado. Pode reformular o pedido?",
         ["bugou?", "você se confundiu?", "isso não ficou coerente", "acho que você não entendeu", "não compreendeu o pedido?", "sua resposta ficou sem sentido", "a resposta saiu errada"]),
        ("closure", "Tudo bem. Podemos conversar quando você quiser.",
         ["nada ue", "só passei para conversar", "não quero nada agora", "sem pedidos por enquanto", "por enquanto não quero nada", "só estou conversando", "não tenho mais pedidos", "só vim conversar com você"]),
        ("clarify", "O que você gostaria que eu fizesse?",
         ["preciso de uma força", "pode ajudar?", "me dê uma ajudinha", "consegue ajudar?", "uma força, por favor", "por favor me ajude"]),
        ("capability", "Olá! Sou o Confere.",
         ["e aí, amigo!", "e aí, Confere", "oi, tudo certo?", "olá Confere!", "opa, olá!", "oi, como tá?", "opa, boa tarde!"]),
    ]
    for task, target, prompts in banks:
        for prompt in prompts:
            for seed in seeds:
                add("conversation_"+task, prompt, target, seed)
    return rows
