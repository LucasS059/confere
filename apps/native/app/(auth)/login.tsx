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
import { AuthField } from "@/components/auth/auth-field";
import { SocialButtons } from "@/components/auth/social-buttons";
import { Blob } from "@/components/ui/blob";
import { Logo } from "@/components/ui/logo";
import { authClient } from "@/lib/auth/client";
import {
  authErrorMessage,
  NETWORK_ERROR_MESSAGE,
} from "@/lib/auth/error-messages";
import { loginSchema } from "@/lib/auth/schemas";

export default function Login() {
  const router = useRouter();
  const { toast } = useToast();
  const passwordRef = useRef<TextInputInstance>(null);
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);

  const showError = (label: string) => toast.show({ variant: "danger", label });

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
          authErrorMessage(error, "Não foi possível entrar. Tente novamente."),
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
          <View className="size-14 items-center justify-center">
            <Logo size={56} />
          </View>
          <Text className="font-instrument-semibold text-[28px] text-ink leading-[32.2px] tracking-[-0.7px]">
            Entrar no Confere
          </Text>
          <Text className="font-instrument text-[15px] text-ink2 leading-[22.5px]">
            Seus projetos e conferências ficam salvos na sua conta.
          </Text>
        </View>

        <View className="gap-2.5">
          <AuthField
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
          />
          <AuthField
            ref={passwordRef}
            label="Senha"
            className="tracking-[3px]"
            value={password}
            onChangeText={setPassword}
            placeholder="••••••••"
            secureTextEntry
            autoComplete="current-password"
            textContentType="password"
            returnKeyType="go"
            onSubmitEditing={submit}
            trailing={
              <Text
                className="font-instrument-medium text-[13px] text-brand"
                accessibilityRole="button"
                onPress={() => router.push("/forgot-password")}
              >
                Esqueci
              </Text>
            }
          />
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

        <SocialButtons onPress={() => toast.show({ label: "Em breve" })} />

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
