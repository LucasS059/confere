import { Ionicons } from "@expo/vector-icons";
import { ScrollView, Text, View } from "react-native";
import { useSafeAreaInsets } from "react-native-safe-area-context";
import { Blob } from "@/components/blob";

export default function HistoricoTabScreen() {
  const insets = useSafeAreaInsets();

  return (
    <View className="flex-1 overflow-hidden bg-canvas">
      <Blob
        color="#2F6BFF"
        className="-top-[120px] -left-[80px] size-[360px] opacity-[0.18] dark:opacity-[0.30]"
      />
      <ScrollView
        contentContainerStyle={{
          gap: 20,
          paddingTop: Math.max(insets.top + 16, 60),
          paddingHorizontal: 20,
          paddingBottom: Math.max(insets.bottom + 100, 120),
        }}
      >
        <Text className="font-instrument-semibold text-[26px] text-ink tracking-[-0.6px]">
          Histórico
        </Text>

        <View className="items-center gap-3 rounded-[22px] border border-hair bg-card p-8 shadow-xs">
          <View className="size-12 items-center justify-center rounded-2xl bg-brand-soft">
            <Ionicons name="time-outline" size={24} color="#2F6BFF" />
          </View>
          <View className="items-center gap-1">
            <Text className="font-instrument-semibold text-[16px] text-ink">
              Nenhuma conferência realizada
            </Text>
            <Text className="text-center font-instrument text-[13.5px] text-ink2 leading-[19px]">
              Quando você submeter uma entrega contra os requisitos de um
              projeto, o histórico e as métricas de cobertura aparecerão aqui.
            </Text>
          </View>
        </View>
      </ScrollView>
    </View>
  );
}
