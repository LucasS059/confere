"""Expande conversa guiada: agradecimento, incerteza e escolha do próximo passo."""
import random
from build_conversation_mix import build as mixed


def build():
    rows=mixed();rng=random.Random(60413)
    hello="Olá! Sou o Confere."
    thanks="Obrigado! Fico feliz em ajudar."
    proposal="Sem problema. Podemos falar de objetivos, requisitos ou evidências."
    focus="Vamos começar pelo tema do seu projeto. Qual é o tema?"
    utterances={
        "train": {
            "greet":["oi","olá","bom dia","oiii"],
            "praise":["que legal","muito legal","obrigado","valeu","boa","gostei","ótimo","legal confere","que massa","que legal, Confere!","obrigado confere!","show","bacana","obrigada"],
            "uncertain":["não sei ainda","nao sei ainda","ainda não sei","não sei por onde começar","estou indeciso","não tenho ideia","não sei o que pedir","não sei como você pode me ajudar","ainda não pensei nisso","não tenho certeza","não sei o que fazer agora","não escolhi nada ainda"],
            "again":["continuo sem saber","ainda não sei o que quero","não faço ideia do que pedir","mesmo assim não sei","não sei o que quero que você faça","estou sem ideia ainda"]},
        "validation": {
            "greet":["opa, bom dia!","e aí, Confere!","oi, como vai?"],
            "praise":["curti sua ideia","que bom poder contar com você","isso parece interessante","adorei conhecer sua função"],
            "uncertain":["ainda não decidi o que quero de você","não tenho clareza de como você poderia ajudar","estou sem direção para começar","não tenho nenhum pedido em mente"],
            "again":["mesmo com essas opções ainda estou em dúvida","ainda não consegui escolher uma dessas coisas","não sei qual dessas opções faz sentido"]},
        "test": {
            "greet":["ei, olá!","oi, Confere!"],
            "praise":["achei sua proposta ótima","parece uma ajuda bacana"],
            "uncertain":["estou indeciso sobre o que pedir a você","não descobri do que preciso ainda"],
            "again":["ainda não consegui decidir nem depois disso","continuo indeciso entre essas opções"]}}
    def add(split, turns):
        group=f"social-{split}-{len(rows)}";history=[]
        for index,(task,prompt,target) in enumerate(turns):
            rows.append({"id":f"{group}-{index}","project_id":group,"split":split,"task":"conversation_"+task,
                         "history":[list(pair) for pair in history],"turn_index":index,"prompt":prompt,"target":target,
                         "provenance":{"kind":"synthetic_authored","note":"Template social do assistente, sem revisão humana; não é diálogo espontâneo."}})
            history.append((prompt,target))
    for split,count in (("train",600),("validation",24),("test",16)):
        bank=utterances[split]
        for _ in range(count):
            add(split,[("social",rng.choice(bank["greet"]),hello),("social",rng.choice(bank["praise"]),thanks),
                       ("guidance",rng.choice(bank["uncertain"]),proposal),("guidance",rng.choice(bank["again"]),focus)])
    for split,count in (("train",200),("validation",12),("test",8)):
        bank=utterances[split]
        for _ in range(count):
            add(split,[("guidance",rng.choice(bank["uncertain"]),proposal),("guidance",rng.choice(bank["again"]),focus)])
    return rows
