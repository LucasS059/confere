import { cors } from "@elysiajs/cors";
import { fetchRequestHandler } from "@trpc/server/adapters/fetch";
import { Elysia } from "elysia";
import { auth } from "./auth";
import { env } from "./env";
import { createContext } from "./trpc/context";
import { type AppRouter, appRouter } from "./trpc/router";

export type { AppRouter };

export const app = new Elysia()
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
  .all("/trpc/*", async (context) => {
    return fetchRequestHandler({
      endpoint: "/trpc",
      router: appRouter,
      req: context.request,
      createContext: () => createContext({ context }),
    });
  })
  .get("/", () => "OK")
  .listen({ port: 3000, hostname: "0.0.0.0" }, () => {
    console.log("Server is running on http://localhost:3000");
  });
