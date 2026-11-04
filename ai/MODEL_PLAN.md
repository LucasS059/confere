# Plano de modelos e versões

`ai/primeiro-modelo` é a branch de desenvolvimento do primeiro sistema de IA do
Confere. Seu nome não limita o número de treinos, checkpoints ou arquiteturas.
Ela continua assim nesta etapa; não foi renomeada.

## O que temos

- Uma família atual de GPTs pequenos, com arquitetura própria, tokenizer e
  descendência de pesos inicialmente aleatórios. A configuração atual tem
  11.827.200 parâmetros e contexto de 1.024 tokens.
- Várias execuções de pré-treino e ajuste. Cada uma preserva corpus, parâmetros,
  métricas, checkpoint de origem, `best.pt`, `last.pt` e relatório.
- Checkpoints experimentais com compromissos diferentes entre conversa e
  conferência documental. São versões de pesos da mesma família; não são
  automaticamente produtos ou arquiteturas diferentes.
- Padrão atual da TUI: `conversation-identity-2026-11-02/last.pt`. Ele continua
  experimental e não comprova conversa aberta. Os candidatos posteriores são
  carregados explicitamente, sem substituir esse padrão automaticamente.

`best.pt` significa menor loss na execução, não melhor modelo para todos os
objetivos. Uma versão só deve ser promovida após avaliação conjunta e revisão
dos erros; um acerto agregado maior não compensa perder uma família importante.

## Direção para a apresentação

O objetivo inicial é um único modelo principal para conversar e interpretar os
trechos fornecidos pelo pipeline. Extração de PDF/DOCX, divisão de contexto,
referências e consolidação ficam no código. O app no simulador acessará o
serviço local do Mac quando a integração estiver pronta; esse fluxo ainda não
está integrado.

Primeiro devemos tentar preservar os dois objetivos num mesmo checkpoint,
medindo qualidade, tempo e memória no Mac. Só devemos avaliar uma arquitetura
maior se dados e diagnóstico justificarem o custo; mais parâmetros ou passos
não garantem compreensão.

Se um checkpoint único continuar perdendo conversa ao especializar documentos,
podemos comparar dois especialistas: um de conversa e outro documental,
ambos derivados do GPT próprio. Isso é uma alternativa a medir, ainda não uma
arquitetura implementada ou escolhida. A comparação precisará incluir custo,
latência, memória e regressões sob as mesmas condições antes de decidir.

## Como organizar o desenvolvimento

Esta branch reúne o primeiro ciclo até a integração revisada. Após seu merge,
melhorias futuras podem usar branches por objetivo, como
`ai/negacao-e-evidencias` ou `ai/contexto-extenso`. A branch identifica trabalho
de código; cada pasta `ai/runs/<execucao>/` identifica uma execução de treino.
Criar uma branch para cada checkpoint acrescentaria manutenção sem melhorar a
rastreabilidade dos pesos.

Código, testes, protocolos e relatórios entram no Git. Pesos e corpora privados
continuam locais, com hashes e manifestos para identificar as versões.
Checkpoints antigos são preservados para comparação e retorno. API, simulador,
merge e promoção de pesos continuam sendo etapas explícitas; o nome da branch
não implica que já foram concluídas.
