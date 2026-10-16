import { useRouter } from "expo-router";
import { useToast } from "heroui-native";
import { useState } from "react";
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
import { ScreenHeader } from "@/components/screen-header";

const forgotSchema = z.object({
  email: z.email("Digite um e-mail válido"),
});

export default function ForgotPasswordScreen() {
  const router = useRouter();
  const insets = useSafeAreaInsets();
  const { toast } = useToast();
  const placeholderColor = useCSSVariable("--ink3") as string | undefined;

  const [email, setEmail] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);

  async function submit() {
    if (isSubmitting) return;
    const parsed = forgotSchema.safeParse({ email: email.trim() });
    if (!parsed.success) {
      toast.show({
        variant: "danger",
        label: parsed.error.issues[0].message,
      });
      return;
    }

    setIsSubmitting(true);
    try {
      toast.show({
        variant: "success",
        label: "Link de recuperação enviado para seu e-mail",
      });
      router.replace("/login");
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
              returnKeyType="send"
              onSubmitEditing={submit}
            />
          </View>

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

        <View className="flex-row items-start gap-2.5 rounded-2xl border-[0.5px] border-glass-bd bg-glass p-4 shadow-glass backdrop-blur-[18px] backdrop-saturate-[180%]">
          <View className="mt-1.5 size-1.5 rounded-full bg-brand" />
          <Text className="flex-1 font-instrument text-[13px] text-ink2 leading-[19px]">
            Entrou com Apple ou Google? Não há senha para recuperar: volte e use
            o mesmo botão.
          </Text>
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
