# Localização de evidências - 05/11/2026

Experimento separado, iniciado em `document-long-contrasts-2026-11-04/best.pt`.
Acrescenta 1.440 exemplos autorais ao corpus anterior, 480 por status, com a
mesma afirmação ou negação em posições diferentes e menções sem comprovação.
O loteador é o mesmo da CLI. Somente o treino muda; validação e teste permanecem
idênticos. Templates compartilhados não são avaliação independente de TCC real.

Dataset: `ai/data/private/evidence-position-2026-11-05/examples.jsonl`, SHA-256
`a708e8b1e412579f82e6763cddf7c59771ed7e7402333714f1e4b9b23975d63a`.
Mesma arquitetura/tokenizer, AdamW novo, taxa 0,00001, batch 2, seed 42,
40% dos lotes documentais e 60% conversacionais. Até 2.400 passos e 360 segundos
de laço, avaliações a cada 400; preparação e geração comparativa fora do teto.
Selecionar pela menor loss, incluindo passo zero; não escolher o final depois
dos acertos. Comparação gerativa comum 1024/64, treino de conversa com orçamento
256. Nenhum checkpoint externo é usado.

Critérios preservados: curtos 100% por status; longos >=90% por status, ambos
com 100% de formato/referências; conversa >=80% por família e sem regressões
ante a origem imediata. Piloto completo precisa de todos os rótulos, conflito
verdadeiro, zero saída inválida e citações sustentadas pelas frases autorais.
Piloto conhecido e validação repetida são diagnósticos, não teste cego.
Sem consulta ao teste reservado ou promoção automática; o app da apresentação
continua limitado a um único modelo selecionado por avaliação conjunta.
