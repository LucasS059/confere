import { useQuery } from "@tanstack/react-query";
import { useRouter } from "expo-router";
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
import { ProjectRow } from "@/components/projects/project-row";
import { Blob } from "@/components/ui/blob";
import { Icon } from "@/components/ui/icon";
import { trpc } from "@/lib/trpc";

export default function AllProjectsTabScreen() {
  const router = useRouter();
  const insets = useSafeAreaInsets();
  const placeholderColor = useCSSVariable("--ink3") as string | undefined;
  const [search, setSearch] = useState("");

  const {
    data: projects = [],
    isLoading,
    isError,
    refetch,
  } = useQuery(trpc.project.list.queryOptions());

  const filtered = projects.filter((p) =>
    p.name.toLowerCase().includes(search.trim().toLowerCase()),
  );

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
        keyboardShouldPersistTaps="handled"
        contentContainerStyle={{
          gap: 16,
          paddingHorizontal: 20,
          paddingTop: Math.max(insets.top + 16, 48),
          paddingBottom: insets.bottom + 110,
        }}
      >
        <View className="flex-row items-center justify-between rounded-3xl border border-line-glass bg-glass p-5 shadow-sm">
          <View className="flex-1 pr-3">
            <Text className="font-bold text-[22px] text-ink">
              Meus projetos
            </Text>
            <Text className="mt-0.5 text-[13px] text-ink2">
              {projects.length === 0
                ? "Nenhum projeto cadastrado"
                : `${projects.length} ${
                    projects.length === 1
                      ? "projeto cadastrado"
                      : "projetos cadastrados"
                  }`}
            </Text>
          </View>

          <Pressable
            onPress={() => router.navigate("/check")}
            className="size-10 items-center justify-center rounded-full bg-brand active:opacity-85"
          >
            <Icon name="plus" fallback="add" size={20} color="#FFFFFF" />
          </Pressable>
        </View>

        <View className="h-[44px] flex-row items-center gap-2.5 rounded-full border border-line-glass bg-glass px-4 shadow-sm">
          <Icon
            name="magnifyingglass"
            fallback="search-outline"
            size={16}
            color="#8A91A0"
          />
          <TextInput
            value={search}
            onChangeText={setSearch}
            placeholder="Buscar projeto..."
            placeholderTextColor={placeholderColor}
            className="flex-1 text-[14px] text-ink web:outline-none"
          />
          {search.length > 0 && (
            <Pressable onPress={() => setSearch("")} hitSlop={8}>
              <Icon
                name="xmark.circle.fill"
                fallback="close-circle"
                size={16}
                color="#8A91A0"
              />
            </Pressable>
          )}
        </View>

        {isLoading ? (
          <ActivityIndicator className="my-10" color="#2F6BFF" />
        ) : isError ? (
          <View className="items-center rounded-3xl border border-line-glass bg-glass p-6 shadow-sm">
            <Text className="font-semibold text-[15px] text-ink">
              Não foi possível carregar os projetos
            </Text>
            <Pressable
              onPress={() => {
                void refetch();
              }}
              className="mt-3 rounded-full bg-brand px-5 py-2.5"
            >
              <Text className="font-semibold text-[13px] text-white">
                Tentar novamente
              </Text>
            </Pressable>
          </View>
        ) : filtered.length === 0 ? (
          <View className="items-center rounded-3xl border border-line-glass bg-glass px-6 py-9 shadow-sm">
            <View className="mb-3 size-12 items-center justify-center rounded-2xl bg-brand/10">
              <Icon
                name="folder.badge.plus"
                fallback="folder-open-outline"
                size={22}
                color="#2F6BFF"
              />
            </View>
            <Text className="font-semibold text-[16px] text-ink">
              {search.trim()
                ? "Nenhum projeto encontrado"
                : "Nenhum projeto ainda"}
            </Text>
            <Text className="mt-1 text-center text-[13px] text-ink3">
              {search.trim()
                ? "Tente buscar por outro nome."
                : "Crie seu primeiro projeto na aba Novo projeto."}
            </Text>
            {!search.trim() && (
              <Pressable
                onPress={() => router.navigate("/check")}
                className="mt-4 rounded-full bg-brand px-5 py-2.5"
              >
                <Text className="font-semibold text-[13.5px] text-white">
                  Criar projeto
                </Text>
              </Pressable>
            )}
          </View>
        ) : (
          <View className="overflow-hidden rounded-3xl border border-line-glass bg-glass shadow-sm">
            {filtered.map((item, idx) => (
              <ProjectRow
                key={item.id}
                project={item}
                showDivider={idx < filtered.length - 1}
                onPress={() =>
                  router.push({
                    pathname: "/projects/details",
                    params: { projectId: item.id },
                  })
                }
              />
            ))}
          </View>
        )}
      </ScrollView>
    </View>
  );
}
