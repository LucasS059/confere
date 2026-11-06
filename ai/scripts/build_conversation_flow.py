"""Diálogos autorais completos com negação, correção e mudança de assunto."""
import json
import random
from build_conversation_identity import build as legacy


FORMS = {
    "train": {
        "hello": ["olá, Confere", "oi, vamos conversar", "bom dia, vamos conversar"],
        "identity": ["qual seu nome mesmo?", "me lembra seu nome?", "como é seu nome mesmo?"],
        "well": ["vou bem também, obrigado", "estou bem também", "comigo está tudo bem"],
        "absent": ["não tenho projeto", "nao tenho", "ainda não tenho um projeto", "não tenho nenhum projeto"],
        "insist": ["acabei de falar que nao tenho", "já disse que não tenho um projeto", "você não entendeu que não tenho projeto?"],
        "switch": ["vamos mudar de assunto", "quero falar de outra coisa", "podemos trocar de assunto?"],
        "topic": ["quero conversar sobre {}", "vamos falar sobre {}", "prefiro falar de {}"],
        "recall": ["qual é o assunto agora?", "sobre o que estamos falando?", "qual assunto eu escolhi?"],
        "have": ["agora tenho um projeto", "mudei de ideia: tenho projeto", "corrigindo: tenho um projeto"],
        "state": ["eu tenho um projeto?", "o que eu disse sobre ter projeto?", "qual é a minha situação com o projeto?"],
        "correct": ["corrigindo: ainda não tenho projeto", "na verdade, não tenho um projeto", "eu errei: não tenho projeto"],
        "repair": ["ue", "essa resposta não combina com o que eu disse", "você se perdeu na conversa?"],
        "close": ["só isso por agora", "não quero mais nada agora", "vou sair, até mais"],
    },
    "validation": {
        "hello": ["oi, bora conversar um pouco", "olá, podemos conversar?"],
        "identity": ["você pode lembrar como se chama?", "qual era mesmo o seu nome?"],
        "well": ["por aqui estou bem também", "está tudo bem comigo também"],
        "absent": ["não possuo um projeto ainda", "no momento estou sem projeto"],
        "insist": ["eu já expliquei que estou sem projeto", "você está insistindo, eu não tenho projeto"],
        "switch": ["vamos conversar de outro assunto", "quero trocar o assunto da conversa"],
        "topic": ["gostaria de conversar a respeito de {}", "o assunto que escolho é {}"],
        "recall": ["qual foi o assunto escolhido?", "do que estamos conversando agora?"],
        "have": ["a situação mudou, agora tenho projeto", "atualizando: eu tenho um projeto agora"],
        "state": ["afinal, eu tenho projeto ou não?", "como ficou a situação do meu projeto?"],
        "correct": ["preciso corrigir: estou sem projeto", "retificando, ainda estou sem um projeto"],
        "repair": ["isso não corresponde ao que falei", "você confundiu o que eu disse"],
        "close": ["encerramos por enquanto", "já podemos parar por aqui"],
    },
    "test": {
        "hello": ["oi, vim bater um papo contigo"],
        "identity": ["me recorde como você se chama"],
        "well": ["também me sinto bem, valeu por perguntar"],
        "absent": ["eu ainda estou sem nenhum projeto"],
        "insist": ["já avisei que não há projeto nenhum"],
        "switch": ["vamos deixar esse assunto e conversar de outra coisa"],
        "topic": ["podemos bater papo a respeito de {}?"],
        "recall": ["você lembra o assunto que selecionei?"],
        "have": ["uma novidade: passei a ter um projeto"],
        "state": ["segundo o que eu contei, tenho projeto?"],
        "correct": ["desculpe, me enganei: continuo sem projeto"],
        "repair": ["você entendeu outra coisa, não foi isso que disse"],
        "close": ["por hoje a nossa conversa acabou"],
    },
}


