"""Reforça identificação sem retirar os exemplos das demais famílias."""
from build_conversation_uncertainty import build as uncertainty


def build():
    rows = uncertainty()
    seeds = [[], [["oi", "Olá! Sou o Confere."]],
             [["o que vc faz?", "Sou um experimento para apoiar a conferência de projetos."]],
             [["vc esta bem?", "Estou pronto para ajudar. E você?"]]]
    for _ in range(40):
        for prompt in ("como posso te chamar?", "como devo chamar você?", "que nome devo usar para você?",
                       "devo te chamar de quê?", "me diga seu nome", "qual é o nome que você usa?",
                       "qual é a sua identificação?", "por qual nome posso chamar você?", "qual seu nome?"):
            for seed in seeds:
                group = f"identity-train-{len(rows)}"
                rows.append(dict(id=group+"-0", project_id=group, split="train", task="conversation_identity",
                                 history=seed, turn_index=0, prompt=prompt, target="Sou o Confere.",
                                 provenance=dict(kind="synthetic_authored", note="Reforço autoral de identidade, repetido; sem revisão humana. Avaliação congelada.")))
    return rows
