# Recuperação de conversa após especialização documental

Execução `conversation-recovery-2026-11-03`, inicializada no final de
`document-paired-2026-11-03`, que tinha 180/180 documentos e 775/871 conversas.
Pesos próprios, novo otimizador, MPS, batch 2, taxa 0,00001, até 6.000 passos
ou 480 segundos de laço. A preparação e a avaliação final são separadas.

## Dados

Snapshot `data/private/conversation-recovery-2026-11-03/examples.jsonl`,
SHA-256 `4b10777cd992d7cbae6242577766769e0d59478e0a122bc4a5248d43a6afd574`.
Treino 74.281; validação 1.051; teste 824. Composição do treino:

- 6.000 documentos de pares mínimos, para retenção;
- 22.257 turnos de replay autoral estratificado por família;
- 31.200 turnos novos: formas informais de conversa com mudança de assunto,
  correção, ausência de projeto, retomada de contexto e função do assistente;
- 14.751 caminhos públicos gerados por modelos Aira, já presentes no projeto;
- 73 caminhos humanos OpenAssistant, também já presentes no projeto.

Os novos diálogos autorais reutilizam estruturas e respostas controladas.
31.200 turnos não significam 31.200 situações semanticamente independentes.
As fontes externas continuam identificadas por revisão/licença/proveniência;
não foram importados pesos. Validação/teste externos não são misturados aos
casos autorais nem ao gradiente. Não houve nova revisão humana local do corpus.

Por lote, as probabilidades são 3% humano, 15% público gerado por modelo e 82%
autoral, com sorteio dentro da fonte. Essas probabilidades não são proporções
de exemplos únicos ou de tokens efetivamente processados. Os contadores reais
da execução são registrados no relatório.

## Avaliação definida antes do resultado

Documentos e conversas reservados autorais são preservados. O treinamento
registra uma comparação com a origem imediata. A avaliação suplementar usa a
referência informal anterior à especialização, reutilizando seu resultado
somente após conferir IDs, tarefas, prompts, alvos, ordem e janelas pareadas
idênticos. Isso evita baixar o critério porque a origem documental regrediu.

O critério documental é 100% por status e referência/formato válidos. O de
conversa é pelo menos 80% por família, sem queda por família ou total ante a
referência informal, na comparação 1.024/64. Seleção pelo menor valor de loss
misturada. Esses critérios medem cenários autorais, não conversa aberta.

`evaluate_open_dialogue.py` registra uma sequência qualitativa de 11 mensagens
com cansaço, recusa de falar de projeto, nome, mudança de assunto e correção.
Cada modelo usa seu próprio histórico gerado em 1.024/256. A sequência foi
composta após preparar o corpus; prompts e intenções individuais podem existir
no treino. Não há nota automática nem revisão humana independente, e esse
diagnóstico não libera o teste reservado. As respostas brutas entram no PDF.

Nenhum padrão da TUI é alterado sem aprovação nos critérios. O trabalho não
inclui integração ao aplicativo nem interpretação validada de projetos reais.

## Resultado da ampliação

O primeiro treino concluiu 4.780 passos pelo limite de tempo, em 484,4 segundos
de laço/avaliações, com 405.066 tokens-alvo incluindo repetição. Processou 256
exemplos humanos (36.464 tokens) e 1.438 públicos gerados por modelos (219.093
tokens). O selecionado por loss foi o passo 4.000: conversa 820/871,
documentos 166/180 (negação 46/60). Ambos os critérios conjuntos reprovaram;
o teste reservado não foi consultado. Formato e referências: 180/180.

O agregado de conversa subiu, mas a sequência completa continuou inadequada:
“hoje tô cansado” recebeu “Obrigado! Fico feliz em ajudar”; a pergunta pelo nome
do usuário recebeu “Sou o Confere”. Esse resultado motivou a consolidação,
sem tratar acerto em templates como prova de conversa normal.

## Consolidação contextual

`conversation-contextual-2026-11-03` parte do selecionado anterior. Novo
otimizador, batch 2, taxa 0,000005, 4.000 passos em 211,0 segundos, 148.382
tokens-alvo. Somente dados autorais nesta rodada; os pesos herdam o treino
externo anterior. Snapshot seguro `data/private/conversation-contextual-safe-2026-11-03`,
SHA-256 `d801288f13c95a02b409ec32bafb89f22b0317f7eb44b9935ef5d4cdd72233d2`:
6.000 documentos, 22.961 turnos de replay e 18.000 turnos contextuais de treino.
Validação 1.051 e teste 824, sem mudança dos grupos reservados.

Os contrastes usam o mesmo histórico para perguntas de identidade, função,
cumprimento, bem-estar, elogio e reparo. Há também diálogos com nome, correção
de nome, assunto e preferência de não falar de projeto. O primeiro snapshot
da preparação duplicava documentos reservados e foi rejeitado pelo carregador;
foi preservado e não foi usado para treino. A correção recebeu teste específico.

O melhor por loss foi o estado inicial, passo 0, igual à origem: 820/871
conversas e 166/180 documentos. A seleção foi preservada. O final foi avaliado
separadamente: conversa 795/871, documentos 149/180 (negação 29/60), formato e
referências 180/180. Informal: 137/144, mas orientação 38/72 e outras famílias
regrediram; o agregado não deve ocultar isso. Reprovado; teste não consultado.

