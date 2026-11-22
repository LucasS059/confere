import { useQuery } from "@tanstack/react-query";
import { useLocalSearchParams } from "expo-router";
import { ActivityIndicator, ScrollView, Text, View } from "react-native";
import { useSafeAreaInsets } from "react-native-safe-area-context";
import { Blob } from "@/components/ui/blob";
import { Icon } from "@/components/ui/icon";
import { ScreenHeader } from "@/components/ui/screen-header";
import { getResultStatusStyle } from "@/lib/format";
import { trpc } from "@/lib/trpc";

export default function RequirementDetailScreen() {
  const insets = useSafeAreaInsets();
  const { projectId, submissionId, resultId } = useLocalSearchParams<{
    projectId: string;
    submissionId: string;
    resultId: string;
  }>();

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

  const submission = project
    ? submissionId
      ? project.submissions.find((s) => s.id === submissionId)
      : project.submissions[0]
    : undefined;

  const result = submission?.results.find((r) => r.id === resultId);

  if (isError || !project || !submission || !result) {
    return (
      <View className="flex-1 bg-canvas">
        <ScreenHeader title="Detalhe do requisito" />
        <View className="flex-1 items-center justify-center px-6">
          <Text className="text-center font-semibold text-[16px] text-ink">
            Resultado não encontrado
          </Text>
          <Text className="mt-1 text-center text-[13px] text-ink3">
            Não foi possível localizar os detalhes deste requisito.
          </Text>
        </View>
      </View>
    );
  }

  const requirement = project.requirements.find(
    (r) => r.id === result.requirementId,
  );

  const title = requirement?.title ?? "Requisito";
  const status = getResultStatusStyle(result.status);

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
        title="Detalhe do requisito"
        subtitle={submission?.version}
      />

      <ScrollView
        showsVerticalScrollIndicator={false}
        contentContainerStyle={{
          paddingHorizontal: 20,
          paddingTop: 16,
          paddingBottom: insets.bottom + 40,
          gap: 16,
        }}
      >
        <View className="rounded-3xl border border-line-glass bg-glass p-5 shadow-sm">
          <View className="flex-row">
            <View
              className={`flex-row items-center gap-1.5 rounded-full px-3 py-1 ${status.bg}`}
            >
              <View className={`size-2 rounded-full ${status.dot}`} />
              <Text className={`font-semibold text-[12.5px] ${status.text}`}>
                {status.label}
              </Text>
            </View>
          </View>

          <Text className="mt-3 font-bold text-[18px] text-ink leading-[24px]">
            {title}
          </Text>

          {requirement?.description ? (
            <Text className="mt-2 text-[14px] text-ink2 leading-[20px]">
              {requirement.description}
            </Text>
          ) : null}
        </View>

        <View className="rounded-3xl border border-line-glass bg-glass p-5 shadow-sm">
          <Text className="font-semibold text-[15px] text-ink">
            Justificativa
          </Text>

          <Text className="mt-2 text-[14px] text-ink2 leading-[22px]">
            {result.feedback ?? "Sem justificativa registrada."}
          </Text>

          {result.pageNumber !== null && result.pageNumber !== undefined ? (
            <View className="mt-3 flex-row items-center gap-1.5 border-line-glass border-t pt-3">
              <Icon
                name="doc.text"
                fallback="document-text-outline"
                size={15}
                color="#8A91A0"
              />
              <Text className="font-medium text-[13px] text-ink2">
                Localizado na página {result.pageNumber}
              </Text>
            </View>
          ) : null}
        </View>

        {result.quote ? (
          <View className="rounded-3xl border border-line-glass bg-glass p-5 shadow-sm">
            <Text className="font-semibold text-[15px] text-ink">
              Trecho citado do documento
            </Text>

            <View className="mt-3 rounded-2xl bg-card/70 p-3.5">
              <Text className="text-[13.5px] text-ink2 italic leading-[20px]">
                “{result.quote}”
              </Text>
            </View>
          </View>
        ) : null}
      </ScrollView>
    </View>
  );
}
