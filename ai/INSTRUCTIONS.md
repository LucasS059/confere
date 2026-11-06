# Piloto de instruções curtas

Esta etapa ajusta o nosso GPT de português, preservando arquitetura e tokenizer.
Não importa pesos externos. O otimizador é novo; passos SFT são contados a partir
de zero, separados dos 10.000 passos de pré-treino da base.

`scripts/build_instructions.py` produz `data/authored/instructions.jsonl`: 167
exemplos de treino, 35 de validação e 34 de teste. São templates sintéticos
construídos pelo assistente, sem revisão humana, sem entregas reais e sem notas.
As tarefas incluem copiar, extrair código, identificar data, informar prazo ou
ausência de informação, além de poucas respostas fixas de identidade/saudação.
Há projetos e textos distintos entre splits, mas tipos de tarefa e respostas
constantes se repetem. Não é avaliação independente de conversa geral.

O loader rejeita projetos atravessando splits, prompts repetidos, IDs duplicados
e origem incompatível. Usa o separador BOS/prompt/SEP/resposta/EOS, com loss
somente na resposta e EOS, como o encoder supervisionado existente. Nada é
truncado silenciosamente para caber em 256 tokens.

```sh
ai/.venv/bin/python ai/scripts/build_instructions.py
ai/.venv/bin/python -m confere_ai.instruct \
  --init-from ai/runs/portuguese-expanded-2026-11-02/best.pt \
  --run-dir ai/runs/uma-nova-instrucao --device mps --steps 2000
```

A execução `instruction-pilot-2026-11-02` treinou 2.000 passos em aproximadamente
63,4 segundos de laço, com batch 8 e learning rate 0,0001. Processou 114.007
tokens supervisionados com repetições. O tempo não inclui a avaliação gerativa
antes/depois. Validação completa de loss é feita a cada 200 passos. `best.pt`
seleciona menor loss de validação; `last.pt` preserva o final. O melhor foi o
passo 200: os passos posteriores só reduziram a perda de treino e pioraram a
validação. Não se recomenda continuar repetindo esse conjunto.

Comparação gerativa nos mesmos 35 pedidos, greedy, limite de 64 tokens e
igualdade exata após strip: base 0/35; melhor SFT 15/35. No melhor SFT: cópia
1/8, extração de código 0/8, presença de data 8/8, prazo/ausência 4/8 e diálogo
fixo 2/3. O modelo saudou e disse o nome corretamente, mas alterou 101 para 11,
extraiu P10 em vez de P101 e respondeu sua identidade à pergunta sobre erros.
Não houve avaliação do teste. A validação seleciona pesos e mede resultado;
não é teste cego, e 15/35 não é uma taxa de acerto geral do Confere.

`instruction-evaluation.json` registra entradas, respostas esperadas e geradas,
além do critério; o PDF inclui comparação, curvas, amostras e limites. As próximas
execuções desse comando geram PDF automaticamente em `output/pdf/training/`.

`bun run ai:chat` agora usa o melhor checkpoint deste piloto. A TUI o identifica
como piloto de instruções. Caminhos explícitos ainda permitem usar as bases
anteriores. Não foi validado diálogo com múltiplos turnos, informação factual
aberta nem conferência de anexos completos. Os próximos dados precisam atacar
cópia e extração com mais diversidade, sem reutilizar a validação no gradiente.

## Segunda versão e refinamento

`scripts/build_instructions_v2.py` cria 4.376 exemplos sintéticos: 4.044 de
treino, 168 de validação e 164 de teste. Projetos têm números de 3 a 6 dígitos,
códigos com prefixos diversos, campos embaralhados e prazos variados. Acrescenta
pedidos sem contexto com alvo explícito de informação insuficiente. Templates
de validação são distintos dos de treino. Saudações e frases do piloto antigo
podem entrar no novo treino; a validação antiga não é mais benchmark para v2.
Os mesmos 168 pedidos novos são usados para comparar cada checkpoint, sem
consultar o split de teste. Alvos são gerados dos campos, sem revisão humana.

```sh
ai/.venv/bin/python ai/scripts/build_instructions_v2.py
ai/.venv/bin/python -m confere_ai.instruct \
  --data ai/data/authored/instructions-v2.jsonl \
  --init-from ai/runs/portuguese-expanded-2026-11-02/best.pt \
  --compare-with ai/runs/instruction-pilot-2026-11-02/best.pt \
  --run-dir ai/runs/uma-nova-v2 --device mps \
  --steps 3000 --batch-size 16 --eval-every 300
```

V2 treinou 3.000 passos em cerca de 141,9s de laço; melhor loss de validação
no passo 2.100. Comparação gerativa: piloto anterior 37/168, v2 151/168.
Loss de treino usa os primeiros 128 exemplos; a validação de loss é completa.
`--compare-with` compara pesos, arquitetura e tokenizer, sem alterar de qual
checkpoint o gradiente é iniciado. O baseline da loss continua sendo a
inicialização do treino, e não necessariamente a referência gerativa.

O refinamento `instruction-v2-refine-2026-11-02` iniciou do melhor v2 com novo
otimizador e taxa 0,00002. Treinou 1.000 passos em 49,7s; melhor checkpoint no
passo 800, com 154/168. Cópia: 29/40; código: 38/40; presença de data: 40/40;
prazo/ausência: 40/40; saudações/identidade: 2/3; informação insuficiente: 5/5.
Os erros remanescentes incluem dígitos repetidos ou omitidos e uma pergunta de
identidade com resposta sobre falibilidade. O teste continua sem uso.

O critério anunciado antes do resultado foi ao menos 80% em cada tarefa crítica
(cópia, código, prazo/ausência, falta de contexto). Ambos falharam em cópia
(72,5%), portanto o padrão da CLI foi preservado. O critério e suas contagens
ficam registrados no JSON de avaliação e no PDF. Ele é exploratório, baseado em
templates e validação consultada repetidamente; não atesta confiabilidade geral.

Para testar o candidato, sem trocar o padrão:

```sh
bun run ai:chat ai/runs/instruction-v2-refine-2026-11-02/best.pt
```

As duas rodadas têm PDF próprio em `output/pdf/training/`. Na verificação real
da CLI, o candidato extraiu REQ-12345 e recusou inferir a nota de um TCC ausente.
Isso não valida perguntas livres, vários turnos ou anexos completos. Esses
comportamentos ainda não são seguros para uma apresentação como assistente geral.
