# Treinamento experimental do zero

O tokenizer BPE e o Transformer causal estão implementados em Python/PyTorch.
Os pesos são inicializados aleatoriamente; não se importa checkpoint externo.
É um primeiro experimento supervisionado em seis exemplos autorais, não um
pré-treinamento amplo de português nem um sistema pronto de conferência.

O experimento posterior de linguagem está em [PRETRAINING.md](PRETRAINING.md).
Ele possui outro tokenizer/checkpoint e não modifica os resultados deste piloto.

## Instalação e execução

Partindo da raiz do repositório e do ambiente descrito no README:

```sh
ai/.venv/bin/python -m pip install -r ai/requirements-train.lock
ai/.venv/bin/python -m pip install --no-deps -e ./ai
ai/.venv/bin/python -m unittest discover -s ai/tests -v

ai/.venv/bin/python -m confere_ai.train \
  --run-dir ai/runs/minha-execucao --device mps --steps 100

ai/.venv/bin/python -m confere_ai.sample \
  ai/runs/minha-execucao/last.pt --id biblioteca-completo-B1 --device mps

ai/.venv/bin/python -m confere_ai.train \
  --run-dir ai/runs/minha-retomada \
  --resume ai/runs/minha-execucao/last.pt --device mps --steps 125
```

`--steps` é o passo total desejado, inclusive na retomada. Pastas de saída
existentes são recusadas. Os mesmos dados, documentos e configurações precisam
ser mantidos na retomada. Checkpoints guardam pesos, estado do AdamW, tokenizer,
passo, geradores aleatórios e fingerprint do conjunto e dos documentos.
Carregue apenas checkpoints produzidos localmente e de origem conhecida.

Use `--device cpu` para CPU. `auto` seleciona MPS quando disponível; selecionar
MPS explicitamente falha se o dispositivo não estiver disponível. Dependências
de treino são opcionais: extração/validação não exigem importar PyTorch.
O ambiente verificado foi Python 3.9.6, PyTorch 2.8.0 e macOS arm64.

## Conversar pelo terminal

Na raiz do repositório:

```sh
bun run ai:chat
```

O comando carrega `ai/runs/conversation-social-context-2026-11-02/best.pt` e seleciona MPS quando
disponível. Para outro checkpoint ou para CPU:

```sh
ai/.venv/bin/python -m confere_ai.chat caminho/last.pt --device cpu
```

Em um terminal interativo, abre uma TUI com histórico rolável, mensagens separadas,
geração progressiva, checkpoint/dispositivo visíveis e métricas de tempo, tokens e
uso de contexto. Enter envia, Ctrl+J insere uma nova linha, Esc interrompe a geração,
Ctrl+L limpa a sessão e Ctrl+Q sai. F1 mostra ajuda; PgUp/PgDn rolam o histórico.
As mesmas ações de sessão estão disponíveis em `/sair`, `/limpar` e `/ajuda`.
O histórico fica somente na memória, sem salvar conversas. A geração roda em
um worker para manter a interface responsiva; a interrupção acontece entre tokens,
e uma saída interrompida não entra no contexto seguinte.

Para a interface simples anterior, acrescente `--plain`. Ela também é selecionada
automaticamente quando entrada ou saída não é um terminal (pipes/redirecionamento).
Nesse modo, Ctrl+C e Ctrl+D encerram.

Quando o contexto enche, turnos antigos inteiros saem do contexto com aviso
(continuam visíveis na TUI);
mensagens individuais grandes demais são recusadas, sem cortar seu texto.
`--max-new-tokens 128` reduz o limite da resposta e reserva mais espaço ao histórico.

