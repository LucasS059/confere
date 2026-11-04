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
import { Blob } from "@/components/blob";
import { Icon } from "@/components/icon";
import { ScreenHeader } from "@/components/screen-header";
import { trpc } from "@/utils/trpc";

export default function ReviewRequirementsScreen() {
  const router = useRouter();
  const insets = useSafeAreaInsets();
  const { toast } = useToast();
  const { projectId } = useLocalSearchParams<{ projectId: string }>();

  const [newTitle, setNewTitle] = useState("");
  const [isAdding, setIsAdding] = useState(false);

  const queryClient = useQueryClient();

  // Busca projeto do banco
  const { data: projectData, isLoading } = useQuery(
    trpc.project.getById.queryOptions(
      { id: projectId || "" },
      { enabled: Boolean(projectId) },
    ),
  );

  const toggleMutation = useMutation(
    trpc.project.toggleRequirement.mutationOptions({
      onSuccess: () => {
        queryClient.invalidateQueries(
          trpc.project.getById.queryFilter({ id: projectId || "" }),
        );
      },
    }),
  );

  const addMutation = useMutation(
    trpc.project.addRequirement.mutationOptions({
      onSuccess: () => {
        queryClient.invalidateQueries(
          trpc.project.getById.queryFilter({ id: projectId || "" }),
        );
        setNewTitle("");
        setIsAdding(false);
        toast.show({ label: "Requisito adicionado!" });
      },
      onError: (err) => {
        toast.show({ variant: "danger", label: err.message || "Erro ao adicionar" });
      },
    }),
  );

  function handleToggle(requirementId: string, currentChecked: boolean) {
    toggleMutation.mutate({
      requirementId,
      checked: !currentChecked,
    });
  }

  function handleAddRequirement() {
    if (!newTitle.trim() || !projectId) return;
    addMutation.mutate({
      projectId,
      title: newTitle.trim(),
    });
  }

  const items = projectData?.requirements || [];
  const selectedCount = items.filter((i) => i.checked).length;

  return (
    <View className="flex-1 overflow-hidden bg-canvas">
      <Blob
        color="#2F6BFF"
        className="-top-[120px] -left-[80px] size-[360px] opacity-[0.16] dark:opacity-[0.28]"
      />
      <Blob
        color="#F59E0B"
        className="top-[320px] -right-[140px] size-[300px] opacity-[0.12] dark:opacity-[0.20]"
      />

      <ScreenHeader
        title="Revisar requisitos"
        subtitle={projectData?.name || "Requisitos da rubrica"}
      />

      <ScrollView
        showsVerticalScrollIndicator={false}
        contentContainerStyle={{
          paddingHorizontal: 20,
          paddingTop: 16,
          paddingBottom: insets.bottom + 120,
        }}
      >
        <View className="mb-4 flex-row items-center justify-between">
          <Text className="text-[14px] text-ink2">
            Critérios selecionados:{" "}
            <Text className="font-bold text-ink">
              {selectedCount}/{items.length}
            </Text>
          </Text>

          <Pressable
            onPress={() => setIsAdding(!isAdding)}
            className="flex-row items-center gap-1 rounded-xl bg-brand/10 px-3 py-1.5 active:opacity-75"
          >
            <Icon name="plus" fallback="add" size={14} color="#2F6BFF" />
            <Text className="text-[13px] font-semibold text-brand">
              Adicionar
            </Text>
          </Pressable>
        </View>

        {isAdding ? (
          <View className="mb-4 rounded-2xl border border-line-glass bg-glass p-3 shadow-sm">
            <TextInput
              value={newTitle}
              onChangeText={setNewTitle}
              placeholder="Descreva o critério da rubrica..."
              placeholderTextColor="#94A3B8"
              autoFocus
              className="mb-3 font-instrument text-[14px] text-ink"
            />
            <View className="flex-row justify-end gap-2">
              <Pressable
                onPress={() => setIsAdding(false)}
                className="rounded-xl px-3 py-1.5"
              >
                <Text className="text-[13px] text-ink2">Cancelar</Text>
              </Pressable>
              <Pressable
                onPress={handleAddRequirement}
                disabled={addMutation.isPending}
                className="rounded-xl bg-brand px-3 py-1.5"
              >
                {addMutation.isPending ? (
                  <ActivityIndicator color="#fff" size="small" />
                ) : (
                  <Text className="text-[13px] font-semibold text-white">
                    Salvar
                  </Text>
                )}
              </Pressable>
            </View>
          </View>
        ) : null}

        {isLoading ? (
          <ActivityIndicator className="my-10" color="#2F6BFF" />
        ) : items.length === 0 ? (
          <View className="items-center justify-center rounded-3xl border border-line-glass bg-glass p-8 text-center my-6">
            <Icon
              name="list.bullet.rectangle"
              fallback="list-outline"
              size={36}
              color="#94A3B8"
            />
            <Text className="mt-3 text-[16px] font-bold text-ink">
              Nenhum requisito cadastrado
            </Text>
            <Text className="mt-1 text-center text-[13px] text-ink2">
              Clique em "+ Adicionar" acima para cadastrar os critérios da rubrica.
            </Text>
          </View>
        ) : (
          <View className="gap-2.5">
            {items.map((item) => (
              <Pressable
                key={item.id}
                onPress={() => handleToggle(item.id, item.checked)}
                className="flex-row items-center gap-3.5 rounded-2xl border border-line-glass bg-glass p-4 shadow-sm active:bg-card/60"
              >
                <View
                  className={`size-6 items-center justify-center rounded-lg border ${
                    item.checked
                      ? "border-brand bg-brand"
                      : "border-line bg-card"
                  }`}
                >
                  {item.checked ? (
                    <Icon
                      name="checkmark"
                      fallback="checkmark"
                      size={14}
                      color="#fff"
                    />
                  ) : null}
                </View>

                <Text
                  className={`flex-1 text-[15px] ${
                    item.checked
                      ? "font-medium text-ink"
                      : "text-ink3 line-through"
                  }`}
                >
                  {item.title}
                </Text>
              </Pressable>
            ))}
          </View>
        )}
      </ScrollView>

      {/* Barra de Ação Inferior */}
      <View
        style={{ paddingBottom: Math.max(insets.bottom, 16) }}
        className="absolute bottom-0 left-0 right-0 border-t border-line-glass bg-glass p-4 backdrop-blur-md"
      >
        <Pressable
          onPress={() => {
            router.push({
              pathname: "/projects/submission",
              params: { projectId: projectId || "" },
            });
          }}
          className="h-[52px] items-center justify-center rounded-2xl bg-brand shadow-brand-button active:opacity-85"
        >
          <Text className="font-instrument-semibold text-[15px] text-white">
            Avançar para entrega do trabalho
          </Text>
        </Pressable>
      </View>
    </View>
  );
}
