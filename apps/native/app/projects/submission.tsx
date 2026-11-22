import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import * as DocumentPicker from "expo-document-picker";
import { useLocalSearchParams, useRouter } from "expo-router";
import { useToast } from "heroui-native";
import { useEffect, useState } from "react";
import {
  ActivityIndicator,
  Pressable,
  Text,
  TextInput,
  View,
} from "react-native";
import { KeyboardAwareScrollView } from "react-native-keyboard-controller";
import { useSafeAreaInsets } from "react-native-safe-area-context";
import { useCSSVariable } from "uniwind";
import { Blob } from "@/components/ui/blob";
import { Icon } from "@/components/ui/icon";
import { ScreenHeader } from "@/components/ui/screen-header";
import { trpc } from "@/lib/trpc";

interface SelectedDocument {
  name: string;
  size: string;
  uri: string;
  mimeType?: string;
  extBadge: string;
}

const ACCEPTED_MIME_TYPES = [
  "application/pdf",
  "application/msword",
  "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
  "application/vnd.ms-excel",
  "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
  "text/plain",
];

function formatBytes(bytes?: number): string {
  if (!bytes) return "";
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
}

function getExtBadge(filename: string): string {
  const ext = filename.split(".").pop()?.toUpperCase() ?? "DOC";
  if (ext === "DOCX" || ext === "DOC") return "DOC";
  if (ext === "XLSX" || ext === "XLS") return "XLS";
  if (ext === "TXT") return "TXT";
  return "PDF";
}

