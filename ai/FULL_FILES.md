# Arquivos completos: integração experimental

Em 04/11/2026 foi iniciado o fluxo da etapa 4, autorizado pelo usuário, sem
declarar conversa e interpretação documental concluídas. Esta etapa não treinou
pesos e não promoveu checkpoints. O chat mantém seu padrão anterior.

## Uso

Na raiz do repositório, com o ambiente Python de treinamento instalado:

```sh
ai/.venv/bin/confere-ai review-project entrega.pdf complemento.docx \
  --requirement "O projeto deve incluir testes." \
  --requirement "O projeto deve incluir backup." \
  --checkpoint ai/runs/document-paired-2026-11-03/last.pt \
  --device mps --output resultado-novo.json
```

Os requisitos são manuais e os arquivos devem ser entregas. O comando aceita
PDF textual e Word `.docx`; `.doc` precisa de conversão. O diretório de saída
deve existir; arquivos existentes são preservados. Sem `--output`, escreve JSON
no stdout. Processamento local, sem envio dos anexos a serviços externos.

## Contrato e cobertura

Cada requisito percorre todo o texto extraído, sem truncamento silencioso.
Trechos cabem no contexto real do checkpoint, reservando 64 tokens de resposta.
Lotes usam até quatro aliases locais; referências retornam ao documento, hash,
unidade original e intervalo de caracteres Unicode, com fim exclusivo. Esses
intervalos referem-se ao texto extraído, não às posições nos bytes do PDF/DOCX.
Documento e checkpoint são carregados de snapshots para manter seus hashes
coerentes com o conteúdo efetivamente usado.

O JSON registra respostas brutas, tokens de entrada, cobertura, avisos e propostas
por requisito. Conflitos entre status conclusivos, unidades sem texto ou qualquer
saída inválida tornam o consolidado inconclusivo. Ausência de evidência em um
trecho não cancela evidência presente em outro. Não há votação nem confiança
inventada; todas as propostas exigem revisão humana. Uma citação literal pode
ser semanticamente irrelevante, mesmo tendo uma referência válida.

`all_extracted_text_processed` significa cobertura do texto extraído. Não cobre
imagens, OCR, tabelas aninhadas, cabeçalhos ou toda a estrutura visual. Não há
busca seletiva nesta primeira versão: custo cresce com texto e requisitos.

## Piloto real de inferência no Mac

Fixtures fictícias: PDF de seis páginas com preenchimento, testes e backup na
última página; DOCX com negação do backup e tabela mencionando relatórios.
Três requisitos autorais, com status esperados por construção, sem revisão
semântica independente. Nenhum TCC real ou teste reservado foi usado.

- Checkpoint: `document-paired-2026-11-03/last.pt`, passo 4.000, MPS,
  contexto 1.024, SHA-256 `42e17d20e5da7c4c418100b6aa1713dd327cc6cbd5a5beedfbd63ef6faca871d`.
- 28.906 caracteres por requisito; 19 lotes por requisito; 57 inferências.
- 16,96 segundos incluindo inicialização da CLI, extração e carga dos pesos.
- Intervalos contíguos e três citações literais auditados contra as fontes.
- 54 saídas inválidas. As três saídas válidas escolheram o registro da equipe,
  sem sustentar nenhum dos requisitos. Todos os consolidados inconclusivos.
- O backup coincide com o rótulo esperado por abstenção, sem detectar o conflito.
  **Cobertura mecânica aprovada; interpretação reprovada.**

Resultados brutos: [JSON](../output/ai/full-file-pilot-2026-11-04.json),
[auditoria](../output/ai/full-file-pilot-2026-11-04.audit.json) e
[PDF](../output/pdf/evaluation/full-file-pilot-2026-11-04.pdf).
Hashes das fontes constam no JSON; fixtures ficam no diretório privado local.
Para reproduzir, usar caminhos novos, pois o script preserva evidências existentes:

```sh
ai/.venv/bin/python ai/scripts/evaluate_full_files.py \
  --directory ai/data/private/full-file-pilot-novo \
  --output output/ai/full-file-pilot-novo.json \
  --report output/pdf/evaluation/full-file-pilot-novo.pdf \
  --checkpoint ai/runs/document-paired-2026-11-03/last.pt
```

## Continuação

O [primeiro treino de contextos longos](DOCUMENT_LONG.md) foi executado em
04/11. Melhorou o formato, mas reprovou interpretação e retenção; o checkpoint
experimental não foi promovido. O guia acima mantém explícito o modelo do
piloto original para preservar sua reprodução.

Preparar treino e validação separados por projeto com contextos extensos,
distratores, evidência distante e contradições entre arquivos. Medir formato,
suporte semântico e retenção de conversa juntos antes de promover pesos.
Depois validar documentos reais anotados e integrar API/simulador. Esta CLI
não comprova interpretação confiável de projetos completos.
