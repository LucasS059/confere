import { env } from "@confere/env/server";

interface SendEmailInput {
  to: string;
  subject: string;
  html: string;
  text: string;
}

// Envio de e-mail
export async function sendEmail({ to, subject, html, text }: SendEmailInput) {
  if (!env.RESEND_API_KEY) {
    if (env.NODE_ENV === "production") {
      throw new Error("RESEND_API_KEY não configurada");
    }
    console.log(`[email:dev] para=${to} assunto="${subject}"\n${text}`);
    return;
  }

  const response = await fetch("https://api.resend.com/emails", {
    method: "POST",
    headers: {
      Authorization: `Bearer ${env.RESEND_API_KEY}`,
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ from: env.EMAIL_FROM, to, subject, html, text }),
  });

  if (!response.ok) {
    throw new Error(`Falha ao enviar e-mail (${response.status})`);
  }
}

// Texto do e-mail de reset
export function resetPasswordEmail(url: string) {
  return {
    subject: "Redefinir sua senha no Confere",
    text: `Recebemos um pedido para redefinir a senha da sua conta.\n\nAbra o link no celular onde o Confere está instalado:\n${url}\n\nSe não foi você, ignore este e-mail. O link expira em 1 hora.`,
    html: `<p>Recebemos um pedido para redefinir a senha da sua conta.</p><p><a href="${url}">Redefinir senha</a></p><p>Se não foi você, ignore este e-mail. O link expira em 1 hora.</p>`,
  };
}
