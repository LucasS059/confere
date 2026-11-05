interface AuthError {
  code?: string;
  status?: number;
  message?: string;
}

const MESSAGES: Record<string, string> = {
  INVALID_EMAIL_OR_PASSWORD: "E-mail ou senha incorretos",
  USER_ALREADY_EXISTS: "Já existe uma conta com este e-mail",
  USER_ALREADY_EXISTS_USE_ANOTHER_EMAIL: "Já existe uma conta com este e-mail",
  PASSWORD_TOO_SHORT: "A senha deve ter pelo menos 8 caracteres",
  INVALID_TOKEN: "Link inválido ou expirado. Peça um novo.",
  EMAIL_NOT_VERIFIED: "Confirme seu e-mail antes de entrar",
};

export const NETWORK_ERROR_MESSAGE =
  "Sem conexão com o servidor. Tente novamente.";

export function authErrorMessage(
  error: AuthError | null | undefined,
  fallback: string,
): string {
  if (error?.code && MESSAGES[error.code]) return MESSAGES[error.code];
  return fallback;
}
