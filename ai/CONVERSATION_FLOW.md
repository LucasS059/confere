# Conversas completas após o feedback de 15h30

O currículo anterior passou em tarefas curtas, mas as capturas mostraram falhas
em paráfrases, negação, retomada de assunto e recuperação de erros. A etapa de
conversa foi reaberta; os 514/535 anteriores não representam conversa normal.
O padrão continua em `conversation-identity-2026-11-02/last.pt` até um candidato
passar na avaliação ampliada e na revisão das sequências relatadas.

## Dados

`build_conversation_flow.py` preserva todos os exemplos anteriores e acrescenta
3.600 conversas de oito turnos ao treino, 24 à validação e 24 ao teste reservado.
São diálogos autorais por cenários, sem revisão humana. A mistura continua com
somente 73 exemplos humanos de treino, dois de validação e sete de teste.
Não foram baixados pesos externos nem usados TCCs.

Os cenários exercitam acolher uma resposta social, reformular uma pergunta de
identidade, aceitar ausência de projeto, corrigir presença/ausência de projeto,
mudar de assunto, recordar um assunto já escolhido e encerrar a conversa.
Negação e informação atualizada são alvos explícitos. Perguntas, contextos e
identificadores são separados por split; o mesmo modelo de cenário e respostas
curtas podem se repetir com outras palavras. Isso limita a independência.

Snapshot `conversation-flow-1024`: 65.923 treino, 729 validação e 597 teste.
SHA-256 `164c36fa7eac863bab8c08c6aff4d0c2b4b81cd2f03a61b7ed14639aec17500f`.
Os exemplos anteriores mantêm os splits. Não há truncamento silencioso no treino.

## Avaliação definida antes dos resultados

O treino registra a comparação pareada na janela de 1.024, saída 64, para seus
727 exemplos sintéticos de validação. A decisão de adoção usa uma avaliação
separada com limites equivalentes à TUI:

- Novos diálogos: janela 1.024, saída 256, respostas geradas no histórico;
  pelo menos 80% em cada família e 50% de conversas inteiras corretas, sem
  descarte de turnos. Uma única falha torna a conversa inteira incorreta.
- Retenção: os mesmos 535 exemplos anteriores, janela 256 e saída 64;
  nenhuma queda agregada ante o checkpoint atual e 80% por família legada.
- Seis regressões anteriores corretas com contexto nativo.
- Melhor por loss e final avaliados na mesma validação. O primeiro que passar
  é selecionado; então o teste reservado é consultado uma vez com os mesmos
  limites por família e conversa. O teste não é usado para ajustar o modelo.
- A sequência nova das capturas é reproduzida sem respostas programadas,
  para revisão qualitativa antes de alterar a TUI.

Igualdade exata penaliza paráfrases válidas. O critério controla consistência
dentro de cenários autorais e não comprova qualidade de conversa aberta.
`flow-evaluation.json` mantém respostas, histórico realmente usado, famílias,
conversas completas e decisão. Cada execução tem seu próprio PDF, inclusive
se reprovada. `evaluate_flow_captures.py` preserva saídas anteriores e não
atribui nota automática a mensagens ambíguas.

## Primeiras execuções

`conversation-flow-2026-11-02`: interrompida pelo limite de 600s no passo 3.149.
Melhor por loss no passo 3.000. Na avaliação nativa: referência 27/192 turnos,
candidato 114/192; ambos 0/24 conversas completas. Retenção 511/535, abaixo dos
514/535 atuais. Melhor e final reprovados; teste reservado não consultado.

`conversation-flow-expanded-2026-11-02`: ampliou somente o treino com outras
formas de dizer as mesmas intenções e reparos autorais. Validação e teste são
idênticos ao snapshot anterior. Corpus: 98.923 treino, 729 validação, 597 teste;
SHA-256 `2e6cb71e79a4d5b254199a5fde0169d855d9e81d14d0a336c9b1849de5b2feed`.
Final e melhor no passo 3.760, após limite de tempo. Foram 177/192 turnos e
15/24 conversas completas, sem truncamento. Retenção caiu para 510/535 e
saudações ficaram em 3/16. Reprovado; teste reservado permanece fechado.

As saudações erradas incluem encerrar diante de “olá de novo” e inventar um
assunto diante de “oi, bora conversar um pouco”. Não são apenas paráfrases
válidas penalizadas pela métrica. A reprodução das capturas ainda perdeu
coerência nos turnos finais. Os candidatos não substituem o padrão da TUI.

## Fonte pública adicional

