import { useRouter } from "expo-router";
import { useState } from "react";
import { Pressable, ScrollView, Text, View } from "react-native";
import { useSafeAreaInsets } from "react-native-safe-area-context";
import { Ionicons } from "@expo/vector-icons";
import { Blob } from "@/components/blob";

interface HistoryCard {
  id: string;
  number: string;
  project: string;
  version: string;
  date: string;
  requirements: number;
  duration: string;
  score: number;
}

interface HistoryGroup {
  section: string;
  items: HistoryCard[];
}

export default function HistoricoTabScreen() {
  const router = useRouter();
  const insets = useSafeAreaInsets();
  const [historyGroups] = useState<HistoryGroup[]>([]);

  return (
    <View className="flex-1 overflow-hidden bg-canvas">
      <Blob
        color="#2F6BFF"
        className="-top-[120px] -left-[80px] size-[360px] opacity-[0.16] dark:opacity-[0.28]"
      />
      <Blob
        color="#10B981"
        className="top-[300px] -right-[120px] size-[300px] opacity-[0.12] dark:opacity-[0.20]"
      />

      <ScrollView
        showsVerticalScrollIndicator={false}
        contentContainerStyle={{
          paddingHorizontal: 20,
          paddingTop: Math.max(insets.top + 16, 50),
          paddingBottom: insets.bottom + 100,
        }}
      >
        <View className="mb-6 flex-row items-center justify-between">
          <Text className="text-[26px] font-bold tracking-tight text-ink">
            Histórico
          </Text>

          <Pressable className="flex-row items-center gap-1.5 rounded-full border border-line-glass bg-glass px-3 py-1.5 shadow-sm">
            <Text className="text-[13px] font-medium text-ink">
              Todos os projetos
            </Text>
            <Ionicons name="chevron-down" size={14} color="#64748B" />
          </Pressable>
        </View>

        {historyGroups.length === 0 ? (
          <View className="items-center rounded-3xl border border-line-glass bg-glass p-8 text-center shadow-sm">
            <View className="mb-3 size-12 items-center justify-center rounded-2xl bg-brand/10">
              <Ionicons name="time-outline" size={24} color="#2F6BFF" />
            </View>
            <Text className="text-[16px] font-semibold text-ink">
              Nenhuma conferência no histórico
            </Text>
            <Text className="mt-1 text-center text-[13px] text-ink3 leading-relaxed">
              Quando você submeter uma entrega contra os requisitos de um
              projeto, o histórico e a evolução de notas aparecerão aqui.
            </Text>
          </View>
        ) : (
          historyGroups.map((group) => {
            return (
              <View key={group.section} className="mb-6">
                <Text className="mb-3 font-mono text-[12px] font-bold tracking-wider text-ink3">
                  {group.section}
                </Text>

                <View className="gap-3">
                  {group.items.map((item) => {
                    const isSuccess = item.score >= 80;
                    const isWarn = item.score >= 60 && item.score < 80;
                    return (
                      <Pressable
                        key={item.id}
                        onPress={() => router.push("/conferences/result")}
                        className="flex-row items-center justify-between rounded-2xl border border-line-glass bg-glass p-4 shadow-sm active:opacity-85"
                      >
                        <View className="flex-row items-center gap-3.5">
                          <View
                            className={`size-11 items-center justify-center rounded-full border-2 ${
                              isSuccess
                                ? "border-ok bg-ok/10"
                                : isWarn
                                ? "border-warn bg-warn/10"
                                : "border-err bg-err/10"
                            }`}
                          >
                            <Text
                              className={`font-mono text-[13px] font-bold ${
                                isSuccess
                                ? "text-ok"
                                : isWarn
                                ? "text-warn"
                                : "text-err"
                              }`}
                            >
                              {item.score}%
                            </Text>
                          </View>

                          <View className="gap-1">
                            <Text className="text-[15px] font-semibold text-ink">
                              {item.number} · {item.project} · {item.version}
                            </Text>
                            <Text className="font-mono text-[12px] text-ink3">
                              {item.date} · {item.requirements} requisitos ·{" "}
                              {item.duration}
                            </Text>
                          </View>
                        </View>

                        <Ionicons
                          name="chevron-forward"
                          size={16}
                          color="#94A3B8"
                        />
                      </Pressable>
                    );
                  })}
                </View>
              </View>
            );
          })
        )}
      </ScrollView>
    </View>
  );
}
