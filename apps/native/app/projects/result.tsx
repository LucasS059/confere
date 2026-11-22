import { useQuery } from "@tanstack/react-query";
import { useLocalSearchParams, useRouter } from "expo-router";
import { useToast } from "heroui-native";
import { useState } from "react";
import {
  ActivityIndicator,
  Pressable,
  ScrollView,
  Text,
  View,
} from "react-native";
import { useSafeAreaInsets } from "react-native-safe-area-context";
import { Blob } from "@/components/ui/blob";
import { Icon } from "@/components/ui/icon";
import { ScreenHeader } from "@/components/ui/screen-header";
import { getResultStatusStyle } from "@/lib/format";
import { trpc } from "@/lib/trpc";

type FilterTab = "todos" | "pendentes" | "atendidos";

export default function ConferenceResultScreen() {
  const router = useRouter();
  const insets = useSafeAreaInsets();
  const { toast } = useToast();
  const { projectId, submissionId } = useLocalSearchParams<{
    projectId: string;
    submissionId: string;
  }>();
  const [tab, setTab] = useState<FilterTab>("todos");

  const {
    data: project,
    isLoading,
    isError,
  } = useQuery(
    trpc.project.getById.queryOptions(
      { id: projectId ?? "" },
      { enabled: Boolean(projectId) },
    ),
  );

  if (isLoading) {
    return (
      <View className="flex-1 items-center justify-center bg-canvas">
        <ActivityIndicator color="#2F6BFF" />
      </View>
    );
  }

  if (isError || !project) {
    return (
      <View className="flex-1 bg-canvas">
        <ScreenHeader title="Resultado" />
        <View className="flex-1 items-center justify-center px-6">
          <Text className="text-center font-semibold text-[16px] text-ink">
            Projeto não encontrado
          </Text>
          <Text className="mt-1 text-center text-[13px] text-ink3">
            Não foi possível carregar o resultado desta entrega.
          </Text>
        </View>
      </View>
    );
  }

  const submission = submissionId
    ? project.submissions.find((s) => s.id === submissionId)
    : project.submissions[0];

  if (!submission) {
    return (
      <View className="flex-1 bg-canvas">
        <ScreenHeader title="Resultado" subtitle={project.name} />
        <View className="flex-1 items-center justify-center px-6">
          <Text className="text-center font-semibold text-[16px] text-ink">
            {submissionId
              ? "Entrega não encontrada"
              : "Nenhuma entrega enviada"}
          </Text>
          <Text className="mt-1 text-center text-[13px] text-ink3">
            {submissionId
              ? "Esta entrega não existe mais ou foi removida."
              : "Envie a primeira versão para conferir os requisitos."}
          </Text>
        </View>
      </View>
    );
  }

  const requirementMap = new Map(project.requirements.map((r) => [r.id, r]));
  const results = submission.results;

  const atendidosCount = results.filter((r) => r.status === "atendido").length;
  const revisarCount = results.filter((r) => r.status === "revisar").length;
  const faltandoCount = results.filter((r) => r.status === "faltando").length;
  const coverage = submission.coverage;

  const scoreboard = [
    { label: "Atendidos", count: atendidosCount, dot: "bg-ok" },
    { label: "Revisar", count: revisarCount, dot: "bg-warn" },
    { label: "Faltando", count: faltandoCount, dot: "bg-err" },
  ];

  const filterTabs: { key: FilterTab; label: string }[] = [
    { key: "todos", label: `Todos ${results.length}` },
    { key: "pendentes", label: `Pendentes ${revisarCount + faltandoCount}` },
    { key: "atendidos", label: `Atendidos ${atendidosCount}` },
  ];

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
        className="top-[320px] -right-[120px] size-[300px] opacity-[0.12] dark:opacity-[0.20]"
      />

      <ScreenHeader
        title={submission ? `Entrega ${submission.version}` : "Resultado"}
        subtitle={submission?.filename ?? project.name}
      />

      <ScrollView
        showsVerticalScrollIndicator={false}
        contentContainerStyle={{
          paddingHorizontal: 20,
          paddingTop: 16,
          paddingBottom: insets.bottom + 110,
          gap: 16,
        }}
      >
        <View className="flex-row items-center rounded-3xl border border-line-glass bg-glass p-5 shadow-sm">
          <View className="size-22 items-center justify-center rounded-full border-4 border-brand/25 bg-brand/8">
            <Text className="font-bold text-[20px] text-ink">
              {coverage !== null ? `${coverage}%` : "—"}
            </Text>
            <Text className="text-[11px] text-ink3">cobertura</Text>
          </View>

          <View className="ml-5 flex-1 gap-2">
            {scoreboard.map((item) => (
              <View
                key={item.label}
                className="flex-row items-center justify-between"
              >
                <View className="flex-row items-center gap-2">
                  <View className={`size-2 rounded-full ${item.dot}`} />
                  <Text className="text-[13.5px] text-ink2">{item.label}</Text>
                </View>
                <Text className="font-bold text-[14px] text-ink">
                  {item.count}
                </Text>
              </View>
            ))}
          </View>
        </View>

        {results.length === 0 ? (
          <View className="items-center rounded-3xl border border-line-glass bg-glass px-6 py-8 shadow-sm">
            <View className="mb-3 size-12 items-center justify-center rounded-2xl bg-brand/10">
              <Icon
                name="checkmark.seal"
                fallback="checkmark-circle-outline"
                size={22}
                color="#2F6BFF"
              />
            </View>
            <Text className="font-semibold text-[16px] text-ink">
              Aguardando conferência
            </Text>
            <Text className="mt-1 text-center text-[13px] text-ink3 leading-[19px]">
              Inicie a análise para comparar esta entrega com os{" "}
              {project.requirements.length} requisitos da rubrica.
            </Text>
            <Pressable
              onPress={() =>
                toast.show({
                  id: "check-pending",
                  label: "Análise automática em breve.",
                })
              }
              className="mt-5 h-[46px] items-center justify-center rounded-full bg-brand px-6 shadow-brand-button active:opacity-85"
            >
              <Text className="font-semibold text-[14px] text-white">
                Iniciar conferência
              </Text>
            </Pressable>
          </View>
        ) : (
          <>
            <View className="flex-row rounded-2xl border border-line-glass bg-glass p-1 shadow-sm">
              {filterTabs.map((item) => {
                const active = tab === item.key;
                return (
                  <Pressable
                    key={item.key}
                    onPress={() => setTab(item.key)}
                    className={`flex-1 items-center justify-center rounded-xl py-2 ${
                      active ? "bg-card shadow-sm" : ""
                    }`}
                  >
                    <Text
                      className={`text-[12.5px] ${
                        active
                          ? "font-semibold text-ink"
                          : "font-medium text-ink3"
                      }`}
                    >
                      {item.label}
                    </Text>
                  </Pressable>
                );
              })}
            </View>

            <View className="overflow-hidden rounded-3xl border border-line-glass bg-glass shadow-sm">
              {filtered.map((item, idx) => {
                const style = getResultStatusStyle(item.status);

                return (
                  <Pressable
                    key={item.id}
                    onPress={() =>
                      router.push({
                        pathname: "/projects/requirement-detail",
                        params: {
                          projectId: project.id,
                          submissionId: submission.id,
                          resultId: item.id,
                        },
                      })
                    }
                    className={`p-4 active:bg-card/50 ${
                      idx < filtered.length - 1
                        ? "border-line-glass border-b"
                        : ""
                    }`}
                  >
                    <View className="flex-row items-center justify-between gap-3">
                      <View className="flex-1 flex-row items-center gap-2.5">
                        <View
                          className={`size-2 shrink-0 rounded-full ${style.dot}`}
                        />
                        <Text
                          numberOfLines={2}
                          className="flex-1 font-semibold text-[14.5px] text-ink"
                        >
                          {requirementMap.get(item.requirementId)?.title ??
                            "Requisito"}
                        </Text>
                      </View>

                      <View
                        className={`rounded-full px-2.5 py-0.5 ${style.bg}`}
                      >
                        <Text
                          className={`font-semibold text-[11.5px] ${style.text}`}
                        >
                          {style.label}
                        </Text>
                      </View>
                    </View>

                    {item.feedback ? (
                      <Text className="mt-1.5 pl-4.5 text-[13px] text-ink2 leading-[19px]">
                        {item.feedback}
                      </Text>
                    ) : null}

                    {item.quote ? (
                      <View className="mt-2 ml-4.5 rounded-2xl bg-card/70 p-3">
                        <Text
                          numberOfLines={2}
                          className="text-[12.5px] text-ink2 italic leading-[18px]"
                        >
                          “{item.quote}”
                        </Text>
                      </View>
                    ) : null}
                  </Pressable>
                );
              })}
            </View>
          </>
        )}
      </ScrollView>

      <View
        pointerEvents="box-none"
        style={{ paddingBottom: Math.max(insets.bottom, 18) }}
        className="absolute right-0 bottom-0 left-0 px-5"
      >
        <Pressable
          onPress={() =>
            router.push({
              pathname: "/projects/submission",
              params: { projectId: project.id },
            })
          }
          className="h-[52px] items-center justify-center rounded-full bg-brand shadow-brand-button active:opacity-85"
        >
          <Text className="font-semibold text-[15px] text-white">
            Enviar nova entrega
          </Text>
        </Pressable>
      </View>
    </View>
  );
}
