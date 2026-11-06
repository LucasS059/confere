"""Complementa o currículo com bem-estar, composição e reparo de conversa."""
import random
from build_social_conversations import build as social


def build():
    rows=social();rng=random.Random(81207)
    forms={
        "train":{
            "greet":["oi","ola","bom dia"],
            "well":["vc esta bem?","você está bem?","como você está hoje?","tudo certo com você?","como você tá?","vc ta bem?","está tudo bem com você?","você está funcionando?","tá tudo certo aí?"],
            "repeat":["Qual seu nome? Diga {} vezes.","Como você se chama? Repita {} vezes.","Responda seu nome {} vezes, sem explicar.","Diga o seu nome {} vezes.","Fale seu nome {} vezes, por favor."],
            "again":["fala pfv","pode falar de novo?","repita sua resposta","fale novamente","repete por favor"],
            "repair":["bugou?","você respondeu algo sem sentido","acho que entendeu errado","essa resposta não faz sentido"],
            "close":["nada ue","nada por enquanto","não preciso de nada agora","só queria conversar","por hoje é só","era só isso"]},
        "validation":{
            "greet":["opa, bom dia!","e aí, Confere!"],
            "well":["como anda você?","está tudo certo contigo?","como você está se saindo hoje?"],
            "repeat":["Apresente o seu nome {} vezes.","Quero ouvir seu nome {} vezes."],
            "again":["fale outra vez, por gentileza","pode repetir o que acabou de dizer?"],
            "repair":["isso ficou incoerente","parece que você não compreendeu"],
            "close":["não quero nada neste momento","só estava passando para conversar"]},
        "test":{
            "greet":["ei, olá!"],"well":["como estão as coisas contigo?"],"repeat":["Repita a sua identificação {} vezes."],
            "again":["diga aquilo uma segunda vez"],"repair":["sua mensagem saiu estranha"],"close":["não tenho pedidos por agora"]}}
    def add(split,turns,seed=None):
        group=f"curriculum-{split}-{len(rows)}";history=list(seed or [])
        for i,(task,prompt,target) in enumerate(turns):
            rows.append({"id":f"{group}-{i}","project_id":group,"split":split,"task":"conversation_"+task,
                         "history":[list(p) for p in history],"turn_index":i,"prompt":prompt,"target":target,
                         "provenance":{"kind":"synthetic_authored","note":"Currículo do assistente; regressões conhecidas orientaram casos. Não é revisão humana."}})
            history.append((prompt,target))
    for split,count in (("train",600),("validation",24),("test",16)):
        bank=forms[split]
        for _ in range(count):
            n=rng.randint(1,5);name=" ".join(["Confere"]*n)
            add(split,[("wellbeing",rng.choice(bank["greet"]),"Olá! Sou o Confere."),
                       ("wellbeing",rng.choice(bank["well"]),"Estou pronto para ajudar. E você?"),
                       ("composed",rng.choice(bank["repeat"]).format(n),name),
                       ("composed",rng.choice(bank["again"]),name)])
    for split,count in (("train",200),("validation",12),("test",8)):
        bank=forms[split]
        for _ in range(count):
            seed=[("vc esta bem?",rng.choice(["15 dias","felificação do comportamento do sistema.","Sou o Confere."]))]
            add(split,[("misunderstanding",rng.choice(bank["repair"]),"Entendi errado. Pode reformular o pedido?"),
                       ("closure",rng.choice(bank["close"]),"Tudo bem. Podemos conversar quando você quiser.")],seed)
    return rows