No diagnóstico final, lembrou Lucas e música; na sequência alternativa, lembrou
Carla e cinema. Isso é um ganho observado de contexto nessas sequências, não
generalização validada. Ainda errou cansaço, recuperação após correção e pedido
de explicação mais simples. Os nomes/assuntos da sequência alternativa e as
respostas completas estão em `fresh-dialogue-last.json`. A sequência conhecida
já informou o desenho dos exemplos, portanto não é cega.

## Balanceamento por lote e posição

Uma terceira rodada, `conversation-balanced-2026-11-03`, parte do final da
consolidação, com novo otimizador, batch 2, taxa 0,000003, até 4.000 passos.
O sampler passa a reservar 40% dos lotes para documentos e 60% para conversa.
Os exemplos de cada lote vêm da mesma categoria; as frações não são proporções
de tokens. Contadores efetivos de exemplos/tokens documentais ficam no summary.
Quando a nova opção não é usada, mantém-se o sorteio anterior, coberto pelos
testes de compatibilidade existentes.

O snapshot `data/private/conversation-balanced-2026-11-03`, SHA-256
`e02837b1646cf63fc6b8f8c6c0bfaa9decd8d43103f419a0310753c1bdf54cbe`, tem
58.914 linhas de treino: 6.000 documentos, 30.914 turnos de replay e 22.000
turnos contextuais. A ordem de humor, recusa de trabalho, nome e assunto varia,
mantendo introdução e correção de nome antes das respectivas perguntas.
As falas sobre humor e recusa também aparecem em contrastes independentes no
mesmo histórico. Validação/teste permanecem iguais; o diagnóstico já conhecido
influenciou esta escolha de dados e isso não é um teste independente.

## Resultado do balanceamento e estado final

O terceiro treino concluiu 4.000 passos em 215,2 segundos, com 174.417 tokens
alvo. Processou 3.146 exemplos documentais e 92.192 tokens documentais,
incluindo repetição: 39,3% dos 8.000 exemplos sorteados, perto da fração de
lotes esperada de 40%. Nenhum exemplo externo foi sorteado nesta rodada.

O menor valor de loss permaneceu no estado inicial, passo 0: 149/180
documentos e 795/871 conversas, iguais à origem imediata. O final foi avaliado
separadamente: 157/180 documentos (negação 37/60), formato e referência válidos
180/180; conversa 785/871. Informal 136/144. Não passou nos critérios conjuntos;
o teste reservado não foi consultado, e o padrão da CLI foi preservado.

No roteiro conhecido, o final respondeu de forma pertinente ao cansaço,
aceitou conversar sem projeto e lembrou Lucas/música. Porém “eu disse música”
recebeu “Prazer, Lucas”, e o pedido de reformulação gerou texto malformado.
No roteiro alternativo, lembrou Carla, mas “qual tema escolhi?” recebeu
“Sou o Confere”, e a despedida foi confundida com pedido de apoio. Esses
resultados não permitem declarar conversa natural resolvida.

Os diagnósticos nativos mantiveram zero turnos descartados. O piloto headless
Textual com os pesos reais do final em MPS conferiu as 11 mensagens do roteiro
alternativo contra a geração direta. Isso valida o transporte e a preservação
do histórico; respostas erradas continuam erradas. Os 103 testes de software
passaram. Não houve teste com o simulador nem com arquivos de projeto reais.

### Comparação de candidatos neste ciclo

| Candidato | Conversa controlada | Informal, subconjunto | Documentos |
| --- | ---: | ---: | ---: |
| Origem documental, final | 775/871 | 103/144 | 180/180 |
| Ampliação, selecionado passo 4.000 | 820/871 | 119/144 | 166/180 |
| Contextual, final passo 4.000 | 795/871 | 137/144 | 149/180 |
| Balanceado, final passo 4.000 | 785/871 | 136/144 | 157/180 |

Mesmos casos e janelas 1.024/64; o grupo informal está incluído nos 871 turnos,
não é uma amostra independente adicional. Não misturar essas contagens com
os diagnósticos qualitativos 1.024/256. A referência fixa anterior ao ciclo
documental continua sendo a informal de 779/871; as regressões por família
impedem a aprovação mesmo quando o total sobe.

Foram 12.780 atualizações e 727.865 tokens-alvo neste ciclo, com repetições.
Os PDFs de cada execução foram preservados separadamente e conferidos por
renderização. A ampliação de dados e o balanceamento trouxeram ganhos locais,
mas não resolveram conjuntamente conversa e retenção documental. Próximo
problema metodológico: uma validação de desenvolvimento com fatos intercalados,
humor, correções e reformulação, definida antes de novos ajustes, além da
revisão de diversidade dos dados. Continuar otimizando só os templates antigos
não comprova avanço em conversa livre.

Para experimentar explicitamente o último candidato:

```sh
bun run ai:chat ai/runs/conversation-balanced-2026-11-03/last.pt
```

Ele permanece experimental. O checkpoint documental de 180/180 e os demais
candidatos anteriores continuam disponíveis.
