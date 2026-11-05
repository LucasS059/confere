import { useRouter } from "expo-router";
import { useToast } from "heroui-native";
import { useState } from "react";
import { ActivityIndicator, Pressable, Text, View } from "react-native";
import { KeyboardAwareScrollView } from "react-native-keyboard-controller";
import { useSafeAreaInsets } from "react-native-safe-area-context";
import { AuthField } from "@/components/auth/auth-field";
import { Blob } from "@/components/ui/blob";
import { ScreenHeader } from "@/components/ui/screen-header";
import { authClient } from "@/lib/auth/client";
import { NETWORK_ERROR_MESSAGE } from "@/lib/auth/error-messages";
import { forgotPasswordSchema } from "@/lib/auth/schemas";

const RESET_REDIRECT_URL = "confere://reset-password";

export default function ForgotPasswordScreen() {
  const router = useRouter();
  const insets = useSafeAreaInsets();
  const { toast } = useToast();

  const [email, setEmail] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);

  async function submit() {
    if (isSubmitting) return;
    const parsed = forgotPasswordSchema.safeParse({ email: email.trim() });
    if (!parsed.success) {
      toast.show({ variant: "danger", label: parsed.error.issues[0].message });
      return;
    }

    setIsSubmitting(true);
    try {
      const { error } = await authClient.requestPasswordReset({
        email: parsed.data.email,
        redirectTo: RESET_REDIRECT_URL,
      });
      if (error) {
        toast.show({
          variant: "danger",
          label: "Não foi possível enviar o link. Tente novamente.",
        });
        return;
      }
      toast.show({
        variant: "success",
        label: "Se houver uma conta com esse e-mail, enviamos o link.",
      });
      router.replace("/login");
    } catch {
      toast.show({ variant: "danger", label: NETWORK_ERROR_MESSAGE });
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <View className="flex-1 overflow-hidden bg-canvas">
      <Blob
        color="#2F6BFF"
        className="-top-[120px] -left-[100px] size-[380px] opacity-[0.20] dark:opacity-[0.34]"
      />
      <Blob
        color="#1E9E62"
        className="top-[360px] -right-[140px] size-[340px] opacity-[0.16] dark:opacity-[0.26]"
      />

      <KeyboardAwareScrollView
        bottomOffset={24}
        keyboardShouldPersistTaps="handled"
        contentContainerStyle={{
          flexGrow: 1,
          gap: 24,
          paddingTop: Math.max(insets.top + 12, 56),
          paddingHorizontal: 24,
          paddingBottom: Math.max(insets.bottom + 24, 40),
        }}
      >
        <ScreenHeader
          title="Recuperar senha"
          onBack={() => router.replace("/login")}
        />

        <View className="gap-2 pt-2">
          <Text className="font-instrument-semibold text-[28px] text-ink leading-[32px] tracking-[-0.7px]">
            Esqueceu a senha?
          </Text>
          <Text className="font-instrument text-[14.5px] text-ink2 leading-[21.5px]">
            Informe o e-mail da sua conta. Enviamos um link para criar uma senha
            nova.
          </Text>
        </View>

        <View className="gap-3">
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
            returnKeyType="send"
            onSubmitEditing={submit}
          />

          <Pressable
            className="h-[54px] items-center justify-center rounded-[27px] bg-brand shadow-brand-button active:opacity-80"
            accessibilityRole="button"
            disabled={isSubmitting}
            onPress={submit}
          >
            {isSubmitting ? (
              <ActivityIndicator color="#fff" />
            ) : (
              <Text className="font-instrument-semibold text-[15px] text-white">
                Enviar link
              </Text>
            )}
          </Pressable>
        </View>

        <Text className="mt-auto text-center font-instrument text-[13px] text-ink2">
          Lembrou?{" "}
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
