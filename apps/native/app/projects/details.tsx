import { useQuery } from "@tanstack/react-query";
import { useLocalSearchParams, useRouter } from "expo-router";
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
import { formatShortDate, getCoverageColor } from "@/lib/format";
import { trpc } from "@/lib/trpc";

const STATUS_LABELS: Record<string, string> = {
  concluido: "Conferido",
  processando: "Analisando",
  erro: "Erro na análise",
  aguardando_analise: "Aguardando análise",
};

export default function ProjectDetailsScreen() {
  const router = useRouter();
  const insets = useSafeAreaInsets();
  const { projectId } = useLocalSearchParams<{ projectId: string }>();

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
        <ScreenHeader title="Projeto" />
        <View className="flex-1 items-center justify-center px-6">
          <Text className="text-center font-semibold text-[16px] text-ink">
            Projeto não encontrado
          </Text>
          <Text className="mt-1 text-center text-[13px] text-ink3">
            Verifique sua conexão ou volte para a lista de projetos.
          </Text>
        </View>
      </View>
    );
  }

  const { submissions, requirements } = project;

  const latestEvaluated =
    submissions.find((sub) => sub.coverage !== null) ?? null;
  const latestCoverage = latestEvaluated?.coverage ?? null;

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

      <ScreenHeader title="Projeto" />

      <ScrollView
        showsVerticalScrollIndicator={false}
        contentContainerStyle={{
          paddingHorizontal: 20,
          paddingTop: 16,
          paddingBottom: insets.bottom + 110,
          gap: 18,
        }}
      >
        <View className="rounded-3xl border border-line-glass bg-glass p-5 shadow-sm">
          <Text className="font-bold text-[22px] text-ink leading-[28px]">
            {project.name}
          </Text>
          <Text className="mt-1 text-[13px] text-ink2">
            {project.description
              ? `${project.description} · ${formatShortDate(project.createdAt)}`
              : `Criado ${formatShortDate(project.createdAt)}`}
          </Text>
        </View>

        <View className="flex-row gap-3">
          <Pressable
            onPress={() =>
              router.push({
                pathname: "/projects/review",
                params: { projectId: project.id },
              })
            }
            className="flex-1 items-center rounded-2xl border border-line-glass bg-glass p-3.5 shadow-sm active:opacity-80"
          >
            <Text className="font-bold text-[20px] text-ink">
              {requirements.length}
            </Text>
            <Text className="text-[12px] text-ink3">
              {requirements.length === 1 ? "requisito" : "requisitos"}
            </Text>
          </Pressable>

          <View className="flex-1 items-center rounded-2xl border border-line-glass bg-glass p-3.5 shadow-sm">
            <Text className="font-bold text-[20px] text-ink">
              {submissions.length}
            </Text>
            <Text className="text-[12px] text-ink3">
              {submissions.length === 1 ? "entrega" : "entregas"}
            </Text>
          </View>

          <View className="flex-1 items-center rounded-2xl border border-line-glass bg-glass p-3.5 shadow-sm">
            <Text
              className={`font-bold text-[20px] ${getCoverageColor(latestCoverage)}`}
            >
              {latestCoverage !== null ? `${latestCoverage}%` : "—"}
            </Text>
            <Text className="text-[12px] text-ink3">cobertura</Text>
          </View>
        </View>

        <Pressable
          onPress={() =>
            router.push({
              pathname: "/projects/review",
              params: { projectId: project.id },
            })
          }
          className="flex-row items-center justify-between gap-3 rounded-3xl border border-line-glass bg-glass p-4 shadow-sm active:opacity-80"
        >
          <View className="size-10 items-center justify-center rounded-xl bg-brand/10">
            <Icon
              name="checklist"
              fallback="list-outline"
              size={18}
              color="#2F6BFF"
            />
          </View>

          <View className="flex-1">
            <Text className="font-semibold text-[15px] text-ink">
              Rubrica e requisitos
            </Text>
            <Text numberOfLines={1} className="mt-0.5 text-[12.5px] text-ink2">
              {requirements.length === 0
                ? "Toque para extrair ou adicionar requisitos"
                : `${requirements.length} ${
                    requirements.length === 1
                      ? "requisito cadastrado"
                      : "requisitos cadastrados"
                  }`}
            </Text>
          </View>

          <Icon
            name="chevron.forward"
            fallback="chevron-forward"
            size={16}
            color="#94A3B8"
          />
        </Pressable>

        <View className="gap-2.5">
          <Text className="px-1 font-bold text-[12px] text-ink3 uppercase tracking-wider">
            Entregas
          </Text>

          {submissions.length === 0 ? (
            <View className="items-center gap-1 rounded-3xl border border-line-glass bg-glass px-6 py-8 shadow-sm">
              <Text className="font-semibold text-[15px] text-ink">
                Nenhuma entrega enviada
              </Text>
              <Text className="text-center text-[13px] text-ink3">
                Toque no botão abaixo para enviar a primeira versão.
              </Text>
            </View>
          ) : (
            <View className="overflow-hidden rounded-3xl border border-line-glass bg-glass shadow-sm">
              {submissions.map((sub, idx) => {
                // Compara com submissions[idx + 1] pois a lista vem ordenada da mais recente para a mais antiga.
                const prevSub = submissions[idx + 1];
                const delta =
                  sub.coverage !== null && prevSub && prevSub.coverage !== null
                    ? sub.coverage - prevSub.coverage
                    : null;
                const statusText =
                  STATUS_LABELS[sub.status] ?? "Aguardando análise";

                return (
                  <Pressable
                    key={sub.id}
                    onPress={() =>
                      router.push({
                        pathname: "/projects/result",
                        params: {
                          projectId: project.id,
                          submissionId: sub.id,
                        },
                      })
                    }
                    className={`flex-row items-center justify-between gap-3 px-4 py-4 active:bg-card/50 ${
                      idx < submissions.length - 1
                        ? "border-line-glass border-b"
                        : ""
                    }`}
                  >
                    <View className="flex-1 flex-row items-center gap-3">
                      <View className="size-10 items-center justify-center rounded-full border-2 border-brand/25 bg-brand/10">
                        <Text className="font-bold text-[11px] text-brand">
                          {sub.version.split(" ")[0]}
                        </Text>
                      </View>

                      <View className="flex-1">
                        <Text
                          numberOfLines={1}
                          className="font-semibold text-[14.5px] text-ink"
                        >
                          {sub.version} · {sub.filename}
                        </Text>
                        <Text
                          numberOfLines={1}
                          className="mt-0.5 text-[12px] text-ink2"
                        >
                          {formatShortDate(sub.createdAt)} · {statusText}
                        </Text>
                      </View>
                    </View>

                    <View className="items-end">
                      <Text className="font-bold text-[14px] text-ink">
                        {sub.coverage !== null ? `${sub.coverage}%` : "—"}
                      </Text>
                      {delta !== null && delta !== 0 && (
                        <Text
                          className={`font-semibold text-[11px] ${
                            delta > 0 ? "text-ok" : "text-err"
                          }`}
                        >
                          {delta > 0 ? `+${delta}` : delta}
                        </Text>
                      )}
                    </View>
                  </Pressable>
                );
              })}
            </View>
          )}
        </View>
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
            Nova entrega
          </Text>
        </Pressable>
      </View>
    </View>
  );
}
