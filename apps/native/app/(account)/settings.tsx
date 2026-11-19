import { useRouter } from "expo-router";
import { Pressable, ScrollView, Text, View } from "react-native";
import { useSafeAreaInsets } from "react-native-safe-area-context";
import { Blob } from "@/components/ui/blob";
import { Icon } from "@/components/ui/icon";
import { ScreenHeader } from "@/components/ui/screen-header";
import { type ThemeMode, useAppTheme } from "@/contexts/app-theme-context";
import { authClient } from "@/lib/auth/client";

const THEME_OPTIONS: { mode: ThemeMode; label: string }[] = [
  { mode: "system", label: "Sistema" },
  { mode: "light", label: "Claro" },
  { mode: "dark", label: "Escuro" },
];

export default function SettingsScreen() {
  const router = useRouter();
  const insets = useSafeAreaInsets();
  const { mode, setMode } = useAppTheme();
  const { data: session } = authClient.useSession();

  const displayName = session?.user?.name || "Estudante";
  const displayEmail = session?.user?.email || "Não informado";

  return (
    <View className="flex-1 overflow-hidden bg-canvas">
      <Blob
        color="#2F6BFF"
        className="-top-[120px] -left-[80px] size-[360px] opacity-[0.16] dark:opacity-[0.28]"
      />

      <ScreenHeader title="Configurações" />

      <ScrollView
        showsVerticalScrollIndicator={false}
        contentContainerStyle={{
          paddingHorizontal: 20,
          paddingTop: 16,
          paddingBottom: insets.bottom + 40,
        }}
      >
        <View className="mb-6">
          <Text className="mb-2 font-bold font-mono text-[12px] text-ink3 uppercase tracking-wider">
            Aparência
          </Text>

          <View className="rounded-3xl border border-line-glass bg-glass p-4 shadow-sm">
            <Text className="mb-2.5 font-medium text-[14px] text-ink">
              Tema do Aplicativo
            </Text>

            <View className="flex-row rounded-2xl border border-line-glass bg-canvas/60 p-1">
              {THEME_OPTIONS.map((option) => (
                <Pressable
                  key={option.mode}
                  onPress={() => setMode(option.mode)}
                  className={`flex-1 items-center justify-center rounded-xl py-2 ${
                    mode === option.mode ? "bg-card shadow-sm" : ""
                  }`}
                >
                  <Text
                    className={`font-medium text-[13px] ${
                      mode === option.mode
                        ? "font-semibold text-ink"
                        : "text-ink3"
                    }`}
                  >
                    {option.label}
                  </Text>
                </Pressable>
              ))}
            </View>
          </View>
        </View>

        <View className="mb-6">
          <Text className="mb-2 font-bold font-mono text-[12px] text-ink3 uppercase tracking-wider">
            Conta
          </Text>

          <View className="gap-4 rounded-3xl border border-line-glass bg-glass p-4 shadow-sm">
            <View className="flex-row items-center justify-between">
              <View className="gap-0.5">
                <Text className="text-[12px] text-ink3">Nome</Text>
                <Text className="font-medium text-[14px] text-ink">
                  {displayName}
                </Text>
              </View>
            </View>

            <View className="h-[1px] bg-line-glass" />

            <View className="flex-row items-center justify-between">
              <View className="gap-0.5">
                <Text className="text-[12px] text-ink3">E-mail</Text>
                <Text className="font-medium text-[14px] text-ink">
                  {displayEmail}
                </Text>
              </View>
            </View>
          </View>
        </View>

        <View className="mb-8">
          <Text className="mb-2 font-bold font-mono text-[12px] text-ink3 uppercase tracking-wider">
            Sobre o App
          </Text>

          <View className="gap-4 rounded-3xl border border-line-glass bg-glass p-4 shadow-sm">
            <View className="flex-row items-center justify-between">
              <Text className="font-medium text-[14px] text-ink">Versão</Text>
              <Text className="font-mono text-[13px] text-ink2">
                1.0.0 (build 42)
              </Text>
            </View>

            <View className="h-[1px] bg-line-glass" />

            <View className="flex-row items-center justify-between">
              <Text className="font-medium text-[14px] text-ink">Ambiente</Text>
              <Text className="font-mono text-[13px] text-ink2">
                Desenvolvimento
              </Text>
            </View>

            <View className="h-[1px] bg-line-glass" />

            <Pressable
              onPress={() => router.push("/terms")}
              className="flex-row items-center justify-between active:opacity-70"
            >
              <Text className="font-medium text-[14px] text-ink">
                Termos de uso
              </Text>
              <Icon
                name="chevron.forward"
                fallback="chevron-forward"
                size={14}
                color="#94A3B8"
              />
            </Pressable>

            <View className="h-[1px] bg-line-glass" />

            <Pressable
              onPress={() => router.push("/privacy")}
              className="flex-row items-center justify-between active:opacity-70"
            >
              <Text className="font-medium text-[14px] text-ink">
                Política de privacidade
              </Text>
              <Icon
                name="chevron.forward"
                fallback="chevron-forward"
                size={14}
                color="#94A3B8"
              />
            </Pressable>
          </View>
        </View>
      </ScrollView>
    </View>
  );
}
