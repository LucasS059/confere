"""Conversas com alternância de tarefas e nomes sintéticos combinatórios."""
import random
from build_conversations import build as base


def build():
    rows=base();rng=random.Random(34217)
    def add(split,turns):
        group=f"mixed-{split}-{len(rows)}";history=[]
        for i,(task,prompt,target) in enumerate(turns):
            rows.append({"id":f"{group}-{i}","project_id":group,"split":split,"task":"conversation_"+task,"history":[list(p) for p in history],"turn_index":i,"prompt":prompt,"target":target,
                "provenance":{"kind":"synthetic_authored","note":"Alternância de tarefas por construção; sem revisão humana."}})
            history.append((prompt,target))
    def pool(split):
        train=split=="train"
        result=[("capability",q,"Sou um experimento para apoiar a conferência de projetos.") for q in (["o que vc faz?","qual sua função?","para que você serve?","como pode ajudar?","me fale sua função"] if train else ["o que consigo fazer com você?","você serve para quê?"])]
        result += [("identity",q,"Sou o Confere.") for q in (["qual seu nome?","quem é você?","como você se chama?"] if train else ["como devo te chamar?"])]
        result += [("clarify",q,"O que você gostaria que eu fizesse?") for q in (["por favor","me ajuda","faz isso","pode fazer?","preciso de ajuda","me dê uma força"] if train else ["por gentileza","consegue me ajudar aqui?"])]
        result += [("insufficient",q,"Não tenho informação suficiente para responder.") for q in (["qual a nota do meu trabalho?","quem é meu professor?","qual a data da minha entrega?"] if train else ["quanto valeu a minha apresentação?","quem vai avaliar meu trabalho?"])]
        result += [("repair",f"{n} dias o quê?","Não há prazo informado nesta conversa.") for n in ([1,2,3,5,7,12,15,18,21,30,60] if train else [4,8,13,25])]
        for n in range(1,6):
            forms=["Diga seu nome {} vezes.","Qual é seu nome? Repita {} vezes.","Fale Confere {} vezes.","Repita seu nome {} vezes."] if train else ["Repita Confere {} vezes, por favor."]
            result += [("repeat",form.format(n)," ".join(["Confere"]*n)) for form in forms]
        definitions=[("requisito","Uma condição que o projeto precisa cumprir."),("evidência","Um trecho que sustenta uma conclusão."),("cronograma","Um plano de atividades e prazos."),("teste","Uma verificação do comportamento do sistema.")]
        for term,target in definitions:
            forms=["O que é {}?","Explique {}.","Defina {}.","O que significa {}?","Me explique a palavra {}."] if train else ["Como você define {}?"]
            result += [("definition",form.format(term),target) for form in forms]
        if split=="test":
            result=[(task,prompt+" Responda de forma direta.",target) for task,prompt,target in result]
        return result
    for split,count in (("train",1600),("validation",40),("test",30)):
        choices=pool(split)
        for _ in range(count): add(split,rng.sample(choices,3))
    used={"Ana","Alice","Pedro","Lara","Caio"} | {r["target"].split(", ",1)[1].rstrip(".") for r in rows if r["target"].startswith("Prazer, ")}
    syllables=["al","be","ca","di","el","fa","gi","he","ja","ki","lu","ma","ni","pe","ra","so","ti","ve","ro","na","le","ia","io","sa","no"]
    for split,count in (("train",800),("validation",24),("test",24)):
        for _ in range(count):
            name="".join(rng.choices(syllables,k=rng.choice([2,3]))).capitalize()
            while name in used: name="".join(rng.choices(syllables,k=3)).capitalize()
            used.add(name)
            opening=rng.choice(["Meu nome é {}.","Eu me chamo {}.","Pode me chamar de {}.","Aqui é {}.","Sou {}."]) if split=="train" else rng.choice(["Aqui é {}.","Sou {}."])
            add(split,[("memory",opening.format(name),f"Prazer, {name}."),("memory","qual é meu nome?",f"Seu nome é {name}."),("memory","repita meu nome",name)])
    return rows
