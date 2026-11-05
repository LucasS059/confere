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
import { trpc } from "@/lib/trpc";

export default function ProjectDetailsScreen() {
  const router = useRouter();
  const insets = useSafeAreaInsets();
  const { projectId } = useLocalSearchParams<{ projectId: string }>();

  const { data: item, isLoading } = useQuery(
    trpc.project.getById.queryOptions(
      { id: projectId || "" },
      { enabled: Boolean(projectId) },
    ),
  );

  if (isLoading || !item) {
    return (
      <View className="flex-1 items-center justify-center bg-canvas">
        <ActivityIndicator color="#2F6BFF" />
      </View>
    );
  }

  const submissions = item.submissions || [];
  const requirements = item.requirements || [];

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

      <ScreenHeader title="Detalhes do Projeto" />

      <ScrollView
        showsVerticalScrollIndicator={false}
        contentContainerStyle={{
          paddingHorizontal: 20,
          paddingTop: 16,
          paddingBottom: insets.bottom + 120,
        }}
      >
        <View className="mb-6 gap-1">
          <Text className="font-mono text-[11px] uppercase tracking-wider text-brand">
            Projeto Acadêmico
          </Text>
          <Text className="text-[24px] font-bold tracking-tight text-ink">
            {item.name}
          </Text>
          <Text className="text-[13px] text-ink2">
            Rubrica: {item.sourceType} ({requirements.length} critérios cadastrados)
          </Text>
        </View>

        <View className="mb-6 flex-row gap-3">
          <View className="flex-1 rounded-2xl border border-line-glass bg-glass p-3.5 shadow-sm">
            <Text className="text-[22px] font-bold text-ink">
              {requirements.length}
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
            <Text className="text-[22px] font-bold text-ink">
              {submissions[0]?.coverage != null
                ? `${submissions[0].coverage}%`
                : "—"}
            </Text>
            <Text className="text-[12px] text-ink3">última nota</Text>
          </View>
        </View>

        {/* Atalho para Requisitos */}
        <Pressable
          onPress={() => {
            router.push({
              pathname: "/projects/review",
              params: { projectId: item.id },
            });
          }}
          className="mb-6 flex-row items-center justify-between rounded-2xl border border-line-glass bg-glass p-4 active:bg-card/60"
        >
          <View className="flex-row items-center gap-3">
            <View className="size-9 items-center justify-center rounded-xl bg-brand/10">
              <Icon
                name="list.bullet.clipboard"
                fallback="list"
                size={18}
                color="#2F6BFF"
              />
            </View>
            <View>
              <Text className="text-[15px] font-bold text-ink">
                Requisitos da Rubrica
              </Text>
              <Text className="text-[12px] text-ink2">
                Ver ou adicionar critérios informados pelo orientador
              </Text>
            </View>
          </View>
          <Icon
            name="chevron.forward"
            fallback="chevron-forward"
            size={16}
            color="#94A3B8"
          />
        </Pressable>

        {/* Seção de Entregas do Trabalho */}
        <View className="mb-3 flex-row items-center justify-between">
          <Text className="text-[17px] font-semibold text-ink">
            Entregas Realizadas
          </Text>
          <Pressable
            onPress={() => {
              router.push({
                pathname: "/projects/submission",
                params: { projectId: item.id },
              });
            }}
          >
            <Text className="text-[13px] font-medium text-brand">
              + Nova entrega
            </Text>
          </Pressable>
        </View>

        {submissions.length === 0 ? (
          <View className="items-center justify-center rounded-2xl border border-line-glass bg-glass p-6 text-center">
            <Text className="text-[14px] font-semibold text-ink">
              Nenhuma entrega cadastrada ainda
            </Text>
            <Text className="mt-1 text-center text-[12px] text-ink2">
              Cadastre os dados da primeira versão. Upload e análise ainda indisponíveis.
            </Text>
            <Pressable
              onPress={() => {
                router.push({
                  pathname: "/projects/submission",
                  params: { projectId: item.id },
                });
              }}
              className="mt-3 rounded-full bg-brand px-4 py-2"
            >
              <Text className="text-[12px] font-semibold text-white">
                Cadastrar entrega do relatório
              </Text>
            </Pressable>
          </View>
        ) : (
          <View className="gap-2.5">
            {submissions.map((sub) => (
              <View
                key={sub.id}
                className="flex-row items-center justify-between rounded-2xl border border-line-glass bg-glass p-4"
              >
                <View className="flex-row items-center gap-3">
                  <View className="size-10 items-center justify-center rounded-xl bg-err/10">
                    <Icon
                      name="doc.text.fill"
                      fallback="document-text"
                      size={20}
                      color="#EF4444"
                    />
                  </View>
                  <View>
                    <Text className="text-[14px] font-bold text-ink">
                      {sub.filename}
                    </Text>
                    <Text className="text-[11px] text-ink3">
                      Versão {sub.version}
                    </Text>
                  </View>
                </View>
                <View className="rounded-full bg-glass px-2.5 py-1">
                  <Text className="font-mono text-[11px] font-bold text-ink2">
                    {sub.status === "concluido"
                      ? "Conferido"
                      : sub.status === "erro"
                        ? "Erro na análise"
                        : sub.status === "processando"
                          ? "Processando"
                          : "Aguardando análise"}
                  </Text>
                </View>
              </View>
            ))}
          </View>
        )}
      </ScrollView>

      {/* Botão de Envio de Nova Versão */}
      <View
        style={{ paddingBottom: Math.max(insets.bottom, 16) }}
        className="absolute bottom-0 left-0 right-0 border-t border-line-glass bg-glass p-4 backdrop-blur-md"
      >
        <Pressable
          onPress={() => {
            router.push({
              pathname: "/projects/submission",
              params: { projectId: item.id },
            });
          }}
          className="h-[52px] items-center justify-center rounded-2xl bg-brand shadow-brand-button active:opacity-85"
        >
          <Text className="font-instrument-semibold text-[15px] text-white">
            Cadastrar nova versão do trabalho
          </Text>
        </Pressable>
      </View>
    </View>
  );
}
