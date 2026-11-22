import { createContext } from "@confere/api/context";
import { appRouter } from "@confere/api/routers/index";
import { auth } from "@confere/auth";
import { env } from "@confere/env/server";
import { cors } from "@elysiajs/cors";
import { fetchRequestHandler } from "@trpc/server/adapters/fetch";
import { Elysia } from "elysia";

const ALLOWED_REDIRECT_PREFIXES = [
  "confere://",
  "exp://",
  "http://localhost:8081",
  env.CORS_ORIGIN,
];

function escapeHtml(value: string): string {
  return value
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;");
}

new Elysia()
  .use(
    cors({
      origin: env.CORS_ORIGIN,
      methods: ["GET", "POST", "OPTIONS"],
      allowedHeaders: ["Content-Type", "Authorization"],
      credentials: true,
    }),
  )
  .all("/api/auth/*", async (context) => {
    const { request, status } = context;
    if (["POST", "GET"].includes(request.method)) {
      return auth.handler(request);
    }
    return status(405);
  })
  // Página intermediária HTTP porque o Safari no iOS bloqueia redirecionamento 302 direto para exp:// ou confere://.
  .get("/reset-app", ({ query, set }) => {
    const { to, token, error } = query;
    const isAllowed =
      typeof to === "string" &&
      ALLOWED_REDIRECT_PREFIXES.some((prefix) => to.startsWith(prefix));

    if (!isAllowed) {
      set.status = 400;
      return "Link de redirecionamento inválido.";
    }

    let target: URL;
    try {
      target = new URL(to);
    } catch {
      set.status = 400;
      return "Link de redirecionamento inválido.";
    }

    if (token) target.searchParams.set("token", token);
    if (error) target.searchParams.set("error", error);

    const deepLink = target.toString();
    const safeHref = escapeHtml(deepLink);
    const safeJsLink = JSON.stringify(deepLink).replace(/</g, "\\u003c");
    const hasError = Boolean(error);

    const html = `<!doctype html>
<html lang="pt-BR">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Confere · Redefinir senha</title>
  <style>
    body { font-family: -apple-system, BlinkMacSystemFont, "Inter", sans-serif; background: #f6f8fc; color: #141821; margin: 0; min-height: 100vh; display: flex; align-items: center; justify-content: center; padding: 24px; }
    .card { background: #fff; border: 1px solid #e5eaf4; border-radius: 24px; padding: 28px 24px; max-width: 360px; width: 100%; text-align: center; box-shadow: 0 8px 24px rgba(15, 23, 42, 0.06); }
    h1 { font-size: 20px; margin: 0 0 8px; }
    p { font-size: 14px; color: #5b6270; line-height: 1.5; margin: 0 0 22px; }
    a { display: inline-block; background: #2f6bff; color: #fff; text-decoration: none; font-weight: 600; font-size: 15px; padding: 14px 24px; border-radius: 999px; }
  </style>
</head>
<body>
  <div class="card">
    <h1>${hasError ? "Link inválido ou expirado" : "Abrir no Confere"}</h1>
    <p>${hasError ? "Volte ao aplicativo e peça um novo link de recuperação." : "Toque no botão abaixo para abrir o aplicativo e cadastrar sua nova senha."}</p>
    <a href="${safeHref}">Abrir aplicativo</a>
  </div>
  <script>window.location.href = ${safeJsLink};</script>
</body>
</html>`;

    return new Response(html, {
      headers: { "Content-Type": "text/html; charset=utf-8" },
    });
  })
  .all("/trpc/*", async (context) => {
    const res = await fetchRequestHandler({
      endpoint: "/trpc",
      router: appRouter,
      req: context.request,
      createContext: () => createContext({ context }),
    });
    return res;
  })
  .get("/", () => "OK")
  .listen(3000, () => {
    console.log("Server is running on http://localhost:3000");
  });
