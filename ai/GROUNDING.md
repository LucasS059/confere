# Piloto de conferência com referências

Esta etapa usa o nosso GPT para gerar apenas um JSON com `status` e `unit`.
Os status mantêm o vocabulário do projeto: `atendido`, `nao_atendido` e
`evidencia_insuficiente`. Uma conclusão exige ID existente; insuficiência usa
`null`. Campos extras, JSON inválido e referências inexistentes são rejeitados.
O programa resolve a citação copiando o texto da unidade extraída; não pede à
rede que reproduza os bytes. Não é um verificador semântico independente.

`scripts/build_grounding.py` cria 1.200 exemplos documentais sintéticos de
treino, 90 de validação e 90 de teste, com classes balanceadas, unidades
embaralhadas e termos/frases distintos entre splits. São páginas fictícias em
JSON, não um conjunto de TCCs. Replay: 300 exemplos de treino e 24 de validação
do corpus v2, preservando splits. Total: 1.704 exemplos. Os alvos são derivados
da construção, sem rótulos humanos ou avaliação do professor. O loader confere
integridade do prompt, referências, tarefa/status e separação por projeto.

```sh
ai/.venv/bin/python ai/scripts/build_grounding.py
ai/.venv/bin/python -m confere_ai.instruct \
  --data ai/data/authored/grounding.jsonl \
  --init-from ai/runs/instruction-v2-refine-2026-11-02/best.pt \
  --run-dir ai/runs/uma-conferencia-nova --device mps \
  --steps 2400 --batch-size 16 --learning-rate 0.00005 --eval-every 300
```

`grounding-pilot-2026-11-02` treinou 2.400 passos em 157,3 segundos de laço,
processando 972.361 tokens supervisionados, com repetições. Melhor checkpoint
no passo 2.400; tokenizer e arquitetura foram preservados, com novo otimizador.
Loss de treino usa 128 exemplos; validação de loss usa todo o split. Avaliações
gerativas anteriores/posteriores ficam fora do tempo do laço.

No mesmo conjunto documental de 90 casos, a referência anterior não produziu
JSON válido (0/90). O novo checkpoint produziu formato e referências válidos
em 90/90, status correto em 90/90 e status/unidade corretos em conjunto em
84/90: atendido 24/30, não atendido 30/30, insuficiência 30/30. Nos seis erros,
selecionou uma página real mas irrelevante. A fidelidade literal não comprova
suporte semântico. Replay: 21/24, contra 22/24 da referência; cópia regrediu de
4/6 para 3/6. O agregado 105/114 mistura objetivos e não representa acurácia
em entregas reais.

O critério exploratório registrado (referências/formato válidos em todos e
90% de acerto conjunto) foi atingido, mas a classe positiva ficou em 80%.
Isso não justifica promover o modelo para uso em documentos completos nem
trocar o padrão de conversa. A validação também seleciona pesos e não é cega;
o teste permaneceu fora das métricas. O relatório registra erros de evidência
além das curvas. Não houve integração com o app/simulador ou treino com TCCs.

## Testar com um arquivo curto

```sh
bun run ai:review caminho/projeto.pdf \
  --requirement "O projeto deve incluir testes."
```

Pode repetir `--unit page:1 --unit page:2` para limitar explicitamente o contexto.
O extrator aceita PDF e DOCX, mas o modelo desta rodada só foi treinado com
`page:N`: capacidade com parágrafos/tabelas DOCX não foi demonstrada.

A CLI preserva hash, avisos e IDs da extração. Contextos que excedem a janela
de 256 tokens são recusados, reservando 64 tokens à geração; nada é truncado.
Selecionar unidades limita a cobertura, não conclui sobre partes não lidas.
Uma saída inválida resulta em `evidencia_insuficiente`, evidências vazias e
flags indicando a falha. `reference_valid` só comprova referência existente.

O teste integrado local usou PDFs sintéticos de três páginas para os três
status e verificou status, citações e hash. Um PDF longo foi recusado sem
truncamento. Isso prova o caminho arquivo-extração-modelo-resolução nesses
exemplos controlados, sem validar arquivos reais, imagens, OCR, vários requisitos
ou consolidação de um projeto completo. `bun run ai:chat` preserva seu padrão
anterior; esta experiência usa `ai:review` e seu checkpoint próprio.
