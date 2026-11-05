import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import * as DocumentPicker from "expo-document-picker";
import { useLocalSearchParams, useRouter } from "expo-router";
import { useToast } from "heroui-native";
import { useState } from "react";
import {
  ActivityIndicator,
  Pressable,
  ScrollView,
  Text,
  TextInput,
  View,
} from "react-native";
import { useSafeAreaInsets } from "react-native-safe-area-context";
import { Blob } from "@/components/ui/blob";
import { Icon } from "@/components/ui/icon";
import { ScreenHeader } from "@/components/ui/screen-header";
import { trpc } from "@/lib/trpc";

interface SelectedDocument {
  name: string;
  size: string;
  pages?: number;
}

function formatBytes(bytes?: number): string {
  if (!bytes) return "";
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
}

export default function NewSubmissionScreen() {
  const router = useRouter();
  const insets = useSafeAreaInsets();
  const { toast } = useToast();
  const { projectId } = useLocalSearchParams<{ projectId: string }>();

  const [document, setDocument] = useState<SelectedDocument | null>(null);
  const [version, setVersion] = useState("v1");

  const queryClient = useQueryClient();

  const { data: projectData } = useQuery(
    trpc.project.getById.queryOptions(
      { id: projectId || "" },
      { enabled: Boolean(projectId) },
    ),
  );

  const submissionMutation = useMutation(
    trpc.project.addSubmission.mutationOptions({
      onSuccess: () => {
        queryClient.invalidateQueries(trpc.project.list.queryFilter());
        queryClient.invalidateQueries(
          trpc.project.getById.queryFilter({ id: projectId || "" }),
        );
        toast.show({ label: "Dados da entrega salvos. Análise ainda indisponível." });
        router.push({
          pathname: "/projects/details",
          params: {
            projectId: projectId || "",
          },
        });
      },
      onError: (err) => {
        toast.show({ variant: "danger", label: err.message || "Erro ao submeter" });
      },
    }),
  );

  async function handlePickFile() {
    try {
      const res = await DocumentPicker.getDocumentAsync({
        type: [
          "application/pdf",
          "application/msword",
          "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        ],
        copyToCacheDirectory: true,
      });

      if (!res.canceled && res.assets && res.assets.length > 0) {
        const file = res.assets[0];
        setDocument({
          name: file.name,
          size: formatBytes(file.size) || "Arquivo anexado",
        });
      }
    } catch {
      toast.show({
        variant: "danger",
        label: "Não foi possível selecionar o arquivo",
      });
    }
  }

  function handleSubmit() {
    if (!document) {
      toast.show({
        variant: "danger",
        label: "Selecione o arquivo PDF do trabalho",
      });
      return;
    }
    if (!projectId) {
      toast.show({
        variant: "danger",
        label: "Projeto inválido",
      });
      return;
    }

    submissionMutation.mutate({
      projectId,
      filename: document.name,
      version: version.trim() || "v1",
      fileSize: document.size,
      totalPages: document.pages,
    });
  }

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

      <ScreenHeader
        title="Entrega do trabalho"
        subtitle={projectData?.name || "Cadastrar dados da entrega"}
      />

      <ScrollView
        showsVerticalScrollIndicator={false}
        contentContainerStyle={{
          paddingHorizontal: 20,
          paddingTop: 16,
          paddingBottom: insets.bottom + 120,
        }}
      >
        {document ? (
          <View className="mb-6 items-center rounded-3xl border border-line-glass bg-glass p-6 shadow-sm">
            <View className="mb-3 size-14 items-center justify-center rounded-2xl bg-err/10">
              <Icon
                name="doc.text.fill"
                fallback="document-text"
                size={26}
                color="#EF4444"
              />
            </View>

            <Text className="text-[17px] font-bold text-ink">
              {document.name}
            </Text>
            <Text className="mt-1 font-mono text-[13px] text-ink2">
              {document.pages ? `${document.pages} páginas · ` : ""}
              {document.size}
            </Text>

            <Pressable
              onPress={() => setDocument(null)}
              className="mt-4 rounded-xl border border-line bg-card px-4 py-2"
            >
              <Text className="text-[13px] font-medium text-ink2">
                Trocar arquivo
              </Text>
            </Pressable>
          </View>
        ) : (
          <Pressable
            onPress={handlePickFile}
            className="mb-6 items-center justify-center rounded-3xl border-2 border-dashed border-line-glass bg-glass p-8 active:opacity-75"
          >
            <View className="mb-3 size-14 items-center justify-center rounded-2xl bg-brand/10">
              <Icon
                name="arrow.up.doc"
                fallback="cloud-upload-outline"
                size={28}
                color="#2F6BFF"
              />
            </View>
            <Text className="text-[16px] font-bold text-ink">
              Selecionar relatório em PDF
            </Text>
            <Text className="mt-1 text-center text-[13px] text-ink2">
              Somente nome e tamanho serão salvos. Upload e análise ainda indisponíveis.
            </Text>
          </Pressable>
        )}

        <View className="gap-4 rounded-3xl border border-line-glass bg-glass p-5 shadow-sm">
          <View className="gap-1.5">
            <Text className="text-[13px] font-medium text-ink">
              Identificação da versão
            </Text>
            <View className="h-12 justify-center rounded-2xl border border-hair bg-card px-4">
              <TextInput
                value={version}
                onChangeText={setVersion}
                placeholder="Ex: v1, 1ª entrega, prévia..."
                placeholderTextColor="#94A3B8"
                className="font-instrument text-[14px] text-ink web:outline-none"
              />
            </View>
          </View>

          <View className="flex-row items-center justify-between border-t border-line-glass pt-3">
            <Text className="text-[13px] text-ink2">Requisitos ativos</Text>
            <Text className="text-[14px] font-bold text-ink">
              {projectData?.requirements?.filter((r) => r.checked).length || 0}{" "}
              critérios
            </Text>
          </View>
        </View>
      </ScrollView>

      {/* Botão de Envio */}
      <View
        style={{ paddingBottom: Math.max(insets.bottom, 16) }}
        className="absolute bottom-0 left-0 right-0 border-t border-line-glass bg-glass p-4 backdrop-blur-md"
      >
        <Pressable
          onPress={handleSubmit}
          disabled={submissionMutation.isPending || !document}
          className={`h-[52px] items-center justify-center rounded-2xl bg-brand shadow-brand-button ${
            !document || submissionMutation.isPending ? "opacity-50" : "active:opacity-85"
          }`}
        >
          {submissionMutation.isPending ? (
            <ActivityIndicator color="#fff" />
          ) : (
            <Text className="font-instrument-semibold text-[15px] text-white">
              Salvar dados da entrega
            </Text>
          )}
        </Pressable>
      </View>
    </View>
  );
}
