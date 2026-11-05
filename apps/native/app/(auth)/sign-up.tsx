import { useRouter } from "expo-router";
import { useToast } from "heroui-native";
import { useRef, useState } from "react";
import {
  ActivityIndicator,
  Pressable,
  Text,
  type TextInputInstance,
  View,
} from "react-native";
import { KeyboardAwareScrollView } from "react-native-keyboard-controller";
import { useSafeAreaInsets } from "react-native-safe-area-context";
import { AuthField } from "@/components/auth/auth-field";
import { SocialButtons } from "@/components/auth/social-buttons";
import { Blob } from "@/components/ui/blob";
import { CheckMark } from "@/components/ui/check-mark";
import { ScreenHeader } from "@/components/ui/screen-header";
import { authClient } from "@/lib/auth/client";
import {
  authErrorMessage,
  NETWORK_ERROR_MESSAGE,
} from "@/lib/auth/error-messages";
import { signUpSchema } from "@/lib/auth/schemas";

const STRENGTH = [
  null,
  { label: "Senha fraca", bar: "bg-err", text: "text-err" },
  { label: "Senha média", bar: "bg-warn", text: "text-warn" },
  { label: "Senha forte", bar: "bg-ok", text: "text-ok" },
] as const;

function getPasswordStrength(password: string): 0 | 1 | 2 | 3 {
  if (!password) return 0;
  if (password.length < 8) return 1;
  if (password.length < 12) return 2;
  return 3;
}

const INSTITUTIONAL_EMAIL = /\.edu(\.br)?$/i;

