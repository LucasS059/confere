"""Amplia formulações de treino e reparos; congela todos os splits anteriores."""
from copy import deepcopy
import json
from build_conversation_flow import FORMS, build as flow


def build():
    rows=flow()
    bank=deepcopy(FORMS["train"])
    extra={
        "hello":["oi, voltei", "olá outra vez", "bom dia novamente", "oi de novo, Confere", "olá, voltei para conversar"],
        "identity":["me recorda o seu nome?", "qual era seu nome?", "como era mesmo seu nome?", "você pode dizer como se chama?", "lembre seu nome para mim"],
        "well":["também estou bem, obrigado por perguntar", "por aqui vai tudo bem", "tudo certo comigo também", "eu estou bem, valeu"],
        "absent":["estou sem um projeto", "eu não possuo nenhum projeto", "não possuo projeto algum", "atualmente não tenho projeto", "por enquanto estou sem projeto"],
        "insist":["você insiste, mas eu já disse que não tenho", "acabei de explicar que estou sem projeto", "não tenho projeto, como já falei", "eu já falei: não há projeto"],
        "switch":["vamos trocar o tema", "podemos mudar o assunto da conversa?", "quero trocar o assunto", "mude o assunto, por favor", "vamos conversar sobre outra coisa"],
        "topic":["vamos conversar a respeito de {}", "minha escolha de assunto é {}", "gostaria de falar sobre {}", "eu escolho o assunto {}", "quero bater papo sobre {}"],
        "recall":["do que estamos falando agora?", "qual é o tema que eu escolhi?", "qual assunto foi selecionado?", "lembra sobre o que estamos conversando?", "o que estamos conversando?"],
        "have":["atualização: agora eu tenho projeto", "atualizando minha situação, tenho um projeto", "a situação mudou: passei a ter projeto", "eu tenho projeto agora", "corrigindo minha informação: tenho projeto"],
        "state":["eu tenho ou não tenho projeto?", "como está minha situação quanto ao projeto?", "de acordo com o que eu falei, tenho projeto?", "afinal tenho projeto?", "o que eu contei sobre meu projeto?"],
        "correct":["retificando minha informação: não tenho projeto", "estou sem projeto, preciso corrigir isso", "corrijo: continuo sem projeto", "me enganei, não tenho projeto", "quero corrigir: estou sem um projeto"],
        "repair":["você confundiu a minha mensagem", "isso não corresponde à minha mensagem", "não foi isso que eu falei", "acho que você se confundiu na resposta"],
        "close":["vamos encerrar a conversa", "podemos parar agora", "por enquanto encerramos", "quero terminar por aqui", "já podemos encerrar", "podemos parar por enquanto"],
    }
    for key, forms in extra.items():bank[key].extend(forms)
    mapping={}
    for row in flow(train_forms=bank):
        if not row["id"].startswith("flow-train-"):continue
        group=mapping.setdefault(row["project_id"],f"flow-expanded-train-{len(rows)}")
        row=dict(row,id=f'{group}-{row["turn_index"]}',project_id=group)
        rows.append(row)
    contexts={json.dumps([r["history"],r["prompt"].strip().casefold()],ensure_ascii=False):(r["split"],r["target"]) for r in rows}
    def add(prompt,target,history):
        key=json.dumps([history,prompt.strip().casefold()],ensure_ascii=False)
        if key in contexts and contexts[key]!=("train",target):return
        contexts[key]=("train",target)
        group=f"flow-repair-train-{len(rows)}"
        rows.append(dict(id=group+"-0",project_id=group,split="train",task="conversation_flow_repair",
                         history=history,turn_index=0,prompt=prompt,target=target,
                         provenance=dict(kind="synthetic_authored",note="Reparo autoral após falhas conhecidas; sem revisão humana. Contexto anterior mascarado.")))
    seeds=[[],[["oi","Olá! Sou o Confere."]],
           [["não tenho projeto","Sem problema. Podemos conversar sem um projeto."]],
           [["qual seu nome mesmo?","Sou o Confere."],["não tenho projeto","Vamos começar pelo tema do seu projeto. Qual é o tema?"]]]
    for _ in range(100):
        for seed in seeds:
            for prompt in ("a","hm","?","...","não entendi essa resposta"):
                add(prompt,"Não entendi. Pode escrever uma mensagem mais completa?",seed)
            for prompt in ("ue","vc é burro?","você não está entendendo","sua resposta saiu errada"):
                add(prompt,"Posso ter entendido errado. Pode me dizer o que devo corrigir?",seed)
            add("qual é o assunto agora?","Você ainda não escolheu um assunto.",seed)
        add("obrigado o que","Eu me confundi. Você apenas me cumprimentou.",[["oi","Obrigado!"]])
        add("obrigado o que","Eu apenas cumprimentei você.",[["oi","Olá! Sou o Confere."]])
    return rows