Foi consultado o [card primário do Instruct-Aira v3](https://huggingface.co/datasets/nicholasKluge/instruct-aira-dataset-v3).
O card informa português/inglês, Apache-2.0 e respostas geradas por modelos,
sem anotação humana. O arquivo português tem 50.000 conversas. Snapshot local
`aira-v3-pt`, revisão `1ca52371453cc9e52b650ba4314f2ca0a69f58ba`, SHA-256 do Parquet
`fc43d5033a3f00740eb595cceeb633562b0d593d8a8eff42117fda52825c162a`.
README e LICENSE originais foram preservados; nenhum peso externo foi baixado.

A auditoria de comprimento encontrou 14.753 caminhos de treino que cabem em
contexto 1.024/saída 256, dos quais 7.977 têm histórico anterior; 890 caminhos
de validação e 806 de teste também cabem. Isso não é aprovação de qualidade.
Conversa inteira normalizada recebe split por hash antes do filtro de tamanho.

`prepare_public_conversations.py` acrescenta somente caminhos públicos de
treino, depois de excluir identidades de outros assistentes, tamanho excedente
e contextos duplicados. Caminhos públicos de validação/teste ficam separados.
A proveniência `public_model_generated` não é contada como humana. O leitor
Parquet é opcional em `requirements-data.lock`; foi usado isoladamente para
preservar as dependências da inferência. O corpus mistura também replay autoral
legado e retomadas/reparos em posições variadas, inclusive casos conhecidos.

O corpus público preparado tem 153.810 exemplos de treino e preserva os
729/597 de validação/teste autorais. SHA-256:
`a9cfdfcbefe403d21a16acb10d6e4a88b5f9386c79cebf69ddb2d00cec49de99`.
Foram acrescentados 14.751 caminhos públicos de treino, 37.050 cópias autorais
para retenção e 3.086 variantes de contexto. A amostra de 16 exemplos revisada
pelo assistente inclui diálogos variados, respostas formais e limitações dos
modelos de origem; não é revisão humana nem validação factual do corpus.

`conversation-flow-public-2026-11-02` sofreu falta de memória MPS com batch 8.
O checkpoint 1.000 foi preservado. Passos executados depois dele e contadores
de tokens não ficaram registrados; o relatório distingue essas ausências e não
reconstrói resultados. Nenhum limite de memória foi removido.

`conversation-flow-public-smallbatch-2026-11-02` inicializou desse checkpoint,
com novo otimizador e batch 2, e concluiu 5.000 atualizações. Melhor no passo
4.000: 181/192 turnos, 16/24 conversas completas, retenção 516/535, porém
saudações 10/16. Final: 181/192, 15/24 completas, retenção 510/535. Ambos
reprovados; teste autoral reservado não consultado. Na mesma amostra pública
de 64 caminhos de validação, a loss foi 4,3485 na referência e 2,9018/2,8517
nos candidatos. Essa medida usa histórico de referência e não decide a adoção.

## Contrastes após encerramento

`prepare_dialogue_restarts.py` acrescenta 20.000 exemplos autorais ao corpus
anterior: no mesmo contexto, cumprimentar, encerrar ou pedir esclarecimento
exigem respostas distintas. Inclui históricos que já encerraram uma conversa.
Todos os exemplos novos são de treino; os grupos reservados permanecem iguais.
Snapshot: 173.810 treino, 729 validação e 597 teste, SHA-256
`4ecfb8692e1f47547aab09739530d3615f0f1b5d9a679d0a38929bc318c60a74`.

`conversation-flow-restarts-2026-11-02` treinou 2.000 atualizações, batch 2,
taxa 0,00001, inicializando do melhor checkpoint público (4.000). O estado
inicial foi o melhor por loss e não passou; o final fez 178/192 turnos e
18/24 conversas inteiras. Saudações 14/16, encerramento 16/16, porém estado
25/32 (abaixo de 80%) e retenção 501/535. Reprovado, sem consultar o teste.
Nas capturas conhecidas, retomou “oi” e respondeu “Eu apenas cumprimentei você”
ao questionamento seguinte, mas “a” ainda gerou uma frase malformada.

## Estado ao encerrar este ciclo

Foram quatro execuções concluídas e uma interrompida por memória, cada uma
com PDF. Nenhum candidato cumpriu todos os critérios ampliados. O padrão da
TUI permanece no modelo `conversation-identity-2026-11-02/last.pt`; documentos
completos não foram iniciados. A etapa de conversa segue aberta.

Os contrastes melhoraram casos conhecidos, mas novas atualizações deslocaram
erros para outras famílias e reduziram retenção. As próximas decisões precisam
priorizar generalização e estabilidade, com revisão de dados e avaliação
qualitativa independente, em vez de tratar acerto em templates como conclusão.
Os 81 testes de software passaram. Isso verifica o pipeline, não inteligência.

Para explorar o último candidato explicitamente, sem alterar o padrão:

```sh
bun run ai:chat ai/runs/conversation-flow-restarts-2026-11-02/last.pt
```

## Continuidade em 3 de novembro

Treino de abreviações e perguntas de continuidade documentado em
[INFORMAL.md](INFORMAL.md), com avaliação separada das três coortes, PDF e
verificação integrada na TUI. O candidato permanece experimental; a etapa de
conversa continua aberta.
