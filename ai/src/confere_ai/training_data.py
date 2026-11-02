import hashlib
import json
from pathlib import Path

from .dataset import validate_dataset
from .extract import extract_document


def load_authored(path):
    """Piloto restrito a dados autorais; candidatos reais não entram implicitamente."""
    path = Path(path).resolve()
    rows = [json.loads(line) for line in path.read_text().splitlines() if line.strip()]
    if any(row.get("provenance", {}).get("kind") not in {"authored", "controlled_variant"} for row in rows):
        raise ValueError("Este piloto aceita somente dados autorais; TCCs candidatos não estão liberados.")
    validate_dataset(path)
    documents = {}
    samples = []
    for row in rows:
        names = [name for name in row["documents"] if name != row["requirement"]["source"]["document"]]
        for name in row["documents"]:
            if name not in documents:
                documents[name] = extract_document(path.parent / name)
        contents = "\n".join(f"Arquivo: {name}\n" + "\n".join(f"[{unit['id']}] {unit['text']}" for unit in documents[name]["units"]) for name in names)
        prompt = f"Confira o requisito usando apenas os documentos. Responda em JSON com status, evidence e justification.\nRequisito: {row['requirement']['text']}\n{contents}\nResposta:\n"
        samples.append({"id": row["id"], "project_id": row["project_id"], "split": row["split"], "prompt": prompt, "target": json.dumps(row["expected"], ensure_ascii=False, sort_keys=True)})
    fingerprint = hashlib.sha256(path.read_bytes() + json.dumps({name: document["sha256"] for name, document in documents.items()}, sort_keys=True).encode()).hexdigest()
    if not any(sample["split"] == "train" for sample in samples):
        raise ValueError("Não há exemplos de treino.")
    return samples, fingerprint


def encode_sample(sample, tokenizer, block_size):
    target = tokenizer.encode(sample["target"])
    if "history" in sample:
        from .chat import prepare_prompt
        budget=sample.get("response_tokens",64)
        if not isinstance(budget,int) or not 0<budget<block_size-2: raise ValueError("Orçamento de resposta inválido.")
        if len(target)+1 > budget:
            raise ValueError(f"{sample['id']}: resposta excede o limite conversacional de {budget} tokens.")
        prefix, dropped = prepare_prompt(sample["history"], sample["prompt"], tokenizer, block_size, budget, "conversation")
        if dropped:
            raise ValueError(f"{sample['id']}: histórico de treino não cabe; nenhuma mensagem será removida silenciosamente.")
    else:
        prefix = [tokenizer.BOS] + tokenizer.encode(sample["prompt"]) + [tokenizer.SEP]
    sequence = prefix + target + [tokenizer.EOS]
    if len(sequence) - 1 > block_size:
        raise ValueError(f"{sample['id']}: {len(sequence) - 1} tokens excedem contexto {block_size}.")
    labels = sequence[1:]
    labels[:len(prefix) - 1] = [-100] * (len(prefix) - 1)
    return sequence[:-1], labels
