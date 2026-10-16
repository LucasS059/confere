import { useRouter } from "expo-router";
import { Pressable, ScrollView, Text, View } from "react-native";
import { useSafeAreaInsets } from "react-native-safe-area-context";
import { Blob } from "@/components/blob";

export default function ConferirTabScreen() {
  const router = useRouter();
  const insets = useSafeAreaInsets();

  return (
    <View className="flex-1 overflow-hidden bg-canvas">
      <Blob
        color="#2F6BFF"
        className="-top-[100px] -right-[80px] size-[340px] opacity-[0.18] dark:opacity-[0.30]"
      />
      <ScrollView
        contentContainerStyle={{
          gap: 18,
          paddingTop: Math.max(insets.top + 16, 60),
          paddingHorizontal: 20,
          paddingBottom: Math.max(insets.bottom + 100, 120),
        }}
      >
        <View className="gap-1">
          <Text className="font-instrument-semibold text-[26px] text-ink tracking-[-0.6px]">
            Conferir entrega
          </Text>
          <Text className="font-instrument text-ink2 text-sm">
            Escolha um projeto existente ou crie um novo para iniciar a
            conferência.
          </Text>
        </View>

        <Pressable
          onPress={() => router.push("/projects/new")}
          className="h-[52px] items-center justify-center rounded-full bg-brand shadow-brand-button active:opacity-85"
        >
          <Text className="font-instrument-semibold text-[15px] text-white">
            + Criar novo projeto
          </Text>
        </Pressable>
      </ScrollView>
    </View>
  );
}