export default function SignUpScreen() {
  const router = useRouter();
  const insets = useSafeAreaInsets();
  const { toast } = useToast();
  const emailRef = useRef<TextInputInstance>(null);
  const passwordRef = useRef<TextInputInstance>(null);

  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [acceptedTerms, setAcceptedTerms] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);

  const isInstitutional = INSTITUTIONAL_EMAIL.test(email.trim());
  const strengthLevel = getPasswordStrength(password);
  const strength = STRENGTH[strengthLevel];

  const showError = (label: string) => toast.show({ variant: "danger", label });

  async function submit() {
    if (isSubmitting) return;
    const parsed = signUpSchema.safeParse({
      name: name.trim(),
      email: email.trim(),
      password,
    });
    if (!parsed.success) {
      showError(parsed.error.issues[0].message);
      return;
    }
    if (!acceptedTerms) {
      showError("Aceite os Termos de uso e a Política de privacidade");
      return;
    }

    setIsSubmitting(true);
    try {
      const { error } = await authClient.signUp.email(parsed.data);
      if (error) {
        showError(
          authErrorMessage(
            error,
            "Não foi possível criar sua conta. Tente novamente.",
          ),
        );
      }
    } catch {
      showError(NETWORK_ERROR_MESSAGE);
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <View className="flex-1 overflow-hidden bg-canvas">
      <Blob
        color="#2F6BFF"
        className="-top-[120px] -left-[80px] size-[380px] opacity-[0.20] dark:opacity-[0.34]"
      />
      <Blob
        color="#1E9E62"
        className="top-[320px] -right-[140px] size-[360px] opacity-[0.18] dark:opacity-[0.28]"
      />

      <KeyboardAwareScrollView
        bottomOffset={24}
        keyboardShouldPersistTaps="handled"
        contentContainerStyle={{
          flexGrow: 1,
          gap: 20,
          paddingTop: Math.max(insets.top + 12, 56),
          paddingHorizontal: 24,
          paddingBottom: Math.max(insets.bottom + 24, 40),
        }}
      >
        <ScreenHeader
          title="Criar conta"
          onBack={() => router.replace("/login")}
          safeTop={false}
        />

        <Text className="font-instrument text-[14.5px] text-ink2 leading-[21.5px]">
          Gratuito para estudantes. Sem limite de{"\n"}conferências.
        </Text>

        <View className="gap-2.5">
          <AuthField
            label="Nome"
            value={name}
            onChangeText={setName}
            placeholder="Seu nome completo"
            autoComplete="name"
            textContentType="name"
            returnKeyType="next"
            submitBehavior="submit"
            onSubmitEditing={() => emailRef.current?.focus()}
          />
          <AuthField
            ref={emailRef}
            label="E-mail"
            value={email}
            onChangeText={setEmail}
            placeholder="seu@email.com"
            keyboardType="email-address"
            autoCapitalize="none"
            autoCorrect={false}
            autoComplete="email"
            textContentType="emailAddress"
            returnKeyType="next"
            submitBehavior="submit"
            onSubmitEditing={() => passwordRef.current?.focus()}
            trailing={
              isInstitutional ? (
                <View className="flex-row items-center gap-1 rounded-full bg-ok-soft px-2.5 py-1">
                  <View className="size-1.5 rounded-full bg-ok" />
                  <Text className="font-instrument-medium text-[11px] text-ok">
                    institucional
                  </Text>
                </View>
              ) : null
            }
          />
          <AuthField
            ref={passwordRef}
            label="Senha"
            className="tracking-[2.5px]"
            value={password}
            onChangeText={setPassword}
            placeholder="••••••••••"
            secureTextEntry={!showPassword}
            autoComplete="new-password"
            textContentType="newPassword"
            returnKeyType="go"
            onSubmitEditing={submit}
            trailing={
              <Pressable
                accessibilityRole="button"
                onPress={() => setShowPassword((prev) => !prev)}
              >
                <Text className="font-instrument text-[13px] text-ink3">
                  {showPassword ? "Ocultar" : "Mostrar"}
                </Text>
              </Pressable>
            }
          />

          {strength ? (
            <View className="flex-row items-center gap-2 px-1 pt-0.5">
              {[1, 2, 3].map((step) => (
                <View
                  key={step}
                  className={`h-1 flex-1 rounded-full ${
                    strengthLevel >= step ? strength.bar : "bg-hair"
                  }`}
                />
              ))}
              <Text
                className={`ml-1 font-instrument-medium text-[11px] ${strength.text}`}
              >
                {strength.label}
              </Text>
            </View>
          ) : null}

          <Pressable
            accessibilityRole="checkbox"
            accessibilityState={{ checked: acceptedTerms }}
            onPress={() => setAcceptedTerms((prev) => !prev)}
            className="mt-1 flex-row items-start gap-2.5 px-1"
          >
            <View
              className={`mt-0.5 size-5 items-center justify-center rounded-[6px] ${
                acceptedTerms ? "bg-brand" : "border border-hair bg-card"
              }`}
            >
              {acceptedTerms ? <CheckMark size={12} /> : null}
            </View>
            <Text className="flex-1 font-instrument text-[12.5px] text-ink2 leading-[18px]">
              Li e aceito os{" "}
              <Text className="font-instrument-medium text-brand">
                Termos de uso
              </Text>{" "}
              e a{" "}
              <Text className="font-instrument-medium text-brand">
                Política de privacidade
              </Text>
              . Meus arquivos não são usados para treinar a IA.
            </Text>
          </Pressable>

          <Pressable
            className="mt-2 h-[54px] items-center justify-center rounded-[27px] bg-brand shadow-brand-button active:opacity-80"
            accessibilityRole="button"
            disabled={isSubmitting}
            onPress={submit}
          >
            {isSubmitting ? (
              <ActivityIndicator color="#fff" />
            ) : (
              <Text className="font-instrument-semibold text-[15px] text-white">
                Criar conta
              </Text>
            )}
          </Pressable>
        </View>

        <View className="flex-row items-center gap-3">
          <View className="h-px flex-1 bg-hair" />
          <Text className="font-instrument text-ink3 text-xs">ou</Text>
          <View className="h-px flex-1 bg-hair" />
        </View>

        <SocialButtons
          compact
          onPress={() => toast.show({ label: "Em breve" })}
        />

        <Text className="mt-auto text-center font-instrument text-[13px] text-ink2">
          Já tem conta?{" "}
          <Text
            className="font-instrument-semibold text-brand"
            accessibilityRole="link"
            onPress={() => router.replace("/login")}
          >
            Entrar
          </Text>
        </Text>
      </KeyboardAwareScrollView>
    </View>
  );
}
