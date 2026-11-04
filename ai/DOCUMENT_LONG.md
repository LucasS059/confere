# Contextos longos - 04/11/2026

## Protocolo

O piloto de arquivos completos percorreu o texto, mas retornou 54/57 respostas
inválidas e três referências irrelevantes. Esta execução trata a diferença entre
os exemplos documentais curtos e os trechos extensos enviados pela CLI. Não há
pesos externos, mudança de arquitetura, tokenizer novo ou integração ao app.

Origem: `ai/runs/document-paired-2026-11-03/last.pt`, passo 4.000, GPT próprio
de 11.827.200 parâmetros e contexto 1.024. Novo otimizador AdamW, taxa 0,00002,
batch 2, seed 42, 60% dos lotes documentais e 40% de conversas autorais.
Plano: até 2.000 atualizações, avaliação a cada 400 e limite de 300 segundos
do laço, incluindo avaliação de loss e checkpoints. Preparação, comparação
gerativa inicial/final e relatório ficam fora desse limite.

Dados: `ai/data/private/document-long-v2-2026-11-04/examples.jsonl`, SHA-256
`74b9114a3d71829b8a75e199f522b4907f33a25352fa32deb20773fcfbea0461`.
São 1.440 novos trechos de treino, 600 documentos curtos de replay e 11.186
turnos conversacionais preservados. Validação: 144 trechos longos novos, 180
documentos curtos anteriores e 871 turnos de conversa anteriores.

Trechos longos variam entre 266 e 950 tokens de entrada, reservando 64 para a
resposta. Têm uma a quatro unidades, presença/negação/ausência de evidência e
frases relevantes no início, meio ou fim do texto. Tópicos, redações de
evidência e preenchimento são separados por split. As receitas de geração são
compartilhadas; números, registros sintéticos e a diversidade limitada podem
introduzir atalhos. Não é avaliação independente nem representa linguagem de
TCC real. Os rótulos são autorais por construção, sem revisão independente.

O primeiro snapshot local `document-long-2026-11-04` não foi usado no treino:
um teste do gerador com tokenizer sem fusões encontrou prompts duplicados quando
não cabia preenchimento. O snapshot v2 acrescenta identificação única na unidade;
o teste passou antes de iniciar a execução.

## Critérios fixados antes dos resultados

Selecionar `best.pt` pela menor loss de validação misturada, incluindo o passo
zero herdado. Não trocar pelo final depois de observar os acertos. Avaliação
gerativa pareada: contexto 1.024 e saída de até 64 tokens para os dois modelos;
histórico de conversa gerado por cada um. Orçamento nativo de treino de conversa:
256 tokens. Não misturar esses dois orçamentos ao interpretar os resultados.

- Documentos curtos: 100% por status e formato/referências válidos em todos.
- Documentos longos: pelo menos 90% por status, formato/referências em todos.
- Conversa: pelo menos 80% por família e sem queda por família ou no agregado
  ante a origem imediata. Uma melhora documental não compensa perda de conversa.
- Arquivos completos: repetir os mesmos arquivos e requisitos do piloto,
  acertar os três consolidados, detectar o conflito do backup, citar as frases
  autorais corretas e não produzir saída inválida. O oráculo dessas frases é
  restrito ao piloto conhecido; não julga suporte em texto livre. Cobertura e
  citações literais continuam auditadas.

O piloto conhecido é diagnóstico fora do gradiente, não benchmark novo. Mesmo
se todos esses critérios passarem, não há promoção automática do chat nem abertura
automática do teste reservado. Documentos reais anotados e avaliação de conversa
aberta continuam necessários. Relatório por execução permanece obrigatório.

## Reprodução

Usar diretórios novos para preservar datasets, pesos e avaliações existentes:

```sh
ai/.venv/bin/python ai/scripts/prepare_long_documents.py CAMINHO_DADOS_NOVO \
  --source ai/data/private/document-paired-2026-11-03/examples.jsonl \
  --checkpoint ai/runs/document-paired-2026-11-03/last.pt

ai/.venv/bin/python -m confere_ai.instruct \
  --data CAMINHO_DADOS_NOVO/examples.jsonl \
  --init-from ai/runs/document-paired-2026-11-03/last.pt \
  --run-dir CAMINHO_EXECUCAO_NOVO --device mps \
  --steps 2000 --batch-size 2 --learning-rate 0.00002 --eval-every 400 \
  --response-tokens 256 --document-fraction 0.6 --evaluation-context 1024 \
  --max-seconds 300

ai/.venv/bin/python ai/scripts/evaluate_long_documents.py CAMINHO_EXECUCAO_NOVO \
  --pilot output/ai/full-file-pilot-2026-11-04.json \
  --files ai/data/private/full-file-pilot-2026-11-04/entrega-longa.pdf \
          ai/data/private/full-file-pilot-2026-11-04/entrega-tabelas.docx
```

O relatório combina treino e avaliação conjunta. Os arquivos brutos do piloto
novo ficam em `full-file-validation.json` dentro da execução; as decisões e
métricas por família ficam em `long-document-evaluation.json`.
