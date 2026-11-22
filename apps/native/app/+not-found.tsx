import { Stack, useRouter } from "expo-router";
import { Pressable, Text, View } from "react-native";

export default function NotFoundScreen() {
  const router = useRouter();

  return (
    <>
      <Stack.Screen options={{ title: "Página não encontrada" }} />
      <View className="flex-1 items-center justify-center bg-canvas px-6">
        <View className="w-full max-w-sm items-center rounded-3xl border border-line-glass bg-glass p-6 shadow-sm">
          <Text className="font-bold text-[18px] text-ink">
            Página não encontrada
          </Text>
          <Text className="mt-1.5 text-center text-[13.5px] text-ink3">
            A tela que você tentou acessar não existe.
          </Text>
          <Pressable
            onPress={() => router.replace("/(tabs)")}
            className="mt-5 h-[44px] items-center justify-center rounded-full bg-brand px-6 active:opacity-85"
          >
            <Text className="font-semibold text-[14px] text-white">
              Voltar ao início
            </Text>
          </Pressable>
        </View>
      </View>
    </>
  );
}
