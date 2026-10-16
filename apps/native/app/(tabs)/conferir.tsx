import { useRouter } from "expo-router";
import { Pressable, ScrollView, Text, View } from "react-native";
import { useSafeAreaInsets } from "react-native-safe-area-context";
import { Ionicons } from "@expo/vector-icons";
import { Blob } from "@/components/blob";

export default function ConferirTabScreen() {
  const router = useRouter();
  const insets = useSafeAreaInsets();

  return (
    <View className="flex-1 overflow-hidden bg-canvas">
      <Blob
        color="#2F6BFF"
        className="-top-[100px] -right-[80px] size-[340px] opacity-[0.16] dark:opacity-[0.28]"
      />
      <Blob
        color="#10B981"
        className="top-[320px] -left-[100px] size-[300px] opacity-[0.12] dark:opacity-[0.20]"
      />

      <ScrollView
        showsVerticalScrollIndicator={false}
        contentContainerStyle={{
          gap: 20,
          paddingTop: Math.max(insets.top + 20, 50),
          paddingHorizontal: 20,
          paddingBottom: insets.bottom + 100,
        }}
      >
        <View className="gap-1">
          <Text className="text-[26px] font-bold tracking-tight text-ink">
            Conferir entrega
          </Text>
          <Text className="text-[14px] text-ink2">
            Escolha um projeto existente ou inicie uma nova conferência.
          </Text>
        </View>

        <View className="gap-3">
          <Pressable
            onPress={() => router.push("/submissions/new")}
            className="rounded-3xl border border-line-glass bg-glass p-5 shadow-sm active:opacity-85"
          >
            <View className="flex-row items-center gap-3.5 mb-2">
              <View className="size-11 items-center justify-center rounded-2xl bg-brand/10">
                <Ionicons name="scan-outline" size={22} color="#2F6BFF" />
              </View>
              <View className="flex-1">
                <Text className="text-[16px] font-bold text-ink">
                  Conferir no projeto atual
                </Text>
                <Text className="text-[12px] text-ink3">
                  Ensino híbrido no ensino médio
                </Text>
              </View>
            </View>
            <Text className="text-[13px] leading-relaxed text-ink2">
              Envie o PDF do seu trabalho para validar contra os 14 requisitos
              ativos.
            </Text>
          </Pressable>

          <Pressable
            onPress={() => router.push("/projects/new")}
            className="rounded-3xl border border-line-glass bg-glass p-5 shadow-sm active:opacity-85"
          >
            <View className="flex-row items-center gap-3.5 mb-2">
              <View className="size-11 items-center justify-center rounded-2xl bg-ok/10">
                <Ionicons name="add-circle-outline" size={22} color="#10B981" />
              </View>
              <View className="flex-1">
                <Text className="text-[16px] font-bold text-ink">
                  Criar novo projeto
                </Text>
                <Text className="text-[12px] text-ink3">
                  Adicionar edital ou requisitos
                </Text>
              </View>
            </View>
            <Text className="text-[13px] leading-relaxed text-ink2">
              Cole o edital ou envie o documento para extrair as regras com IA.
            </Text>
          </Pressable>
        </View>
      </ScrollView>
    </View>
  );
}
