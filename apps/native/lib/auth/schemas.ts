import z from "zod";

export const emailSchema = z.email("Digite um e-mail válido");

export const newPasswordSchema = z
  .string()
  .min(8, "A senha deve ter pelo menos 8 caracteres");

export const loginSchema = z.object({
  email: emailSchema,
  password: z.string().min(1, "Digite sua senha"),
});

export const signUpSchema = z.object({
  name: z.string().trim().min(2, "Digite seu nome completo"),
  email: emailSchema,
  password: newPasswordSchema,
});

export const forgotPasswordSchema = z.object({ email: emailSchema });

export const resetPasswordSchema = z
  .object({
    password: newPasswordSchema,
    confirmPassword: z.string(),
  })
  .refine((data) => data.password === data.confirmPassword, {
    path: ["confirmPassword"],
    message: "As senhas não coincidem",
  });