def build(train_forms=None):
    rows = legacy()
    rng = random.Random(11307)
    contexts = {json.dumps([r["history"], r["prompt"].strip().casefold()], ensure_ascii=False):
                (r["split"], r["target"]) for r in rows}

    def add(split, turns, seed):
        history, proposed = list(seed), []
        group = f"flow-{split}-{len(rows)}"
        for i, (task, prompt, target) in enumerate(turns):
            key = json.dumps([history, prompt.strip().casefold()], ensure_ascii=False)
            if key in contexts and contexts[key] != (split, target):
                return False
            proposed.append((key, dict(id=f"{group}-{i}", project_id=group, split=split,
                task="conversation_flow_"+task, prompt=prompt, target=target,
                history=[list(p) for p in history], turn_index=i,
                provenance=dict(kind="synthetic_authored", note="Diálogo autoral por cenário; sem revisão humana. Formas e conversas separadas por split."))))
            history = history + [[prompt, target]]
        for key, row in proposed:
            contexts[key] = (split, row["target"])
            rows.append(row)
        return True

    for split, count in (("train", 3600), ("validation", 24), ("test", 24)):
        bank = train_forms if split=="train" and train_forms is not None else FORMS[split]
        pick = lambda key: rng.choice(bank[key])
        for index in range(count):
            topic = rng.choice(["música", "cinema", "jogos", "livros", "estudos", "viagens"])
            # Prefixos independentes tornam a posição do pedido variável.
            seed = [] if rng.random()<.5 else [["qual seu nome?", "Sou o Confere."]]
            if index % 3 == 0:
                turns = [("greeting", pick("hello"), "Olá! Sou o Confere."),
                    ("acknowledgement", pick("well"), "Que bom! Sobre o que você quer conversar?"),
                    ("identity", pick("identity"), "Sou o Confere."),
                    ("negation", pick("absent"), "Sem problema. Podemos conversar sem um projeto."),
                    ("negation", pick("insist"), "Entendi: você ainda não tem um projeto. Não vou insistir no tema."),
                    ("switch", pick("switch"), "Claro. Sobre o que você quer conversar?"),
                    ("greeting", "oi" if split=="train" else "olá de novo" if split=="validation" else "oi novamente", "Olá! Sou o Confere."),
                    ("closure", pick("close"), "Tudo bem. Podemos conversar quando você quiser.")]
            elif index % 3 == 1:
                turns = [("state", pick("have"), "Entendi: agora você tem um projeto."),
                    ("state", pick("state"), "Você disse que tem um projeto."),
                    ("identity", pick("identity"), "Sou o Confere."),
                    ("state", pick("correct"), "Entendi: você ainda não tem um projeto."),
                    ("state", pick("state"), "Você disse que ainda não tem um projeto."),
                    ("switch", pick("switch"), "Claro. Sobre o que você quer conversar?"),
                    ("topic", pick("topic").format(topic), f"Podemos conversar sobre {topic}."),
                    ("topic", pick("recall"), f"Estamos conversando sobre {topic}.")]
            else:
                turns = [("topic", pick("topic").format(topic), f"Podemos conversar sobre {topic}."),
                    ("identity", pick("identity"), "Sou o Confere."),
                    ("negation", pick("absent"), "Sem problema. Podemos conversar sem um projeto."),
                    ("topic", pick("recall"), f"Estamos conversando sobre {topic}."),
                    ("repair", pick("repair"), "Minha resposta não correspondeu ao que você disse. Pode reformular?"),
                    ("acknowledgement", pick("well"), "Que bom! Sobre o que você quer conversar?"),
                    ("switch", pick("switch"), "Claro. Sobre o que você quer conversar?"),
                    ("closure", pick("close"), "Tudo bem. Podemos conversar quando você quiser.")]
            if not add(split, turns, seed):
                raise ValueError("Cenário colidiu com outro split ou alvo; reveja o gerador.")
    return rows
