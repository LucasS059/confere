"""Ponteiros verificáveis: citações vêm da fonte, nunca são reescritas pela rede."""
import json

STATUSES = {"atendido", "nao_atendido", "evidencia_insuficiente"}


def unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("Chaves duplicadas na resposta.")
        result[key] = value
    return result


def prompt_for(requirement, units):
    return "Confira o requisito. Retorne JSON com status e unit.\nRequisito: " + requirement + "\n" + "\n".join(f'[{unit["id"]}] {unit["text"]}' for unit in units)


def resolve(raw, document, units):
    fallback = {"status": "evidencia_insuficiente", "evidence": [], "justification": "Saída inválida do modelo; conferência inconclusiva."}
    result = {"valid_format": False, "reference_valid": False, "result": fallback}
    try:
        value = json.loads(raw, object_pairs_hook=unique_object)
    except (ValueError, TypeError):
        return result
    if not isinstance(value, dict) or set(value) != {"status", "unit"} or not isinstance(value["status"], str) or value["status"] not in STATUSES:
        return result
    status, unit_id = value["status"], value["unit"]
    if (status == "evidencia_insuficiente" and unit_id is not None) or (status != "evidencia_insuficiente" and not isinstance(unit_id, str)):
        return result
    result["valid_format"] = True
    if unit_id is None:
        result["reference_valid"] = True
        result["result"] = {"status": status, "evidence": [], "justification": "Modelo não encontrou evidência suficiente no contexto fornecido."}
        return result
    matches = [unit for unit in units if unit["id"] == unit_id and unit["text"].strip()]
    if len(matches) != 1:
        return result
    result["reference_valid"] = True
    result["result"] = {"status": status, "evidence": [{"document": document, "unit": unit_id, "quote": matches[0]["text"]}],
                        "justification": "Classificação experimental do modelo; trecho selecionado na fonte. Suporte semântico ainda exige verificação."}
    return result


def judge(raw, row):
    resolved = resolve(raw, row["document"], row["units"])
    expected = json.loads(row["target"])
    try:
        value = json.loads(raw)
    except ValueError:
        value = {}
    valid = resolved["valid_format"] and resolved["reference_valid"]
    status_correct = valid and value["status"] == expected["status"]
    unit_correct = valid and value["unit"] == expected["unit"]
    return {**resolved, "status_correct": bool(status_correct), "unit_correct": bool(unit_correct),
            "exact_match": bool(status_correct and unit_correct)}
