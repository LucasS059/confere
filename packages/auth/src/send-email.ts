import { env } from "@confere/env/server";
import nodemailer from "nodemailer";

interface SendEmailInput {
  to: string;
  subject: string;
  html: string;
  text: string;
}

export async function sendEmail({ to, subject, html, text }: SendEmailInput) {
  const user = env.GMAIL_USER;
  const pass = env.GMAIL_APP_PASSWORD;

  if (Boolean(user) !== Boolean(pass)) {
    throw new Error("Configure GMAIL_USER e GMAIL_APP_PASSWORD juntos no .env");
  }

  if (!user || !pass) {
    if (env.NODE_ENV === "production") {
      throw new Error("GMAIL_USER e GMAIL_APP_PASSWORD não configurados");
    }
    console.log(`[email:dev] para=${to} assunto="${subject}"\n${text}`);
    return;
  }

  const transporter = nodemailer.createTransport({
    service: "gmail",
    auth: { user, pass },
  });

  await transporter.sendMail({
    from: `Confere <${user}>`,
    to,
    subject,
    text,
    html,
  });
}

export function resetPasswordEmail(url: string) {
  return {
    subject: "Redefinir sua senha no Confere",
    text: `Recebemos um pedido para redefinir a senha da sua conta.\n\nAbra o link no celular onde o Confere está instalado:\n${url}\n\nSe não foi você, ignore este e-mail. O link expira em 1 hora.`,
    html: `<p>Recebemos um pedido para redefinir a senha da sua conta.</p><p><a href="${url}">Redefinir senha</a></p><p>Se não foi você, ignore este e-mail. O link expira em 1 hora.</p>`,
  };
}