export default function NewSubmissionScreen() {
  const router = useRouter();
  const insets = useSafeAreaInsets();
  const { toast } = useToast();
  const placeholderColor = useCSSVariable("--ink3") as string | undefined;
  const { projectId } = useLocalSearchParams<{ projectId: string }>();
  const queryClient = useQueryClient();

  const [document, setDocument] = useState<SelectedDocument | null>(null);
  const [version, setVersion] = useState("v1");
  const [label, setLabel] = useState("");
  const [isUploading, setIsUploading] = useState(false);

  const { data: project } = useQuery(
    trpc.project.getById.queryOptions(
      { id: projectId ?? "" },
      { enabled: Boolean(projectId) },
    ),
  );

  useEffect(() => {
    if (project) {
      const nextNum = project.submissions.length + 1;
      setVersion(`v${nextNum}`);
    }
  }, [project]);

  const getUploadUrlMutation = useMutation(
    trpc.project.getUploadUrl.mutationOptions(),
  );

  const submissionMutation = useMutation(
    trpc.project.addSubmission.mutationOptions({
      onSuccess: (created) => {
        queryClient.invalidateQueries(trpc.project.list.queryFilter());
        queryClient.invalidateQueries(
          trpc.project.getById.queryFilter({ id: projectId ?? "" }),
        );
        router.replace({
          pathname: "/projects/result",
          params: { projectId: projectId ?? "", submissionId: created.id },
        });
      },
      onError: (err) => {
        toast.show({
          id: "submission-error",
          variant: "danger",
          label: err.message || "Erro ao enviar entrega",
        });
      },
    }),
  );

  async function handlePickFile() {
    try {
      const res = await DocumentPicker.getDocumentAsync({
        type: ACCEPTED_MIME_TYPES,
        copyToCacheDirectory: true,
      });

      if (!res.canceled && res.assets?.length) {
        const file = res.assets[0];
        setDocument({
          name: file.name,
          size: formatBytes(file.size),
          uri: file.uri,
          mimeType: file.mimeType,
          extBadge: getExtBadge(file.name),
        });
      }
    } catch {
      toast.show({
        id: "submission-error",
        variant: "danger",
        label: "Não foi possível selecionar o arquivo",
      });
    }
  }

  async function handleSubmit() {
    if (!document || !projectId) {
      toast.show({
        id: "submission-error",
        variant: "danger",
        label: "Selecione o arquivo do trabalho",
      });
      return;
    }

    setIsUploading(true);
    try {
      // Fluxo em 2 etapas: gera URL pré-assinada e sobe o arquivo direto pro S3 antes de salvar no banco.
      const uploadTarget = await getUploadUrlMutation.mutateAsync({
        projectId,
        filename: document.name,
        contentType: document.mimeType,
      });

      if (uploadTarget.mode === "s3" && uploadTarget.uploadUrl) {
        const fileResponse = await fetch(document.uri);
        const blob = await fileResponse.blob();
        const uploadRes = await fetch(uploadTarget.uploadUrl, {
          method: "PUT",
          headers: {
            "Content-Type": document.mimeType || "application/octet-stream",
          },
          body: blob,
        });

        if (!uploadRes.ok) {
          throw new Error("Não foi possível enviar o arquivo ao armazenamento");
        }
      }

      await submissionMutation.mutateAsync({
        projectId,
        filename: document.name,
        version: version.trim() || "v1",
        label: label.trim() || undefined,
        fileSize: document.size || undefined,
        fileUrl: uploadTarget.key,
      });
    } catch (err) {
      toast.show({
        id: "submission-error",
        variant: "danger",
        label:
          err instanceof Error
            ? err.message
            : "Erro ao preparar envio do arquivo",
      });
    } finally {
      setIsUploading(false);
    }
  }

  const isBusy = isUploading || submissionMutation.isPending;

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

      <ScreenHeader title="Nova entrega" subtitle={project?.name} />

      <KeyboardAwareScrollView
        bottomOffset={24}
        keyboardShouldPersistTaps="handled"
        showsVerticalScrollIndicator={false}
        contentContainerStyle={{
          paddingHorizontal: 20,
          paddingTop: 18,
          paddingBottom: insets.bottom + 110,
          gap: 16,
        }}
      >
        <Pressable
          onPress={handlePickFile}
          className="items-center rounded-3xl border border-line-glass bg-glass px-6 py-7 shadow-sm active:opacity-85"
        >
          <View className="size-14 items-center justify-center rounded-2xl bg-brand/10">
            {document ? (
              <Text className="font-bold text-[12px] text-brand">
                {document.extBadge}
              </Text>
            ) : (
              <Icon
                name="arrow.up.doc"
                fallback="cloud-upload-outline"
                size={24}
                color="#2F6BFF"
              />
            )}
          </View>

          <Text
            numberOfLines={1}
            className="mt-3.5 text-center font-semibold text-[16px] text-ink"
          >
            {document ? document.name : "Selecionar arquivo da entrega"}
          </Text>

          <Text className="mt-1 text-center text-[13px] text-ink3">
            {document
              ? `${document.size || "Arquivo pronto"} · pronto para conferência`
              : "PDF, Word, Excel ou Texto"}
          </Text>

          <Text className="mt-3 font-semibold text-[13.5px] text-brand">
            {document ? "Trocar arquivo" : "Escolher arquivo"}
          </Text>
        </Pressable>

        <View className="flex-row gap-3">
          <View className="w-[115px] rounded-2xl border border-line-glass bg-glass px-4 py-3 shadow-sm">
            <Text className="text-[11.5px] text-ink3">Versão</Text>
            <TextInput
              value={version}
              onChangeText={setVersion}
              placeholder="v1"
              placeholderTextColor={placeholderColor}
              className="mt-0.5 font-semibold text-[15px] text-ink web:outline-none"
            />
          </View>

          <View className="flex-1 rounded-2xl border border-line-glass bg-glass px-4 py-3 shadow-sm">
            <Text className="text-[11.5px] text-ink3">
              Identificação (opcional)
            </Text>
            <TextInput
              value={label}
              onChangeText={setLabel}
              placeholder="Ex: Versão final"
              placeholderTextColor={placeholderColor}
              className="mt-0.5 font-medium text-[15px] text-ink web:outline-none"
            />
          </View>
        </View>
      </KeyboardAwareScrollView>

      <View
        pointerEvents="box-none"
        style={{ paddingBottom: Math.max(insets.bottom, 18) }}
        className="absolute right-0 bottom-0 left-0 px-5"
      >
        <Pressable
          onPress={handleSubmit}
          disabled={isBusy || !document}
          className="h-[52px] items-center justify-center rounded-full bg-brand shadow-brand-button active:opacity-85 disabled:opacity-50"
        >
          {isBusy ? (
            <ActivityIndicator color="#fff" />
          ) : (
            <Text className="font-semibold text-[15px] text-white">
              Continuar
            </Text>
          )}
        </Pressable>
      </View>
    </View>
  );
}
