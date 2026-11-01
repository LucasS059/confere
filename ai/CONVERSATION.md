# Conversas com histórico

As capturas do usuário mostravam o piloto inicial de instruções, passo 200.
Ele foi treinado com respostas isoladas; a inferência incluía respostas anteriores
que o treino não usava. Esta etapa compartilha o formato de `chat.prepare_prompt`
com o encoder supervisionado: BOS/pergunta/SEP/resposta/EOS por turno, com loss
somente na resposta atual. Histórico e respostas anteriores ficam mascarados.

O orçamento conversacional padrão é 64 tokens de saída, na janela de 256.
Exemplos de treino que precisassem cortar histórico ou resposta são rejeitados.
Na inferência, turnos antigos ainda podem sair do contexto com aviso. Isso não
constitui memória persistente. Não há respostas programadas na TUI: todo o texto
mostrado como resposta continua vindo da rede local.

## Dados e fonte humana

`build_conversations.py` cria 1.187 exemplos sintéticos (1.008 treino, 103
validação, 76 teste), agrupados em conversas. Há saudação/função, nomes,
repetição, esclarecimento, correção de prazo inventado e quatro definições.
No reparo, um erro anterior é fornecido como contexto, não como alvo da loss.

Consultamos [OpenAssistant/oasst1](https://huggingface.co/datasets/OpenAssistant/oasst1),
Apache-2.0, revisão `fdf72ae0827c1cda404aff25b6603abec9e3399b`. O arquivo oficial
`2023-04-12_oasst_ready.messages.jsonl.gz` tem SHA-256
`286a6e9a5a413b3272ae9c0b5a20d327983dea1c24342ae28cb244a6da65185c`.
LICENSE, README, revisão e snapshot ficam em `ai/data/private/oasst1-pt/`.
Há 1.203 mensagens pt-BR. O preparo filtra mensagens humanas revisadas, respostas
rank 0, qualidade >=0,6 e fails_task=0; todo o caminho de pais precisa estar
aprovado. Árvores recebem split por hash antes da filtragem de tamanho.

Só 9 respostas humanas de treino e 1 de teste couberam nos limites sem corte;
137 candidatas foram excluídas por tamanho e 58 por caminho ausente/não aprovado.
Não sobrou validação humana. Isso não é uma expansão suficiente de diálogo real:
a mistura permanece essencialmente sintética, sem revisão humana local.
Mensagens são rastreadas por IDs e revisão; IDs dos usuários não vão aos exemplos.
Não foram importados pesos externos. Licença e card da fonte foram preservados.

`prepare_conversations.py` exige os arquivos oficiais no diretório `--source`.
Não baixa dados implicitamente. Depois de congelar esses arquivos e `revision.txt`:

```sh
ai/.venv/bin/python ai/scripts/prepare_conversations.py \
  ai/data/private/uma-conversa-nova --variant mixed
```

O preparo verifica o tamanho com o tokenizer local e grava manifesto, hashes,
contagens e exemplos. Diretórios de saída devem ser novos. A API de filtro
consultada falhou; usamos o snapshot oficial completo, sem depender dela.

## Duas rodadas

`conversation-pilot-2026-11-02`: 3.000 passos, 148,9s de laço, 719.728 tokens
supervisionados com repetições; inicialização do melhor instruction-v2-refine,
novo otimizador, batch 16, taxa 0,00005. Loss mínima no passo 300. Nos mesmos 103
pedidos, a referência antiga fez 0 acertos exatos, o passo 300 fez 66 e o passo
3.000 fez 69. Com histórico gerado, nomes e definições falharam muito. A repetição
da sequência das capturas continuou prendendo o modelo ao assunto anterior.
Ambos os checkpoints e as avaliações foram preservados; não é teste cego.

`build_conversation_mix.py` acrescentou alternância de tarefas dentro da mesma
conversa e nomes sintéticos combinatórios. Eles não representam nomes de pessoas
reais. O corpus misto tem 8.217 exemplos de treino, 295 de validação e 239 de teste
(incluindo os mesmos 9 exemplos humanos de treino e 1 de teste). Prefixos
idênticos com mesmo alvo podem se repetir no treino, mas não atravessam splits.
Projetos/conversas não atravessam splits; enunciados de teste são distintos.

```sh
ai/.venv/bin/python -m confere_ai.instruct \
  --data ai/data/private/conversation-corpus-mixed/examples.jsonl \
  --init-from ai/runs/conversation-pilot-2026-11-02/last.pt \
  --compare-with ai/runs/conversation-pilot-2026-11-02/last.pt \
  --run-dir ai/runs/uma-conversa-mista-nova --device mps \
  --steps 3000 --batch-size 16 --learning-rate 0.00005 --eval-every 300
```

A rodada mista treinou 3.000 passos. O melhor checkpoint por loss foi o passo
1.800, com 248/295 acertos exatos, contra 95/295 da referência anterior, nos mesmos
295 pedidos. O final fez 244/295 e foi preservado, mas não escolhido para a TUI.
No melhor: função 22/26, memória 96/96, repetição 38/46, esclarecimento 30/38,
reparo 33/33, definições 5/32, identidade 8/8 e falta de informação 16/16.
O critério exploratório de 80% em cada família não foi atingido. O teste permaneceu
fora de treino e métricas; a validação foi usada repetidamente na seleção.

O acerto é igualdade exata após strip, não avaliação humana de qualidade.
Paráfrases válidas podem ser penalizadas. A avaliação sintética usa respostas
geradas como histórico dos turnos seguintes, sem inserir respostas de referência.
A loss usa histórico de referência. Respostas humanas, quando avaliadas, começam
do caminho de pais fornecido; nenhuma ficou na validação desta rodada.
As curvas de treino usam os primeiros 128 exemplos, que são legados na mistura;
por isso a loss de treino arredondada a zero não implica domínio do corpus novo.
A validação usa todos os exemplos do split correspondente.

## Uso e limitações

`bun run ai:chat` agora abre `conversation-mixed-2026-11-02/best.pt`, como prévia
experimental para conversas. Feche uma TUI antiga com Ctrl+Q e reabra: os pesos
são carregados uma vez e não mudam numa sessão já aberta. O cabeçalho mostra
caminho e passo 1.800. Para preservar mais histórico, o limite padrão é 64 tokens.

Na sequência exata inspirada nas capturas, o modelo saudou, explicou sua função,
pediu esclarecimento a "por favor" e não inventou prazo. Ainda errou o pedido
composto "qual seu nome? diga 3 vezes". Esses testes foram solicitados pelo usuário
e não são um benchmark independente. As saídas sem edição estão em
`interactive-regressions.json`, e aparecem nos dois PDFs.

Isto não torna o modelo um assistente de conversa geral. O pré-treino e a amostra
humana continuam pequenos; definições, paráfrases e instruções compostas falham.
Uma expansão séria de diálogo real exigirá rever contexto/orçamento de resposta
e uma base linguística muito maior, com avaliação qualitativa independente.
Os padrões experimentais da TUI não são aprovação de confiabilidade. O fluxo
documental `ai:review` e seu checkpoint permanecem separados.
