import { useRouter } from "expo-router";
import { useEffect, useState } from "react";
import { Pressable, Text, View } from "react-native";
import { useSafeAreaInsets } from "react-native-safe-area-context";
import { Ionicons } from "@expo/vector-icons";
import { Blob } from "@/components/blob";

export default function ConferenceProgressScreen() {
  const router = useRouter();
  const insets = useSafeAreaInsets();
  const [progress, setProgress] = useState(58);

  useEffect(() => {
    const timer = setTimeout(() => {
      setProgress(100);
      setTimeout(() => {
        router.replace("/conferences/result");
      }, 800);
    }, 2500);

    return () => clearTimeout(timer);
  }, []);

  return (
    <View
      style={{
        paddingTop: insets.top + 20,
        paddingBottom: insets.bottom + 20,
        paddingHorizontal: 24,
      }}
      className="flex-1 justify-between overflow-hidden bg-canvas"
    >
      <Blob
        color="#2F6BFF"
        className="-top-[100px] left-[20px] size-[380px] opacity-[0.20] dark:opacity-[0.32]"
      />
      <Blob
        color="#10B981"
        className="bottom-[80px] -right-[120px] size-[320px] opacity-[0.14] dark:opacity-[0.22]"
      />

      <View className="items-center gap-1.5">
        <Text className="text-[13px] font-medium text-ink3">Conferindo</Text>
        <Text className="text-[20px] font-bold text-ink">
          relatorio-final-v3.pdf
        </Text>
      </View>

      <View className="items-center justify-center my-6">
        <View className="size-48 items-center justify-center rounded-full border-8 border-brand/20 bg-glass shadow-lg shadow-brand/10">
          <View className="items-center gap-1">
            <Text className="font-mono text-[46px] font-bold text-brand">
              {progress}%
            </Text>
            <Text className="text-[12px] font-medium text-ink2">
              {progress === 100 ? "concluído!" : "mapeando requisitos"}
            </Text>
          </View>
        </View>
      </View>

      <View className="rounded-3xl border border-line-glass bg-glass p-5 shadow-sm gap-4">
        <View className="flex-row items-center justify-between">
          <View className="flex-row items-center gap-3">
            <View className="size-6 items-center justify-center rounded-full bg-ok">
              <Ionicons name="checkmark" size={14} color="#FFFFFF" />
            </View>
            <Text className="text-[14px] font-medium text-ink">Lendo o PDF</Text>
          </View>
          <Text className="font-mono text-[12px] text-ok">ok</Text>
        </View>

        <View className="flex-row items-center justify-between">
          <View className="flex-row items-center gap-3">
            <View className="size-6 items-center justify-center rounded-full bg-brand/20">
              <Ionicons name="sync" size={14} color="#2F6BFF" />
            </View>
            <Text className="text-[14px] font-medium text-ink">
              Mapeando requisitos
            </Text>
          </View>
          <Text className="font-mono text-[12px] text-ink3">14 itens</Text>
        </View>

        <View className="flex-row items-center justify-between">
          <View className="flex-row items-center gap-3">
            <View className="size-6 items-center justify-center rounded-full border border-line bg-canvas" />
            <Text className="text-[14px] text-ink3">Buscando evidências</Text>
          </View>
        </View>

        <View className="flex-row items-center justify-between">
          <View className="flex-row items-center gap-3">
            <View className="size-6 items-center justify-center rounded-full border border-line bg-canvas" />
            <Text className="text-[14px] text-ink3">Calculando confiança</Text>
          </View>
        </View>
      </View>

      <View className="items-center gap-4">
        <Text className="text-center text-[12px] text-ink3">
          Pode sair desta tela. Avisamos quando terminar.
        </Text>

        <Pressable
          onPress={() => router.back()}
          className="h-12 w-full items-center justify-center rounded-2xl border border-line-glass bg-glass active:opacity-80"
        >
          <Text className="text-[15px] font-semibold text-ink2">Cancelar</Text>
        </Pressable>
      </View>
    </View>
  );
}
