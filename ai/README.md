# IA local do Confere

Esta pasta contém preparação de dados, tokenizer BPE e Transformer causal com
treinamento experimental do zero em PyTorch. Há checkpoints locais e geração de
texto experimental, sem integração com o app. O conjunto autoral é mínimo e não
comprova qualidade de análise de projetos reais.

Para treinar, retomar e gerar respostas, veja [o guia de treinamento](TRAINING.md).
O [pré-treino de linguagem em português](PRETRAINING.md) usa um snapshot da
Wikipédia com proveniência e splits por artigo; ainda não é um chat validado.

## Executar

Python 3.9 ou mais recente. Os comandos abaixo partem da raiz do repositório.

```sh
python3 -m venv ai/.venv
ai/.venv/bin/python -m pip install --upgrade pip
ai/.venv/bin/python -m pip install -r ai/requirements.lock
ai/.venv/bin/python -m pip install --no-deps -e ./ai

ai/.venv/bin/confere-ai validate ai/data/authored/examples.jsonl
ai/.venv/bin/confere-ai extract ai/data/authored/documents/biblioteca-enunciado.pdf
ai/.venv/bin/confere-ai extract ai/data/authored/documents/biblioteca-completo.docx
ai/.venv/bin/python -m unittest discover -s ai/tests -v
```

A extração escreve JSON no stdout, sem modificar o arquivo original. Para salvar,
use um diretório local ignorado, como `ai/data/extracted/`. Não sobrescreva o
arquivo de entrada com redirecionamento de shell.

`pyproject.toml` declara as dependências; `requirements.lock` registra o ambiente
usado nesta primeira verificação, incluindo o gerador de fixtures. Não é
necessário instalar PyTorch para executar esta etapa.

## Documentos e localização

- PDF textual: uma unidade por página, como `page:2`, com texto e SHA-256 do arquivo.
- DOCX: parágrafos e linhas das tabelas de primeiro nível, em ordem documental,
  como `paragraph:3` e `table:1:row:2`. Não se inventa uma página para DOCX.
- Os identificadores pertencem à versão do arquivo; mudanças exigem nova extração
  e revisão das referências.
- PDF sem texto: aviso por página e aviso geral quando todo o documento está vazio.
  Uma página vazia pode ser branca ou escaneada; o extrator não distingue isso.
- PDF protegido por senha e o formato legado `.doc` são recusados com mensagem.

Limites do extrator padrão: sem OCR automático, leitura de imagens, compreensão visual de plantas ou
reconstrução das tabelas do PDF. DOCX usa somente o corpo e tabelas de primeiro
nível; caixas de texto, tabelas aninhadas, cabeçalhos, rodapés, notas e revisões
não têm cobertura completa. A presença de texto não comprova extração integral.
Os avisos acompanham o JSON para não tratar conteúdo não lido como conformidade.
O limite de entrada é 50 MiB por arquivo e 100 MiB de conteúdo descompactado no
DOCX. Este é um CLI local, ainda sem isolamento para processar anexos em servidor.

Há um [piloto local de OCR e anotação de um TCC real](research/maua-2240.md),
com execução manual em macOS via `scripts/ocr_pdf.py`. Ele cria uma cópia
pesquisável para o extrator existente; ainda não há OCR automático no app.
Os dados reais são candidatos privados, separados do conjunto autoral.
O [segundo piloto](research/maua-329.md) aplica o processo a uma monografia de
60 páginas, com novos casos sobre evidências, resultados e limitações.

## Contrato dos exemplos

O contrato versionado está em `src/confere_ai/example.schema.json`. Cada linha de
`examples.jsonl` é uma avaliação de um requisito, com:

- `schema_version`, `id`, `project_id` e `split`;
- `provenance`: autoral, variação controlada ou real, condição de uso, revisão e origem;
- `documents`: caminhos relativos ao diretório do JSONL, incluindo a referência e a entrega;
- `requirement`: texto, identificador e citação do enunciado;
- `expected`: status, citações da entrega e justificativa.

`atendido` exige evidência que sustente o requisito. `nao_atendido` é usado neste
conjunto quando existe descumprimento explícito. `evidencia_insuficiente` indica
que os trechos disponíveis não demonstram atendimento; não equivale a aprovação
nem prova que a funcionalidade não existe fora do documento.

