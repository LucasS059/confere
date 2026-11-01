# Pré-treinamento de português

Esta etapa usa o mesmo Transformer implementado no projeto, com pesos iniciados
aleatoriamente, para prever o próximo token de textos em português. Não importa
pesos externos, não usa os TCCs candidatos e não ensina diálogo por si só.

## Corpus e proveniência

Fonte: [Wikimedia Wikipedia](https://huggingface.co/datasets/wikimedia/wikipedia),
configuração `20231101.pt`, via [API pública de linhas](https://huggingface.co/docs/dataset-viewer/rows).
O card da fonte declara CC BY-SA 3.0 e GFDL, com ressalvas sobre textos somente
Creative Commons. O piloto preserva card, URLs dos artigos, atribuição aos
colaboradores, links de licença e hashes. Não trate o texto como autoria do Confere
ou como material sem condições de atribuição/compartilhamento. Publicação de um
corpus derivado ou dos pesos é uma etapa separada; nada foi publicado.

Foi consultado o prefixo de 1.000 linhas, aproveitando 942 artigos com ao menos
500 caracteres e sem células truncadas pelo servidor. Cada artigo foi limitado
aos primeiros 8.000 caracteres, com a alteração registrada. Isso gerou cerca de
5,87 milhões de caracteres. É uma amostra de conveniência de texto enciclopédico,
não um corpus equilibrado de português contemporâneo ou de conversas.

O split é determinado pelo hash do ID do artigo antes de criar janelas:
846 artigos de treino, 49 de validação e 47 de teste. A preparação removeu
duplicatas exatas do texto normalizado; o carregador também bloqueia textos
idênticos atravessando splits. Não há deduplicação semântica. Os artigos de teste
não são tokenizados para treino nem usados nas métricas. Foram feitas inspeções
de amostras durante a pesquisa; não se afirma que este seja um benchmark cego.

O snapshot está em `ai/data/private/wikipedia-pt-pilot/`, ignorado pelo Git:

- `articles.jsonl`: IDs, títulos, URLs, texto, split, atribuição e licenças.
- `manifest.json`: seleção, contagens e SHA-256 do snapshot e do card.
- `SOURCE_CARD.md`: card da fonte capturado.

A API não fixa uma revisão Git nesta chamada. A configuração tem data explícita
e a reprodução local usa os bytes congelados e seu hash; um novo download pode
produzir um snapshot diferente. A limpeza usa NFC e remove espaços externos,
sem reconstrução de equações, revisão factual ou correção completa de prosa.

## Preparar e treinar

Instale as dependências de `requirements-train.lock` conforme `TRAINING.md`.
Na raiz do repositório:

```sh
ai/.venv/bin/python ai/scripts/prepare_portuguese.py \
  ai/data/private/meu-corpus-pt --rows 1000

ai/.venv/bin/python -m confere_ai.pretrain \
  --data ai/data/private/meu-corpus-pt/articles.jsonl \
  --run-dir ai/runs/meu-base-pt --device mps --steps 2000 --max-seconds 180
```

Os diretórios de saída precisam ser novos. O limite de tempo vale para o laço de
treino, depois da preparação, e é verificado após cada atualização; avaliações
e gravações podem ultrapassar esse prazo. Não é um limite rígido de duração do
processo inteiro. O checkpoint final é salvo se o tempo se esgotar.

O tokenizer BPE é treinado em até 128.000 caracteres de prefixos de artigos de
treino, com ordem embaralhada por seed. Validação e teste ficam fora das fusões.
Sua codificação foi acelerada com uma fila de prioridades, mantendo o mesmo
resultado do algoritmo anterior em testes de paridade, inclusive Unicode.

O vocabulário possui 1.024 tokens, a janela 256 tokens, e a rede seis blocos de
largura 384 com seis cabeças: 11.532.288 parâmetros. O objetivo causal usa todos
os tokens válidos, ignorando apenas padding. Janelas nunca cruzam artigos; uma
janela intermediária pode começar no meio de uma palavra tokenizada. São 8.964
janelas e aproximadamente 2,19 milhões de tokens distintos de posições de treino,
amostrados com reposição. O contador processado inclui repetições.

`best.pt` seleciona a menor perda de validação observada nesta execução;
`last.pt` permite retomar o último passo com otimizador e estado aleatório.
As perdas são medidas em 32 janelas fixas por split, não em toda a validação.
As frequências de avaliação e a amostra são registradas no `run.json`.
Não houve busca extensa de hiperparâmetros ou treinamento de um modelo maior.

Para continuar de um checkpoint local mantendo a configuração:

```sh
ai/.venv/bin/python -m confere_ai.pretrain \
  --data ai/data/private/wikipedia-pt-pilot/articles.jsonl \
  --run-dir ai/runs/pt-continuacao \
  --resume ai/runs/portuguese-base-2026-11-02/last.pt \
  --device mps --steps 4000 --max-seconds 180
```

`--steps` é o total desejado. O melhor checkpoint é selecionado dentro de cada
execução; a retomada não copia automaticamente o melhor checkpoint histórico do
diretório anterior. Guardar e comparar as execuções é necessário antes de promover
um modelo. Vocabulário diferente torna os checkpoints incompatíveis: o tokenizer
do experimento supervisionado antigo não pode ser aplicado a estes pesos.

## Testar o checkpoint desta etapa

```sh
bun run ai:chat ai/runs/portuguese-base-2026-11-02/best.pt --max-new-tokens 96
```

A TUI detecta o objetivo causal e entra em **continuação de texto**. Digite, por
exemplo, o início de uma frase, preservando o espaço final quando quiser começar
uma nova palavra. Ela não acrescenta o separador de instruções do modelo antigo.
Enter envia e Ctrl+J insere uma linha; Esc interrompe, Ctrl+L limpa e Ctrl+Q sai.
`/limpar` remove o contexto anterior; `/sair` encerra. Use `--plain` para o modo
simples ou pipes. O limite de geração padrão
se adapta ao contexto do checkpoint. Mensagens grandes demais são recusadas.

Os checkpoints base devem ser informados explicitamente. O padrão atual de
`bun run ai:chat` é o piloto de instruções descrito em `INSTRUCTIONS.md`.

## Resultado do piloto

Em 2 de novembro de 2026, o processo completou 2.000 atualizações no MPS em cerca
de 119 segundos, além de aproximadamente 13,5 segundos de preparação. Foram
processados 3.905.663 tokens, incluindo repetições. Os pesos partiram de valores
aleatórios. O maior valor MPS observado depois de um passo foi cerca de 393 MB;
o RSS máximo do processo, cerca de 745 MB. Isso não mede memória total do sistema
nem comportamento com o simulador aberto.

As perdas de treino e validação diminuíram durante a execução. As amostras
greedy de três prefixos novos produziram palavras e fragmentos em português,
mas continuam repetitivas, incoerentes e sem confiabilidade factual. A CLI foi
testada com o checkpoint real, incluindo limpeza de histórico e encerramento.
Os resultados brutos estão em `ai/runs/portuguese-base-2026-11-02/`.

Uma queda de perda não comprova fluência, compreensão de instruções ou capacidade
de conferir documentos. Não foi executada uma avaliação quantitativa de diálogo,
nem se afirma que os 2.000 passos sejam treinamento suficiente. A próxima etapa
de capacidade envolve ampliar/qualificar o pré-treino e depois treinamento
supervisionado de instruções, com validação independente. Os TCCs continuam como
candidatos separados, não entram nesta etapa implicitamente.

## Continuação até 6.000 passos

Na segunda rodada de 2 de novembro, retomamos `last.pt` do passo 2.000 sem
alterar corpus, tokenizer, otimizador ou arquitetura. A rodada terminou no passo
6.000 em 239,4 segundos no MPS, processando mais 7.796.829 tokens (com repetições).
Os checkpoints e métricas estão em `ai/runs/portuguese-continue-2026-11-02/`.
O melhor checkpoint observado nas avaliações da rodada foi o do passo 6.000.

A comparação posterior usou todas as 474 janelas dos 49 artigos de validação,
totalizando 114.985 tokens-alvo, com o mesmo tokenizer para ambos. A perda por
token passou de 3,6521 no passo 2.000 para 3,1753 no passo 6.000. Nenhum artigo de
teste foi usado. Este resultado não é diretamente igual à avaliação em 32 janelas
feita durante o treino. A validação já foi consultada repetidamente: não é teste
final independente.

Os mesmos cinco prefixos foram gerados com greedy e limite de 96 tokens. As
saídas continuam repetitivas e incoerentes; o novo checkpoint inventou uma
localização na África do Sul ao continuar "O Brasil é" e não respondeu à pergunta
"Qual é o seu nome?". Portanto, não foi promovido a chat confiável. A distância
entre perdas de treino e validação aumentou e os ganhos de validação reduziram
no fim da rodada. Repetir indefinidamente esse corpus pequeno não é o próximo
passo recomendado: ampliar/qualificar os dados vem antes de outra rodada longa,
seguido de dados de instruções com avaliação separada. Não houve SFT nesta rodada.

Para experimentar na TUI:

```sh
bun run ai:chat ai/runs/portuguese-continue-2026-11-02/best.pt --max-new-tokens 96
```

Para reproduzir a comparação (use um caminho de saída novo):

```sh
ai/.venv/bin/python ai/scripts/evaluate_language.py \
  ai/runs/portuguese-base-2026-11-02/best.pt \
  ai/runs/portuguese-continue-2026-11-02/best.pt \
  --data ai/data/private/wikipedia-pt-pilot/articles.jsonl \
  --output ai/runs/minha-comparacao.json --device mps
```

O script confere hash do corpus, objetivo, arquitetura e tokenizer antes da
comparação. Os resultados completos, incluindo saídas sem edição, estão no
`comparison.json` da nova execução. O checkpoint anterior e o padrão da CLI
foram preservados. Os 45 testes passaram; não foi feito treinamento com o
simulador aberto nem avaliação de anexos completos nesta rodada.

## Expansão do corpus e relatórios

O snapshot `ai/data/private/wikipedia-pt-expanded/` contém os primeiros 5.000
registros consultados, com 4.468 artigos aceitos e 21.348.023 caracteres após
filtros e limite de tamanho. São 4.036 artigos de treino, 196 de validação e 236
de teste. As condições de licença, atribuição e viés da seleção continuam as
mesmas. O download encontrou HTTP 429 e foi retomado com cache de páginas e
espera entre tentativas; o manifesto e o hash só são gravados após terminar.

Retomar com novos dados exige `--previous-data`: o hash deve corresponder ao
checkpoint e todos os artigos anteriores precisam continuar presentes com os
mesmos textos e splits. Conteúdo idêntico não pode atravessar splits antigos e
novos. Esta verificação não faz deduplicação semântica. O tokenizer é preservado
para manter a compatibilidade com os pesos; não é ajustado à nova validação.

```sh
ai/.venv/bin/python -m confere_ai.pretrain \
  --data ai/data/private/wikipedia-pt-expanded/articles.jsonl \
  --previous-data ai/data/private/wikipedia-pt-pilot/articles.jsonl \
  --resume ai/runs/portuguese-continue-2026-11-02/last.pt \
  --run-dir ai/runs/uma-expansao-nova --device mps \
  --steps 10000 --max-seconds 300 --eval-every 400
```

Os PDFs de todas as execuções concluídas estão em `output/pdf/training/`.
As próximas execuções geram seu relatório automaticamente ao finalizar, conforme
`TRAINING.md`. As curvas em corpora diferentes não devem ser comparadas como
se fossem o mesmo conjunto de validação. Para uma comparação direta no corpus
ampliado, use `evaluate_language.py --validation-transfer --previous-data ...`:
o script confere a preservação dos splits antes de avaliar os dois checkpoints
nas mesmas janelas de validação.

### Resultado da rodada ampliada

`portuguese-expanded-2026-11-02` retomou do passo 6.000 e concluiu no 10.000,
em 237,1 segundos de laço no MPS, processando mais 7.714.469 tokens com
repetições. O melhor checkpoint observado foi o final. A perda na amostra fixa
de 32 janelas de validação caiu de 3,2181 para 2,6303 dentro desta rodada.

Na comparação completa sobre as mesmas 1.618 janelas dos 196 artigos de
validação ampliada (389.898 tokens-alvo), o checkpoint antigo do passo 6.000
teve perda 3,3340; o novo, 2,7657. Teste permanece fora. A validação não é cega e
as métricas medem previsão do próximo token, não compreensão ou fidelidade.
As amostras ainda localizam o Brasil incorretamente na África e repetem
expressões. Não há evidência suficiente para afirmar que o modelo converse
ou confira documentos com confiabilidade. Não foi iniciado treino de instruções.

O PDF da rodada inclui a comparação completa e os trechos gerados sem correção
editorial. O checkpoint pode ser aberto com:

```sh
bun run ai:chat ai/runs/portuguese-expanded-2026-11-02/best.pt --max-new-tokens 96
```
