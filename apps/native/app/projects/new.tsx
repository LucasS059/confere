import { useMutation, useQueryClient } from "@tanstack/react-query";
import * as DocumentPicker from "expo-document-picker";
import { useRouter } from "expo-router";
import { useToast } from "heroui-native";
import { useState } from "react";
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

type RubricInputMode = "text" | "file";

interface SelectedFile {
  name: string;
  size?: string;
  uri?: string;
}

function formatBytes(bytes?: number): string {
  if (!bytes) return "";
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
}

export default function NewProjectScreen() {
  const router = useRouter();
  const insets = useSafeAreaInsets();
  const { toast } = useToast();
  const placeholderColor = useCSSVariable("--ink3") as string | undefined;

  // 1. Dados básicos
  const [name, setName] = useState("");

  // 2. Rubrica do Professor / Requisitos
  const [rubricMode, setRubricMode] = useState<RubricInputMode>("text");
  const [rubricText, setRubricText] = useState("");
  const [rubricFile, setRubricFile] = useState<SelectedFile | null>(null);

  // 3. Conteúdo do Trabalho do Aluno (ex: 1ª versão em PDF)
  const [studentWorkFile, setStudentWorkFile] = useState<SelectedFile | null>(null);

  const queryClient = useQueryClient();
  const createMutation = useMutation(
    trpc.project.create.mutationOptions({
      onSuccess: (newProject) => {
        queryClient.invalidateQueries(trpc.project.list.queryFilter());
        toast.show({ label: "Projeto criado com sucesso!" });

        // A análise ficará disponível após a integração do modelo.
        if (newProject.submission) {
          router.push({
            pathname: "/projects/details",
            params: {
              projectId: newProject.id,
            },
          });
        } else {
          // Senão, segue para revisar os requisitos do professor
          router.push({
            pathname: "/projects/review",
            params: { projectId: newProject.id },
          });
        }
      },
      onError: (err) => {
        toast.show({
          variant: "danger",
          label: err.message || "Erro ao criar projeto",
        });
      },
    }),
  );

  // Selecionar documento de rubrica (PDF / DOCX)
  async function handlePickRubricFile() {
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
        setRubricFile({
          name: file.name,
          size: formatBytes(file.size),
          uri: file.uri,
        });
        if (!rubricText.trim()) {
          setRubricText(`Arquivo de rubrica anexado: ${file.name}`);
        }
      }
    } catch {
      toast.show({
        variant: "danger",
        label: "Não foi possível selecionar o arquivo da rubrica",
      });
    }
  }

  // Selecionar documento do trabalho do estudante (PDF / DOCX)
  async function handlePickStudentWork() {
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
        setStudentWorkFile({
          name: file.name,
          size: formatBytes(file.size),
          uri: file.uri,
        });
      }
    } catch {
      toast.show({
        variant: "danger",
        label: "Não foi possível selecionar o arquivo do seu trabalho",
      });
    }
  }

  function handleSave() {
    if (!name.trim()) {
      toast.show({
        variant: "danger",
        label: "Dê um nome para o seu projeto ou disciplina",
      });
      return;
    }

    const effectiveRubric =
      rubricMode === "text"
        ? rubricText.trim()
        : rubricFile
          ? `Rubrica em anexo: ${rubricFile.name}`
          : "";

    if (!effectiveRubric) {
      toast.show({
        variant: "danger",
        label:
          rubricMode === "text"
            ? "Cole a rubrica ou critérios informados pelo professor"
            : "Anexe o arquivo PDF/DOCX da rubrica",
      });
      return;
    }

    createMutation.mutate({
      name: name.trim(),
      rawRubric: effectiveRubric,
      sourceType: rubricMode === "text" ? "Texto" : "PDF/DOCX",
      rubricFilename: rubricFile?.name,
      initialSubmission: studentWorkFile
        ? {
            filename: studentWorkFile.name,
            fileSize: studentWorkFile.size,
            version: "v1",
          }
        : undefined,
    });
  }

  return (
    <View className="flex-1 overflow-hidden bg-canvas">
      <Blob
        color="#2F6BFF"
        className="-top-[120px] -left-[80px] size-[360px] opacity-[0.18] dark:opacity-[0.30]"
      />
      <Blob
        color="#1E9E62"
        className="top-[340px] -right-[140px] size-[320px] opacity-[0.14] dark:opacity-[0.24]"
      />

      <KeyboardAwareScrollView
        bottomOffset={24}
        keyboardShouldPersistTaps="handled"
        contentContainerStyle={{
          flexGrow: 1,
          gap: 20,
          paddingTop: Math.max(insets.top + 12, 56),
          paddingHorizontal: 20,
          paddingBottom: Math.max(insets.bottom + 24, 40),
        }}
      >
        <ScreenHeader
          title="Novo projeto"
          subtitle="Cadastre o que o professor pediu e o seu trabalho"
          safeTop={false}
        />

        {/* 1. Nome do Projeto */}
        <View className="gap-1.5">
          <Text className="px-1 font-instrument-medium text-ink2 text-xs">
            Nome do projeto / disciplina
          </Text>
          <View className="h-[52px] justify-center rounded-2xl border border-hair bg-card px-4 shadow-xs">
            <TextInput
              value={name}
              onChangeText={setName}
              placeholder="Ex: TCC, Relatório de Física, Artigo Científico..."
              placeholderTextColor={placeholderColor}
              className="font-instrument-medium text-[15px] text-ink web:outline-none"
            />
          </View>
        </View>

        {/* 2. O que o professor pediu (Rubrica / Critérios) */}
        <View className="gap-2.5">
          <View className="flex-row items-center justify-between px-1">
            <Text className="font-instrument-semibold text-[13px] text-ink">
              1. Critérios do professor (Rubrica / Edital)
            </Text>
            <View className="flex-row rounded-full border border-hair bg-card p-0.5">
              <Pressable
                onPress={() => setRubricMode("text")}
                className={`rounded-full px-3 py-1 ${
                  rubricMode === "text" ? "bg-ink" : ""
                }`}
              >
                <Text
                  className={`font-instrument text-xs ${
                    rubricMode === "text" ? "text-canvas" : "text-ink2"
                  }`}
                >
                  Colar texto
                </Text>
              </Pressable>
              <Pressable
                onPress={() => setRubricMode("file")}
                className={`rounded-full px-3 py-1 ${
                  rubricMode === "file" ? "bg-ink" : ""
                }`}
              >
                <Text
                  className={`font-instrument text-xs ${
                    rubricMode === "file" ? "text-canvas" : "text-ink2"
                  }`}
                >
                  Anexar PDF/DOCX
                </Text>
              </Pressable>
            </View>
          </View>

          {rubricMode === "text" ? (
            <View className="gap-2 rounded-[22px] border border-hair bg-card p-4 shadow-xs">
              <Text className="font-instrument text-[12px] text-ink3">
                Cole abaixo o enunciado, orientações ou critérios de avaliação:
              </Text>
              <TextInput
                value={rubricText}
                onChangeText={setRubricText}
                placeholder="Ex: 'O relatório deve conter introdução, metodologia com 3 referências ABNT, análise de dados e conclusão...'"
                placeholderTextColor={placeholderColor}
                multiline
                textAlignVertical="top"
                className="min-h-[140px] font-instrument text-[13.5px] text-ink leading-[21px] web:outline-none"
              />
            </View>
          ) : (
            <View className="rounded-[22px] border border-hair bg-card p-4 shadow-xs">
              {rubricFile ? (
                <View className="flex-row items-center justify-between rounded-2xl border border-line-glass bg-glass p-3.5">
                  <View className="flex-row items-center gap-3">
                    <View className="size-10 items-center justify-center rounded-xl bg-brand/10">
                      <Icon
                        name="doc.text.fill"
                        fallback="document-text"
                        size={20}
                        color="#2F6BFF"
                      />
                    </View>
                    <View>
                      <Text
                        numberOfLines={1}
                        className="font-instrument-semibold text-[13.5px] text-ink"
                      >
                        {rubricFile.name}
                      </Text>
                      <Text className="font-instrument text-[11px] text-ink3">
                        {rubricFile.size || "Documento anexado"}
                      </Text>
                    </View>
                  </View>
                  <Pressable
                    onPress={() => setRubricFile(null)}
                    className="p-1 active:opacity-70"
                  >
                    <Text className="font-instrument-medium text-xs text-err">
                      Remover
                    </Text>
                  </Pressable>
                </View>
              ) : (
                <Pressable
                  onPress={handlePickRubricFile}
                  className="items-center justify-center rounded-2xl border border-dashed border-hair py-6 active:opacity-75"
                >
                  <View className="mb-2 size-10 items-center justify-center rounded-xl bg-card shadow-xs">
                    <Icon
                      name="arrow.up.doc"
                      fallback="cloud-upload"
                      size={20}
                      color="#2F6BFF"
                    />
                  </View>
                  <Text className="font-instrument-medium text-[13px] text-ink">
                    Selecionar PDF ou DOCX da rubrica
                  </Text>
                  <Text className="font-instrument text-[11px] text-ink3">
                    Instruções, edital ou critérios do professor
                  </Text>
                </Pressable>
              )}
            </View>
          )}
        </View>

        {/* 3. O que o aluno fez (1ª versão do relatório em PDF) */}
        <View className="gap-2.5">
          <View className="px-1">
            <Text className="font-instrument-semibold text-[13px] text-ink">
              2. Seu trabalho (Relatório / Artigo em PDF)
            </Text>
            <Text className="font-instrument text-[11.5px] text-ink3">
              Selecione a primeira versão para cadastrar os dados do relatório
            </Text>
          </View>

          <View className="rounded-[22px] border border-hair bg-card p-4 shadow-xs">
            {studentWorkFile ? (
              <View className="flex-row items-center justify-between rounded-2xl border border-line-glass bg-glass p-3.5">
                <View className="flex-row items-center gap-3">
                  <View className="size-10 items-center justify-center rounded-xl bg-success/10">
                    <Icon
                      name="checkmark.circle.fill"
                      fallback="checkmark-circle"
                      size={20}
                      color="#10B981"
                    />
                  </View>
                  <View>
                    <Text
                      numberOfLines={1}
                      className="font-instrument-semibold text-[13.5px] text-ink"
                    >
                      {studentWorkFile.name}
                    </Text>
                    <Text className="font-instrument text-[11px] text-ink3">
                      Versão v1 • {studentWorkFile.size || "Pronto para análise"}
                    </Text>
                  </View>
                </View>
                <Pressable
                  onPress={() => setStudentWorkFile(null)}
                  className="p-1 active:opacity-70"
                >
                  <Text className="font-instrument-medium text-xs text-err">
                    Trocar
                  </Text>
                </Pressable>
              </View>
            ) : (
              <Pressable
                onPress={handlePickStudentWork}
                className="items-center justify-center rounded-2xl border border-dashed border-hair py-6 active:opacity-75"
              >
                <View className="mb-2 size-10 items-center justify-center rounded-xl bg-card shadow-xs">
                  <Icon
                    name="doc.badge.plus"
                    fallback="add-circle"
                    size={20}
                    color="#10B981"
                  />
                </View>
                <Text className="font-instrument-medium text-[13px] text-ink">
                  Anexar primeira versão do relatório (PDF)
                </Text>
                <Text className="font-instrument text-[11px] text-ink3">
                  Somente nome e tamanho serão salvos. Upload e análise ainda indisponíveis.
                </Text>
              </Pressable>
            )}
          </View>
        </View>

        {/* Botão Salvar */}
        <Pressable
          onPress={handleSave}
          disabled={createMutation.isPending}
          className="mt-2 h-[54px] items-center justify-center rounded-[27px] bg-brand shadow-brand-button active:opacity-85"
        >
          {createMutation.isPending ? (
            <ActivityIndicator color="#fff" />
          ) : (
            <Text className="font-instrument-semibold text-[15px] text-white">
              {studentWorkFile
                ? "Salvar projeto e cadastrar entrega"
                : "Salvar projeto e revisar requisitos"}
            </Text>
          )}
        </Pressable>
      </KeyboardAwareScrollView>
    </View>
  );
}
