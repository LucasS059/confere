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


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument("run_dir",type=Path)
    root=p.parse_args().run_dir;output=root/"open-dialogue.json"
    if output.exists():p.error("Diagnóstico existente; preserve as respostas.")
    info=json.loads((root/"run.json").read_text());torch.set_num_threads(4)
    result=dict(scope="Sequência composta após preparar o corpus; prompts e intenções individuais podem existir no treino. Leitura qualitativa, sem revisão humana independente. Não é benchmark de conversa aberta.")
    for key,path in (("before",Path(info["resume_from"])),("after",root/"best.pt")):
        model,tokenizer,step=load_model(path)
        result[key]=dict(checkpoint=str(path),step=step,messages=capture(model,tokenizer,PROMPTS))
        del model
    output.write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n")
    print(json.dumps(result,ensure_ascii=False),flush=True);print(create_report(root))


if __name__=="__main__":main()
