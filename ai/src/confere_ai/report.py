"""Relatório PDF reprodutível a partir dos artefatos locais de uma execução."""

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from xml.sax.saxutils import escape

from reportlab.graphics.shapes import Drawing, Line, PolyLine, String
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_LEFT
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak


REPORTS = Path("output/pdf/training")


def read_json(path):
    return json.loads(path.read_text()) if path.exists() else None


def record_failure(run_dir, error):
    """Preserva checkpoints e distingue métricas registradas de passos perdidos."""
    import torch
    run_dir=Path(run_dir)
    metrics_path=run_dir/"metrics.jsonl"
    checkpoint_path=run_dir/"last.pt"
    if not (run_dir/"run.json").exists() or not metrics_path.exists() or not checkpoint_path.exists():
        return None
    failure_path=run_dir/"failure.json"
    if failure_path.exists():raise ValueError("Falha já registrada; evidência preservada.")
    checkpoint=torch.load(checkpoint_path,map_location="cpu",weights_only=True)
    step=checkpoint["step"]
    metrics=[json.loads(line) for line in metrics_path.read_text().splitlines() if line.strip()]
    recorded=[row for row in metrics if row["step"]<=step]
    if not recorded:return None
    failure=dict(error=str(error),recorded_at=datetime.now(timezone.utc).isoformat(),last_checkpoint_step=step,
                 scope="O total de passos executados após o último checkpoint não foi registrado. Tempos e loss abaixo cobrem somente os registros preservados.")
    failure_path.write_text(json.dumps(failure,ensure_ascii=False,indent=2)+"\n")
    summary_path=run_dir/"summary.json"
    if not summary_path.exists():
        summary_path.write_text(json.dumps(dict(start_step=recorded[0]["step"],final_step=step,
             elapsed_seconds=recorded[-1]["elapsed_seconds"],initial=recorded[0],final=recorded[-1],
             stop_reason="failure",measurement_scope="until_last_checkpoint_only"),indent=2)+"\n")
    return create_report(run_dir)


def save_samples(run_dir, model, tokenizer, device, prompts):
    import torch
    model.eval()
    rows = []
    for label, ids in prompts:
        limit = min(96, model.config.block_size - len(ids))
        if limit <= 0:
            continue
        generated = model.generate(torch.tensor([ids], device=device), limit, tokenizer.EOS)
        rows.append({"prompt": label, "continuation": tokenizer.decode(generated[0, len(ids):].tolist()),
                     "decoding": "greedy", "max_new_tokens": limit})
    (Path(run_dir) / "report-samples.json").write_text(json.dumps(rows, ensure_ascii=False, indent=2))


