import { useRouter } from "expo-router";
import { useState } from "react";
import { Pressable, ScrollView, Text, View } from "react-native";
import { useSafeAreaInsets } from "react-native-safe-area-context";
import { Blob } from "@/components/blob";
import { Icon } from "@/components/icon";
import { ScreenHeader } from "@/components/screen-header";

type FilterTab = "todos" | "pendentes" | "atendidos";

interface ResultItem {
  id: string;
  title: string;
  status: "atendido" | "revisar" | "faltando";
  description?: string;
  citation?: string;
  quote?: string;
}

export default function ConferenceResultScreen() {
  const router = useRouter();
  const insets = useSafeAreaInsets();
  const [tab, setTab] = useState<FilterTab>("todos");
  const [results] = useState<ResultItem[]>([]);

  const atendidosCount = results.filter((r) => r.status === "atendido").length;
  const revisarCount = results.filter((r) => r.status === "revisar").length;
  const faltandoCount = results.filter((r) => r.status === "faltando").length;
  const coverage =
    results.length > 0
      ? Math.round((atendidosCount / results.length) * 100)
      : 0;

  const filtered = results.filter((item) => {
    if (tab === "pendentes") return item.status !== "atendido";
    if (tab === "atendidos") return item.status === "atendido";
    return true;
  });

  return (
    <View className="flex-1 overflow-hidden bg-canvas">
      <Blob
        color="#2F6BFF"
        className="-top-[120px] -left-[80px] size-[360px] opacity-[0.16] dark:opacity-[0.28]"
      />
      <Blob
        color="#10B981"
        className="top-[340px] -right-[140px] size-[300px] opacity-[0.12] dark:opacity-[0.20]"
      />

      <ScreenHeader
        title="Resultado da conferência"
        subtitle="relatório de conformidade"
        rightElement={
          <Pressable
            hitSlop={8}
            className="flex-row items-center gap-1 rounded-xl border border-line-glass bg-glass px-2.5 py-1.5"
          >
            <Icon name="doc.text" fallback="document-text" size={14} color="#2F6BFF" />
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
          paddingBottom: insets.bottom + 40,
        }}
      >
        <View className="mb-6 flex-row items-center rounded-3xl border border-line-glass bg-glass p-5 shadow-sm">
          <View className="size-24 items-center justify-center rounded-full border-4 border-brand/30 bg-brand/10">
            <Text className="text-[26px] font-bold text-brand">
              {results.length > 0 ? `${coverage}%` : "—"}
            </Text>
            <Text className="text-[10px] uppercase font-bold text-ink3">
              cobertura
            </Text>
          </View>

          <View className="ml-5 flex-1 gap-1.5">
            <View className="flex-row items-center justify-between">
              <View className="flex-row items-center gap-2">
                <View className="size-2 rounded-full bg-ok" />
                <Text className="text-[13px] text-ink2">Atendidos</Text>
              </View>
              <Text className="font-mono text-[13px] font-bold text-ink">
                {atendidosCount}
              </Text>
            </View>

            <View className="flex-row items-center justify-between">
              <View className="flex-row items-center gap-2">
                <View className="size-2 rounded-full bg-warn" />
                <Text className="text-[13px] text-ink2">Revisar</Text>
              </View>
              <Text className="font-mono text-[13px] font-bold text-ink">
                {revisarCount}
              </Text>
            </View>

            <View className="flex-row items-center justify-between">
              <View className="flex-row items-center gap-2">
                <View className="size-2 rounded-full bg-err" />
                <Text className="text-[13px] text-ink2">Faltando</Text>
              </View>
              <Text className="font-mono text-[13px] font-bold text-ink">
                {faltandoCount}
              </Text>
            </View>
          </View>
        </View>

        <View className="mb-4 flex-row gap-2">
          <Pressable
            onPress={() => setTab("todos")}
            className={`flex-1 items-center justify-center rounded-2xl py-2.5 border ${
              tab === "todos"
                ? "border-brand bg-brand"
                : "border-line-glass bg-glass"
            }`}
          >
            <Text
              className={`text-[13px] font-semibold ${
                tab === "todos" ? "text-white" : "text-ink2"
              }`}
            >
              Todos {results.length}
            </Text>
          </Pressable>

          <Pressable
            onPress={() => setTab("pendentes")}
            className={`flex-1 items-center justify-center rounded-2xl py-2.5 border ${
              tab === "pendentes"
                ? "border-brand bg-brand"
                : "border-line-glass bg-glass"
            }`}
          >
            <Text
              className={`text-[13px] font-semibold ${
                tab === "pendentes" ? "text-white" : "text-ink2"
              }`}
            >
              Pendentes {revisarCount + faltandoCount}
            </Text>
          </Pressable>

          <Pressable
            onPress={() => setTab("atendidos")}
            className={`flex-1 items-center justify-center rounded-2xl py-2.5 border ${
              tab === "atendidos"
                ? "border-brand bg-brand"
                : "border-line-glass bg-glass"
            }`}
          >
            <Text
              className={`text-[13px] font-semibold ${
                tab === "atendidos" ? "text-white" : "text-ink2"
              }`}
            >
              Atendidos {atendidosCount}
            </Text>
          </Pressable>
        </View>

        {results.length === 0 ? (
          <View className="items-center rounded-3xl border border-line-glass bg-glass p-8 text-center shadow-sm">
            <View className="mb-3 size-12 items-center justify-center rounded-2xl bg-brand/10">
              <Icon
                name="checkmark.circle"
                fallback="checkmark-done-circle-outline"
                size={24}
                color="#2F6BFF"
              />
            </View>
            <Text className="text-[16px] font-semibold text-ink">
              Nenhuma conferência processada
            </Text>
            <Text className="mt-1 text-center text-[13px] text-ink3 leading-relaxed">
              Inicie uma nova conferência enviando um arquivo para conferir os
              itens.
            </Text>
          </View>
        ) : (
          <View className="gap-3">
            {filtered.map((item) => {
              const isRevisar = item.status === "revisar";
              const isAtendido = item.status === "atendido";

              return (
                <Pressable
                  key={item.id}
                  onPress={() => router.push("/projects/requirement-detail")}
                  className="rounded-2xl border border-line-glass bg-glass p-4 shadow-sm active:opacity-85"
                >
                  <View className="flex-row items-start justify-between gap-2">
                    <View className="flex-1 flex-row items-start gap-2.5">
                      <View
                        className={`mt-1.5 size-2 rounded-full ${
                          isAtendido
                            ? "bg-ok"
                            : isRevisar
                            ? "bg-warn"
                            : "bg-err"
                        }`}
                      />
                      <Text className="flex-1 text-[15px] font-semibold leading-snug text-ink">
                        {item.title}
                      </Text>
                    </View>

                    <View
                      className={`rounded-xl px-2.5 py-1 ${
                        isAtendido
                          ? "bg-ok/10"
                          : isRevisar
                          ? "bg-warn/10"
                          : "bg-err/10"
                      }`}
                    >
                      <Text
                        className={`text-[11px] font-bold uppercase tracking-wider ${
                          isAtendido
                            ? "text-ok"
                            : isRevisar
                            ? "text-warn"
                            : "text-err"
                        }`}
                      >
                        {item.status}
                      </Text>
                    </View>
                  </View>

                  {item.description ? (
                    <Text className="mt-2 text-[13px] leading-relaxed text-ink2">
                      {item.description}
                    </Text>
                  ) : null}

                  {item.citation ? (
                    <View className="mt-3 flex-row items-center justify-between border-t border-line-glass pt-2.5">
                      <Text className="font-mono text-[12px] text-ink3">
                        {item.citation}
                      </Text>
                      <Pressable
                        onPress={(e) => {
                          e.stopPropagation();
                        }}
                      >
                        <Text className="text-[12px] font-semibold text-brand">
                          Abrir no PDF
                        </Text>
                      </Pressable>
                    </View>
                  ) : null}

                  {item.quote ? (
                    <View className="mt-2 rounded-xl bg-canvas/60 p-2.5">
                      <Text className="text-[12px] italic text-ink2 leading-relaxed">
                        {item.quote}
                      </Text>
                    </View>
                  ) : null}
                </Pressable>
              );
            })}
          </View>
        )}
      </ScrollView>
    </View>
  );
}
