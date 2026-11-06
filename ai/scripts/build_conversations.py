"""Conversas sintéticas curtas; histórico explícito, sem rótulos humanos."""
import json
from pathlib import Path


def build():
    rows=[]
    def add(split, category, turns, seed=None):
        group=f"conv-{split}-{len(rows)}"
        history=list(seed or [])
        for index,(prompt,target) in enumerate(turns):
            rows.append({"id":f"{group}-{index}","project_id":group,"split":split,"task":"conversation_"+category,
                "history":[list(p) for p in history],"turn_index":index,"prompt":prompt,"target":target,
                "provenance":{"kind":"synthetic_authored","note":"Template do assistente; respostas anteriores são contexto, não alvo da loss."}})
            history.append((prompt,target))
    greetings={"train":["oi","olá","ola","oi!","bom dia","boa tarde","boa noite","oii","oiii","olá, tudo bem?","e aí?","olá!"],"validation":["e aí, Confere!","opa, bom dia!","oi, como vai?"],"test":["ei, olá!","oi, Confere!"]}
    capabilities={"train":["o que você faz?","o que vc faz?","para que você serve?","qual sua função?","como pode ajudar?","me explique sua função"],"validation":["o que consigo fazer com você?","você serve para quê?"],"test":["em que você pode me ajudar?"]}
    for split in greetings:
        for greeting in greetings[split]:
            for question in capabilities[split]:
                add(split,"capability",[(greeting,"Olá! Sou o Confere."),(question,"Sou um experimento para apoiar a conferência de projetos."),("como começo?","Escolha um requisito e um trecho do documento.")])
    names={"train":["Ana","Bruno","Carlos","Diana","Elisa","Fabio","Gabriel","Helena","Igor","Julia","Lucas","Maria","Nina","Otavio","Paula","Rafael","Sofia","Tiago","Vera","Vitor"],"validation":["Alice","Caio","Lara","Pedro"],"test":["Bia","Davi","Eva","Leo"]}
    for split in names:
        forms=["Meu nome é {}.","Pode me chamar de {}.","Eu me chamo {}."] if split=="train" else ["Aqui é {}.","Sou {}."]
        for name in names[split]:
            for form in forms:
                add(split,"memory",[(form.format(name),f"Prazer, {name}."),("qual é meu nome?",f"Seu nome é {name}."),("repita meu nome",name)])
    roots={"train":["qual seu nome?","qual é seu nome?","quem é você?","como você se chama?"],"validation":["como devo te chamar?"],"test":["me diga como você é chamado"]}
    for split in roots:
        forms={"train":["Repita seu nome {} vezes.","Diga Confere {} vezes.","Fale seu nome {} vezes."],"validation":["Repita Confere {} vezes, por favor."],"test":["Pode falar seu nome {} vezes?"]}[split]
        for root in roots[split]:
            for form in forms:
                for n in range(1,6): add(split,"repeat",[(root,"Sou o Confere."),(form.format(n)," ".join(["Confere"]*n))])
    ambiguous={"train":["por favor","me ajuda","ajuda","faz isso","pode fazer?","você consegue?","preciso de ajuda","e agora?"],"validation":["pode me dar uma força?","por gentileza","consegue me ajudar aqui?"],"test":["me dá uma ajuda?","e então?"]}
    for split, questions in ambiguous.items():
        for greeting in greetings[split]:
            for question in questions:
                add(split,"clarify",[(greeting,"Olá! Sou o Confere."),(question,"O que você gostaria que eu fizesse?"),("não sei o que informar","Diga qual é o projeto e o que você quer verificar.")])
    for split,start,count in (("train",10,90),("validation",201,8),("test",301,8)):
        for n in range(start,start+count):
            add(split,"repair",[(f"{n} dias o quê?","Eu errei: não há prazo informado."),("então qual é o prazo?","Não tenho essa informação.")],seed=[("qual o meu prazo?",f"{n} dias")])
    concepts=[("requisito","Uma condição que o projeto precisa cumprir.","Exigir login para acessar dados é um requisito."),
        ("evidência","Um trecho que sustenta uma conclusão.","Uma descrição dos testes pode ser uma evidência."),
        ("cronograma","Um plano de atividades e prazos.","Listar tarefas e datas é um exemplo de cronograma."),
        ("teste","Uma verificação do comportamento do sistema.","Verificar se o login aceita uma senha correta é um teste.")]
    for split in greetings:
        forms={"train":["O que é {}?","Explique {}.","O que significa {}?"],"validation":["Como você define {}?"],"test":["Me diga o significado de {}."]}[split]
        for term,definition,example in concepts:
            for form in forms: add(split,"definition",[(form.format(term),definition),("dê um exemplo",example)])
    return rows


if __name__=="__main__":
    path=Path("ai/data/authored/conversations.jsonl")
    path.write_text("".join(json.dumps(r,ensure_ascii=False)+"\n" for r in build()))
    print(path,len(build()))
