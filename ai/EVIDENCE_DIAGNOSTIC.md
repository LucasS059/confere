# Diagnóstico de contexto e evidências - 05/11/2026

Sem treino novo. Checkpoint `document-long-contrasts-2026-11-04/best.pt`, mesmo
hash do piloto anterior, rede própria em MPS. As 57 consultas conhecidas foram
reconstruídas a partir das unidades e intervalos originais, com hashes dos
arquivos conferidos. As respostas completas anteriores foram reutilizadas.

Preparadas anotações locais por frases autorais exatas: status e referência
esperados para cada lote. É um controle deste piloto fictício, sem revisão
semântica independente ou uso de TCCs candidatos no treinamento.

Um lote de backup contém simultaneamente afirmação e negação em unidades
diferentes. Foi preservado no JSON, fora do acerto local dos outros 56 lotes.
O contrato atual de um único status/unit por lote não expressa as duas
evidências. Exigir detecção completa desse conflito com esse contrato é uma
limitação do pipeline, além das falhas do modelo. Conflitos entre lotes já são
tratados; múltiplas evidências dentro do mesmo lote continuam pendentes.

Ablação: manter requisito e aliases, substituir o texto relevante pela frase
autoral correta e os distratores por um registro curto de reunião. Esse
`oracle_short` usa acesso à resposta anotada e não é um mecanismo de busca.
Ele muda conteúdo e comprimento, portanto não isola apenas o efeito da janela.

| Condição | Status e unidade | Só lotes com evidência |
| --- | ---: | ---: |
| Contexto completo em cache | 36/56 | 0/2 |
| Controle curto com evidência conhecida | 55/56 | 1/2 |

Há apenas dois lotes relevantes fora do conflito; os demais 54 exigem
abstenção. O agregado não mede qualidade geral. Mesmo com a evidência correta
isolada, o caso de relatórios, esperado em `page:4`, recebeu insuficiência.
Logo reduzir contexto e fornecer a evidência não resolve todos os erros.
Nenhum resultado permite promover pesos ou afirmar interpretação confiável.

Próxima correção: representar todas as evidências relevantes de um lote,
inclusive opostas, mantendo as referências às fontes e a compatibilidade com
resultados anteriores. Depois avaliar seleção e classificação separadamente,
com casos autorais variados e evidências reais revisadas quando disponíveis.
Novos passos de treino só após definir o contrato e os alvos correspondentes.

Os 120 testes de software passaram. Teste reservado não consultado, pesos e
padrão do chat preservados, sem integração ao app. O [plano de modelo único](MODEL_PLAN.md)
para a apresentação continua vigente.

Artefatos: [JSON e anotações](../output/ai/evidence-context-diagnostic-2026-11-05.json)
e [relatório](../output/pdf/evaluation/evidence-context-diagnostic-2026-11-05.pdf).
O comando `ai/scripts/diagnose_evidence_context.py --help` informa os parâmetros;
saídas existentes são recusadas para preservar os resultados.
