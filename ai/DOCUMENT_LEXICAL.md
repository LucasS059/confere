# Iterações lexicais - 03/11/2026

Meta solicitada: buscar 100% nos casos controlados, preservando conversa.
Essa meta não equivale a perfeição em documentos reais ou conversa aberta.
Protocolo: duas iterações com taxas 0,00002 e 0,00001, até 4.000 atualizações
cada, batch 2, MPS, contexto 1.024, orçamento conversacional 256. Cada uma
inicializa no melhor checkpoint da anterior, com novo otimizador. A primeira
parte de `document-contrasts-2026-11-03/best.pt`. A referência comparativa fixa
é `conversation-informal-2026-11-03/last.pt`.

Dados `data/private/document-lexical-2026-11-03/examples.jsonl`, SHA-256
`49a6e5bc41420fb105a857ca80a7549952587b5abba659b18e239cf17b7f86c8`:
3.000 casos documentais de treino e 11.186 turnos de conversa estratificados
por família, preservando todos os turnos disponíveis dos grupos escolhidos e
seus históricos. Casos de treino incluem presença/ausência,
existência/inexistência, suporte/falta de suporte e previsão/exclusão.
Validação e teste são idênticos aos snapshots anteriores; só o treino mudou.
As redações e respostas reservadas já influenciaram decisões de projeto via
validação, portanto os resultados não são uma estimativa cega de generalização.

Cada execução mantém pesos, métricas e PDF próprios. Seleção pelo menor valor
de loss misturada, sem descartar candidatos ou ajustar rótulos depois dos
resultados. Na avaliação suplementar, `--perfect-documents` exige 100% de
status/unidade em cada família documental e 100% de formato/referências. A
retenção conversacional mantém 80% por família e nenhuma queda por família ou
no total ante a referência, na comparação pareada 1.024/64. O diagnóstico
nativo usa 1.024/256; não substitui a comparação pareada. Teste somente após
ambos os critérios, sem transformá-lo em dados de ajuste. Nenhum resultado
substitui automaticamente o padrão da TUI.

## Ampliação do protocolo após a primeira avaliação

A primeira iteração acertou 26/60 negações, com forte dependência da posição:
page:1 1/17, page:2 6/17, page:3 9/9, page:4 10/17. Isso motivou uma terceira
iteração com pares mínimos, sem modificar as linhas de validação ou teste.
Para o mesmo cenário e posição, o treino contém presença, ausência e falta de
evidência. São 6.000 documentos de treino e os mesmos 11.186 turnos de replay.
Snapshot `data/private/document-paired-2026-11-03/examples.jsonl`, SHA-256
`698934ad93ea750ae27214217eb222a1e72e3dee5d29370e4c106f88fb72872f`.
O terceiro treino parte do melhor checkpoint do segundo, com novo otimizador,
taxa 0,00001 e até 4.000 passos. É uma adaptação informada pela validação, não
uma confirmação independente do resultado.

Também foi acrescentado diagnóstico exploratório dos documentos de validação
do checkpoint final de cada execução, para observar a diferença entre ele e
o selecionado por loss. Não altera a seleção registrada, não consulta teste e
não valida retenção completa de conversa do checkpoint final.

## Resultados das duas primeiras iterações

| Execução | Passo selecionado | Documentos | Negação | Conversa pareada |
| --- | ---: | ---: | ---: | ---: |
| Lexical | 1.000 | 146/180 | 26/60 | 790/871 |
| Refinamento lexical | 4.000 | 151/180 | 31/60 | 798/871 |

Ambas concluíram 4.000 atualizações. Formato e referências foram válidos em
180/180; presença e evidência insuficiente acertaram 60/60 em cada execução.
Ambas reprovaram a meta documental e o critério de retenção por família. A
referência informal acertou 779/871, mas o agregado não apaga as regressões:
no refinamento, saudação informal 14/24 e função informal 14/24, por exemplo.
Teste não consultado e padrão da TUI preservado.

O diagnóstico documental do checkpoint final da primeira execução fez
137/180 (17/60 negações), pior que o selecionado; no refinamento o final é o
próprio selecionado, 151/180. Esse diagnóstico não foi usado para trocar
retrospectivamente a seleção. Ambos os PDFs foram renderizados e inspecionados.

## Terceira iteração: perfeição documental controlada, conversa pendente

Concluiu 4.000 atualizações em 194,3 segundos de laço. A menor loss foi a do
estado herdado, passo 0: 151/180 documentos e 798/871 conversas, iguais ao
checkpoint de origem. Esse resultado é preservado como seleção por loss;
não se afirma que a terceira execução melhorou o checkpoint selecionado.

No diagnóstico exploratório do final, passo 4.000, atingiu 180/180 documentos:
60/60 presença, 60/60 ausência e 60/60 evidência insuficiente, com 180/180
formatos e referências válidos. Essa é a primeira execução que atingiu 100%
nesses casos de validação documentais. Não é teste cego nem prova em TCC real.

Por isso foi aberta uma avaliação exploratória separada da conversa do final,
no mesmo contexto e orçamento pareados: 775/871, ante 779/871 na referência.
Função informal 12/24, saudação informal 13/24, bem-estar 37/48 e outras
famílias ficaram abaixo de 80%. O ganho documental não preservou toda a
conversa. O teste reservado não foi consultado; o padrão da TUI não mudou.
O protocolo de seleção não foi reescrito para adotar o resultado exploratório.

Pilotos headless Textual com os pesos reais em MPS conferiram dez mensagens
do selecionado e dez do final, cada uma contra a geração direta correspondente.
Isso confirma o transporte das respostas, não sua correção semântica. Os
95 testes de software passaram. Os três PDFs foram renderizados e inspecionados.

Artefatos detalhados da terceira: `contrast-evaluation.json` (selecionado),
`last-document-diagnostic.json`, `final-conversation-validation.json`,
`tui-smoke.json` e `tui-smoke-final.json` na pasta local da execução. Cada
execução mantém seu PDF em `../output/pdf/training/` com o nome da execução.

Para experimentar o final explicitamente, sem alterar o padrão:

```sh
bun run ai:chat ai/runs/document-paired-2026-11-03/last.pt
```

Próximo problema a resolver: preservar a conversa enquanto se mantém o domínio
dos contrastes documentais. O resultado atual é parcial: a meta documental
controlada foi atingida no final; a meta conjunta permanece aberta.
