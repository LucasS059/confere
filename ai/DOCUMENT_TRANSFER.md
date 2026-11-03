# Transferência para conferência documental - 03/11/2026

O usuário autorizou avançar após o treino informal. A etapa documental foi
retomada como experimento isolado; isso não encerra os problemas de conversa.
Nenhum padrão da TUI foi alterado, e não houve integração ao aplicativo.

Execução `grounding-transfer-2026-11-03`: inicialização no checkpoint próprio
`conversation-informal-2026-11-03/last.pt`, novo otimizador, 2.000 atualizações,
batch 2, taxa 0,00003, MPS, janela 1.024, saída 64. Reutiliza o corpus
`data/authored/grounding.jsonl`: documentos fictícios de três unidades,
requisitos e rótulos derivados da construção, com replay de instruções curtas.
Não contém TCCs reais nem replay de diálogo. Os splits já foram explorados
em experimentos anteriores; não constituem um benchmark independente novo.

O melhor checkpoint por loss foi o passo 1.500. Nos 90 casos documentais de
validação, acertou status e unidade em 72 (80%). Formato e referência foram
válidos em 90/90. O critério exige 90% de acerto conjunto e 100% de formato e
referências válidos. Foi reprovado; os casos de teste não foram consultados
nesta execução. A avaliação geral de 114 casos inclui replay de outras tarefas
e não deve ser apresentada como 114 casos documentais.

Falha relevante: para “A entrega não apresenta relatórios”, selecionou a página
correta mas respondeu `atendido`. Uma referência existente e uma citação fiel
não comprovam interpretação correta. Os 18 erros completos estão registrados
em `document-transfer.json` na pasta local da execução.

O diagnóstico de 10 mensagens usa histórico gerado, antes e depois do treino.
Após a especialização, “e oq vc faz?” respondeu “Sou o Confere”. Esse teste é
conhecido e limitado; não representa avaliação completa de retenção. O modelo
documental permanece separado e não substitui o modelo de conversa.

Os 87 testes de software passaram. O PDF foi renderizado e inspecionado.
Artefato: `../output/pdf/training/grounding-transfer-2026-11-03.pdf`.
Pesos, dados e JSONs completos ficam locais; scripts, testes e PDF versionados.

Próximo experimento: contrastes de afirmação/negação em diferentes redações,
com distratores e replay de diálogo, avaliando explicitamente cada objetivo.
Não misturar os acertos documentais e conversacionais em uma única nota.
Documentos reais ainda precisam de licença de uso verificada e evidências
anotadas antes de sustentar qualquer avaliação de projetos completos.
