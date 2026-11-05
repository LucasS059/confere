import { useLocalSearchParams, useRouter } from "expo-router";
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
import { Blob } from "@/components/ui/blob";
import { ScreenHeader } from "@/components/ui/screen-header";
import { authClient } from "@/lib/auth/client";
import {
  authErrorMessage,
  NETWORK_ERROR_MESSAGE,
} from "@/lib/auth/error-messages";
import { resetPasswordSchema } from "@/lib/auth/schemas";

export default function ResetPasswordScreen() {
  const router = useRouter();
  const insets = useSafeAreaInsets();
  const { toast } = useToast();
  const confirmRef = useRef<TextInputInstance>(null);
  const { token, error: linkError } = useLocalSearchParams<{
    token?: string;
    error?: string;
  }>();

  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);

  const linkInvalid = !token || Boolean(linkError);

  async function submit() {
    if (isSubmitting || !token) return;
    const parsed = resetPasswordSchema.safeParse({ password, confirmPassword });
    if (!parsed.success) {
      toast.show({ variant: "danger", label: parsed.error.issues[0].message });
      return;
    }

    setIsSubmitting(true);
    try {
      const { error } = await authClient.resetPassword({
        newPassword: parsed.data.password,
        token,
      });
      if (error) {
        toast.show({
          variant: "danger",
          label: authErrorMessage(
            error,
            "Não foi possível redefinir a senha. Tente novamente.",
          ),
        });
        return;
      }
      toast.show({ variant: "success", label: "Senha atualizada. Entre." });
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
          title="Nova senha"
          onBack={() => router.replace("/login")}
        />

        {linkInvalid ? (
          <View className="gap-4 pt-2">
            <Text className="font-instrument-semibold text-[24px] text-ink">
              Link inválido ou expirado
            </Text>
            <Text className="font-instrument text-[14.5px] text-ink2 leading-[21.5px]">
              Peça um novo link de recuperação para continuar.
            </Text>
            <Pressable
              className="h-[54px] items-center justify-center rounded-[27px] bg-brand shadow-brand-button active:opacity-80"
              accessibilityRole="button"
              onPress={() => router.replace("/forgot-password")}
            >
              <Text className="font-instrument-semibold text-[15px] text-white">
                Pedir novo link
              </Text>
            </Pressable>
          </View>
        ) : (
          <>
            <View className="gap-2 pt-2">
              <Text className="font-instrument-semibold text-[28px] text-ink leading-[32px] tracking-[-0.7px]">
                Crie uma nova senha
              </Text>
              <Text className="font-instrument text-[14.5px] text-ink2 leading-[21.5px]">
                Use pelo menos 8 caracteres. Você será desconectado dos outros
                dispositivos.
              </Text>
            </View>

            <View className="gap-3">
              <AuthField
                label="Senha"
                value={password}
                onChangeText={setPassword}
                placeholder="••••••••••"
                secureTextEntry
                autoComplete="new-password"
                textContentType="newPassword"
                returnKeyType="next"
                submitBehavior="submit"
                onSubmitEditing={() => confirmRef.current?.focus()}
              />
              <AuthField
                ref={confirmRef}
                label="Repetir"
                value={confirmPassword}
                onChangeText={setConfirmPassword}
                placeholder="••••••••••"
                secureTextEntry
                autoComplete="new-password"
                textContentType="newPassword"
                returnKeyType="go"
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
                    Salvar nova senha
                  </Text>
                )}
              </Pressable>
            </View>
          </>
        )}
      </KeyboardAwareScrollView>
    </View>
  );
}
