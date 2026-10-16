# Confere

Sistema mobile para conferencia, validacao e auditoria de projetos e documentos tecnicos contra requisitos normativos e listas de conformidade.

---

## Sobre o Projeto

O Confere foi desenvolvido para digitalizar e agilizar o processo de auditoria de projetos tecnicos. O sistema permite que usuarios cadastrem projetos, enviem documentos para analise e acompanhem o resultado da conferencia de requisitos com status de conformidade em tempo real.

### Escopo e Telas Implementadas

O aplicativo mobile contempla 16 telas organizadas em tres fluxos principais:

1. **Autenticacao e Entrada (`apps/native/app/(auth)`):**
   - Onboarding e apresentacao da proposta do sistema.
   - Selecao de perfil e boas-vindas.
   - Login de usuario.
   - Cadastro e recuperacao de senha.

2. **Navegacao Principal por Abas (`apps/native/app/(tabs)`):**
   - **Inicio:** Dashboard com resumo das ultimas atividades e metricas.
   - **Conferir:** Atalho direto para iniciar uma nova conferencia.
   - **Historico:** Listagem de todas as conferencias e projetos ja submetidos.
   - **Perfil:** Dados da conta, preferencias e acesso as configuracoes.

3. **Fluxo de Projetos e Conferencia (`apps/native/app/projects`):**
   - Criacao e cadastro de novo projeto.
   - Revisao dos dados preenchidos.
   - Detalhes e especificacoes do projeto.
   - Submissao e upload de documentos.
   - Revisao pre-analise e tela de processamento.
   - Resultado consolidado da conferencia (aprovado, reprovado ou pendente).
   - Detalhamento tecnico de cada requisito avaliado.

---

## Arquitetura

O projeto utiliza a arquitetura de **monorepo** com Turborepo e Bun, garantindo compartilhamento de tipos de ponta a ponta (*end-to-end type safety*):

```
                        App Mobile (React Native / Expo)
                                      │
                         tRPC (HTTP / Typesafe RPC)
                                      │
                        Backend (ElysiaJS / Bun Server)
                                      │
                   ┌──────────────────┴──────────────────┐
                   ▼                                     ▼
        PostgreSQL 17 (Drizzle ORM)             Armazenamento S3 (AWS SDK)
```

### Tecnologias

- **Frontend Mobile (`apps/native`):**
  - React Native (0.86) e Expo SDK (57).
  - Expo Router para navegacao baseada em pastas (`(auth)`, `(tabs)`, `projects`).
  - Tailwind CSS / NativeWind com componentes HeroUI Native.
  - Tipografia padronizada com a fonte **Inter** (`@expo-google-fonts/inter`).
  - Iconografia nativa via `expo-symbols`.
  - Comunicacao via tRPC Client com cache gerenciado por TanStack React Query.
  - Sessao e autenticacao persistidas no Expo SecureStore.

- **Backend (`apps/server`):**
  - Runtime Bun com servidor HTTP ElysiaJS.
  - Procedimentos e rotas tRPC validadas com schemas Zod.
  - Persistencia relacional com PostgreSQL e Drizzle ORM.
  - Autenticacao com Better Auth.
  - Gerenciamento de arquivos e presigned URLs via AWS S3 SDK.

- **Infraestrutura e Padronizacao:**
  - Docker Compose orquestrando banco de dados e servidor.
  - Biome para linting e formatacao de codigo.
  - TypeScript em modo estrito.

---

## Estrutura de Diretorios

```text
confere/
├── apps/
│   ├── native/                  # Aplicativo mobile (React Native / Expo)
│   │   ├── app/                 # Rotas do Expo Router ((auth), (tabs), projects)
│   │   ├── components/          # Componentes visuais e icones
│   │   └── utils/               # Conexao tRPC e clientes de servico
│   │
│   └── server/                  # Backend da aplicacao
│       ├── src/
│       │   ├── auth/            # Regras e plugins do Better Auth
│       │   ├── db/              # Conexao e schemas Drizzle (PostgreSQL)
│       │   ├── storage/         # Adaptador para AWS S3
│       │   ├── trpc/            # Procedures e routers da API
│       │   └── index.ts         # Ponto de entrada do ElysiaJS
│       └── Dockerfile           # Imagem de producao do backend
│
├── packages/
│   └── config/                  # Configuracoes compartilhadas de TypeScript
│
├── docker-compose.yml           # Orquestracao do PostgreSQL e Backend
├── biome.json                   # Regras de formatacao e linter
└── package.json                 # Scripts do monorepo e dependencias raiz
```

---

## Como Rodar o Projeto

### Pre-requisitos

- [Bun](https://bun.sh/) (v1.2+)
- [Docker](https://www.docker.com/) e Docker Compose
- Dispositivo com o aplicativo **Expo Go** instalado ou emulador Android/iOS

---

### Opcao 1: Rodando com Docker (Recomendado)

O Docker Compose do projeto sobe tanto o banco PostgreSQL quanto o servidor backend (que aplica as migracoes do banco automaticamente ao inicializar).

1. **Instale as dependencias na raiz:**
   ```bash
   bun install
   ```

2. **Suba os containers (PostgreSQL e Servidor):**
   ```bash
   bun run docker:up
   ```
   *O PostgreSQL subira na porta `5433` e o servidor na porta `3000`.*

3. **Inicie o aplicativo mobile:**
   ```bash
   bun run dev:native
   ```
   *Pressione `a` para abrir no Android, `i` para iOS, ou escaneie o QR Code no terminal com o app Expo Go no celular.*

Para acompanhar os logs ou encerrar os containers:
```bash
bun run docker:logs   # Ver logs do backend e banco
bun run docker:down   # Parar os containers
```

---

### Opcao 2: Desenvolvimento Local (Apenas Banco no Docker)

Se desejar rodar o backend localmente com hot-reload ativo durante o desenvolvimento:

1. **Inicie apenas o PostgreSQL via Docker:**
   ```bash
   docker compose up -d postgres
   ```

2. **Sincronize o schema com o banco:**
   ```bash
   bun run db:push
   ```

3. **Inicie o backend:**
   ```bash
   bun run dev:server
   ```

4. **Em outro terminal, inicie o app mobile:**
   ```bash
   bun run dev:native
   ```

---

## Comandos Uteis

| Comando | Descricao |
|---|---|
| `bun run check-types` | Checagem de tipos estrita do TypeScript em todo o monorepo |
| `bun run check` | Analise estatica e formatacao automatica com o Biome |
| `bun run db:push` | Sincroniza alteracoes do schema Drizzle com o PostgreSQL |
| `bun run db:studio` | Interface visual no navegador para inspecionar tabelas do banco |
| `bun run docker:up` | Constroi e inicia os containers Docker em segundo plano |
| `bun run docker:down` | Encerra os containers Docker |
