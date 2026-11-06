"""Reproduz a sequência conhecida das capturas, sem editar a saída da rede."""
import argparse
import json
from pathlib import Path
import torch
from confere_ai.chat import prepare_prompt
from evaluate_conversation_flow import load_model

PROMPTS = ["ola", "como vai?", "vou bem tambem, obrigado", "qual seu nome mesmo?", "ue",
           "nao tenho", "acabei de falar que nao tenho", "vc é burro?", "a", "oi", "obrigado o que"]


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("checkpoint",type=Path)
    parser.add_argument("output",type=Path)
    args=parser.parse_args()
    if args.output.exists():parser.error("Saída já existe.")
    torch.set_num_threads(4)
    model,tokenizer,step=load_model(args.checkpoint)
    history=[];results=[]
    for prompt in PROMPTS:
        ids,dropped=prepare_prompt(history,prompt,tokenizer,1024,256,"conversation")
        output=model.generate(torch.tensor([ids],device="mps"),256,tokenizer.EOS)
        answer=tokenizer.decode(output[0,len(ids):].tolist())
        results.append(dict(prompt=prompt,answer=answer,dropped_turns=dropped))
        history=history[dropped:]+[(prompt,answer)]
    record=dict(checkpoint=str(args.checkpoint),step=step,scope="Falhas conhecidas; não é teste independente.",results=results)
    args.output.write_text(json.dumps(record,ensure_ascii=False,indent=2)+"\n")
    print(json.dumps(record,ensure_ascii=False))


if __name__=="__main__":main()
