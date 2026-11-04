"""Varredura experimental de arquivos completos, com cobertura e citações rastreáveis."""
import hashlib
from io import BytesIO
from pathlib import Path

from .extract import extract_document
from .grounding import prompt_for, resolve

RESPONSE_TOKENS = 64
MAX_UNITS = 4


def input_ids(requirement, units, tokenizer):
    return [tokenizer.BOS] + tokenizer.encode(prompt_for(requirement, units)) + [tokenizer.SEP]


def batches_for(documents, requirement, tokenizer, context_size):
    """Divide por caracteres Unicode; cada intervalo preserva literalmente a fonte."""
    batches = []; parts = []

    def fits(texts):
        units = [dict(id=f"page:{i+1}", text=text) for i, text in enumerate(texts)]
        return len(input_ids(requirement, units, tokenizer)) + RESPONSE_TOKENS <= context_size

    if not fits([""]):
        raise ValueError("O requisito excede o contexto disponível.")
    for doc_index, document in enumerate(documents, 1):
        for unit in document["units"]:
            text = unit["text"]
            if not text.strip(" |"):
                continue
            start = 0
            while start < len(text):
                # Busca limitada por trecho, mantendo todos os caracteres para os próximos lotes.
                low, high, length = 1, min(len(text)-start,context_size*4), 0
                while low <= high:
                    middle = (low+high)//2
                    if fits([text[start:start+middle]]):
                        length = middle; low = middle+1
                    else:
                        high = middle-1
                if not length:
                    raise ValueError("Não há espaço para um caractere da fonte; reduza o requisito.")
                # Preferir fronteira de palavra sem remover espaços nem alterar offsets.
                end = start+length
                if end < len(text):
                    boundary = text.rfind(" ", start+length//2, end)
                    if boundary >= start:
                        end = boundary+1
                piece = text[start:end]
                if parts and (len(parts) == MAX_UNITS or not fits([p["text"] for p in parts]+[piece])):
                    batches.append(parts); parts = []
                parts.append(dict(document_id=f"doc:{doc_index}", document=document["name"],
                                  source_sha256=document["sha256"], source_unit=unit["id"],
                                  char_start=start, char_end=end, text=piece))
                start = end
    if parts:
        batches.append(parts)
    return batches


def review_extracted(documents, requirements, tokenizer, context_size, predict):
    if not documents or not requirements or any(not isinstance(r, str) or not r.strip() for r in requirements):
        raise ValueError("Informe arquivos e pelo menos um requisito não vazio.")
    if len({d["sha256"] for d in documents}) != len(documents):
        raise ValueError("Arquivos repetidos na mesma conferência.")
    if not any(u["text"].strip(" |") for d in documents for u in d["units"]):
        raise ValueError("Nenhum texto utilizável foi extraído dos arquivos.")
    # Planejar todos os requisitos antes da primeira inferência evita trabalho parcial oculto.
    plans = [batches_for(documents, r, tokenizer, context_size) for r in requirements]
    missing = [dict(document_id=f"doc:{i}", unit=u["id"]) for i,d in enumerate(documents,1)
               for u in d["units"] if not u["text"].strip(" |")]
    results = []
    for number, (requirement, batches) in enumerate(zip(requirements, plans), 1):
        calls = []; evidence = []; statuses = set(); valid = True
        for index, parts in enumerate(batches, 1):
            aliases = [dict(id=f"page:{i+1}", text=p["text"]) for i,p in enumerate(parts)]
            ids = input_ids(requirement, aliases, tokenizer)
            if len(ids)+RESPONSE_TOKENS > context_size:
                raise ValueError("O lote planejado excede o contexto; conferência interrompida.")
            raw = predict(ids)
            resolved = resolve(raw, "batch", aliases)
            sound = resolved["valid_format"] and resolved["reference_valid"]
            valid = valid and sound
            status = resolved["result"]["status"]
            if sound and status != "evidencia_insuficiente":
                statuses.add(status)
            mapping = [dict(alias=a["id"], **{k:v for k,v in p.items() if k!="text"}) for a,p in zip(aliases,parts)]
            for quote in resolved["result"]["evidence"]:
                part = parts[[a["id"] for a in aliases].index(quote["unit"])]
                evidence.append(dict(**{k:v for k,v in part.items() if k!="text"}, quote=part["text"], model_status=status))
            calls.append(dict(batch=index, input_tokens=len(ids), raw_model_output=raw,
                              valid_format=resolved["valid_format"], reference_valid=resolved["reference_valid"],
                              proposed_status=status, sources=mapping))
        conflict = len(statuses)>1
        status = next(iter(statuses)) if len(statuses)==1 and valid and not missing else "evidencia_insuficiente"
        results.append(dict(id=f"R{number}", requirement=requirement, status=status,
                            requires_human_review=True, conflicting_evidence=conflict, model_outputs_valid=valid,
                            evidence=evidence, calls=calls,
                            coverage=dict(scope="all_extracted_text", all_extracted_text_processed=True,
                                          text_characters=sum(len(u["text"]) for d in documents for u in d["units"] if u["text"].strip(" |")),
                                          processed_characters=sum(p["char_end"]-p["char_start"] for batch in batches for p in batch),
                                          batches=len(batches), units_without_text=missing)))
    return dict(schema_version=1, experimental=True, offset_unit="unicode_codepoints",
                scope_note="Propostas restritas ao texto extraído. Referência válida não garante suporte semântico; imagens e demais conteúdos não extraídos exigem revisão.",
                sources=[dict(id=f"doc:{i}", name=d["name"], sha256=d["sha256"], format=d["format"],
                              warnings=d["warnings"], units=[dict(id=u["id"],characters=len(u["text"])) for u in d["units"]])
                         for i,d in enumerate(documents,1)], requirements=results)


def review_files(paths, requirements, checkpoint_path, device="auto"):
    import torch
    from .model import GPT, GPTConfig
    from .tokenizer import ByteBPE
    from .train import choose_device

    documents = [extract_document(path) for path in paths]
    payload = Path(checkpoint_path).read_bytes()
    checkpoint_hash = hashlib.sha256(payload).hexdigest()
    checkpoint = torch.load(BytesIO(payload), map_location="cpu", weights_only=True)
    del payload
    if checkpoint["settings"].get("objective") not in {"conversation", "document_grounding"}:
        raise ValueError("Use um checkpoint próprio de conferência documental ou treino misto.")
    tokenizer = ByteBPE(checkpoint["merges"]); config = GPTConfig(**checkpoint["config"])
    torch.set_num_threads(4); target = choose_device(device)
    model = GPT(config).to(target); model.load_state_dict(checkpoint["model"]); model.eval()
    def predict(ids):
        output = model.generate(torch.tensor([ids],device=target),RESPONSE_TOKENS,tokenizer.EOS)
        return tokenizer.decode(output[0,len(ids):].tolist())
    result = review_extracted(documents, requirements, tokenizer, config.block_size, predict)
    result["model"] = dict(checkpoint=str(checkpoint_path), sha256=checkpoint_hash, step=checkpoint["step"],
                           device=str(target), context_size=config.block_size, response_tokens=RESPONSE_TOKENS)
    return result
