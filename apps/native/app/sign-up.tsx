import { useRouter } from "expo-router";
import { useToast } from "heroui-native";
import { useRef, useState } from "react";
import {
  ActivityIndicator,
  Pressable,
  Text,
  TextInput,
  View,
} from "react-native";
import { KeyboardAwareScrollView } from "react-native-keyboard-controller";
import { useSafeAreaInsets } from "react-native-safe-area-context";
import { useCSSVariable } from "uniwind";
import z from "zod";
import { Blob } from "@/components/blob";
import { CheckMark } from "@/components/check-mark";
import { ScreenHeader } from "@/components/screen-header";
import { authClient } from "@/lib/auth-client";

const signUpSchema = z.object({
  name: z.string().trim().min(2, "Digite seu nome completo"),
  email: z.email("Digite um e-mail válido"),
  password: z.string().min(8, "A senha deve ter pelo menos 8 caracteres"),
});

const GOOGLE_COLORS = ["#EA4335", "#4285F4", "#FBBC05", "#34A853"];

function getPasswordStrength(password: string): {
  level: 0 | 1 | 2 | 3;
  label: string;
} {
  if (!password) return { level: 0, label: "" };
  if (password.length < 6) return { level: 1, label: "Senha fraca" };
  if (password.length < 10) return { level: 2, label: "Senha média" };
  return { level: 3, label: "Senha forte" };
}

export default function SignUpScreen() {
  const router = useRouter();
  const insets = useSafeAreaInsets();
  const { toast } = useToast();
  const emailRef = useRef<TextInput>(null);
  const passwordRef = useRef<TextInput>(null);
  const placeholderColor = useCSSVariable("--ink3") as string | undefined;

  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [emailFocused, setEmailFocused] = useState(false);
  const [showPassword, setShowPassword] = useState(false);
  const [acceptedTerms, setAcceptedTerms] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);

  const isInstitutional = Boolean(
    email.trim() && /(\.edu(\.br)?|\.br)$/i.test(email.trim()),
  );
  const strength = getPasswordStrength(password);

  const showError = (label: string) => toast.show({ variant: "danger", label });
  const comingSoon = () => toast.show({ label: "Em breve" });

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
          error.message || "Não foi possível criar sua conta. Tente novamente.",
        );
      }
    } catch {
      showError("Sem conexão com o servidor. Tente novamente.");
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
        />

        <Text className="font-instrument text-[14.5px] text-ink2 leading-[21.5px]">
          Gratuito para estudantes. Sem limite de{"\n"}conferências.
        </Text>

        <View className="gap-2.5">
          <View className="h-[54px] flex-row items-center gap-2.5 rounded-2xl border border-hair bg-card px-4">
            <Text className="w-[52px] font-instrument text-ink3 text-xs">
              Nome
            </Text>
            <TextInput
              className="h-full flex-1 font-instrument text-[15px] text-ink web:outline-none"
              placeholderTextColor={placeholderColor}
              accessibilityLabel="Nome"
              value={name}
              onChangeText={setName}
              placeholder="Seu nome completo"
              autoComplete="name"
              textContentType="name"
              returnKeyType="next"
              submitBehavior="submit"
              onSubmitEditing={() => emailRef.current?.focus()}
            />
          </View>

          <View
            className={`h-[54px] flex-row items-center gap-2.5 rounded-2xl bg-card px-4 ${
              emailFocused
                ? "border-[1.5px] border-brand"
                : "border border-hair"
            }`}
          >
            <Text className="w-[52px] font-instrument text-ink3 text-xs">
              E-mail
            </Text>
            <TextInput
              ref={emailRef}
              className="h-full flex-1 font-instrument text-[15px] text-ink web:outline-none"
              placeholderTextColor={placeholderColor}
              accessibilityLabel="E-mail"
              value={email}
              onFocus={() => setEmailFocused(true)}
              onBlur={() => setEmailFocused(false)}
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
            />
            {isInstitutional ? (
              <View className="flex-row items-center gap-1 rounded-full bg-ok-soft px-2.5 py-1">
                <View className="size-1.5 rounded-full bg-ok" />
                <Text className="font-instrument-medium text-[11px] text-ok">
                  institucional
                </Text>
              </View>
            ) : null}
          </View>

          <View className="h-[54px] flex-row items-center gap-2.5 rounded-2xl border border-hair bg-card px-4">
            <Text className="w-[52px] font-instrument text-ink3 text-xs">
              Senha
            </Text>
            <TextInput
              ref={passwordRef}
              className="h-full flex-1 font-instrument text-[15px] text-ink tracking-[2.5px] web:outline-none"
              placeholderTextColor={placeholderColor}
              accessibilityLabel="Senha"
              value={password}
              onChangeText={setPassword}
              placeholder="••••••••••"
              secureTextEntry={!showPassword}
              autoComplete="new-password"
              textContentType="newPassword"
              returnKeyType="go"
              onSubmitEditing={submit}
            />
            <Pressable
              accessibilityRole="button"
              onPress={() => setShowPassword((prev) => !prev)}
            >
              <Text className="font-instrument text-[13px] text-ink3">
                {showPassword ? "Ocultar" : "Mostrar"}
              </Text>
            </Pressable>
          </View>

          {strength.level > 0 && (
            <View className="flex-row items-center gap-2 px-1 pt-0.5">
              <View className="h-1 flex-1 rounded-full bg-ok" />
              <View
                className={`h-1 flex-1 rounded-full ${
                  strength.level >= 2 ? "bg-ok" : "bg-hair"
                }`}
              />
              <View
                className={`h-1 flex-1 rounded-full ${
                  strength.level >= 3 ? "bg-ok" : "bg-hair"
                }`}
              />
              <Text className="ml-1 font-instrument-medium text-[11px] text-ok">
                {strength.label}
              </Text>
            </View>
          )}

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

        <View className="flex-row gap-2.5">
          <Pressable
            className="h-[50px] flex-1 flex-row items-center justify-center gap-2 rounded-[25px] border-[0.5px] border-glass-bd bg-glass shadow-glass backdrop-blur-[18px] backdrop-saturate-[180%] active:opacity-80"
            accessibilityRole="button"
            onPress={comingSoon}
          >
            <View className="size-4 rounded-full bg-ink" />
            <Text className="font-instrument-semibold text-ink text-sm">
              Apple
            </Text>
          </Pressable>

          <Pressable
            className="h-[50px] flex-1 flex-row items-center justify-center gap-2 rounded-[25px] border-[0.5px] border-glass-bd bg-glass shadow-glass backdrop-blur-[18px] backdrop-saturate-[180%] active:opacity-80"
            accessibilityRole="button"
            onPress={comingSoon}
          >
            <View className="size-4 flex-row flex-wrap overflow-hidden rounded-full">
              {GOOGLE_COLORS.map((color) => (
                <View
                  key={color}
                  className="size-2"
                  style={{ backgroundColor: color }}
                />
              ))}
            </View>
            <Text className="font-instrument-semibold text-ink text-sm">
              Google
            </Text>
          </Pressable>
        </View>

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
