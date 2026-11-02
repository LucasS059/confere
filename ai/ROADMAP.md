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
3. **Conferência documental com evidências.** Só retomar a especialização após
   a etapa de conversa. Já existe um piloto separado com documentos sintéticos
   curtos, status e referência a unidade real; ainda pode escolher evidência
   irrelevante. Validar requisitos e evidências anotadas de documentos reais,
   sem tratar nota de apresentação como rótulo de correção documental.
4. **Projetos completos e aplicativo.** Extração PDF/DOCX, divisão em unidades,
   recuperação, análise por requisito e consolidação rastreável antes da API e
   integração ao simulador. Extração existente não significa que a rede consiga
   interpretar um arquivo inteiro. Testar tabelas, páginas digitalizadas,
   documentos longos e ausência de evidência separadamente.

Os TCCs candidatos não foram usados para treinar. Disponibilidade pública não
substitui verificação de licença nem anotação de evidências. Se não obtivermos
entregas antigas utilizáveis, manter o corpus autoral e ajustar o escopo de
avaliação, registrando que ele não representa projetos reais.

Cada execução mantém manifesto, hashes, splits, checkpoint, métricas, saídas
sem edição e PDF, inclusive quando falha. Validação consultada repetidamente
não é teste cego. Teste permanece fora do gradiente e da seleção. Pesos e dados
privados ficam locais; código, testes e relatórios entram em commits pequenos.
