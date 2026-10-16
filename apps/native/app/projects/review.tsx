import { useRouter } from "expo-router";
import { useState } from "react";
import { Pressable, ScrollView, Text, TextInput, View } from "react-native";
import { useSafeAreaInsets } from "react-native-safe-area-context";
import { Blob } from "@/components/blob";
import { Icon } from "@/components/icon";
import { ScreenHeader } from "@/components/screen-header";

interface RequirementItem {
  id: string;
  title: string;
  code?: string;
  checked: boolean;
  warning?: string;
  disabledNote?: string;
}

export default function ReviewRequirementsScreen() {
  const router = useRouter();
  const insets = useSafeAreaInsets();
  const [items, setItems] = useState<RequirementItem[]>([]);
  const [newTitle, setNewTitle] = useState("");
  const [isAdding, setIsAdding] = useState(false);

  function toggleItem(id: string) {
    setItems((prev) =>
      prev.map((item) =>
        item.id === id ? { ...item, checked: !item.checked } : item
      )
    );
  }

  function handleAddRequirement() {
    if (!newTitle.trim()) return;
    const newItem: RequirementItem = {
      id: String(Date.now()),
      title: newTitle.trim(),
      checked: true,
    };
    setItems((prev) => [...prev, newItem]);
    setNewTitle("");
    setIsAdding(false);
  }

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
        subtitle="requisitos do projeto"
        rightElement={
          <Pressable
            onPress={() => setIsAdding((prev) => !prev)}
            hitSlop={8}
            className="size-9 items-center justify-center rounded-full border border-line-glass bg-glass"
          >
            <Icon
              name={isAdding ? "xmark" : "plus"}
              fallback={isAdding ? "close" : "add"}
              size={18}
              color="#2F6BFF"
            />
          </Pressable>
        }
      />

      <ScrollView
        showsVerticalScrollIndicator={false}
        contentContainerStyle={{
          paddingHorizontal: 20,
          paddingTop: 16,
          paddingBottom: insets.bottom + 100,
        }}
      >
        {isAdding && (
          <View className="mb-4 rounded-2xl border border-brand/30 bg-glass p-3.5 shadow-sm gap-2.5">
            <Text className="text-[13px] font-semibold text-ink">
              Adicionar requisito manual
            </Text>
            <View className="h-11 justify-center rounded-xl border border-line bg-canvas px-3">
              <TextInput
                value={newTitle}
                onChangeText={setNewTitle}
                placeholder="Ex: Resumo em português e inglês"
                placeholderTextColor="#94A3B8"
                className="text-[14px] text-ink"
              />
            </View>
            <Pressable
              onPress={handleAddRequirement}
              className="h-10 items-center justify-center rounded-xl bg-brand active:opacity-90"
            >
              <Text className="text-[13px] font-semibold text-white">
                Adicionar
              </Text>
            </Pressable>
          </View>
        )}

        <View className="mb-4 flex-row items-center gap-2.5 rounded-2xl border border-line-glass bg-glass p-3.5 shadow-sm">
          <Icon
            name="info.circle"
            fallback="information-circle-outline"
            size={18}
            color="#2F6BFF"
          />
          <Text className="flex-1 text-[13px] leading-snug text-ink2">
            <Text className="font-semibold text-ink">
              {items.length} requisitos encontrados.
            </Text>{" "}
            Toque para editar ou marcar o que se aplica.
          </Text>
        </View>

        {items.length === 0 ? (
          <View className="items-center rounded-3xl border border-line-glass bg-glass p-8 text-center shadow-sm">
            <View className="mb-3 size-12 items-center justify-center rounded-2xl bg-brand/10">
              <Icon
                name="list.bullet"
                fallback="list-outline"
                size={22}
                color="#2F6BFF"
              />
            </View>
            <Text className="text-[16px] font-semibold text-ink">
              Nenhum requisito cadastrado
            </Text>
            <Text className="mt-1 text-center text-[13px] text-ink3 leading-relaxed">
              Toque no botão + acima para adicionar regras ou avance para criar
              requisitos depois.
            </Text>
          </View>
        ) : (
          <View className="gap-3">
            {items.map((item) => {
              return (
                <Pressable
                  key={item.id}
                  onPress={() => toggleItem(item.id)}
                  className={`rounded-2xl border p-4 shadow-sm ${
                    item.checked
                      ? "border-line-glass bg-glass"
                      : "border-line/40 bg-card/40 opacity-60"
                  }`}
                >
                  <View className="flex-row items-start gap-3">
                    <View
                      className={`mt-0.5 size-5 items-center justify-center rounded-md border ${
                        item.checked
                          ? "border-brand bg-brand"
                          : "border-line bg-canvas"
                      }`}
                    >
                      {item.checked && (
                        <Icon
                          name="checkmark"
                          fallback="checkmark"
                          size={13}
                          color="#FFFFFF"
                        />
                      )}
                    </View>

                    <View className="flex-1 gap-1.5">
                      <Text
                        className={`text-[15px] font-medium leading-snug ${
                          item.disabledNote
                            ? "line-through text-ink3"
                            : item.checked
                            ? "text-ink"
                            : "text-ink3"
                        }`}
                      >
                        {item.title}
                      </Text>

                      {item.code ? (
                        <Text className="font-mono text-[12px] text-ink3">
                          {item.code}
                        </Text>
                      ) : null}

                      {item.warning ? (
                        <View className="mt-1 rounded-xl border border-warn/30 bg-warn/10 p-2.5">
                          <Text className="text-[12px] font-medium leading-snug text-warn">
                            {item.warning}
                          </Text>
                        </View>
                      ) : null}

                      {item.disabledNote ? (
                        <Text className="text-[12px] italic text-ink3">
                          {item.disabledNote}
                        </Text>
                      ) : null}
                    </View>
                  </View>
                </Pressable>
              );
            })}
          </View>
        )}
      </ScrollView>

      <View
        style={{ paddingBottom: Math.max(insets.bottom, 16) }}
        className="absolute bottom-0 left-0 right-0 border-t border-line-glass bg-canvas/90 px-5 pt-3"
      >
        <Pressable
          onPress={() => router.push("/projects/details")}
          className="h-13 items-center justify-center rounded-2xl bg-brand shadow-lg shadow-brand/25 active:opacity-90"
        >
          <Text className="text-[16px] font-semibold text-white">
            {selectedCount > 0
              ? `Salvar ${selectedCount} requisitos`
              : "Avançar para o projeto"}
          </Text>
        </Pressable>
      </View>
    </View>
  );
}
