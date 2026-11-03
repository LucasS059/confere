# Contrastes documentais e replay de conversa

Execução `document-contrasts-2026-11-03`, inicializada no melhor checkpoint de
`grounding-transfer-2026-11-03`, com novo otimizador. A comparação usa o modelo
informal anterior à especialização, não o modelo documental que já apresentava
erros de conversa. O padrão da TUI não é alterado por este experimento.

## Dados e protocolo definido antes dos resultados

`prepare_document_contrasts.py` gera 3.000 casos documentais de treino, 180 de
validação e 90 de teste. Cada documento fictício tem quatro unidades, incluindo
um distrator sobre acessibilidade. A unidade que sustenta o requisito muda de
posição. Os status são balanceados. Redações conhecidas como “não apresenta”
entram no treino; presença/ausência explícita são novas redações reservadas.
Essa separação não equivale a generalização em documentos reais.

Acrescenta 3.002 turnos autorais de conversa de grupos de treino sorteados com
seed fixa, preservando os turnos completos dos grupos escolhidos. Conserva os
grupos de validação/teste de conversa, incluindo os casos informais. Não usa
pesos externos, TCCs reais ou dados públicos adicionais nesta execução.

Snapshot local: `data/private/document-contrasts-2026-11-03/examples.jsonl`.
SHA-256: `b44c941ca70ba64e515c8202f2357d88774dbf99b18b68a98ec57233363663e1`.
Configuração: MPS, batch 2, taxa 0,00002, até 4.000 atualizações ou 360 segundos
de laço; contexto 1.024, orçamento de treino conversacional 256.

O pipeline calcula a aprovação dos objetivos separadamente. A avaliação
suplementar exige 90% em cada status documental e 100% de formato/referências.
Na conversa exige 80% por família e nenhuma queda, por família ou no total,
ante a referência informal. A comparação pareada usa 1.024/64, iguais nos dois
modelos. O diagnóstico das capturas usa 1.024/256, com histórico produzido pela
rede. Não se deve apresentar os acertos mistos como uma única acurácia.

O checkpoint selecionado é o melhor por loss de validação misturada; essa
escolha pode favorecer uma capacidade em detrimento da outra. O teste fica
reservado até ambos os critérios passarem; esta execução não altera o padrão
da TUI nem declara aprovação para documentos reais mesmo se os critérios
controlados passarem. Artefatos detalhados e resultados são registrados após
a execução, sem substituir os dados ou os resultados de etapas anteriores.

## Resultados

Concluídas 4.000 atualizações em 199,7 segundos de laço, com 186.734 tokens-alvo
incluindo repetições. O melhor por loss foi o passo 1.000. Validação documental:
120/180, com formato e referências válidos em 180/180. Presença 60/60,
evidência insuficiente 60/60, ausência 0/60. A nova redação “Foi confirmada a
ausência de ...” não foi interpretada corretamente. Não é lícito tratar esse
resultado como domínio de negação, mesmo com treino de negativas conhecidas.

Conversa na comparação pareada: referência informal 779/871; candidato
799/871. O agregado esconde quedas em algumas famílias: saudação do fluxo
11/16, conversa social 18/24 e incompreensão 9/12, entre outras. A função
informal ficou em 14/24. Portanto os dois objetivos foram reprovados nos
critérios registrados; teste não consultado e padrão da TUI preservado.

No diagnóstico nativo, “e oq vc faz?” e “e o que voce faz?” responderam à
função, mas “ok, que tipo de projetos?” gerou encerramento fora de contexto.
Esse diagnóstico conhecido não substitui o conjunto reservado nem uma
avaliação completa na interface. Não houve novo piloto Textual nesta execução.

A exportação inicial do PDF falhou após o treino por assumir fonte humana em
todo manifesto de conversa. O gerador foi corrigido para reconhecer a fonte
OpenAssistant explicitamente, com teste de regressão para manifesto autoral.
Os pesos, métricas e avaliação já salvos foram preservados; o treino não foi
repetido para corrigir a exportação. Os 90 testes de software passaram.

PDF: `../output/pdf/training/document-contrasts-2026-11-03.pdf`. JSONs completos
e checkpoints continuam locais. Próximo ajuste necessário: diversidade lexical
de negação (ausência, falta, inexistência) e replay mais representativo por
família; estes resultados de validação já foram consultados e não são cegos.
