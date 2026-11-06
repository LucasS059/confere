# Português informal

Esta etapa adapta o GPT próprio a abreviações e perguntas de continuidade.
Continua a cadeia de pesos treinados localmente, sem modelo pré-treinado externo.
O texto enviado à CLI não é reescrito e as respostas não são substituídas.

`scripts/prepare_informal_dialogues.py` aplica variações somente às entradas de
treino autorais: vc/cê, oq/o q, pq, n/nao, tb/tbm, pfv, msm, to/tô, ta/tá,
obg/vlw. Preserva respostas e exclui tarefas de memória de nomes da transformação
para não remover acentos de um nome enquanto mantém outro nome no alvo.
Também acrescenta diálogos com identidade, função, tipos de projetos,
cumprimentos, elogios e ausência de projeto. Os casos relatados pelo usuário
entram no treino e no diagnóstico conhecido; não são um teste cego.

Snapshot utilizado: `data/private/conversation-informal-safe-2026-11-03`.
São 202.110 linhas de treino, 873 de validação e 741 de teste. Acréscimo de
28.588 linhas ao corpus anterior, incluindo as novas linhas reservadas.
SHA-256: `0a3b98cc2780764c526d3fd42cc71e155fef52dc64c6d8b411fc961bcbe4afd3`.
Um snapshot preliminar, sem a exclusão de tarefas de memória, foi preservado
localmente e não foi utilizado no treinamento.

## Protocolo

O avaliador `scripts/evaluate_informal_dialogues.py` separa três coortes:

- 144 turnos em 24 diálogos informais, com formulações reservadas;
- 192 turnos dos diálogos completos da etapa anterior;
- 535 casos legados, sem somar os casos novos à retenção antiga.

Os diálogos nativos usam janela 1.024 e saída até 256 tokens; cada resposta
gerada entra no histórico seguinte. A retenção legada mantém janela 256 e
saída 64 para conservar a comparação anterior. A validação exige 80% em
cada família, 50% de conversas inteiramente corretas e nenhum descarte de
turnos nas duas primeiras coortes. O legado deve atingir pelo menos 514/535,
sem queda ante a referência, e 80% por família.

O primeiro candidato entre best e last que cumprir o conjunto é selecionado
para consultar uma única vez os 144 turnos informais de teste reservado.
As formulações reservadas compartilham intenções, respostas e receitas de
diálogo com o treino; não são 24 situações semanticamente independentes.
A validação informal contém 12 prompts distintos e 90 contextos de referência
distintos nos 144 turnos; repetições continuam visíveis no relatório.
Acerto exato em respostas autorais não mede conversa aberta e pode penalizar
paráfrases válidas. O diagnóstico conhecido registra texto bruto sem nota.

## Execução

`conversation-informal-2026-11-03` inicializa do último checkpoint de
`conversation-flow-restarts-2026-11-02` (passo 2.000), com novo otimizador.
Configuração: MPS, batch 2, taxa 0,00002, até 4.000 atualizações ou 480 segundos
no laço. Preparação e avaliação final não fazem parte desse limite. Amostragem
por batch: 1% humano OpenAssistant, 3% público gerado por modelos Aira,
96% autoral. Os conjuntos públicos reservados permanecem separados.

Foram concluídas 4.000 atualizações em 248,3 segundos de laço, com 177.421
tokens-alvo processados, incluindo repetições. O melhor por loss foi o passo
3.000; o checkpoint final do passo 4.000 ficou melhor na avaliação informal.

| Coorte | Referência | Melhor por loss (3.000) | Final (4.000) |
| --- | ---: | ---: | ---: |
| Informal, turnos | 36/144 | 93/144 | 97/144 |
| Informal, conversas completas | 0/24 | 3/24 | 4/24 |
| Fluxo anterior, turnos | 178/192 | 178/192 | 184/192 |
| Fluxo anterior, conversas completas | 18/24 | 12/24 | 16/24 |
| Retenção legada | 501/535 | 481/535 | 498/535 |

Nenhum turno foi descartado. O final atingiu o critério nas famílias do fluxo
anterior, mas não nas famílias informais nem na retenção legada. Ambos os
candidatos foram reprovados no conjunto; o teste reservado não foi consultado.
O padrão da TUI permanece `conversation-identity-2026-11-02/last.pt`.

Na sequência conhecida das capturas, o final respondeu à função em
“e oq vc faz?” e ao escopo em “que tipo de projetos?”. Ainda confundiu
“e o que voce faz?” com identidade, não entendeu o elogio “boa muleke” e
produziu uma frase malformada ao pedido de amizade. Esses casos mostram
dependência do contexto e generalização incompleta, mesmo em formas próximas.

Verificação integrada: 10 envios no piloto headless do Textual com os pesos
reais em MPS, sem alterar entradas ou respostas, conferidos contra a execução
direta. Os 86 testes de software passaram. Isso valida o transporte e o
pipeline; não aprova conversa aberta nem processamento de anexos completos.
Relatório: `../output/pdf/training/conversation-informal-2026-11-03.pdf`.

Para experimentar explicitamente o checkpoint final:

```sh
bun run ai:chat ai/runs/conversation-informal-2026-11-03/last.pt
```

Para reproduzir a avaliação em uma nova execução, após o treinamento:

```sh
ai/.venv/bin/python ai/scripts/evaluate_informal_dialogues.py ai/runs/NOVA-EXECUCAO
```

O avaliador rejeita sobrescrita de uma avaliação já registrada, preservando
a seleção e o eventual teste reservado. Os pesos e dados privados permanecem
locais; o PDF e os scripts ficam versionados na branch `ai/primeiro-modelo`.
