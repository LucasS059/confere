# Negação e evidências em lotes reais - 04/11/2026

## Protocolo

Origem: `document-long-2026-11-04/best.pt`, passo 1.200. Mesma rede própria e
tokenizer, contexto 1.024; nenhum peso externo. Candidato separado, padrão da
TUI preservado. O [plano de versões](MODEL_PLAN.md) distingue família,
checkpoint, execução e modelo principal.

Dados: `ai/data/private/document-long-contrasts-v2-2026-11-04/examples.jsonl`,
SHA-256 `df80c1ee52205ff72356ca194f7d7818be8a195b32d2604625c656859345f4ad`.
Somente treino alterado: 1.614 novos exemplos, balanceados em 538 por status,
600 documentos curtos de replay e 11.186 turnos conversacionais anteriores.
895 exemplos vêm de contrastes em trechos e 719 de documentos fictícios maiores
divididos pelo mesmo loteador da CLI. Entradas entre 76 e 960 tokens; parte
dos lotes finais é curta. Nenhum arquivo do piloto conhecido foi usado no treino.

O gerador cria presença, negação e menção sem comprovação para o mesmo cenário,
com diferentes formas lexicais e posições. O balanceamento seleciona um
subconjunto, portanto nem todos os pares completos ficam no corpus final.
Fragmentos sem a frase completa recebem evidência insuficiente. São rótulos
locais autorais, não anotações humanas independentes de TCCs reais.

O primeiro snapshot, sem sufixo v2, foi recusado por conter fragmentos idênticos
sem evidência, repetidos entre as polaridades. Ele não treinou pesos. O gerador
agora deduplica prompts e rejeita alvos conflitantes antes da seleção; os testes
passaram antes de criar o snapshot v2.

Validação e teste são idênticos aos do primeiro treino longo: 871 turnos de
conversa, 180 documentos curtos e 144 trechos longos em validação. As redações
de validação já influenciaram decisões anteriores; não é um benchmark cego.
O teste não entra no gradiente ou na seleção deste experimento.

Novo AdamW, taxa 0,00001, batch 2, seed 42; 45% dos lotes documentais e 55%
conversacionais. Até 2.400 passos, avaliação a cada 400 e teto de 360 segundos
do laço. Preparação e geração comparativa inicial/final ficam fora desse teto.
Selecionar pela menor loss, incluindo o estado inicial. Não trocar pelo final
após observar os acertos. Comparação gerativa 1.024/64 para os dois modelos;
treino de conversa mantém orçamento de 256 tokens.

Critérios anteriores preservados: curtos 100% por status; longos >=90% por
status; ambos com 100% de formato/referências; conversa >=80% por família e sem
queda por família ou agregado ante a origem imediata. Piloto completo precisa
dos três rótulos, conflito verdadeiro do backup, zero saída inválida e citações
com as frases autorais corretas. O piloto é conhecido e diagnóstico.

Sem promoção automática ou abertura automática do teste, mesmo se passar.
As métricas devem ser lidas junto com o histórico: a origem imediata já havia
regredido ante o especialista curto, logo recuperar sua média não prova retenção
de toda a qualidade anterior.

## Resultado

Execução `document-long-contrasts-2026-11-04`: concluiu 2.400 atualizações em
345,88 segundos de laço. Processou 2.092 exemplos documentais, incluindo
repetições. Selecionado pela menor loss: passo 1.200, 0,01845; estado inicial
0,03543 e final 0,01991. A duração não inclui preparação e geração comparativa.

| Coorte | Origem imediata | Selecionado |
| --- | ---: | ---: |
| Documentos curtos | 168/180 | 180/180 |
| Trechos longos | 87/144 | 126/144 |
| Negação nos trechos longos | 0/48 | 42/48 |
| Turnos de conversa | 769/871 | 796/871 |

Nos longos, presença caiu de 40/48 para 37/48; insuficiência ficou em 47/48.
Formato e referência válidos em 143/144. O critério por status não passou,
apesar da melhora agregada e em negação. Curtos recuperaram 60/60 em cada
status e 180/180 formatos/referências: esse critério passou.
Os acertos documentais acima exigem status e unidade corretos juntos.
Considerando somente o status, o novo modelo acertou 139/144 longos: em 13
casos classificou corretamente, mas escolheu a unidade errada. Isso ajuda a
priorizar a seleção da evidência, sem descartar as falhas de classificação.

A conversa recuperou repetição, reparos e outras famílias, mas continuidade de
assunto caiu de 29/32 para 26/32. Bem-estar 37/48, pedidos compostos 37/48,
saudação informal 16/24 e função informal 17/24 continuam abaixo de 80%.
Portanto a retenção conjunta também não passou. São acertos exatos em diálogos
autorais, sem classificação independente da naturalidade de conversa aberta.

Piloto dos mesmos arquivos completos: todo o texto extraído foi percorrido,
com 57 consultas. Saídas inválidas caíram de 9 para 3; citações literais caíram
de 48 para 18. Nenhuma dessas 18 continha a frase autoral necessária para
sustentar a classificação. Foram sinalizados conflitos nos três requisitos,
incluindo conflitos espúrios; todos ficaram inconclusivos. Redução de saídas
inválidas não demonstra interpretação confiável nesse piloto.

**Só o critério documental curto passou.** Os outros três reprovaram. O padrão
da TUI permanece separado e o teste reservado não foi consultado. Checkpoint
selecionado: `ai/runs/document-long-contrasts-2026-11-04/best.pt`, SHA-256
`d86d03e807bc1da34fd813e3797a8149e2d893f71d95ee92ae84bbeb941d11d0`.

Para experimentar explicitamente, sem alterar o padrão:

```sh
bun run ai:chat ai/runs/document-long-contrasts-2026-11-04/best.pt
```

Os 117 testes de software passaram. Artefatos versionados:
[métricas e proveniência](../output/ai/document-long-contrasts-2026-11-04.json),
[respostas completas do piloto](../output/ai/document-long-contrasts-full-files-2026-11-04.json)
e [relatório PDF](../output/pdf/training/document-long-contrasts-2026-11-04.pdf).
Pesos e dados ficam locais. Próximo foco: preservar afirmação enquanto melhora
negação, abster-se de citar trechos irrelevantes e recuperar as famílias de
conversa pendentes. Dados diversos e anotação real continuam necessários;
mais iterações de templates não comprovam compreensão geral.
