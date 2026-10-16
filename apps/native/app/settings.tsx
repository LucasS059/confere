import { useState } from "react";
import { Pressable, ScrollView, Switch, Text, View } from "react-native";
import { useSafeAreaInsets } from "react-native-safe-area-context";
import { Ionicons } from "@expo/vector-icons";
import { Blob } from "@/components/blob";
import { ScreenHeader } from "@/components/screen-header";

export default function SettingsScreen() {
  const insets = useSafeAreaInsets();

  const [theme, setTheme] = useState<"sistema" | "claro" | "escuro">("sistema");
  const [showConfidence, setShowConfidence] = useState(true);
  const [compareVersions, setCompareVersions] = useState(true);
  const [useDataForTraining, setUseDataForTraining] = useState(false);
  const [notifyOnComplete, setNotifyOnComplete] = useState(true);

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
          <Text className="mb-2 font-mono text-[12px] font-bold uppercase tracking-wider text-ink3">
            Aparência
          </Text>

          <View className="rounded-3xl border border-line-glass bg-glass p-4 shadow-sm">
            <Text className="mb-2.5 text-[14px] font-medium text-ink">Tema</Text>

            <View className="flex-row rounded-2xl border border-line-glass bg-canvas/60 p-1">
              <Pressable
                onPress={() => setTheme("sistema")}
                className={`flex-1 items-center justify-center py-2 rounded-xl ${
                  theme === "sistema" ? "bg-card shadow-sm" : ""
                }`}
              >
                <Text
                  className={`text-[13px] font-medium ${
                    theme === "sistema" ? "text-ink font-semibold" : "text-ink3"
                  }`}
                >
                  Sistema
                </Text>
              </Pressable>

              <Pressable
                onPress={() => setTheme("claro")}
                className={`flex-1 items-center justify-center py-2 rounded-xl ${
                  theme === "claro" ? "bg-card shadow-sm" : ""
                }`}
              >
                <Text
                  className={`text-[13px] font-medium ${
                    theme === "claro" ? "text-ink font-semibold" : "text-ink3"
                  }`}
                >
                  Claro
                </Text>
              </Pressable>

              <Pressable
                onPress={() => setTheme("escuro")}
                className={`flex-1 items-center justify-center py-2 rounded-xl ${
                  theme === "escuro" ? "bg-card shadow-sm" : ""
                }`}
              >
                <Text
                  className={`text-[13px] font-medium ${
                    theme === "escuro" ? "text-ink font-semibold" : "text-ink3"
                  }`}
                >
                  Escuro
                </Text>
              </Pressable>
            </View>
          </View>
        </View>

        <View className="mb-6">
          <Text className="mb-2 font-mono text-[12px] font-bold uppercase tracking-wider text-ink3">
            Conferência
          </Text>

          <View className="rounded-3xl border border-line-glass bg-glass p-4 shadow-sm gap-4">
            <Pressable className="flex-row items-center justify-between">
              <View className="gap-0.5">
                <Text className="text-[14px] font-medium text-ink">
                  Rigor padrão
                </Text>
                <Text className="text-[12px] text-ink3">
                  Padrão aceita evidência parcial
                </Text>
              </View>
              <View className="flex-row items-center gap-1">
                <Text className="text-[13px] font-medium text-ink2">
                  Padrão
                </Text>
                <Ionicons name="chevron-forward" size={14} color="#94A3B8" />
              </View>
            </Pressable>

            <View className="h-[1px] bg-line-glass" />

            <View className="flex-row items-center justify-between">
              <View className="flex-1 pr-3 gap-0.5">
                <Text className="text-[14px] font-medium text-ink">
                  Mostrar confiança da IA
                </Text>
                <Text className="text-[12px] text-ink3">
                  Barra e porcentagem por requisito
                </Text>
              </View>
              <Switch
                value={showConfidence}
                onValueChange={setShowConfidence}
                trackColor={{ false: "#CBD5E1", true: "#2F6BFF" }}
              />
            </View>

            <View className="h-[1px] bg-line-glass" />

            <View className="flex-row items-center justify-between">
              <View className="flex-1 pr-3 gap-0.5">
                <Text className="text-[14px] font-medium text-ink">
                  Comparar com versão anterior
                </Text>
                <Text className="text-[12px] text-ink3">
                  Mostra o que mudou entre entregas
                </Text>
              </View>
              <Switch
                value={compareVersions}
                onValueChange={setCompareVersions}
                trackColor={{ false: "#CBD5E1", true: "#2F6BFF" }}
              />
            </View>
          </View>
        </View>

        <View className="mb-8">
          <Text className="mb-2 font-mono text-[12px] font-bold uppercase tracking-wider text-ink3">
            Privacidade e Notificações
          </Text>

          <View className="rounded-3xl border border-line-glass bg-glass p-4 shadow-sm gap-4">
            <Pressable className="flex-row items-center justify-between">
              <View className="gap-0.5">
                <Text className="text-[14px] font-medium text-ink">
                  Apagar arquivos após
                </Text>
                <Text className="text-[12px] text-ink3">
                  Entregas e editais enviados
                </Text>
              </View>
              <View className="flex-row items-center gap-1">
                <Text className="font-mono text-[13px] text-ink2">30 dias</Text>
                <Ionicons name="chevron-forward" size={14} color="#94A3B8" />
              </View>
            </Pressable>

            <View className="h-[1px] bg-line-glass" />

            <View className="flex-row items-center justify-between">
              <View className="flex-1 pr-3 gap-0.5">
                <Text className="text-[14px] font-medium text-ink">
                  Usar meus dados para treinar
                </Text>
                <Text className="text-[12px] text-ink3">
                  Desligado por padrão
                </Text>
              </View>
              <Switch
                value={useDataForTraining}
                onValueChange={setUseDataForTraining}
                trackColor={{ false: "#CBD5E1", true: "#2F6BFF" }}
              />
            </View>

            <View className="h-[1px] bg-line-glass" />

            <View className="flex-row items-center justify-between">
              <View className="flex-1 pr-3 gap-0.5">
                <Text className="text-[14px] font-medium text-ink">
                  Avisar quando a conferência terminar
                </Text>
              </View>
              <Switch
                value={notifyOnComplete}
                onValueChange={setNotifyOnComplete}
                trackColor={{ false: "#CBD5E1", true: "#2F6BFF" }}
              />
            </View>
          </View>
        </View>

        <View className="items-center pb-6">
          <Text className="font-mono text-[12px] text-ink3">
            Confere 1.0 (build 42)
          </Text>
        </View>
      </ScrollView>
    </View>
  );
}