Instale/atualize `ai/requirements-train.lock` para obter Textual 6.12.0 e suas
dependências. A interface usa o worker de thread do Textual e mensagens para
atualizar a tela, conforme a [documentação oficial](https://textual.textualize.io/guide/workers/).

É uma interface para experimentar o checkpoint existente: não houve novo treino
de diálogo, não há API externa e as respostas podem ser repetitivas, incoerentes
ou conter JSON memorizado. A capacidade de conversa geral e o histórico de
múltiplos turnos ainda não foram validados.

## Configurações do treinamento

### Relatório obrigatório por execução

`confere_ai.train` e `confere_ai.pretrain` agora geram automaticamente um PDF ao
concluir, incluindo conclusão por limite de tempo no pré-treino. O arquivo fica
em `output/pdf/training/<nome-da-execucao>.pdf`, com configuração, dados, hash,
passos, tempo, curvas, perdas, amostras greedy e limitações. Os artefatos JSON e
checkpoints permanecem na pasta original. As amostras são geradas depois do
treino e não entram no aprendizado; não são um benchmark de qualidade.

Para gerar novamente após uma avaliação complementar ou para execuções antigas:

```sh
ai/.venv/bin/python -m confere_ai.report ai/runs/nome-da-execucao
```

O relatório usa somente resultados registrados. Ausência de amostras ou de uma
avaliação fica explícita. O PDF é atualizado atomicamente; checkpoints não são
alterados. Execuções que falhem antes de gravar `summary.json` não são apresentadas
como concluídas e exigem diagnóstico antes de gerar um relatório de resultados.

### Hiperparâmetros do experimento supervisionado

- `--preset smoke`: 2 blocos, largura 128, 4 cabeças. Com vocabulário 512 e
  contexto 1024, são 658.944 parâmetros.
- `--preset small`: 6 blocos, largura 384, 6 cabeças. Na mesma configuração,
  são 11.433.984 parâmetros.
- Padrões: batch 2, learning rate 0,0003, AdamW, seed 42, avaliação a cada
  25 passos. Sem dropout, sem roteamento de modelos ou busca de hiperparâmetros.

Exemplo com a configuração maior:

```sh
ai/.venv/bin/python -m confere_ai.train \
  --preset small --run-dir ai/runs/meu-small --device mps --steps 100
```

O BPE parte de 256 bytes, reserva quatro tokens especiais e aprende as fusões
somente com prompts e respostas do split `train`. Texto novo usa os bytes de
fallback, incluindo UTF-8 que não ocorreu no treino. A resposta é delimitada por
tokens especiais, sem interpretar strings do documento como delimitadores.

A rede tem embeddings de tokens e posições, LayerNorm, atenção multi-head
causal, MLP com GELU e conexões residuais. A implementação usa a operação
[scaled dot product attention do PyTorch](https://docs.pytorch.org/docs/2.8/generated/torch.nn.functional.scaled_dot_product_attention.html)
com `is_causal=True`. O [backend MPS](https://docs.pytorch.org/docs/2.8/notes/mps.html)
permite executar os tensores na GPU do Mac. A referência didática é a
[aula de construção de GPT do Karpathy](https://github.com/karpathy/ng-video-lecture);
este código não é uma reprodução de capacidade ou desempenho do GPT-2.

## Separação dos dados

`load_authored` valida o conjunto e bloqueia linhas marcadas como `real`; os TCCs
candidatos não são incorporados implicitamente. O arquivo padrão é
`ai/data/authored/examples.jsonl`, com seis avaliações da biblioteca para treino,
três da horta para validação e três do portal acessível fora deste experimento.

Prompts contêm o requisito e as unidades de texto dos documentos de entrega;
`expected` é somente o alvo. A loss ignora tokens do prompt e padding e inclui
a resposta e EOS. Validação não atualiza pesos nem aprende fusões do tokenizer.
Os registros de teste podem ser lidos para validar o contrato e calcular o hash,
mas não entram no tokenizer, gradientes ou métricas; não são um teste cego real,
pois os fixtures já foram inspecionados durante o desenvolvimento.

Não há truncamento silencioso: um exemplo maior que `--block-size` é recusado.
O código ainda não faz busca de trechos, janela deslizante ou consolidação de
arquivos completos. Não use prompts maiores do que a janela como se fossem
analisados integralmente.

## Arquivos produzidos

Dentro de cada `ai/runs/<execucao>/`, ignorado pelo Git e pelo Docker:

- `run.json`: dimensões, parâmetros, ambiente, IDs e hash dos dados.
- `tokenizer.json`: fusões aprendidas do treino.
- `metrics.jsonl`: perda por token da resposta, em treino e validação.
- `last.pt`: último checkpoint, salvo no intervalo de avaliação e no final.
- `summary.json`: duração, tokens supervisionados processados e memória.

As métricas de memória distinguem RSS máximo do processo e o maior valor MPS
observado depois de um passo. Este último não é um pico contínuo de memória da
GPU nem toda a memória unificada do sistema. O throughput inclui avaliação e
checkpoint; duração não inclui instalação, preparação/tokenização ou simulação.
Não foi medido desempenho com o simulador aberto ou documentos extensos.

O comando de geração usa decodificação gulosa e informa se a saída é JSON e
se atende ao formato da resposta. Nenhum desses sinais comprova classificação
correta ou citações verdadeiras. A saída experimental não é mostrada ao usuário
do aplicativo como uma conferência pronta.

## Resultado verificado em 2 de novembro de 2026

Foram executados o smoke por 100 passos, sua retomada no MPS até 125 e o small
por 100 passos. O teste automatizado de retomada em CPU também comparou os pesos
de duas atualizações contínuas com uma atualização seguida de retomada: idênticos.

No small, o treino usou sequências de até 246 tokens e a validação, até 351,
embora a capacidade configurada seja 1024. O intervalo medido do treino levou
aproximadamente 6,17 segundos, com RSS de cerca de 636 MB e maior alocação MPS
observada após um passo de cerca de 230 MB. Esses números não são uma previsão
para um corpus grande ou para a aplicação completa.

O modelo reproduziu exatamente a resposta do exemplo de treino
`biblioteca-completo-B1`, mas a amostra `horta-entrega-H1` falhou no contrato de
resposta. A perda de treino caiu enquanto a validação piorou após o passo 25.
Isso é evidência de sobreajuste no conjunto mínimo, não de compreensão geral.
Não se calculou acurácia de conferência em todos os exemplos e não se selecionou
um checkpoint de produção. O último checkpoint não é necessariamente o melhor.

Os 30 testes de preparação, OCR, tokenizer, causalidade, máscara, isolamento
dos TCCs e retomada passaram. Os resultados brutos estão em:

- `ai/runs/smoke-2026-11-02/`
- `ai/runs/smoke-resumed-2026-11-02/`
- `ai/runs/small-2026-11-02/`

O próximo avanço de qualidade exige dados de treino mais variados e revisão das
avaliações, além de um corpus de português permitido para pré-treinamento. Rodar
mais passos nesses seis exemplos tende a memorizar o conjunto. Integração com
anexos completos e app continua pendente.
