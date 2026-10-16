import { useRouter } from "expo-router";
import { useState } from "react";
import { Pressable, ScrollView, Text, View } from "react-native";
import { useSafeAreaInsets } from "react-native-safe-area-context";
import { Blob } from "@/components/blob";
import { ScreenHeader } from "@/components/screen-header";

export default function ConferenceReviewScreen() {
  const router = useRouter();
  const insets = useSafeAreaInsets();
  const [rigor, setRigor] = useState<"padrao" | "rigoroso">("padrao");
  const [documentName] = useState("documento.pdf");
  const [requirementsCount] = useState(0);

  return (
    <View className="flex-1 overflow-hidden bg-canvas">
      <Blob
        color="#2F6BFF"
        className="-top-[120px] -left-[80px] size-[360px] opacity-[0.16] dark:opacity-[0.28]"
      />
      <Blob
        color="#10B981"
        className="top-[320px] -right-[140px] size-[300px] opacity-[0.12] dark:opacity-[0.20]"
      />

      <ScreenHeader title="Revisar e iniciar" />

      <ScrollView
        showsVerticalScrollIndicator={false}
        contentContainerStyle={{
          paddingHorizontal: 20,
          paddingTop: 16,
          paddingBottom: insets.bottom + 100,
        }}
      >
        <View className="mb-6 rounded-2xl border border-line-glass bg-glass p-4 shadow-sm">
          <View className="flex-row items-center justify-between py-2 border-b border-line-glass">
            <Text className="text-[14px] text-ink2">Entrega</Text>
            <View className="flex-row items-center gap-2">
              <Text className="text-[14px] font-semibold text-ink">
                {documentName}
              </Text>
            </View>
          </View>

          <View className="flex-row items-center justify-between py-2 border-b border-line-glass">
            <Text className="text-[14px] text-ink2">Requisitos</Text>
            <View className="flex-row items-center gap-2">
              <Text className="text-[14px] font-semibold text-ink">
                {requirementsCount > 0 ? `${requirementsCount} ativos` : "Nenhum cadastrado"}
              </Text>
              <Pressable onPress={() => router.push("/projects/review-requirements")}>
                <Text className="text-[13px] font-medium text-brand">
                  Revisar
                </Text>
              </Pressable>
            </View>
          </View>

          <View className="flex-row items-center justify-between pt-2">
            <Text className="text-[14px] text-ink2">Comparar com</Text>
            <View className="items-end">
              <Text className="text-[14px] font-semibold text-ink3">Primeira versão</Text>
            </View>
          </View>
        </View>

        <View className="mb-6 gap-2">
          <Text className="text-[14px] font-semibold text-ink">
            Rigor da conferência
          </Text>

          <View className="flex-row rounded-2xl border border-line-glass bg-glass p-1">
            <Pressable
              onPress={() => setRigor("padrao")}
              className={`flex-1 items-center justify-center py-2.5 rounded-xl ${
                rigor === "padrao" ? "bg-card shadow-sm" : ""
              }`}
            >
              <Text
                className={`text-[14px] font-semibold ${
                  rigor === "padrao" ? "text-ink" : "text-ink3"
                }`}
              >
                Padrão
              </Text>
            </Pressable>

            <Pressable
              onPress={() => setRigor("rigoroso")}
              className={`flex-1 items-center justify-center py-2.5 rounded-xl ${
                rigor === "rigoroso" ? "bg-card shadow-sm" : ""
              }`}
            >
              <Text
                className={`text-[14px] font-semibold ${
                  rigor === "rigoroso" ? "text-ink" : "text-ink3"
                }`}
              >
                Rigoroso
              </Text>
            </Pressable>
          </View>

          <Text className="px-1 text-[12px] leading-relaxed text-ink3">
            {rigor === "padrao"
              ? "Padrão aceita evidência parcial como “Revisar”. Rigoroso marca como “Faltando” tudo que não estiver explícito."
              : "Rigoroso marca como “Faltando” tudo que não estiver explicitamente fundamentado com evidência clara."}
          </Text>
        </View>

        <View className="rounded-2xl border border-line-glass bg-glass p-4 shadow-sm">
          <Text className="mb-3 text-[14px] font-semibold text-ink">
            O que a IA vai fazer
          </Text>

          <View className="gap-3">
            <View className="flex-row items-start gap-3">
              <View className="size-6 items-center justify-center rounded-full bg-brand/10">
                <Text className="text-[12px] font-bold text-brand">1</Text>
              </View>
              <Text className="flex-1 text-[13px] leading-snug text-ink2">
                Ler as páginas e indexar por página e linha
              </Text>
            </View>

            <View className="flex-row items-start gap-3">
              <View className="size-6 items-center justify-center rounded-full bg-brand/10">
                <Text className="text-[12px] font-bold text-brand">2</Text>
              </View>
              <Text className="flex-1 text-[13px] leading-snug text-ink2">
                Buscar, para cada requisito, os trechos que o atendem
              </Text>
            </View>

            <View className="flex-row items-start gap-3">
              <View className="size-6 items-center justify-center rounded-full bg-brand/10">
                <Text className="text-[12px] font-bold text-brand">3</Text>
              </View>
              <Text className="flex-1 text-[13px] leading-snug text-ink2">
                Classificar com justificativa, citação e confiança
              </Text>
            </View>
          </View>
        </View>
      </ScrollView>

      <View
        style={{ paddingBottom: Math.max(insets.bottom, 16) }}
        className="absolute bottom-0 left-0 right-0 border-t border-line-glass bg-canvas/90 px-5 pt-3"
      >
        <Pressable
          onPress={() => router.push("/conferences/progress")}
          className="h-13 items-center justify-center rounded-2xl bg-brand shadow-lg shadow-brand/25 active:opacity-90"
        >
          <Text className="text-[16px] font-semibold text-white">
            Iniciar conferência
          </Text>
        </Pressable>
      </View>
    </View>
  );
}
