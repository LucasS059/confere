"""Diagnóstico qualitativo novo, sem nota automática nem consulta ao teste."""
import argparse
import json
from pathlib import Path
import torch
from confere_ai.report import create_report
from evaluate_conversation_flow import load_model
from evaluate_informal_dialogues import capture

PROMPTS=["oi, como vc tá?","hoje tô cansado","só quero conversar, sem falar de projeto",
         "meu nome é Lucas","qual é meu nome?","agora vamos falar de música",
         "qual era o assunto?","vc se perdeu?","eu disse música","explica de outro jeito","valeu, até mais"]
FRESH_PROMPTS=["olá, tudo tranquilo?","não dormi bem, tô sem disposição","hoje não quero tratar de trabalho",
               "pode me chamar de Carla","como eu me chamo?","vamos conversar sobre cinema",
               "qual tema escolhi?","não era isso, você confundiu","eu pedi cinema","fala de um jeito mais simples","até outro dia"]


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument("run_dir",type=Path)
    p.add_argument("--fresh",action="store_true",help="Diagnóstico adicional com nome, assunto e formulações diferentes.")
    args=p.parse_args();root=args.run_dir;output=root/("fresh-dialogue.json" if args.fresh else "open-dialogue.json")
    if output.exists():p.error("Diagnóstico existente; preserve as respostas.")
    info=json.loads((root/"run.json").read_text());torch.set_num_threads(4)
    result=dict(scope="Sequência diagnóstica; a anterior já informou ajustes. Prompts e intenções individuais podem existir no treino. Leitura qualitativa, sem revisão humana independente. Não é benchmark de conversa aberta.")
    for key,path in (("before",Path(info["resume_from"])),("after",root/"best.pt")):
        model,tokenizer,step=load_model(path)
        result[key]=dict(checkpoint=str(path),step=step,messages=capture(model,tokenizer,FRESH_PROMPTS if args.fresh else PROMPTS))
        del model
    output.write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n")
    print(json.dumps(result,ensure_ascii=False),flush=True);print(create_report(root))


if __name__=="__main__":main()
