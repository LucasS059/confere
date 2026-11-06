# Segundo piloto de OCR e anotação

Fonte: [Práticas ágeis e arquiteturais para otimização no desenvolvimento de software](https://repositorio.maua.br/handle/MAUA/329),
Mauá, 2022, `CMD03.pdf`, 60 páginas. O original baixado pelo navegador foi
preservado em `ai/data/private/maua-329/original.pdf`, com hash registrado.

## Dados preparados

O OCR local com Apple Vision foi executado nas 60 páginas. A página PDF 2 está
em branco, confirmada visualmente, e permanece sem texto. A cópia pesquisável
tem texto extraível nas outras 59 páginas. As referências usam a posição física
no PDF, não uma numeração inferida do sumário.

Foram preparadas dez avaliações candidatas com checklist autoral: seis
`atendido`, duas `nao_atendido` e duas `evidencia_insuficiente`. As citações foram
conferidas visualmente nas páginas PDF 38, 41, 43, 49, 54, 55 e 56. A revisão
visual incluiu também a página em branco. Não foi feita revisão visual integral
do conteúdo de todas as 60 páginas nem medição de CER/WER.

Os casos cobrem descrição do escopo, critérios de aceite, entrega contínua,
tecnologias, percentuais de correção, limitações metodológicas e erros documentais.
Há exemplos importantes para não confundir:

- percentual de commits de correção com taxa de defeitos do software;
- correlação observada com efeito causal isolado de uma metodologia;
- dados ilustrativos com observações reais;
- texto de erro já presente no PDF com falha do reconhecedor.

Os critérios são exercícios editoriais do Confere, não requisitos oficiais da
Mauá nem uma avaliação acadêmica dos autores. Os rótulos ainda precisam de
revisão independente. A validade das informações externas citadas pelo TCC
não foi auditada; o objetivo é conferir o conteúdo e seus limites documentais.

## Organização local

Dentro de `ai/data/private/maua-329/`, ignorado pelo Git e pelo contexto Docker:

- `source.json`: origem, hash, restrições e escopo da revisão.
- `ocr-v1/`: imagens de páginas, linhas reconhecidas, texto bruto e `searchable.pdf`.
- `annotations-source.json`: critérios, trechos e justificativas editoriais.
- `checklist.pdf`: versão legível dos critérios experimentais.
- `examples.candidate.jsonl`: dez exemplos no contrato versionado.
- `reviewed-excerpts.jsonl`: recortes de entrada e alvos, sem autoria, figuras e
  bibliografia, exceto a mensagem de erro usada no exemplo específico.

Todo este projeto e seus derivados foram designados ao split `validation`.
É uma validação de desenvolvimento já inspecionada, não um teste final cego.
O primeiro TCC permanece no split `train`. A agregação local dos dois conjuntos
está em `ai/data/private/examples.candidate.jsonl`, com 18 exemplos e caminhos
relativos para os quatro documentos de entrada, sem duplicar PDFs.

A condição de uso no treinamento permanece não confirmada, registrada em
`training_eligible: false`. Nenhum corpus aprovado foi substituído e nenhum
treinamento foi executado. A classificação dos arquivos como candidatos e a
metadata deverão ser respeitadas pelo futuro preparador de treinamento; o
validador atual verifica consistência, não libera materiais para treinamento.

## Correções motivadas pelo documento real

O reconhecimento terminou, mas a montagem inicial da cópia falhou em uma página
sem linhas. O gerador agora finaliza explicitamente a página de overlay mesmo
quando ela está vazia; há teste de regressão para esse caso. Foi reaproveitado
o `ocr.json` completo, sem repetir o reconhecimento das 60 páginas.

A mesclagem também expandia streams do PDF e produzia um arquivo acima do
limite de entrada. A compactação sem perda dos streams foi incorporada ao
gerador. A cópia resultante tem cerca de 17,2 MB, abaixo do limite de 50 MiB;
o limite do extrator não foi ampliado.

Verificação concluída: as 60 páginas da cópia compactada renderizaram com pixels
idênticos às imagens do original na mesma resolução. O hash do original foi
preservado, as citações dos dez exemplos e a agregação de 18 candidatos passaram
no validador, e os 22 testes automatizados passaram. A comparação de pixels
confere aparência, não a correção semântica de todo o texto reconhecido.

## Conferir

```sh
ai/.venv/bin/confere-ai validate ai/data/private/maua-329/examples.candidate.jsonl
ai/.venv/bin/confere-ai validate ai/data/private/examples.candidate.jsonl
ai/.venv/bin/python -m unittest discover -s ai/tests -v
```

A qualidade do OCR de imagens, código e diagramas não é garantida. Os exemplos
usam os trechos conferidos, sem assumir que um documento publicado atende todos
os critérios possíveis. O conjunto continua pequeno para treinar um GPT do zero.
