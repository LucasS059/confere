import { useRouter } from "expo-router";
import { Pressable, ScrollView, Text, View } from "react-native";
import { useSafeAreaInsets } from "react-native-safe-area-context";
import { Blob } from "@/components/ui/blob";
import { Icon } from "@/components/ui/icon";
import { authClient } from "@/lib/auth/client";
import { queryClient } from "@/lib/trpc";

export default function PerfilTabScreen() {
  const router = useRouter();
  const insets = useSafeAreaInsets();
  const { data: session } = authClient.useSession();

  const displayName = session?.user?.name || "Estudante";
  const displayEmail = session?.user?.email || "";
  const initials = displayName
    .split(" ")
    .map((n) => n[0])
    .filter(Boolean)
    .slice(0, 2)
    .join("")
    .toUpperCase();

  async function handleSignOut() {
    await authClient.signOut();
    queryClient.clear();
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

      <ScrollView
        showsVerticalScrollIndicator={false}
        contentContainerStyle={{
          paddingHorizontal: 20,
          paddingTop: Math.max(insets.top + 20, 50),
          paddingBottom: insets.bottom + 100,
        }}
      >
        <View className="mb-6 items-center">
          <View className="mb-3 size-20 items-center justify-center rounded-full bg-brand shadow-brand/30 shadow-lg">
            <Text className="font-bold text-[24px] text-white tracking-wide">
              {initials}
            </Text>
          </View>

          <Text className="font-bold text-[20px] text-ink">{displayName}</Text>
          {displayEmail ? (
            <Text className="mt-0.5 text-[13px] text-ink2">{displayEmail}</Text>
          ) : null}
        </View>

        <View className="mb-6 flex-row gap-3">
          <View className="flex-1 items-center rounded-2xl border border-line-glass bg-glass p-3.5 shadow-sm">
            <Text className="font-bold text-[20px] text-ink">0</Text>
            <Text className="text-[12px] text-ink3">projetos</Text>
          </View>
          <View className="flex-1 items-center rounded-2xl border border-line-glass bg-glass p-3.5 shadow-sm">
            <Text className="font-bold text-[20px] text-ink">0</Text>
            <Text className="text-[12px] text-ink3">conferências</Text>
          </View>
          <View className="flex-1 items-center rounded-2xl border border-line-glass bg-glass p-3.5 shadow-sm">
            <Text className="font-bold text-[20px] text-ink">0</Text>
            <Text className="text-center text-[11px] text-ink3">
              requisitos
            </Text>
          </View>
        </View>

        <View className="mb-6 rounded-3xl border border-line-glass bg-glass p-2 shadow-sm">
          <Pressable
            onPress={() => router.push("/settings")}
            className="flex-row items-center justify-between rounded-2xl p-3.5 active:bg-card/50"
          >
            <View className="flex-row items-center gap-3">
              <View className="size-9 items-center justify-center rounded-xl bg-brand/10">
                <Icon
                  name="gearshape"
                  fallback="settings-outline"
                  size={18}
                  color="#2F6BFF"
                />
              </View>
              <Text className="font-medium text-[15px] text-ink">
                Configurações
              </Text>
            </View>
            <Icon
              name="chevron.forward"
              fallback="chevron-forward"
              size={16}
              color="#94A3B8"
            />
          </Pressable>

          <View className="mx-3.5 h-[1px] bg-line-glass" />

          <Pressable className="flex-row items-center justify-between rounded-2xl p-3.5 active:bg-card/50">
            <View className="flex-row items-center gap-3">
              <View className="size-9 items-center justify-center rounded-xl bg-ok/10">
                <Icon
                  name="arrow.down.to.line"
                  fallback="download-outline"
                  size={18}
                  color="#10B981"
                />
              </View>
              <Text className="font-medium text-[15px] text-ink">
                Relatórios exportados
              </Text>
            </View>
            <View className="flex-row items-center gap-2">
              <View className="rounded-full bg-line px-2 py-0.5">
                <Text className="font-bold font-mono text-[11px] text-ink2">
                  0
                </Text>
              </View>
              <Icon
                name="chevron.forward"
                fallback="chevron-forward"
                size={16}
                color="#94A3B8"
              />
            </View>
          </Pressable>

          <View className="mx-3.5 h-[1px] bg-line-glass" />

          <Pressable className="flex-row items-center justify-between rounded-2xl p-3.5 active:bg-card/50">
            <View className="flex-row items-center gap-3">
              <View className="size-9 items-center justify-center rounded-xl bg-warn/10">
                <Icon
                  name="person.2"
                  fallback="people-outline"
                  size={18}
                  color="#F59E0B"
                />
              </View>
              <Text className="font-medium text-[15px] text-ink">
                Orientadores conectados
              </Text>
            </View>
            <View className="flex-row items-center gap-2">
              <View className="rounded-full bg-line px-2 py-0.5">
                <Text className="font-bold font-mono text-[11px] text-ink2">
                  0
                </Text>
              </View>
              <Icon
                name="chevron.forward"
                fallback="chevron-forward"
                size={16}
                color="#94A3B8"
              />
            </View>
          </Pressable>

          <View className="mx-3.5 h-[1px] bg-line-glass" />

          <Pressable className="flex-row items-center justify-between rounded-2xl p-3.5 active:bg-card/50">
            <View className="flex-row items-center gap-3">
              <View className="size-9 items-center justify-center rounded-xl bg-ink/5">
                <Icon
                  name="questionmark.circle"
                  fallback="help-circle-outline"
                  size={18}
                  color="#64748B"
                />
              </View>
              <Text className="font-medium text-[15px] text-ink">
                Ajuda e feedback
              </Text>
            </View>
            <Icon
              name="chevron.forward"
              fallback="chevron-forward"
              size={16}
              color="#94A3B8"
            />
          </Pressable>
        </View>

        <Pressable
          onPress={handleSignOut}
          className="h-12 items-center justify-center rounded-2xl border border-err/20 bg-err/5 active:bg-err/10"
        >
          <Text className="font-semibold text-[15px] text-err">
            Sair da conta
          </Text>
        </Pressable>
      </ScrollView>
    </View>
  );
}
