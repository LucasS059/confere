# Ordem do desenvolvimento da IA

Modelo treinado de pesos aleatórios, inferência no Mac e integração posterior
ao aplicativo no simulador. Nenhum peso externo substitui a rede própria.

1. **Base linguística.** Ampliar português e contexto, comparando checkpoints
   nas mesmas janelas antes de ajustar diálogo. A expansão para 8.792 artigos e
   contexto 1.024 concluiu em 02/11. A comparação pareada de loss melhorou;
   amostras ainda são incoerentes. Isso libera um experimento de diálogo,
   não comprova fluência nem conhecimento confiável.
2. **Conversa e instruções.** Ajustar a base, testar histórico gerado pela rede,
   mudanças de assunto, repetição, pedidos compostos e recuperação de erros.
   Etapa reaberta pelo feedback de 15h30: [avaliação ampliada](CONVERSATION_FLOW.md)
   exige diálogos completos, correção de informação e teste reservado. O sucesso
   no currículo curto abaixo não encerra a etapa de conversa normal.
   O primeiro currículo de 02/11 foi reprovado. Após quatro ajustes, o final de
   `conversation-identity-2026-11-02` passou no currículo controlado e foi adotado
   como padrão experimental: 514/535, 6/6 regressões conhecidas e pelo menos
   80% nas 15 famílias. A conversa aberta permanece não validada. Para adoção:
   acertar os seis casos conhecidos, preservar o acerto agregado nos 415 casos
   anteriores e alcançar 80% em cada família nova. O critério amplo continua
   sendo 80% em todas as famílias; ganhos locais não comprovam conversa aberta.
   A próxima ampliação deve priorizar diálogo humano diverso e avaliação
   qualitativa independente. Acrescentar templates dos erros conhecidos pode
   corrigir exemplos, mas não constitui aumento geral de inteligência.
   [Recuperação de conversa](CONVERSATION_RECOVERY.md) concluiu três novos
   treinos: houve ganho pontual em nomes/assuntos e informalidade, mas perda de
   retenção e falhas em correção/reformulação. Nenhum candidato foi aprovado;
   o teste reservado e o padrão atual foram preservados.
3. **Conferência documental com evidências.** Só retomar a especialização após
   a etapa de conversa. Já existe um piloto separado com documentos sintéticos
   curtos, status e referência a unidade real; ainda pode escolher evidência
   irrelevante. Validar requisitos e evidências anotadas de documentos reais,
   sem tratar nota de apresentação como rótulo de correção documental.
   Em 03/11, o usuário autorizou avançar; foi aberto um experimento isolado
   apesar das limitações de conversa ainda presentes, sem declarar a etapa 2
   concluída. [Transferência documental](DOCUMENT_TRANSFER.md): 72/90 casos,
   reprovada por erros semânticos; checkpoint separado e teste não consultado.
   [Contrastes com replay](DOCUMENT_CONTRASTS.md) concluíram outro treino:
   novas negações 0/60, validação conjunta reprovada, teste ainda reservado.
   [Três iterações lexicais e pareadas](DOCUMENT_LEXICAL.md) chegaram a
   180/180 documentos no checkpoint final exploratório, mas conversa 775/871
   com regressões por família. Meta conjunta aberta; teste não consultado.
4. **Projetos completos e aplicativo.** Extração PDF/DOCX, divisão em unidades,
   recuperação, análise por requisito e consolidação rastreável antes da API e
   integração ao simulador. Extração existente não significa que a rede consiga
   interpretar um arquivo inteiro. Testar tabelas, páginas digitalizadas,
   documentos longos e ausência de evidência separadamente.
   Em 04/11, o usuário autorizou a próxima etapa: [CLI de arquivos completos](FULL_FILES.md)
   iniciada como integração isolada. A varredura preservou todo o texto extraído
   no piloto PDF/DOCX; a interpretação falhou e os três resultados ficaram
   inconclusivos. Nenhum treino novo, padrão de chat alterado ou integração ao
   aplicativo. As metas conjuntas das etapas 2 e 3 continuam abertas.
   O [treino de contextos longos](DOCUMENT_LONG.md) fez 2.000 atualizações:
   87/144 trechos longos, 168/180 curtos e 769/871 turnos de conversa. Negações
   longas 0/48 e nenhuma das 48 citações do piloto completo sustentou o rótulo.
   Critérios conjuntos reprovados; teste reservado e padrão da TUI preservados.
   [Contrastes em lotes reais](DOCUMENT_LONG_CONTRASTS.md) recuperaram 180/180
   curtos e chegaram a 126/144 longos, 42/48 negações longas e 796/871 turnos
   de conversa. Presença longa regrediu e o piloto completo seguiu sem citações
   com suporte: só o critério curto passou. Nenhum checkpoint promovido.

O [plano de modelos e versões](MODEL_PLAN.md) exige um único modelo no app da
apresentação: o mais competente na avaliação conjunta. Internamente podemos
manter vários modelos e arquiteturas para pesquisa e comparação no Mac.

O [experimento de localização](EVIDENCE_POSITIONS.md), em 05/11, acrescentou
1.440 exemplos e concluiu 2.400 passos. O passo zero herdado continuou melhor
por loss; não houve ganho no selecionado. Avaliações e PDF foram preservados,
sem promoção ou consulta ao teste reservado.

Os TCCs candidatos não foram usados para treinar. Disponibilidade pública não
substitui verificação de licença nem anotação de evidências. Se não obtivermos
entregas antigas utilizáveis, manter o corpus autoral e ajustar o escopo de
avaliação, registrando que ele não representa projetos reais.

Cada execução mantém manifesto, hashes, splits, checkpoint, métricas, saídas
sem edição e PDF, inclusive quando falha. Validação consultada repetidamente
não é teste cego. Teste permanece fora do gradiente e da seleção. Pesos e dados
privados ficam locais; código, testes e relatórios entram em commits pequenos.
