"""Casos documentais sintéticos curtos; rótulos derivados da construção."""
import json
import random
from pathlib import Path
from confere_ai.grounding import prompt_for


def build():
    rng = random.Random(9218)
    rows = []
    topics = {"train": ["testes", "backup", "cronograma", "orçamento", "documentação", "protótipo", "controle de acesso", "cadastro", "login", "acessibilidade", "integração", "treinamento"],
              "validation": ["monitoramento", "relatórios", "busca", "exportação"],
              "test": ["auditoria", "importação", "recuperação de senha"]}
    forms = {"train": [("O projeto inclui {}.", "O projeto não inclui {}."), ("Há {} no projeto.", "Não há {} no projeto."), ("O sistema oferece {}.", "O sistema não oferece {}.")],
             "validation": [("A entrega apresenta {}.", "A entrega não apresenta {}.")],
             "test": [("O produto contém {}.", "O produto não contém {}.")]}
    for split, count in (("train", 1200), ("validation", 90), ("test", 90)):
        for i in range(count):
            feature = rng.choice(topics[split])
            status = ("atendido", "nao_atendido", "evidencia_insuficiente")[i%3]
            positive, negative = rng.choice(forms[split])
            texts = [f"Equipe: {rng.randint(100000,999999)}.", "Tema: biblioteca.",
                     positive.format(feature) if status == "atendido" else negative.format(feature) if status == "nao_atendido" else "A equipe trabalha no projeto."]
            rng.shuffle(texts)
            units = [{"id": f"page:{j+1}", "text": text} for j,text in enumerate(texts)]
            unit = next((u["id"] for u in units if feature in u["text"]), None)
            requirement = f"O projeto deve incluir {feature}."
            rows.append({"id":f"ground-{split}-{i}", "project_id":f"ground-project-{split}-{i}", "split":split,
                "task":"grounded_"+status, "requirement":requirement, "document":f"project-{split}-{i}.pdf", "units":units,
                "prompt":prompt_for(requirement,units), "target":json.dumps({"status":status,"unit":unit},ensure_ascii=False),
                "provenance":{"kind":"synthetic_authored","note":"Documento fictício e rótulo por construção; sem revisão humana."}})
    # Replay somente de dados já separados: não converte validação em treino.
    replay = [json.loads(line) for line in Path("ai/data/authored/instructions-v2.jsonl").read_text().splitlines()]
    rows += [r for r in replay if r["split"]=="train"][:300]
    rows += [r for r in replay if r["split"]=="validation"][:24]
    return rows


if __name__ == "__main__":
    path = Path("ai/data/authored/grounding.jsonl")
    path.write_text("".join(json.dumps(row,ensure_ascii=False)+"\n" for row in build()))
    print(path, len(build()), "exemplos")
