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
import { useCSSVariable } from "uniwind";
import z from "zod";
import { Blob } from "@/components/blob";
import { CheckMark } from "@/components/check-mark";
import { authClient } from "@/lib/auth-client";

const loginSchema = z.object({
  email: z.email("Digite um e-mail válido"),
  password: z.string().min(1, "Digite sua senha"),
});

const GOOGLE_COLORS = ["#EA4335", "#4285F4", "#FBBC05", "#34A853"];

export default function Login() {
  const router = useRouter();
  const { toast } = useToast();
  const passwordRef = useRef<TextInput>(null);
  const placeholderColor = useCSSVariable("--ink3") as string | undefined;
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);

  const showError = (label: string) => toast.show({ variant: "danger", label });
  const comingSoon = () => toast.show({ label: "Em breve" });

  async function submit() {
    if (isSubmitting) return;
    const parsed = loginSchema.safeParse({ email: email.trim(), password });
    if (!parsed.success) {
      showError(parsed.error.issues[0].message);
      return;
    }
    setIsSubmitting(true);
    try {
      const { error } = await authClient.signIn.email(parsed.data);
      if (error) {
        showError(
          error.status === 401
            ? "E-mail ou senha incorretos"
            : "Não foi possível entrar. Tente novamente.",
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
        className="-top-[140px] -left-[100px] size-[420px] opacity-[0.22] dark:opacity-[0.38]"
      />
      <Blob
        color="#1E9E62"
        className="top-[300px] -right-[160px] size-[360px] opacity-[0.18] dark:opacity-[0.3]"
      />

      <KeyboardAwareScrollView
        bottomOffset={24}
        keyboardShouldPersistTaps="handled"
        contentContainerStyle={{
          flexGrow: 1,
          gap: 28,
          paddingTop: 120,
          paddingHorizontal: 24,
          paddingBottom: 40,
        }}
      >
        <View className="items-start gap-3.5">
          <Pressable
            onPress={() => router.push("/onboarding")}
            className="size-14 items-center justify-center rounded-[17px] bg-brand-gradient shadow-brand-tile"
          >
            <CheckMark size={30} />
          </Pressable>
          <Text className="font-instrument-semibold text-[28px] text-ink leading-[32.2px] tracking-[-0.7px]">
            Entrar no Confere
          </Text>
          <Text className="font-instrument text-[15px] text-ink2 leading-[22.5px]">
            Seus projetos e conferências ficam salvos na sua conta.
          </Text>
        </View>

        <View className="gap-2.5">
          <View className="h-[54px] flex-row items-center gap-2.5 rounded-2xl border border-hair bg-card px-4">
            <Text className="w-[52px] font-instrument text-ink3 text-xs">
              E-mail
            </Text>
            <TextInput
              className="h-full flex-1 font-instrument text-[15px] text-ink web:outline-none"
              placeholderTextColor={placeholderColor}
              accessibilityLabel="E-mail"
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
            />
          </View>
          <View className="h-[54px] flex-row items-center gap-2.5 rounded-2xl border border-hair bg-card px-4">
            <Text className="w-[52px] font-instrument text-ink3 text-xs">
              Senha
            </Text>
            <TextInput
              ref={passwordRef}
              className="h-full flex-1 font-instrument text-[15px] text-ink tracking-[3px] web:outline-none"
              placeholderTextColor={placeholderColor}
              accessibilityLabel="Senha"
              value={password}
              onChangeText={setPassword}
              placeholder="••••••••"
              secureTextEntry
              autoComplete="current-password"
              textContentType="password"
              returnKeyType="go"
              onSubmitEditing={submit}
            />
            <Text
              className="font-instrument-medium text-[13px] text-brand"
              accessibilityRole="button"
              onPress={() => router.push("/forgot-password")}
            >
              Esqueci
            </Text>
          </View>
          <Pressable
            className="mt-1.5 h-[54px] items-center justify-center rounded-[27px] bg-brand shadow-brand-button active:opacity-80"
            accessibilityRole="button"
            disabled={isSubmitting}
            onPress={submit}
          >
            {isSubmitting ? (
              <ActivityIndicator color="#fff" />
            ) : (
              <Text className="font-instrument-semibold text-[15px] text-white">
                Entrar
              </Text>
            )}
          </Pressable>
        </View>

        <View className="flex-row items-center gap-3">
          <View className="h-px flex-1 bg-hair" />
          <Text className="font-instrument text-ink3 text-xs">ou</Text>
          <View className="h-px flex-1 bg-hair" />
        </View>

        <View className="gap-2.5">
          <Pressable
            className="h-[52px] flex-row items-center justify-center gap-2.5 rounded-[26px] border-[0.5px] border-glass-bd bg-glass shadow-glass backdrop-blur-[18px] backdrop-saturate-[180%] active:opacity-80"
            accessibilityRole="button"
            onPress={comingSoon}
          >
            <View className="size-[18px] rounded-full bg-ink" />
            <Text className="font-instrument-semibold text-ink text-sm">
              Continuar com Apple
            </Text>
          </Pressable>
          <Pressable
            className="h-[52px] flex-row items-center justify-center gap-2.5 rounded-[26px] border-[0.5px] border-glass-bd bg-glass shadow-glass backdrop-blur-[18px] backdrop-saturate-[180%] active:opacity-80"
            accessibilityRole="button"
            onPress={comingSoon}
          >
            <View className="size-[18px] flex-row flex-wrap overflow-hidden rounded-full">
              {GOOGLE_COLORS.map((color) => (
                <View
                  key={color}
                  className="size-[9px]"
                  style={{ backgroundColor: color }}
                />
              ))}
            </View>
            <Text className="font-instrument-semibold text-ink text-sm">
              Continuar com Google
            </Text>
          </Pressable>
        </View>

        <Text className="mt-auto text-center font-instrument text-[13px] text-ink2">
          Novo por aqui?{" "}
          <Text
            className="font-instrument-semibold text-brand"
            accessibilityRole="link"
            onPress={() => router.push("/sign-up")}
          >
            Criar conta
          </Text>
        </Text>
      </KeyboardAwareScrollView>
    </View>
  );
}
