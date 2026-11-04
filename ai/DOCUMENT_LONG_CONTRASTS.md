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
