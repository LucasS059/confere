"""Contrastes por intenção e fatos mutáveis em históricos de conversa."""
import argparse
import hashlib
import json
import random
from collections import Counter
from pathlib import Path
from confere_ai.instruct import load_instructions
from prepare_document_lexical import paired_documents, balanced_replay

BANKS={
    "hello":(["opa, bora conversar?","e aí, podemos trocar ideia?","oi, voltei aqui","salve, Confere"],"Olá! Sou o Confere."),
    "function":(["oq tu consegue fazer?","que trabalho tu faz?","qual é o seu trabalho aí?","me descreve oq vc faz"],"Sou um experimento para apoiar a conferência de projetos."),
    "identity":(["e como tu se chama?","qual teu nome aí?","me lembra como vc se chama","quem é vc mesmo?"],"Sou o Confere."),
    "wellbeing":(["vc tá bem?","tá tudo bem contigo?","como vc tá hoje?","como tu tá?"],"Estou pronto para ajudar. E você?"),
    "praise":(["vlw pela ajuda","obg, foi útil","boa, gostei disso","isso ajudou, obrigado"],"Valeu! Se quiser, podemos continuar."),
    "repair":(["acho que vc n entendeu","não foi isso que eu quis dizer","sua resposta não combina com a pergunta","vc confundiu minha pergunta"],"Entendi errado. Pode reformular o pedido?")}
NAMES=["Ana","Bruno","Carlos","Diana","Elisa","Fabio","Gabriel","Helena","Igor","Julia","Maria","Nina","Otavio","Paula","Rafael","Sofia","Tiago","Vera","Vitor"]


def contextual_rows(source,counterbalanced=False):
    rng=random.Random(318)
    seeds=[r["history"][-2:] for r in source if r["split"]=="train" and r["task"].startswith("conversation_")]
    result=[]
    def add(group,turns,seed):
        if counterbalanced:group="balanced-"+group
        history=[list(p) for p in seed]
        for index,(task,prompt,target) in enumerate(turns):
            result.append(dict(id=f"{group}-{index}",project_id=group,split="train",task="conversation_context_"+task,
                               history=[list(p) for p in history],turn_index=index,prompt=prompt,target=target,response_tokens=256,
                               provenance=dict(kind="synthetic_authored",note="Contrastes de intenção e fatos mutáveis; treino conhecido, sem revisão humana.")))
            history.append([prompt,target])
    banks=dict(BANKS)
    if counterbalanced:
        banks["mood"]=( ["tô exausto hoje","tô sem energia hj","preciso descansar, tô cansado","meu dia tá difícil"],"Entendi. Quer me contar o que aconteceu?")
        banks["boundary"]=( ["não tô a fim de discutir projeto agora","vamos deixar trabalho de lado","quero um papo fora do projeto","não quero tratar de tarefa hoje"],"Sem problema. Podemos conversar sem um projeto.")
    for i in range(500):
        seed=rng.choice(seeds)
        for task,(prompts,target) in banks.items():
            for j,prompt in enumerate(prompts):add(f"intent-{i}-{task}-{j}",[(task,prompt,target)],seed)
    for i in range(750):
        first,second=rng.sample(NAMES,2);topic=rng.choice(["música","cinema","jogos","livros","estudos","viagens"])
        turns=[("memory",rng.choice(["pode me chamar de {}","eu sou {}","me chama de {}"]).format(first),f"Prazer, {first}."),
               ("memory",rng.choice(["lembra como eu me chamo?","como eu me chamo mesmo?"]),f"Seu nome é {first}."),
               ("boundary",rng.choice(["não quero falar de trabalho agora","deixa projeto de lado por enquanto"]),"Sem problema. Podemos conversar sem um projeto."),
               ("topic",rng.choice(["tô afim de falar sobre {}","podemos conversar de {} agora?"]).format(topic),f"Podemos conversar sobre {topic}."),
               ("topic",rng.choice(["me lembra de que a gente tá falando","qual assunto estávamos tratando?"]),f"Estamos conversando sobre {topic}."),
               ("memory",rng.choice(["na verdade, meu nome é {}","corrigindo: pode me chamar de {}"]).format(second),f"Prazer, {second}."),
               ("memory",rng.choice(["e qual é meu nome agora?","você lembra meu nome mesmo?"]),f"Seu nome é {second}."),
               ("mood",rng.choice(["tô exausto hoje","não tô num dia bom","tô meio pra baixo","estou cansado, preciso conversar"]),"Entendi. Quer me contar o que aconteceu?")]
        if counterbalanced:
            blocks={"first":turns[:2],"topic":turns[3:5],"correction":turns[5:7],"boundary":turns[2:3],"mood":turns[7:]}
            order=["first","topic","boundary","mood"];rng.shuffle(order)
            order.insert(rng.randrange(order.index("first")+1,len(order)+1),"correction")
            turns=[turn for name in order for turn in blocks[name]]
        elif i%2:turns=turns[:2]+turns[3:5]+turns[2:3]+turns[5:]
        add(f"contextual-{i}",turns,rng.choice(seeds))
    return result


def build_rows(source,counterbalanced=False):
    replay=balanced_replay(source,600);extra=contextual_rows(source,counterbalanced)
    rows=paired_documents()+replay+extra+[r for r in source if r["split"]!="train" and r["task"].startswith("conversation_")]
    return rows,len(replay),len(extra)


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument("output",type=Path);p.add_argument("--source",type=Path,required=True)
    p.add_argument("--counterbalanced",action="store_true");args=p.parse_args()
    if args.output.exists():p.error("Saída deve ser nova.")
    source,fingerprint=load_instructions(args.source)
    rows,replay_count,extra_count=build_rows(source,args.counterbalanced)
    args.output.mkdir(parents=True);path=args.output/"examples.jsonl"
    path.write_text("".join(json.dumps(r,ensure_ascii=False)+"\n" for r in rows));load_instructions(path)
    manifest=dict(source_sha256=fingerprint,dataset_sha256=hashlib.sha256(path.read_bytes()).hexdigest(),
                  document_train=6000,replay_train=replay_count,contextual_train=extra_count,counterbalanced=args.counterbalanced,splits=dict(Counter(r["split"] for r in rows)),
                  note="Somente autoral nesta consolidação. Pesos herdam treino externo anterior. Validação/teste preservados; diagnósticos conhecidos informaram o desenho.")
    (args.output/"manifest.json").write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+"\n")
    print(json.dumps(manifest,ensure_ascii=False))


if __name__=="__main__":main()
