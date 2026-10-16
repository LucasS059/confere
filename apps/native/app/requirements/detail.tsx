import { useRouter } from "expo-router";
import { useState } from "react";
import { Pressable, ScrollView, Text, View } from "react-native";
import { useSafeAreaInsets } from "react-native-safe-area-context";
import { Ionicons } from "@expo/vector-icons";
import { Blob } from "@/components/blob";
import { ScreenHeader } from "@/components/screen-header";

interface EvidenceItem {
  id: string;
  location: string;
  quote: string;
  coverageNote: string;
}

export default function RequirementDetailScreen() {
  const router = useRouter();
  const insets = useSafeAreaInsets();
  const [isResolved, setIsResolved] = useState(false);
  const [title] = useState("Requisito de conferência");
  const [status] = useState<"atendido" | "revisar" | "faltando">("revisar");
  const [origin] = useState("edital / projeto");
  const [justification] = useState("Aguardando conferência da IA.");
  const [confidence] = useState(0);
  const [evidences] = useState<EvidenceItem[]>([]);
  const [suggestion] = useState("");

  return (
    <View className="flex-1 overflow-hidden bg-canvas">
      <Blob
        color="#2F6BFF"
        className="-top-[120px] -left-[80px] size-[360px] opacity-[0.16] dark:opacity-[0.28]"
      />
      <Blob
        color="#F59E0B"
        className="top-[320px] -right-[140px] size-[300px] opacity-[0.12] dark:opacity-[0.20]"
      />

      <ScreenHeader
        title="Detalhes do Requisito"
        rightElement={
          <Pressable
            hitSlop={8}
            className="flex-row items-center gap-1 rounded-xl border border-line-glass bg-glass px-2.5 py-1.5"
          >
            <Ionicons name="document-text" size={14} color="#2F6BFF" />
            <Text className="font-mono text-[12px] font-bold text-brand">
              PDF
            </Text>
          </Pressable>
        }
      />

      <ScrollView
        showsVerticalScrollIndicator={false}
        contentContainerStyle={{
          paddingHorizontal: 20,
          paddingTop: 16,
          paddingBottom: insets.bottom + 110,
        }}
      >
        <View className="mb-6 gap-2">
          <View className="flex-row items-center gap-2">
            <View
              className={`size-2 rounded-full ${
                isResolved
                  ? "bg-ok"
                  : status === "atendido"
                  ? "bg-ok"
                  : status === "revisar"
                  ? "bg-warn"
                  : "bg-err"
              }`}
            />
            <Text
              className={`text-[12px] font-bold uppercase tracking-wider ${
                isResolved
                  ? "text-ok"
                  : status === "atendido"
                  ? "text-ok"
                  : status === "revisar"
                  ? "text-warn"
                  : "text-err"
              }`}
            >
              {isResolved ? "Resolvido" : status}
            </Text>
          </View>

          <Text className="text-[22px] font-bold tracking-tight leading-snug text-ink">
            {title}
          </Text>

          <Text className="font-mono text-[12px] text-ink3">
            origem: {origin}
          </Text>
        </View>

        <View className="mb-5 rounded-2xl border border-line-glass bg-glass p-4 shadow-sm">
          <Text className="text-[14px] font-bold text-ink mb-1.5">
            Análise do requisito
          </Text>
          <Text className="text-[13px] leading-relaxed text-ink2 mb-4">
            {justification}
          </Text>

          {confidence > 0 && (
            <View className="border-t border-line-glass pt-3 gap-1.5">
              <View className="flex-row items-center justify-between">
                <Text className="text-[12px] font-medium text-ink2">
                  Confiança
                </Text>
                <Text className="font-mono text-[12px] font-bold text-ink">
                  {confidence}%
                </Text>
              </View>
              <View className="h-2 overflow-hidden rounded-full bg-line">
                <View
                  style={{ width: `${confidence}%` }}
                  className="h-full rounded-full bg-warn"
                />
              </View>
            </View>
          )}
        </View>

        <View className="mb-5 gap-3">
          <Text className="text-[15px] font-semibold text-ink">
            Evidências encontradas ({evidences.length})
          </Text>

          {evidences.length === 0 ? (
            <View className="rounded-2xl border border-line-glass bg-glass p-6 text-center shadow-sm">
              <Text className="text-center text-[13px] text-ink3">
                Nenhum trecho de evidência indexado ainda.
              </Text>
            </View>
          ) : (
            evidences.map((ev) => (
              <View
                key={ev.id}
                className="rounded-2xl border border-line-glass bg-glass p-4 shadow-sm gap-2"
              >
                <View className="flex-row items-center justify-between">
                  <Text className="font-mono text-[12px] font-medium text-brand">
                    {ev.location}
                  </Text>
                  <Pressable>
                    <Text className="text-[12px] font-semibold text-brand">
                      Abrir no PDF
                    </Text>
                  </Pressable>
                </View>

                <Text className="text-[13px] italic leading-relaxed text-ink2">
                  “{ev.quote}”
                </Text>

                <Text className="font-mono text-[11px] text-ok">
                  {ev.coverageNote}
                </Text>
              </View>
            ))
          )}
        </View>

        {suggestion ? (
          <View className="rounded-2xl border border-line-glass bg-glass p-4 shadow-sm">
            <Text className="text-[14px] font-bold text-ink mb-1">Sugestão</Text>
            <Text className="text-[13px] leading-relaxed text-ink2">
              {suggestion}
            </Text>
          </View>
        ) : null}
      </ScrollView>

      <View
        style={{ paddingBottom: Math.max(insets.bottom, 16) }}
        className="absolute bottom-0 left-0 right-0 flex-row gap-3 border-t border-line-glass bg-canvas/90 px-5 pt-3"
      >
        <Pressable
          onPress={() => router.back()}
          className="h-13 flex-1 items-center justify-center rounded-2xl border border-line-glass bg-glass active:opacity-80"
        >
          <Text className="text-[15px] font-semibold text-ink2">Discordar</Text>
        </Pressable>

        <Pressable
          onPress={() => {
            setIsResolved(true);
            setTimeout(() => router.back(), 300);
          }}
          className="h-13 flex-1 items-center justify-center rounded-2xl bg-brand shadow-lg shadow-brand/25 active:opacity-90"
        >
          <Text className="text-[15px] font-semibold text-white">
            {isResolved ? "Resolvido!" : "Marcar resolvido"}
          </Text>
        </Pressable>
      </View>
    </View>
  );
}
