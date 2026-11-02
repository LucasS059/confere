# Ajustes de conversa após a expansão de contexto

Esta etapa continua a ordem de `ROADMAP.md`. A rede própria mantém contexto
1.024 e saída máxima 256. Nenhum fallback de respostas foi acrescentado à TUI.
Validação congelada: 535 pedidos sintéticos, sendo 415 legados e 120 do novo
currículo. Mais dois exemplos humanos entram somente na loss. Teste permanece
fora da seleção. Consultar a mesma validação repetidamente reduz sua independência.

## Critérios de adoção

`evaluate_conversation_adoption.py` testa o melhor checkpoint por loss e o final.
Seleciona o primeiro que cumprir simultaneamente:

- Seis regressões conhecidas corretas, com contexto nativo e histórico gerado.
- Pelo menos 80% de acertos exatos em **cada** família de conversa.
- Nenhuma queda agregada nos mesmos 415 casos legados ante o padrão da TUI.

A comparação dos 535 pedidos usa janela comum 256 e saída 64, incluindo os
turnos gerados como histórico. As seis regressões usam janela 1.024 e saída 256.
“Repetir a última resposta” é comparado com o alvo esperado do pedido anterior;
propagar uma contagem errada continua sendo erro. Igualdade exata pode penalizar
paráfrases válidas. Os alvos vêm de templates, sem avaliação humana independente.
Cumprir o critério é aprovação do currículo controlado, não de conversa aberta.

## Rodada robusta

`conversation-robust-2026-11-02` parte do currículo anterior, passo 1.200, com
novo otimizador, taxa 0,00003, batch 16 e 6.000 atualizações. Lotes humanos têm
probabilidade 0,02. O gerador varia prefixos e acrescenta reparo/encerramento
depois de histórico correto, incorreto e vazio. Validação e teste são idênticos
ao snapshot anterior, inclusive os exemplos humanos.

Corpus: 24.091 treino, 537 validação e 405 teste. SHA-256:
`6aeb0fd069d27dae1044c612157178bf5c2cc3fc00de7a53f936b2efb24de529`.
O melhor por loss é o passo 1.200: 463/535, sendo 361/415 legados e 102/120 novos.
O padrão anterior faz 371/535 (325/415 e 46/120) no mesmo conjunto. Melhor e final
passam nas seis regressões, mas ambos reprovam em famílias de conversa.
O final faz 459/535. A TUI permanece no checkpoint anterior.

As principais falhas do melhor são função 19/26, esclarecimento 27/38,
contexto social 15/24, elogios 15/24 e pedidos compostos 35/48. Repetição simples
faz 46/46, recuperação 12/12 e encerramento 12/12. As métricas completas e saídas
sem edição estão nos JSONs locais e no PDF da execução, inclusive a reprovação.

## Rodada de contrastes

`build_conversation_contrasts.py` preserva os splits de avaliação e amplia só o
treino com diferenças entre intenção de ajuda, pergunta sobre função, elogio e
repetição literal. Os novos contrastes são repetidos 12 vezes deliberadamente
para aumentar seu peso; não são novas conversas humanas. Amostras humanas
permanecem 73 de treino, duas de validação e sete de teste.

Corpus ponderado: 32.155 treino, 537 validação e 405 teste. SHA-256:
`84f4a189879d0b8fc93d4464325567757f912b1efc6a5d1b8d79106ece53df21`.
O snapshot preliminar não ponderado foi preservado, mas não usado em treino.
Cada execução usa diretório novo; não sobrescreve checkpoints ou relatórios.

`conversation-contrasts-2026-11-02` partiu do melhor robusto, passo 1.200:
4.000 atualizações, batch 16, taxa 0,00002, lotes humanos com probabilidade 0,01.
O melhor por loss, passo 1.000, fez 504/535; o final, 509/535. Ambos ficaram
em 10/16 na falta de informação e 4/6 nas regressões com histórico nativo.
O melhor fez 384/415 legados e 120/120 novos, mas a sequência mais longa das
capturas ainda repetia o nome em vez de reparar e encerrar. Isso mostra por que
o resultado da janela comum não substitui a checagem nativa. Rodada reprovada.