def create_report(run_dir, output=None):
    run_dir = Path(run_dir)
    info, summary = read_json(run_dir / "run.json"), read_json(run_dir / "summary.json")
    if not info or not summary:
        raise ValueError("Relatório exige run.json e summary.json de uma execução concluída.")
    metrics = [json.loads(line) for line in (run_dir / "metrics.jsonl").read_text().splitlines() if line.strip()]
    output = Path(output) if output else REPORTS / (run_dir.name + ".pdf")
    output.parent.mkdir(parents=True, exist_ok=True)
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle("SmallConfere", fontName="Helvetica", fontSize=9, leading=13, spaceAfter=7, alignment=TA_LEFT))
    styles["Title"].textColor = colors.HexColor("#102B46")
    styles["Heading2"].textColor = colors.HexColor("#176981")
    story = []
    def p(text, style="SmallConfere"):
        story.append(Paragraph(escape(str(text)).replace("\n", "<br/>"), styles[style]))
    def heading(text):
        p(text, "Heading2")
    def table(rows):
        data = [[Paragraph(escape(str(value)), styles["SmallConfere"]) for value in row] for row in rows]
        widget = Table(data, colWidths=[165, 340], hAlign="LEFT")
        widget.setStyle(TableStyle([("VALIGN", (0,0), (-1,-1), "TOP"), ("BACKGROUND", (0,0), (0,-1), colors.HexColor("#EDF3F7")), ("LINEBELOW", (0,0), (-1,-1), .4, colors.HexColor("#D5E0E8")), ("LEFTPADDING", (0,0), (-1,-1), 8), ("RIGHTPADDING", (0,0), (-1,-1), 8)]))
        story.append(widget)
    objective = info.get("objective", "supervised")
    config = info.get("config", info.get("model_config", {}))
    p("CONFERE | Treinamento local", "Title")
    p(run_dir.name, "Heading2")
    p("Relatório gerado em " + datetime.now(timezone.utc).strftime("%d/%m/%Y %H:%M UTC") + ". Fonte: artefatos da execução, sem inferência de resultados ausentes.")
    failure=read_json(run_dir/"failure.json")
    if failure:
        p("EXECUÇÃO INTERROMPIDA. " + failure["scope"])
        p("Erro registrado: " + failure["error"].split("Use PYTORCH")[0][:500])
    heading("1. Execução e dados")
    splits = info.get("document_splits") or {"train": len(info.get("train_ids", [])), "validation": len(info.get("validation_ids", []))}
    table([
        ("Objetivo", "Previsão do próximo token (português)" if objective == "causal_lm" else "Conversas com histórico; loss na resposta atual" if objective == "conversation" else "Instruções sintéticas; loss somente na resposta" if objective == "instruction" else "Supervisionado documental; loss somente na resposta"),
        ("Inicialização", info.get("initialization", "Não registrada") + "; origem: " + str(info.get("resume_from") or "pesos aleatórios")),
        ("Passos / duração do laço", f'{summary["start_step"]} a {summary["final_step"]} / {summary["elapsed_seconds"]:.1f}s'),
        ("Rede", f'{info["parameters"]:,} parâmetros; {config.get("layers")} blocos, largura {config.get("width")}, {config.get("heads")} cabeças'),
        ("Contexto / vocabulário", f'{config.get("block_size")} / {config.get("vocab_size")} tokens'),
        ("Dispositivo / ambiente", f'{info.get("device")} / Python {info.get("python")}, PyTorch {info.get("torch")}'),
        ("Dados / split", str(info.get("data")) + " | " + str(splits)),
        ("Batch / taxa / seed", " / ".join(str(info.get("settings", {}).get(key, "?")) for key in ("batch_size", "learning_rate", "seed"))),
        ("Tokens nesta rodada", str(summary.get("tokens_processed", summary.get("supervised_tokens_processed", "Não registrado"))) + " (inclui repetições)"),
        ("RSS máximo do processo", f'{summary["process_peak_rss_bytes"] / 1e6:.1f} MB' if summary.get("process_peak_rss_bytes") else "Não registrado"),
    ])
    p("SHA-256 dos dados: " + info.get("dataset_fingerprint", "Não registrado"))
    if info.get("context_note"):
        p("Adaptação de contexto: " + str(info.get("source_context")) + " para " + str(config.get("block_size")) + " tokens; passo de origem " + str(info.get("source_step")) + ". " + info["context_note"])
    if info.get("previous_dataset_fingerprint"):
        p("Corpus ampliado a partir de: " + info["previous_dataset_fingerprint"])
    heading("2. Evolução da perda")
    chart = Drawing(505, 155)
    losses = [row[key] for row in metrics for key in ("train_loss", "validation_loss") if row.get(key) is not None]
    ceiling = max(losses) * 1.1 or 1
    first, last = metrics[0]["step"], metrics[-1]["step"]
    for tick in range(5):
        value, y = ceiling * tick / 4, 25 + 105 * tick / 4
        chart.add(Line(35, y, 490, y, strokeColor=colors.HexColor("#DFE7ED")))
        label = f"{value:.3f}" if ceiling < .2 else f"{value:.2f}" if ceiling < 2 else f"{value:.1f}"
        chart.add(String(0, y-3, label, fontSize=8))
    for key, color, label, x in (("train_loss", "#176981", "Treino", 35), ("validation_loss", "#C36C13", "Validação", 150)):
        points = []
        for row in metrics:
            if row.get(key) is not None:
                points.extend([35 + (row["step"]-first)/max(last-first, 1)*455, 25+row[key]/ceiling*105])
        if len(points) >= 4:
            chart.add(PolyLine(points, strokeColor=colors.HexColor(color), strokeWidth=1.8))
        chart.add(String(x, 145, label, fontSize=9, fillColor=colors.HexColor(color)))
    chart.add(String(35, 8, str(first), fontSize=8))
    chart.add(String(440, 8, f"{last} passos", fontSize=8))
    story.append(chart)
    p("Perda em nats por token; menor é melhor. Curvas não medem acurácia factual ou capacidade de conferir projetos.")
    story.append(PageBreak())
    heading("3. Resultados e amostras")
    table([("Perda", "Inicial / final"), ("Treino", f'{metrics[0]["train_loss"]:.4f} / {metrics[-1]["train_loss"]:.4f}'), ("Validação", f'{metrics[0]["validation_loss"]:.4f} / {metrics[-1]["validation_loss"]:.4f}')])
    p("Avaliação durante treino: " + (f'{info.get("evaluation_windows_per_split")} janelas fixas por split.' if objective == "causal_lm" else "exemplos autorais de treino e validação; projetos separados."))
    if objective=="conversation":
        p("Loss usa histórico de referência. Na avaliação gerativa, a resposta do modelo entra nos próximos turnos da conversa. Alguns casos de reparo recebem histórico artificialmente incorreto como contexto; esse erro anterior não é alvo da loss. As expansões também variam o contexto de treino.")
        manifest=read_json(Path(info["data"]).parent/"manifest.json")
        if manifest:
            p("Fonte humana: " + manifest["source"] + ", Apache-2.0, revisão " + manifest["revision"] + ". Mensagens pt-BR na fonte: " + str(manifest["source_pt_messages"]) + "; respostas aproveitadas: treino " + str(manifest["filters"].get("human_train",0)) + ", validação " + str(manifest["filters"].get("human_validation",0)) + ", teste " + str(manifest["filters"].get("human_test",0)) + ". A mistura é majoritariamente sintética.")
            if manifest.get("additional_source"):
                public_source=manifest["additional_source"]
                p("Fonte pública adicional: " + public_source["source"] + ", " + public_source["license"] + ", revisão " + public_source["revision"] + ". Respostas geradas por modelos, sem anotação humana; " + str(public_source["counts"].get("public_train_added",0)) + " caminhos de treino incluídos. Validação e teste públicos permanecem em arquivo reservado separado, fora desta execução.")
                if "public_examples_processed" in summary:
                    p(f'Lotes públicos esperados: {info["settings"].get("public_fraction",0)}; processados {summary["public_examples_processed"]} exemplos e {summary["public_tokens_processed"]} tokens-alvo, com repetição. Os dados públicos não são respostas programadas na inferência nem pesos pré-treinados importados.')
                else:
                    p(f'Lotes públicos esperados: {info["settings"].get("public_fraction",0)}. Contadores de exemplos e tokens processados não foram preservados na execução interrompida.')
        if info.get("paired_evaluation_context"):
            p(f'Comparação gerativa: janela comum {info["paired_evaluation_context"]}, saída {info["paired_evaluation_response_tokens"]} tokens. O candidato usa contexto nativo {config["block_size"]}; orçamento da TUI {info["settings"].get("generation_budget",64)}. Casos humanos longos não entram no acerto exato pareado.')
        if summary.get("human_examples_processed"):
            p(f'Amostragem humana em lotes homogêneos: fração esperada {info["settings"].get("human_fraction")}; {summary["human_examples_processed"]} exemplos processados com repetição, {summary["human_tokens_processed"]} tokens-alvo humanos. Validação humana de loss: {info.get("human_validation_loss_examples",0)} exemplos, insuficiente para qualidade geral.')
        if "human_validation_loss" in summary.get("initial", {}):
            p(f'Loss humana de referência: inicial {summary["initial"]["human_validation_loss"]:.4f}; final {summary["final"]["human_validation_loss"]:.4f}. A loss agregada dominada por templates não comprova melhora no diálogo humano.')
    instruction = read_json(run_dir / "instruction-evaluation.json")
    social_report=bool(instruction and (instruction.get("cohort_comparison") or instruction.get("curriculum_gate")))
    if instruction:
        p(f'Validação sintética, acerto exato: referência {instruction["baseline"]["correct"]}/{instruction["baseline"]["total"]}; checkpoint SFT selecionado no passo {instruction["selected_step"]}: {instruction["selected"]["correct"]}/{instruction["selected"]["total"]}. Critério: {instruction["selected"]["criterion"]}')
        if instruction.get("selection_policy"):
            p("Seleção do checkpoint: " + instruction["selection_policy"])
        if instruction.get("cohort_comparison"):
            for phase,label in (("baseline","Referência"),("selected","Candidato")):
                cohort=instruction["cohort_comparison"][phase]
                p(f'{label}: conjunto anterior {cohort["shared_correct"]}/{cohort["shared_total"]}; casos novos {cohort["new_correct"]}/{cohort["new_total"]}; resposta ao elogio {cohort["praise_correct"]}/{cohort["praise_total"]}.')
        if instruction.get("adoption_decision"):
            p("Decisão experimental: " + instruction["adoption_decision"])
        candidates = read_json(run_dir / "adoption-candidates.json")
        if candidates:
            final_candidate = candidates[-1]
            counts = {}
            for sample in final_candidate["result"]["samples"]:
                pair = counts.setdefault(sample["task"], [0, 0])
                pair[0] += sample["exact_match"]; pair[1] += 1
            failed = "; ".join(f"{task}: {correct}/{total}" for task, (correct, total) in counts.items() if correct/total < .8)
            p(f'Candidato final, passo {final_candidate["step"]}: {final_candidate["result"]["correct"]}/{final_candidate["result"]["total"]}. Famílias abaixo de 80%: ' + (failed or "nenhuma") + ".")
        if instruction.get("curriculum_gate"):
            gate=instruction["curriculum_gate"]
            for phase,label in (("baseline","Referência"),("selected","Candidato")):
                cohort=gate[phase]
                p(f'{label}: retenção dos casos anteriores {cohort["old_correct"]}/{cohort["old_total"]}; currículo novo {cohort["new_correct"]}/{cohort["new_total"]}.')
            p(f'Regressões conhecidas com contexto nativo e histórico gerado: checkpoint selecionado {gate["known_regressions_correct"]}/6; checkpoint final {gate["final_regressions_correct"]}/6. Exigência: 6/6, sem queda agregada nos casos anteriores e pelo menos 80% em cada família de conversa. Resultado: ' + ("atingido." if gate["passed"] else "não atingido."))
        if info.get("baseline_checkpoint"):
            sampling=info.get("train_evaluation_policy","primeiros exemplos, não necessariamente representativos da mistura")
            p("Referência comparativa: " + info["baseline_checkpoint"] + ". Loss de treino em " + str(info.get("train_evaluation_examples")) + " exemplos (" + sampling + "); validação em todo o split.")
            counts = {}
            for sample in instruction["selected"]["samples"]:
                pair = counts.setdefault(sample["task"], [0, 0])
                pair[0] += sample["exact_match"]; pair[1] += 1
            p("Acertos por tarefa: " + "; ".join(f"{task}: {pair[0]}/{pair[1]}" for task, pair in counts.items()) + ".")
        if instruction.get("acceptance"):
            description = instruction["acceptance"].get("description", "Ao menos 80% em cada tarefa crítica: cópia, código, prazo/ausência e falta de contexto.")
            p("Critério exploratório: " + description + " Resultado: " + ("atingido" if instruction["acceptance"]["passed"] else "não atingido") + ". Não é aprovação de uso em documentos completos.")
        grounded = [s for s in instruction["selected"]["samples"] if s["task"].startswith("grounded_")]
        if grounded:
            p(f'Documentos sintéticos ({len(grounded)} casos): formato válido {sum(s["valid_format"] for s in grounded)}; referência válida {sum(s["reference_valid"] for s in grounded)}; status correto {sum(s["status_correct"] for s in grounded)}; status e unidade corretos {sum(s["exact_match"] for s in grounded)}. A citação é recuperada da fonte; isso não prova suporte semântico fora dos rótulos controlados.')
            replay = [s for s in instruction["selected"]["samples"] if not s["task"].startswith("grounded_")]
            p(f'Replay de tarefas anteriores: {sum(s["exact_match"] for s in replay)}/{len(replay)} acertos. O total agregado mistura tarefas distintas e não é acurácia de conferência real.')
    comparison = read_json(run_dir / "comparison.json")
    if comparison:
        for item in comparison["results"]:
            p(f'Avaliação completa: passo {item["step"]}, perda {item["validation_loss"]:.4f}, {item["validation_windows"]} janelas e {item["validation_tokens"]} tokens-alvo.')
    samples = read_json(run_dir / "report-samples.json") or read_json(run_dir / "samples.json") or []
    if not samples:
        for name in ("sample-train.json", "sample-validation.json"):
            item = read_json(run_dir / name)
            if item:
                samples.append({"prompt": str(item.get("id")) + " | split=" + str(item.get("split")), "continuation": item.get("text", ""), "inspection": f'JSON válido: {item.get("valid_json", "não registrado")}; schema válido: {item.get("valid_response_schema", "não registrado")}.'})
    if comparison:
        current = next((item for item in comparison["results"] if Path(item["checkpoint"]).parent == run_dir), None)
        if current:
            samples = current["samples"]
    for sample in ([] if social_report else samples[:3]):
        label = sample.get("prompt", sample.get("prefix", "Não registrada"))
        if objective == "document_grounding":
            label = next((line for line in label.splitlines() if line.startswith("Requisito:")), label)
        p("Entrada: " + label, "Heading3")
        text = sample.get("continuation", "")
        p(text[:550] + (" [trecho abreviado no PDF]" if len(text) > 550 else ""))
        if sample.get("inspection"):
            p(sample["inspection"])
        if objective == "document_grounding" and instruction:
            item = next((s for s in instruction["selected"]["samples"] if s["prompt"] == sample.get("prompt")), None)
            if item:
                for evidence in item["result"]["evidence"]:
                    p("Citação recuperada (" + evidence["unit"] + "): " + evidence["quote"])
    if not samples:
        p("Não há amostras de geração registradas para esta execução. Nenhuma foi reconstruída retroativamente.")
    if social_report:
        p("A sequência gerada na interface está na seção 5. As respostas completas da validação estão no JSON de avaliação da execução.")
        story.append(PageBreak())
    heading("4. Interpretação e limites")
    if objective == "causal_lm":
        p("Corpus enciclopédico limitado, com atribuição/licenças em manifesto local. BPE próprio e pesos originados do zero. Sem treino de diálogo nesta etapa. Saídas experimentais podem repetir, inventar fatos e não seguir instruções. Teste não usado nas métricas; validação consultada repetidamente, sem caráter de teste final cego.")
    elif objective=="conversation":
        p(f'Piloto de conversas e respostas humanas limitadas pelo contexto. Templates do assistente, sem revisão humana local. Repetições de prefixos no treino são intencionais; conversas e árvores humanas não atravessam splits. Acerto exato penaliza paráfrases válidas e não mede inteligência geral. Validação seleciona pesos; não é teste cego. Janela nativa {config["block_size"]}, orçamento de geração {info["settings"].get("generation_budget",64)} tokens. O modelo pode esquecer, inventar ou responder fora do pedido.')
    elif objective in {"instruction", "document_grounding"}:
        p("Piloto de instruções sintéticas construídas por templates do assistente, sem revisão humana. Inicializa dos pesos locais pré-treinados, com novo otimizador. Projetos/IDs de validação não são usados no gradiente; tarefas e respostas constantes podem se repetir entre splits. Acerto exato neste conjunto pequeno não demonstra compreensão geral nem eliminação de alucinações. A validação também seleciona o checkpoint; não é teste cego.")
        if objective == "document_grounding":
            p("A rede gera status e ponteiro, não a citação. O programa copia o texto da unidade existente e rejeita referência inválida. A unidade pode ser real e ainda assim não sustentar semanticamente a conclusão. O corpus só exercita unidades page:N e contextos curtos; DOCX, tabelas, imagens e documentos longos não foram validados como capacidade do modelo.")
    else:
        p("Corpus mínimo autoral. Este experimento verifica a infraestrutura e pode memorizar respostas. JSON válido não comprova evidência correta. Não há validação de conversa geral ou análise confiável de anexos completos.")
    p("Não foram usados TCCs candidatos nesta execução. Não há avaliação de notas de apresentação, uso com simulador aberto ou confiabilidade de documentos completos. Tempos referem-se ao laço e incluem avaliação; preparação é separada. Métricas de memória não representam toda a memória do Mac.")
    p("Rastreabilidade: run.json, summary.json, metrics.jsonl e amostras/comparison.json quando presentes, na pasta " + str(run_dir) + ".")
    tui = read_json(run_dir / "tui-smoke.json")
    if tui:
        p(f'Verificação integrada: piloto headless do Textual com modelo real em {tui["device"]}, passo {tui["step"]}; {len(tui["messages"])} envios conferidos. Contexto {tui["context"]}, geração {tui["generation_budget"]}.')
    regressions=read_json(run_dir/"interactive-regressions.json")
    if objective=="conversation" and regressions:
        if not social_report: story.append(PageBreak())
        heading("5. Regressões de conversa observadas na interface")
        p("Prompts derivados das falhas relatadas pelo usuário; não são um benchmark cego. Respostas geradas sem edição, mantendo histórico da própria rede até a limpeza da sessão.")
        for item in regressions:
            p("Você: " + item["prompt"],"Heading3")
            p("Modelo: " + (item["answer"] or "[sem texto]"))
        p("O ganho em templates não comprova linguagem geral, cumprimento de pedidos compostos ou memória confiável para nomes novos. Não houve aprovação de uso como assistente geral.")
    if objective == "document_grounding" and instruction:
        failures = [s for s in instruction["selected"]["samples"] if s["task"].startswith("grounded_") and not s["exact_match"]]
        if failures:
            story.append(PageBreak())
            heading("5. Falhas documentais observadas")
            p(f'{len(failures)} casos não acertaram status e unidade em conjunto. Abaixo, exemplos sem correção editorial; textos diferentes do mesmo padrão podem aparecer em outros casos do JSON.')
            seen = set()
            for item in failures:
                requirement = next((line for line in item["prompt"].splitlines() if line.startswith("Requisito:")), item["id"])
                if requirement in seen: continue
                seen.add(requirement)
                p(requirement, "Heading3")
                p(item["prompt"])
                p("Saída: " + item["actual"] + "\nAlvo controlado: " + item["expected"])
                for evidence in item["result"]["evidence"]:
                    p("Trecho selecionado: " + evidence["quote"])
                if len(seen) >= 3: break
            p("Uma citação pode ser literalmente fiel ao arquivo e, ainda assim, irrelevante para o requisito. Esta camada de referência não elimina erros de interpretação.")
    flow = read_json(run_dir / "flow-evaluation.json")
    if flow:
        if regressions:
            story.append(PageBreak())
        heading(("6" if regressions else "5") + ". Diálogos completos com histórico nativo")
        p(flow["policy"])
        p("Janela 1024 e saída até 256 tokens; cada resposta gerada entra no próximo turno. Os cenários são autorais, sem revisão humana independente. O acerto exato não mede conversa aberta. As mesmas situações e respostas podem aparecer com outras palavras no treino.")
        def describe_flow(label, result):
            groups = {}
            for sample in result["samples"]:
                groups.setdefault(sample["project_id"], []).append(sample)
            complete = sum(all(s["exact_match"] for s in group) for group in groups.values())
            p(f'{label}: turnos {result["correct"]}/{result["total"]}; conversas inteiras {complete}/{len(groups)}; turnos descartados {sum(s["dropped_turns"] for s in result["samples"])}.')
        describe_flow("Referência", flow["baseline_flow"])
        if flow.get("baseline_public_loss") is not None:
            p(f'Validação pública separada: {len(flow["public_validation_ids"])} caminhos, um por conversa, sem contexto exato repetido no treino público. Loss da referência {flow["baseline_public_loss"]:.4f}; histórico de referência. Essa loss não participa da decisão de adoção e não é avaliação humana de qualidade.')
        for candidate in flow["candidates"]:
            describe_flow("Candidato passo " + str(candidate["step"]), candidate["flow"])
            p(f'Retenção legada na janela comum 256: {candidate["legacy"]["correct"]}/{candidate["legacy"]["total"]}; regressões conhecidas {sum(r["exact_match"] for r in candidate["known"])}/6; critério de validação ' + ("atingido." if candidate["passed"] else "não atingido."))
            if candidate.get("public_validation_loss") is not None:
                p(f'Loss nos mesmos caminhos públicos reservados de validação: {candidate["public_validation_loss"]:.4f}.')
        if flow["test"]:
            describe_flow("Teste reservado, consultado após a seleção", flow["test"])
        else:
            p("Teste reservado não consultado: nenhum candidato passou na validação ampliada.")
        p("Adoção: " + ("aprovada no conjunto autoral ampliado." if flow["adopted"] else "reprovada; TUI preservada."))
        failures=[s for s in flow["candidates"][-1]["flow"]["samples"] if not s["exact_match"] and len(s["actual"])<=250]
        shown=set()
        for sample in failures:
            key=(sample["prompt"],sample["actual"])
            if key in shown:continue
            shown.add(key)
            p("Você: " + sample["prompt"], "Heading3")
            p("Modelo: " + (sample["actual"] or "[sem texto]"))
            p("Alvo autoral: " + sample["expected"])
            if len(shown)==2:break
        p("Os históricos completos, respostas, famílias e falhas de cada candidato estão em flow-evaluation.json. Teste consultado não deve virar fonte de ajuste numa repetição desta avaliação.")
    def footer(canvas, doc):
        canvas.setFont("Helvetica", 8)
        canvas.setFillColor(colors.HexColor("#526777"))
        canvas.drawString(45, 24, "Confere | Pesquisa experimental | " + run_dir.name)
        canvas.drawRightString(550, 24, str(doc.page))
    temporary = output.with_suffix(".tmp.pdf")
    SimpleDocTemplate(str(temporary), pagesize=(595.28, 841.89), rightMargin=45, leftMargin=45,
                      topMargin=35, bottomMargin=40, title="Confere - " + run_dir.name,
                      author="Confere").build(story, onFirstPage=footer, onLaterPages=footer)
    temporary.replace(output)
    return output


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("run_dir", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    print(create_report(args.run_dir, args.output))


if __name__ == "__main__":
    main()
