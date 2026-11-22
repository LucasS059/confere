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
import { useCSSVariable } from "uniwind";
import { Icon } from "@/components/ui/icon";
import { trpc } from "@/lib/trpc";

export function ProjectForm() {
  const router = useRouter();
  const { toast } = useToast();
  const placeholderColor = useCSSVariable("--ink3") as string | undefined;
  const queryClient = useQueryClient();

  const [name, setName] = useState("");
  const [description, setDescription] = useState("");
  const [sourceType, setSourceType] = useState<"Texto" | "PDF/DOCX">("Texto");
  const [rubricFilename, setRubricFilename] = useState("");
  const [rubricText, setRubricText] = useState("");

  const createMutation = useMutation(
    trpc.project.create.mutationOptions({
      onSuccess: (created) => {
        queryClient.invalidateQueries(trpc.project.list.queryFilter());
        setName("");
        setDescription("");
        setSourceType("Texto");
        setRubricFilename("");
        setRubricText("");
        toast.show({ label: "Projeto criado!" });

        router.push({
          pathname: "/projects/details",
          params: { projectId: created.id },
        });
      },
      onError: (err) => {
        toast.show({
          id: "new-project-error",
          variant: "danger",
          label: err.message || "Não foi possível criar o projeto",
        });
      },
    }),
  );

  async function handlePickRubricFile() {
    try {
      const res = await DocumentPicker.getDocumentAsync({
        type: [
          "application/pdf",
          "application/msword",
          "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
          "text/plain",
        ],
        copyToCacheDirectory: true,
      });

      if (!res.canceled && res.assets?.length) {
        setRubricFilename(res.assets[0].name);
      }
    } catch {
      toast.show({
        id: "rubric-file-error",
        variant: "danger",
        label: "Não foi possível selecionar o arquivo",
      });
    }
  }

  function handleSave() {
    const trimmedName = name.trim();
    const rawRubric = rubricText.trim();

    if (!trimmedName) {
      toast.show({
        id: "new-project-error",
        variant: "danger",
        label: "Informe o nome do projeto",
      });
      return;
    }

    if (sourceType === "PDF/DOCX" && !rubricFilename && !rawRubric) {
      toast.show({
        id: "new-project-error",
        variant: "danger",
        label: "Selecione o arquivo ou informe a rubrica",
      });
      return;
    }

    if (sourceType === "Texto" && !rawRubric) {
      toast.show({
        id: "new-project-error",
        variant: "danger",
        label: "Cole os requisitos da rubrica",
      });
      return;
    }

    createMutation.mutate({
      name: trimmedName,
      description: description.trim() || undefined,
      rawRubric: rawRubric || `Rubrica enviada por arquivo: ${rubricFilename}`,
      sourceType,
      rubricFilename:
        sourceType === "PDF/DOCX" ? rubricFilename || undefined : undefined,
    });
  }

  return (
    <View className="gap-4">
      <View className="gap-3.5 rounded-3xl border border-line-glass bg-glass p-4 shadow-sm">
        <View className="gap-1">
          <Text className="font-medium text-[12.5px] text-ink3">
            Nome do projeto *
          </Text>
          <TextInput
            value={name}
            onChangeText={setName}
            placeholder="Ex: Artigo PIBIC 2026"
            placeholderTextColor={placeholderColor}
            returnKeyType="next"
            className="font-medium text-[15px] text-ink web:outline-none"
          />
        </View>

        <View className="h-[1px] bg-line-glass" />

        <View className="gap-1">
          <Text className="font-medium text-[12.5px] text-ink3">
            Descrição / disciplina (opcional)
          </Text>
          <TextInput
            value={description}
            onChangeText={setDescription}
            placeholder="Ex: TCC · Ciência da Computação"
            placeholderTextColor={placeholderColor}
            returnKeyType="next"
            className="text-[14.5px] text-ink web:outline-none"
          />
        </View>
      </View>

      <View className="gap-3.5 rounded-3xl border border-line-glass bg-glass p-4 shadow-sm">
        <View className="flex-row items-center justify-between">
          <Text className="font-semibold text-[14.5px] text-ink">
            Rubrica *
          </Text>
          <Text className="text-[12px] text-ink3">
            {rubricText.length} caracteres
          </Text>
        </View>

        <View className="flex-row rounded-2xl border border-line-glass bg-canvas/60 p-1">
          {(["Texto", "PDF/DOCX"] as const).map((type) => (
            <Pressable
              key={type}
              onPress={() => setSourceType(type)}
              className={`flex-1 items-center justify-center rounded-xl py-2 ${
                sourceType === type ? "bg-card shadow-sm" : ""
              }`}
            >
              <Text
                className={`text-[13px] ${
                  sourceType === type
                    ? "font-semibold text-ink"
                    : "font-medium text-ink3"
                }`}
              >
                {type}
              </Text>
            </Pressable>
          ))}
        </View>

        {sourceType === "PDF/DOCX" && (
          <Pressable
            onPress={handlePickRubricFile}
            className="flex-row items-center justify-between rounded-2xl border border-line-glass bg-card/70 px-4 py-3 active:opacity-80"
          >
            <View className="flex-1 flex-row items-center gap-3">
              <Icon
                name="paperclip"
                fallback="attach"
                size={17}
                color="#2F6BFF"
              />
              <Text
                numberOfLines={1}
                className="flex-1 font-medium text-[14px] text-ink"
              >
                {rubricFilename || "Selecionar arquivo da rubrica"}
              </Text>
            </View>
            <Text className="font-semibold text-[12.5px] text-brand">
              {rubricFilename ? "Trocar" : "Escolher"}
            </Text>
          </Pressable>
        )}

        <TextInput
          value={rubricText}
          onChangeText={setRubricText}
          placeholder={
            sourceType === "PDF/DOCX"
              ? "Observações ou requisitos complementares da rubrica (opcional)..."
              : "Cole aqui o edital, a rubrica ou as orientações do professor..."
          }
          placeholderTextColor={placeholderColor}
          multiline
          textAlignVertical="top"
          className="min-h-[170px] rounded-2xl border border-line-glass bg-card/60 p-3.5 text-[14px] text-ink leading-[21px] web:outline-none"
        />
      </View>

      <Pressable
        onPress={handleSave}
        disabled={createMutation.isPending}
        className="h-[52px] items-center justify-center rounded-full bg-brand shadow-brand-button active:opacity-85 disabled:opacity-60"
      >
        {createMutation.isPending ? (
          <ActivityIndicator color="#fff" />
        ) : (
          <Text className="font-semibold text-[15px] text-white">
            Criar projeto
          </Text>
        )}
      </Pressable>
    </View>
  );
}