O validador confere estrutura, IDs, caminhos, existência das unidades e citações
literais, normalizando apenas espaços. Ele não verifica se uma justificativa faz
sentido ou se o rótulo está semanticamente correto: isso exige revisão.
Não há percentual de confiança; qualquer confiança futura precisa ser calibrada.

## Conjunto autoral

`data/authored/projects.json` contém os textos e rótulos editáveis. O gerador
`scripts/build_authored.py` produz três enunciados PDF, quatro entregas DOCX e
12 exemplos JSONL. Ele usa os rótulos escritos no arquivo fonte, sem modelo externo.

- Treino: biblioteca, entrega completa e variação com acesso indevido, justificativa ausente e prazo reduzido.
- Validação: irrigação da horta, com informação presente, ausente e descumprimento explícito.
- Teste de integração: portal acessível, com restrição de teclado, teste futuro e responsável identificado.

Famílias e variações de um projeto ficam no mesmo split. Arquivos idênticos
também não podem atravessar splits. O validador não reconhece automaticamente
paráfrases ou conversões entre formatos: o `project_id` deve manter juntas todas
as versões e documentos derivados. O conjunto já foi inspecionado durante o
desenvolvimento; não é um teste final cego nem mede generalização de um modelo.

Para reconstruir os fixtures após editar a fonte:

```sh
ai/.venv/bin/python ai/scripts/build_authored.py
ai/.venv/bin/python -m unittest discover -s ai/tests -v
```

Revise novamente todos os rótulos quando alterar os documentos. O gerador e o
validador confirmam que as citações existem, não que as conclusões são verdadeiras.
Os arquivos gerados são fixtures pequenos de integração, não um corpus suficiente
para aprender português e conferência documental.

## Se os projetos antigos não vierem

O código não depende do professor, de uma disciplina ou dos exemplos acima.
Podemos criar novos conjuntos autorais ou incluir materiais públicos com uso
permitido, preservando proveniência e revisão. Materiais reais devem ficar em
`data/private/`, ignorado pelo Git. Verifique autorização e retire identificadores
antes de usá-los; nenhum arquivo é enviado a serviços externos por estes comandos.

Trocar os dados exige ajustar documentos, rótulos e avaliação; não exige alterar
a arquitetura da rede. Isso não elimina a necessidade de dados variados e de
uma avaliação realista antes de afirmar qualidade fora do conjunto autoral.

## Próxima etapa e critérios

1. Revisar os exemplos e ampliar a variedade de requisitos, redações e documentos.
2. Construir um tokenizer BPE usando somente o corpus de treino e um Transformer
   causal com pesos aleatórios. Usar o Karpathy como referência, sem importar
   checkpoints pré-treinados.
3. Começar com um experimento de 10–30 milhões de parâmetros e contexto de
   1.024–2.048 tokens, ajustando apenas após medir memória e velocidade no Mac.
   São hipóteses iniciais, não configurações validadas.
4. Medir sobreajuste em poucos exemplos e depois desempenho em projetos separados.
   Queda de loss ou memorização dos fixtures não demonstram interpretação geral.
5. Desenvolver busca de trechos, tratamento de contexto extenso e consolidação
   entre anexos; validar cobertura antes de resumir documentos completos.
6. Integrar o processo Python ao backend e às telas somente após existir inferência
   real e um contrato de resultado verificado. OCR entra antes de declarar suporte
   a PDFs escaneados.

Avaliação futura: cobertura da extração e dos requisitos, macro-F1 dos três
status, falsos atendimentos, precisão das evidências, abstenções e desempenho
por requisito. Medir tempo por documento e pico de memória com o simulador aberto.
Definir metas numéricas após o primeiro benchmark. O teste final terá documentos
novos e rótulos revisados, separados por projeto e preferencialmente por enunciado.

Branch desta etapa: `ai/primeiro-modelo`. Dados privados, ambientes, checkpoints
e execuções não entram no Git. Commits sem `Co-Authored-By`; PRs sem `Generated with`.
Merge na `main` fica para a integração revisada.
