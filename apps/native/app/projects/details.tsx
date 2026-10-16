import { useRouter } from "expo-router";
import { useState } from "react";
import { Pressable, ScrollView, Text, View } from "react-native";
import { useSafeAreaInsets } from "react-native-safe-area-context";
import { Ionicons } from "@expo/vector-icons";
import { Blob } from "@/components/blob";
import { ScreenHeader } from "@/components/screen-header";

interface SubmissionItem {
  id: string;
  version: string;
  filename: string;
  date: string;
  pages: number;
  score: number;
  diff?: string;
}

export default function ProjectDetailsScreen() {
  const router = useRouter();
  const insets = useSafeAreaInsets();
  const [submissions] = useState<SubmissionItem[]>([]);
  const [projectTitle] = useState("Meu Projeto");
  const [requirementsCount] = useState(0);

  return (
    <View className="flex-1 overflow-hidden bg-canvas">
      <Blob
        color="#2F6BFF"
        className="-top-[120px] -left-[80px] size-[360px] opacity-[0.16] dark:opacity-[0.28]"
      />
      <Blob
        color="#10B981"
        className="top-[300px] -right-[120px] size-[300px] opacity-[0.14] dark:opacity-[0.22]"
      />

      <ScreenHeader
        title="Projeto"
        rightElement={
          <Pressable
            hitSlop={8}
            className="size-9 items-center justify-center rounded-full border border-line-glass bg-glass"
          >
            <Ionicons name="ellipsis-horizontal" size={18} color="#64748B" />
          </Pressable>
        }
      />

      <ScrollView
        showsVerticalScrollIndicator={false}
        contentContainerStyle={{
          paddingHorizontal: 20,
          paddingTop: 16,
          paddingBottom: insets.bottom + 100,
        }}
      >
        <View className="mb-6 gap-2">
          <Text className="font-mono text-[12px] uppercase tracking-wider text-brand">
            Projeto Acadêmico
          </Text>
          <Text className="text-[24px] font-bold tracking-tight text-ink">
            {projectTitle}
          </Text>
          <Text className="text-[14px] text-ink2">
            Acompanhe suas entregas e índice de conformidade
          </Text>
        </View>

        <View className="mb-6 flex-row gap-3">
          <View className="flex-1 rounded-2xl border border-line-glass bg-glass p-3.5 shadow-sm">
            <Text className="text-[22px] font-bold text-ink">
              {requirementsCount}
            </Text>
            <Text className="text-[12px] text-ink3">requisitos</Text>
          </View>
          <View className="flex-1 rounded-2xl border border-line-glass bg-glass p-3.5 shadow-sm">
            <Text className="text-[22px] font-bold text-ink">
              {submissions.length}
            </Text>
            <Text className="text-[12px] text-ink3">entregas</Text>
          </View>
          <View className="flex-1 rounded-2xl border border-line-glass bg-glass p-3.5 shadow-sm">
            <Text className="text-[22px] font-bold text-ink3">—</Text>
            <Text className="text-[12px] text-ink3">última cobertura</Text>
          </View>
        </View>

        <View className="mb-3 flex-row items-center justify-between">
          <Text className="text-[17px] font-semibold text-ink">Entregas</Text>
          <Pressable onPress={() => router.push("/(tabs)/historico")}>
            <Text className="text-[13px] font-medium text-brand">
              Ver histórico
            </Text>
          </Pressable>
        </View>

        {submissions.length === 0 ? (
          <View className="items-center rounded-3xl border border-line-glass bg-glass p-8 text-center shadow-sm">
            <View className="mb-3 size-12 items-center justify-center rounded-2xl bg-brand/10">
              <Ionicons name="document-text-outline" size={24} color="#2F6BFF" />
            </View>
            <Text className="text-[16px] font-semibold text-ink">
              Nenhuma entrega realizada
            </Text>
            <Text className="mt-1 text-center text-[13px] text-ink3 leading-relaxed">
              Envie o primeiro arquivo para o Confere analisar os requisitos do seu
              trabalho.
            </Text>
          </View>
        ) : (
          <View className="gap-3">
            {submissions.map((sub) => {
              return (
                <Pressable
                  key={sub.id}
                  onPress={() => router.push("/conferences/result")}
                  className="flex-row items-center justify-between rounded-2xl border border-line-glass bg-glass p-4 shadow-sm active:opacity-85"
                >
                  <View className="flex-row items-center gap-3.5">
                    <View
                      className={`size-10 items-center justify-center rounded-full border-2 ${
                        sub.score >= 70
                          ? "border-warn/50 bg-warn/10"
                          : "border-err/50 bg-err/10"
                      }`}
                    >
                      <Ionicons
                        name="document-text"
                        size={18}
                        color={sub.score >= 70 ? "#F59E0B" : "#EF4444"}
                      />
                    </View>

                    <View className="gap-1">
                      <Text className="text-[15px] font-semibold text-ink">
                        {sub.version} · {sub.filename}
                      </Text>
                      <Text className="text-[12px] text-ink3">
                        {sub.date} · {sub.pages} páginas
                      </Text>
                    </View>
                  </View>

                  <View className="items-end gap-0.5">
                    <Text
                      className={`text-[16px] font-bold ${
                        sub.score >= 70 ? "text-warn" : "text-err"
                      }`}
                    >
                      {sub.score}%
                    </Text>
                    {sub.diff ? (
                      <Text className="font-mono text-[11px] font-medium text-ok">
                        {sub.diff}
                      </Text>
                    ) : null}
                  </View>
                </Pressable>
              );
            })}
          </View>
        )}
      </ScrollView>

      <View
        style={{ paddingBottom: Math.max(insets.bottom, 16) }}
        className="absolute bottom-0 left-0 right-0 border-t border-line-glass bg-canvas/90 px-5 pt-3"
      >
        <Pressable
          onPress={() => router.push("/submissions/new")}
          className="h-13 items-center justify-center rounded-2xl bg-brand shadow-lg shadow-brand/25 active:opacity-90"
        >
          <Text className="text-[16px] font-semibold text-white">
            Nova entrega
          </Text>
        </Pressable>
      </View>
    </View>
  );
}
