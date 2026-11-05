import { expo } from "@better-auth/expo";
import { createDb } from "@confere/db";
import * as schema from "@confere/db/schema/auth";
import { env } from "@confere/env/server";
import { betterAuth } from "better-auth";
import { drizzleAdapter } from "better-auth/adapters/drizzle";
import { resetPasswordEmail, sendEmail } from "./send-email";

export function createAuth() {
  const db = createDb();

  return betterAuth({
    database: drizzleAdapter(db, {
      provider: "pg",
      schema: schema,
    }),
    // Origens permitidas
    trustedOrigins: [
      env.CORS_ORIGIN,
      "confere://",
      "confere://*",
      "exp://",
      "exp://*",
      "http://localhost:8081",
    ],
    // Login com e-mail e senha
    emailAndPassword: {
      enabled: true,
      // Senha mínima
      minPasswordLength: 8,
      // Reset de senha: link vale 1 hora e desloga os outros aparelhos
      resetPasswordTokenExpiresIn: 60 * 60,
      revokeSessionsOnPasswordReset: true,
      // Envio do e-mail de reset
      sendResetPassword: async ({ user, url }) => {
        void sendEmail({ to: user.email, ...resetPasswordEmail(url) }).catch(
          (error) => console.error("[auth] falha ao enviar e-mail", error),
        );
      },
    },
    // Chave e URL do servidor
    secret: env.BETTER_AUTH_SECRET,
    baseURL: env.BETTER_AUTH_URL,
    // Cookies
    advanced: {
      defaultCookieAttributes: {
        sameSite: "lax",
        secure: env.NODE_ENV === "production",
        httpOnly: true,
      },
    },
    plugins: [expo()],
  });
}

export const auth = createAuth();
