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
import { authClient } from "@/lib/auth/client";
import { trpc } from "@/lib/trpc";

const RECENT_LIMIT = 5;

export default function HomeProjectsScreen() {
  const router = useRouter();
  const insets = useSafeAreaInsets();
  const placeholderColor = useCSSVariable("--ink3") as string | undefined;
  const { data: session } = authClient.useSession();
  const [search, setSearch] = useState("");

  const {
    data: projects = [],
    isLoading,
    isError,
    refetch,
  } = useQuery(trpc.project.list.queryOptions());

  const rawName = (session?.user as { name?: string } | undefined)?.name;
  const firstName = rawName?.trim().split(/\s+/)[0] || "Estudante";

  const initials = rawName
    ? rawName
        .trim()
        .split(" ")
        .map((n: string) => n[0])
        .filter(Boolean)
        .slice(0, 2)
        .join("")
        .toUpperCase()
    : "ES";

  const filteredProjects = projects.filter((p) =>
    p.name.toLowerCase().includes(search.trim().toLowerCase()),
  );
  const displayedProjects = search.trim()
    ? filteredProjects
    : filteredProjects.slice(0, RECENT_LIMIT);

  const featuredWithSub =
    projects.find((p) => p.latestSubmission !== null) ?? null;

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
          paddingTop: Math.max(insets.top + 16, 48),
          paddingHorizontal: 20,
          paddingBottom: insets.bottom + 110,
        }}
      >
        <View className="flex-row items-center justify-between rounded-3xl border border-line-glass bg-glass p-5 shadow-sm">
          <View className="flex-1 pr-3">
            <Text numberOfLines={1} className="font-bold text-[22px] text-ink">
              Olá, {firstName}
            </Text>
            <Text className="mt-1 text-[13px] text-ink2 leading-[18px]">
              Confira seus trabalhos com a rubrica antes de enviar
            </Text>
          </View>

          <Pressable
            onPress={() => router.navigate("/profile")}
            className="size-11 items-center justify-center rounded-full bg-brand shadow-brand/30 shadow-md active:opacity-80"
          >
            <Text className="font-bold text-[14px] text-white">{initials}</Text>
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
            placeholder="Buscar projetos..."
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

        {featuredWithSub?.latestSubmission && !search.trim() && (
          <Pressable
            onPress={() =>
              router.push({
                pathname: "/projects/details",
                params: { projectId: featuredWithSub.id },
              })
            }
            className="rounded-3xl border border-line-glass bg-glass p-5 shadow-sm active:opacity-85"
          >
            <View className="flex-row items-center justify-between gap-3">
              <View className="flex-1">
                <Text className="font-bold text-[11px] text-brand uppercase tracking-wider">
                  {featuredWithSub.latestSubmission.coverage !== null
                    ? "Conferido"
                    : "Pendente"}
                </Text>
                <Text
                  numberOfLines={1}
                  className="mt-1 font-bold text-[17px] text-ink"
                >
                  {featuredWithSub.name}
                </Text>
                <Text
                  numberOfLines={1}
                  className="mt-0.5 text-[12.5px] text-ink2"
                >
                  {featuredWithSub.latestSubmission.version} ·{" "}
                  {featuredWithSub.latestSubmission.filename}
                </Text>
              </View>

              <View className="size-13 items-center justify-center rounded-full border-[3px] border-brand/25 bg-brand/10">
                <Text className="font-bold text-[13px] text-ink">
                  {featuredWithSub.latestSubmission.coverage !== null
                    ? `${featuredWithSub.latestSubmission.coverage}%`
                    : "—"}
                </Text>
              </View>
            </View>

            {(featuredWithSub.latestSubmission.faltandoCount > 0 ||
              featuredWithSub.latestSubmission.revisarCount > 0) && (
              <View className="mt-3 flex-row items-center gap-2">
                {featuredWithSub.latestSubmission.faltandoCount > 0 && (
                  <View className="rounded-full bg-err/12 px-2.5 py-0.5">
                    <Text className="font-semibold text-[11.5px] text-err">
                      {featuredWithSub.latestSubmission.faltandoCount} faltando
                    </Text>
                  </View>
                )}
                {featuredWithSub.latestSubmission.revisarCount > 0 && (
                  <View className="rounded-full bg-warn/15 px-2.5 py-0.5">
                    <Text className="font-semibold text-[11.5px] text-warn">
                      {featuredWithSub.latestSubmission.revisarCount} revisar
                    </Text>
                  </View>
                )}
              </View>
            )}
          </Pressable>
        )}

        <View className="gap-2.5">
          <View className="flex-row items-center justify-between px-1">
            <Text className="font-bold text-[12px] text-ink3 uppercase tracking-wider">
              {search.trim() ? "Resultados" : "Projetos recentes"}
            </Text>
            {projects.length > RECENT_LIMIT && !search.trim() ? (
              <Pressable
                onPress={() => router.navigate("/projects")}
                hitSlop={8}
              >
                <Text className="font-semibold text-[13px] text-brand">
                  Ver todos ({projects.length})
                </Text>
              </Pressable>
            ) : (
              <Pressable onPress={() => router.navigate("/check")} hitSlop={8}>
                <Text className="font-semibold text-[13px] text-brand">
                  + Novo
                </Text>
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
          ) : displayedProjects.length === 0 ? (
            <View className="items-center justify-center rounded-3xl border border-line-glass bg-glass px-6 py-9 shadow-sm">
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
                  : "Nenhum projeto cadastrado"}
              </Text>
              <Text className="mt-1 text-center text-[13px] text-ink3">
                {search.trim()
                  ? "Tente buscar por outro nome."
                  : "Crie seu primeiro projeto para conferir suas entregas."}
              </Text>
              {!search.trim() && (
                <Pressable
                  onPress={() => router.navigate("/check")}
                  className="mt-4 rounded-full bg-brand px-5 py-2.5"
                >
                  <Text className="font-semibold text-[13.5px] text-white">
                    + Novo projeto
                  </Text>
                </Pressable>
              )}
            </View>
          ) : (
            <View className="overflow-hidden rounded-3xl border border-line-glass bg-glass shadow-sm">
              {displayedProjects.map((item, idx) => (
                <ProjectRow
                  key={item.id}
                  project={item}
                  showDivider={idx < displayedProjects.length - 1}
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
        </View>
      </ScrollView>
    </View>
  );
}