## Rodada de incerteza e histórico longo

`build_conversation_uncertainty.py` mantém o mesmo conjunto de avaliação.
Acrescenta somente treino de nota/apresentação/avaliador sem informação disponível
e sequências de seis turnos com repetição, reparo e encerramento. As frases das
capturas aparecem deliberadamente no treino: acertá-las não é generalização.
Os exemplos de falta de informação são repetidos 24 vezes. Prefixos e respostas
anteriores são mascarados na loss; não se ensina a produzir os erros do contexto.

Corpus: 35.683 treino, 537 validação e 405 teste. SHA-256:
`1da8f6f7e8a3531a865cd88e2dc4e5997f1eb86cada0cd853ebd8d59e640faa7`.
A inicialização usa o final dos contrastes (4.000), que preservou melhor memória
e identidade na validação já consultada. Isso não é seleção independente.

`conversation-uncertainty-2026-11-02`: 2.500 atualizações, batch 16, taxa 0,00002,
probabilidade de lote humano 0,01, 308,5s. O melhor por loss foi o estado inicial,
passo zero, com 509/535 e 4/6 regressões. O final também fez 509/535, porém
recuperou falta de informação (16/16) e as seis regressões conhecidas. Reprovou
somente em identidade, 6/8 (75%); todas as demais famílias ficaram acima de 80%.
Essa troca entre famílias não fica visível no acerto agregado. Nenhum foi adotado.

## Rodada curta de identidade

`build_conversation_identity.py` preserva os exemplos anteriores e acrescenta
1.440 exemplos autorais de identificação, com repetição deliberada. Corpus:
37.123 treino, 537 validação, 405 teste, SHA-256
`47f04a49eef1c1bd88d547a44727851791b3845034ab97de584766f2db4b394a`.
Inicializa do final da incerteza e usa ajuste curto com taxa 0,00001.

`conversation-identity-2026-11-02` treinou 1.000 atualizações, batch 16,
probabilidade de lote humano 0,01. O estado inicial foi o melhor por loss, mas
reprovou a adoção. Pelo procedimento definido antes da avaliação, o final foi
consultado e passou em todos os critérios: 514/535, 394/415 legados, 120/120 novos,
6/6 regressões conhecidas e pelo menos 80% em cada família. Identidade 8/8,
falta de informação 16/16, repetição simples 46/46 e composta 48/48. Os pontos
mais fracos ainda são orientação 61/72, elogios 21/24 e definições 29/32.

O padrão experimental da TUI passa para `conversation-identity-2026-11-02/last.pt`,
passo 1.000, contexto 1.024 e saída 256. As três tentativas anteriores permanecem
reprovadas e arquivadas com seus PDFs. Pesos/corpora são locais. A seleção usou
validação repetidamente; teste ficou fora. O resultado aprova o currículo
controlado e não comprova inteligência geral, conversa aberta ou conferência
confiável de projetos completos. A próxima fase planejada é documental.

Verificação integrada: seis mensagens enviadas pelo piloto headless do Textual
com o checkpoint final real no MPS. Todas coincidiram com a avaliação nativa,
sem bloqueio da interface e mantendo o histórico. Evidência em `tui-smoke.json`
na pasta da execução; isso não representa uma apresentação com simulador aberto.
Os 70 testes de software passaram após a mudança do padrão da TUI.

Para reproduzir os dados com o snapshot humano já congelado:

```sh
ai/.venv/bin/python ai/scripts/prepare_conversations.py \
  ai/data/private/uma-identidade-nova --variant identity \
  --source ai/data/private/oasst2-pt --source-release oasst2 \
  --context-size 1024 --response-tokens 256 \
  --tokenizer-from ai/runs/foundation-1024-2026-11-02/best.pt
```
