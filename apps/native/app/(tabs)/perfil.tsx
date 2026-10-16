import { Ionicons } from "@expo/vector-icons";
import { useRouter } from "expo-router";
import { Pressable, ScrollView, Text, View } from "react-native";
import { useSafeAreaInsets } from "react-native-safe-area-context";
import { useCSSVariable } from "uniwind";
import { Blob } from "@/components/blob";
import { authClient } from "@/lib/auth-client";
import { queryClient } from "@/utils/trpc";

export default function PerfilTabScreen() {
  const router = useRouter();
  const insets = useSafeAreaInsets();
  const { data: session } = authClient.useSession();
  const chevronColor = (useCSSVariable("--ink3") as string) || "#8A91A0";

  const userName = session?.user?.name || "Estudante";
  const userEmail = session?.user?.email || "";
  const initials = session?.user?.name
    ? session.user.name
        .trim()
        .split(" ")
        .filter(Boolean)
        .slice(0, 2)
        .map((p) => p[0]?.toUpperCase())
        .join("")
    : "CF";

  return (
    <View className="flex-1 overflow-hidden bg-canvas">
      <Blob
        color="#2F6BFF"
        className="-top-[120px] -left-[80px] size-[360px] opacity-[0.18] dark:opacity-[0.30]"
      />

      <ScrollView
        contentContainerStyle={{
          gap: 20,
          paddingTop: Math.max(insets.top + 20, 64),
          paddingHorizontal: 20,
          paddingBottom: Math.max(insets.bottom + 100, 120),
        }}
      >
        <View className="flex-row items-center gap-4">
          <View className="size-16 items-center justify-center rounded-full bg-brand shadow-brand-tile">
            <Text className="font-instrument-semibold text-white text-xl">
              {initials}
            </Text>
          </View>
          <View className="flex-1 gap-0.5">
            <Text className="font-instrument-semibold text-[22px] text-ink tracking-[-0.5px]">
              {userName}
            </Text>
            {userEmail ? (
              <Text className="font-instrument text-ink2 text-xs">
                {userEmail}
              </Text>
            ) : null}
          </View>
        </View>

        <View className="flex-row gap-2.5">
          <View className="flex-1 gap-0.5 rounded-2xl border border-hair bg-card p-3.5 shadow-xs">
            <Text className="font-instrument-semibold text-[22px] text-ink">
              0
            </Text>
            <Text className="font-instrument text-ink3 text-xs">projetos</Text>
          </View>
          <View className="flex-1 gap-0.5 rounded-2xl border border-hair bg-card p-3.5 shadow-xs">
            <Text className="font-instrument-semibold text-[22px] text-ink">
              0
            </Text>
            <Text className="font-instrument text-ink3 text-xs">
              conferências
            </Text>
          </View>
          <View className="flex-1 gap-0.5 rounded-2xl border border-hair bg-card p-3.5 shadow-xs">
            <Text className="font-instrument-semibold text-[22px] text-ink">
              0
            </Text>
            <Text className="font-instrument text-ink3 text-xs">
              requisitos
            </Text>
          </View>
        </View>

        <View className="gap-2.5">
          <Pressable className="flex-row items-center justify-between rounded-2xl border border-hair bg-card px-4 py-4 active:opacity-80">
            <Text className="font-instrument-medium text-[14px] text-ink">
              Ajuda e feedback
            </Text>
            <Ionicons name="chevron-forward" size={16} color={chevronColor} />
          </Pressable>
        </View>

        <Pressable
          accessibilityRole="button"
          onPress={() => {
            authClient.signOut();
            queryClient.invalidateQueries();
          }}
          className="mt-2 items-center py-3 active:opacity-70"
        >
          <Text className="font-instrument-semibold text-[14px] text-err">
            Sair da conta
          </Text>
        </Pressable>
      </ScrollView>
    </View>
  );
}
