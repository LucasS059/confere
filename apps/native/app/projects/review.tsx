import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
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
import { useCSSVariable } from "uniwind";
import { Blob } from "@/components/ui/blob";
import { Icon } from "@/components/ui/icon";
import { ScreenHeader } from "@/components/ui/screen-header";
import { trpc } from "@/lib/trpc";

export default function ReviewRequirementsScreen() {
  const router = useRouter();
  const insets = useSafeAreaInsets();
  const { toast } = useToast();
  const placeholderColor = useCSSVariable("--ink3") as string | undefined;
  const { projectId } = useLocalSearchParams<{ projectId: string }>();
  const queryClient = useQueryClient();

  const [isEditingRubric, setIsEditingRubric] = useState(false);
  const [rubricDraft, setRubricDraft] = useState("");
  const [isAddingReq, setIsAddingReq] = useState(false);
  const [newTitle, setNewTitle] = useState("");

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

  function refreshProject() {
    queryClient.invalidateQueries(
      trpc.project.getById.queryFilter({ id: projectId ?? "" }),
    );
    queryClient.invalidateQueries(trpc.project.list.queryFilter());
  }

  const updateRubricMutation = useMutation(
    trpc.project.updateRubric.mutationOptions({
      onSuccess: () => {
        refreshProject();
        setIsEditingRubric(false);
        toast.show({ id: "rubric-saved", label: "Rubrica atualizada!" });
      },
      onError: (err) => {
        toast.show({
          id: "rubric-error",
          variant: "danger",
          label: err.message || "Erro ao salvar rubrica",
        });
      },
    }),
  );

  const deleteReqMutation = useMutation(
    trpc.project.deleteRequirement.mutationOptions({
      onSuccess: () => {
        refreshProject();
        toast.show({ id: "req-deleted", label: "Requisito excluído!" });
      },
      onError: (err) => {
        toast.show({
          id: "req-error",
          variant: "danger",
          label: err.message || "Erro ao excluir requisito",
        });
      },
    }),
  );

  const addMutation = useMutation(
    trpc.project.addRequirement.mutationOptions({
      onSuccess: () => {
        refreshProject();
        setNewTitle("");
        setIsAddingReq(false);
        toast.show({ id: "req-added", label: "Requisito adicionado!" });
      },
      onError: (err) => {
        toast.show({
          id: "req-error",
          variant: "danger",
          label: err.message || "Erro ao adicionar requisito",
        });
      },
    }),
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
        <ScreenHeader title="Rubrica e requisitos" />
        <View className="flex-1 items-center justify-center px-6">
          <Text className="text-center font-semibold text-[16px] text-ink">
            Projeto não encontrado
          </Text>
          <Text className="mt-1 text-center text-[13px] text-ink3">
            Não foi possível carregar os requisitos deste projeto.
          </Text>
        </View>
      </View>
    );
  }

  const items = project.requirements;

  function openRubricEdit() {
    if (isEditingRubric) {
      setIsEditingRubric(false);
      return;
    }
    setRubricDraft(project?.rawRubric ?? "");
    setIsEditingRubric(true);
  }

  function saveRubric() {
    const trimmed = rubricDraft.trim();
    if (!trimmed || !projectId) {
      toast.show({
        id: "rubric-error",
        variant: "danger",
        label: "A rubrica não pode ficar vazia",
      });
      return;
    }
    updateRubricMutation.mutate({ projectId, rawRubric: trimmed });
  }

  function addRequirement() {
    const title = newTitle.trim();
    if (!title || !projectId) return;
    addMutation.mutate({ projectId, title });
  }

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

      <ScreenHeader title="Rubrica e requisitos" subtitle={project.name} />

      <ScrollView
        showsVerticalScrollIndicator={false}
        keyboardShouldPersistTaps="handled"
        contentContainerStyle={{
          paddingHorizontal: 20,
          paddingTop: 16,
          paddingBottom: insets.bottom + 110,
          gap: 18,
        }}
      >
        <View className="rounded-3xl border border-line-glass bg-glass p-4 shadow-sm">
          <View className="mb-2.5 flex-row items-center justify-between">
            <Text className="font-semibold text-[15px] text-ink">
              Rubrica cadastrada
            </Text>
            <Pressable onPress={openRubricEdit} hitSlop={8}>
              <Text className="font-semibold text-[13px] text-brand">
                {isEditingRubric ? "Cancelar" : "Editar"}
              </Text>
            </Pressable>
          </View>

          {isEditingRubric ? (
            <View className="gap-3">
              <TextInput
                value={rubricDraft}
                onChangeText={setRubricDraft}
                placeholder="Digite os requisitos da rubrica..."
                placeholderTextColor={placeholderColor}
                multiline
                autoFocus
                textAlignVertical="top"
                className="min-h-[130px] rounded-2xl border border-line-glass bg-card/70 p-3 text-[14px] text-ink leading-[20px] web:outline-none"
              />
              <Pressable
                onPress={saveRubric}
                disabled={updateRubricMutation.isPending}
                className="h-[44px] items-center justify-center rounded-full bg-brand active:opacity-85"
              >
                {updateRubricMutation.isPending ? (
                  <ActivityIndicator color="#fff" size="small" />
                ) : (
                  <Text className="font-semibold text-[14px] text-white">
                    Salvar rubrica
                  </Text>
                )}
              </Pressable>
            </View>
          ) : (
            <>
              <Text className="text-[14px] text-ink2 leading-[21px]">
                {project.rawRubric}
              </Text>

              <Pressable
                onPress={() =>
                  toast.show({
                    id: "extract-pending",
                    label: "Extração automática em breve.",
                  })
                }
                className="mt-3.5 h-[42px] flex-row items-center justify-center gap-2 rounded-full bg-brand/10 active:opacity-80"
              >
                <Icon
                  name="arrow.clockwise"
                  fallback="refresh"
                  size={14}
                  color="#2F6BFF"
                />
                <Text className="font-semibold text-[13.5px] text-brand">
                  Extrair requisitos da rubrica
                </Text>
              </Pressable>
            </>
          )}
        </View>

        {isAddingReq && (
          <View className="gap-3 rounded-3xl border border-line-glass bg-glass p-4 shadow-sm">
            <TextInput
              value={newTitle}
              onChangeText={setNewTitle}
              placeholder="Descreva o requisito..."
              placeholderTextColor={placeholderColor}
              autoFocus
              className="rounded-2xl border border-line-glass bg-card/70 px-3.5 py-2.5 text-[14px] text-ink web:outline-none"
            />
            <Pressable
              onPress={addRequirement}
              disabled={addMutation.isPending}
              className="h-[42px] items-center justify-center rounded-full bg-brand active:opacity-85"
            >
              {addMutation.isPending ? (
                <ActivityIndicator color="#fff" size="small" />
              ) : (
                <Text className="font-semibold text-[13.5px] text-white">
                  Adicionar requisito
                </Text>
              )}
            </Pressable>
          </View>
        )}

        <View className="gap-2.5">
          <View className="flex-row items-center justify-between px-1">
            <Text className="font-bold text-[12px] text-ink3 uppercase tracking-wider">
              Requisitos ({items.length})
            </Text>
            <Pressable
              onPress={() => {
                setIsAddingReq((prev) => !prev);
                setNewTitle("");
              }}
              hitSlop={8}
            >
              <Text className="font-semibold text-[13px] text-brand">
                {isAddingReq ? "Cancelar" : "+ Adicionar"}
              </Text>
            </Pressable>
          </View>

          {items.length === 0 ? (
            <View className="items-center gap-1 rounded-3xl border border-line-glass bg-glass px-6 py-8 shadow-sm">
              <Text className="font-semibold text-[15px] text-ink">
                Nenhum requisito cadastrado
              </Text>
              <Text className="text-center text-[13px] text-ink3">
                Extraia da rubrica acima ou toque no + para adicionar.
              </Text>
            </View>
          ) : (
            <View className="overflow-hidden rounded-3xl border border-line-glass bg-glass shadow-sm">
              {items.map((item, idx) => (
                <View
                  key={item.id}
                  className={`flex-row items-center justify-between gap-3 px-4 py-3.5 ${
                    idx < items.length - 1 ? "border-line-glass border-b" : ""
                  }`}
                >
                  <View className="flex-1 flex-row items-start gap-3">
                    <View className="mt-0.5 size-6 items-center justify-center rounded-lg bg-brand/12">
                      <Text className="font-bold text-[12px] text-brand">
                        {idx + 1}
                      </Text>
                    </View>

                    <Text
                      numberOfLines={3}
                      className="flex-1 font-medium text-[14.5px] text-ink leading-[20px]"
                    >
                      {item.title}
                    </Text>
                  </View>

                  <Pressable
                    hitSlop={8}
                    disabled={deleteReqMutation.isPending}
                    onPress={() =>
                      deleteReqMutation.mutate({ requirementId: item.id })
                    }
                    className="p-1 active:opacity-60"
                  >
                    <Icon
                      name="trash"
                      fallback="trash-outline"
                      size={16}
                      color="#94A3B8"
                    />
                  </Pressable>
                </View>
              ))}
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
          onPress={() => router.back()}
          className="h-[52px] items-center justify-center rounded-full bg-brand shadow-brand-button active:opacity-85"
        >
          <Text className="font-semibold text-[15px] text-white">Concluir</Text>
        </Pressable>
      </View>
    </View>
  );
}
