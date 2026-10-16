import { useRouter } from "expo-router";
import { useState } from "react";
import { Pressable, ScrollView, Text, TextInput, View } from "react-native";
import { useSafeAreaInsets } from "react-native-safe-area-context";
import Svg, { Circle } from "react-native-svg";
import { useCSSVariable } from "uniwind";
import { Blob } from "@/components/blob";
import { Icon } from "@/components/icon";
import { authClient } from "@/lib/auth-client";

export type Project = {
  id: string;
  tag: string;
  title: string;
  meta: string;
  coverage: number | null;
  pendingDelivery?: {
    filename: string;
    date: string;
    missingCount: number;
    reviewCount: number;
    coverage: number;
  };
};

function CoverageRing({ coverage }: { coverage: number }) {
  const size = 56;
  const strokeWidth = 5;
  const radius = (size - strokeWidth) / 2;
  const circumference = 2 * Math.PI * radius;
  const progressLength = circumference * (coverage / 100);

  return (
    <View className="size-14 items-center justify-center">
      <Svg
        width={size}
        height={size}
        style={{ transform: [{ rotate: "-90deg" }] }}
      >
        <Circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          stroke="rgba(30, 158, 98, 0.2)"
          strokeWidth={strokeWidth}
          fill="none"
        />
        <Circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          stroke="#1E9E62"
          strokeWidth={strokeWidth}
          fill="none"
          strokeDasharray={`${progressLength} ${circumference}`}
          strokeLinecap="round"
        />
      </Svg>
      <Text className="absolute font-instrument-semibold text-[13px] text-ink">
        {coverage}%
      </Text>
    </View>
  );
}

export default function HomeProjectsScreen() {
  const router = useRouter();
  const insets = useSafeAreaInsets();
  const { data: session } = authClient.useSession();
  const placeholderColor = useCSSVariable("--ink3") as string | undefined;
  const [search, setSearch] = useState("");
  const [projects] = useState<Project[]>([]);

  const firstName = session?.user?.name
    ? session.user.name.trim().split(" ")[0]
    : "Estudante";

  const initials = session?.user?.name
    ? session.user.name
        .trim()
        .split(" ")
        .filter(Boolean)
        .slice(0, 2)
        .map((p) => p[0]?.toUpperCase())
        .join("")
    : "CF";

  const filteredProjects = projects.filter((p) =>
    p.title.toLowerCase().includes(search.trim().toLowerCase()),
  );

  const pendingProject = projects.find((p) => Boolean(p.pendingDelivery));

  return (
    <View className="flex-1 overflow-hidden bg-canvas">
      <Blob
        color="#2F6BFF"
        className="-top-[120px] -left-[80px] size-[360px] opacity-[0.18] dark:opacity-[0.30]"
      />
      <Blob
        color="#1E9E62"
        className="top-[320px] -right-[140px] size-[320px] opacity-[0.14] dark:opacity-[0.24]"
      />

      <ScrollView
        contentContainerStyle={{
          gap: 18,
          paddingTop: Math.max(insets.top + 12, 56),
          paddingHorizontal: 20,
          paddingBottom: Math.max(insets.bottom + 100, 120),
        }}
        keyboardShouldPersistTaps="handled"
      >
        <View className="flex-row items-center justify-between">
          <View>
            <Text className="font-instrument text-ink2 text-xs">Boa tarde,</Text>
            <Text className="font-instrument-semibold text-[28px] text-ink leading-[32px] tracking-[-0.7px]">
              {firstName}
            </Text>
          </View>
          <Pressable
            accessibilityRole="button"
            onPress={() => router.push("/(tabs)/perfil")}
            className="size-10 items-center justify-center rounded-full border-[0.5px] border-glass-bd bg-brand/15 shadow-glass"
          >
            <Text className="font-instrument-semibold text-[13px] text-brand">
              {initials}
            </Text>
          </Pressable>
        </View>

        <View className="h-[44px] flex-row items-center gap-2.5 rounded-full border-[0.5px] border-glass-bd bg-glass px-4 shadow-glass backdrop-blur-[18px] backdrop-saturate-[180%]">
          <Icon
            name="magnifyingglass"
            fallback="search-outline"
            size={16}
            color={placeholderColor || "#8A91A0"}
          />
          <TextInput
            value={search}
            onChangeText={setSearch}
            placeholder="Buscar projetos"
            placeholderTextColor={placeholderColor}
            className="h-full flex-1 font-instrument text-ink text-sm web:outline-none"
          />
        </View>

        {pendingProject && pendingProject.pendingDelivery && (
          <Pressable
            onPress={() => router.push("/projects/new")}
            className="gap-3.5 rounded-[22px] border border-hair bg-card p-4 shadow-xs active:opacity-90"
          >
            <View className="flex-row items-center justify-between gap-3">
              <View className="flex-1 gap-1">
                <Text className="font-instrument-semibold text-[10px] text-brand tracking-[0.8px]">
                  PENDENTE
                </Text>
                <Text className="font-instrument-semibold text-[16px] text-ink leading-[20px]">
                  {pendingProject.title}
                </Text>
                <Text className="font-instrument text-ink3 text-xs">
                  {pendingProject.pendingDelivery.filename} ·{" "}
                  {pendingProject.pendingDelivery.date}
                </Text>
              </View>

              <CoverageRing
                coverage={pendingProject.pendingDelivery.coverage}
              />
            </View>

            <View className="flex-row items-center gap-2">
              <View className="rounded-full bg-err-soft px-3 py-1">
                <Text className="font-instrument-semibold text-[11px] text-err">
                  {pendingProject.pendingDelivery.missingCount} faltando
                </Text>
              </View>
              <View className="rounded-full bg-warn-soft px-3 py-1">
                <Text className="font-instrument-semibold text-[11px] text-warn">
                  {pendingProject.pendingDelivery.reviewCount} revisar
                </Text>
              </View>
            </View>
          </Pressable>
        )}

        <View className="gap-3 pt-1">
          <View className="flex-row items-center justify-between px-1">
            <Text className="font-instrument-semibold text-[15px] text-ink">
              Meus projetos
            </Text>
            <Pressable
              accessibilityRole="button"
              onPress={() => router.push("/projects/new")}
            >
              <Text className="font-instrument-semibold text-[13px] text-brand">
                + Novo
              </Text>
            </Pressable>
          </View>

          {filteredProjects.length === 0 ? (
            <View className="items-center gap-3 rounded-[22px] border border-hair bg-card p-6 shadow-xs">
              <View className="size-12 items-center justify-center rounded-2xl bg-brand-soft">
                <Icon name="folder" fallback="folder-open-outline" size={24} color="#2F6BFF" />
              </View>
              <View className="items-center gap-1">
                <Text className="font-instrument-semibold text-[16px] text-ink">
                  Nenhum projeto cadastrado
                </Text>
                <Text className="text-center font-instrument text-[13.5px] text-ink2 leading-[19px]">
                  Crie seu primeiro projeto para colar ou enviar o edital e
                  começar a conferir requisitos.
                </Text>
              </View>
              <Pressable
                onPress={() => router.push("/projects/new")}
                className="mt-1 h-11 flex-row items-center justify-center rounded-full bg-brand px-5 shadow-brand-button active:opacity-85"
              >
                <Text className="font-instrument-semibold text-[14px] text-white">
                  + Criar projeto
                </Text>
              </Pressable>
            </View>
          ) : (
            <View className="gap-2.5">
              {filteredProjects.map((project) => (
                <Pressable
                  key={project.id}
                  onPress={() => router.push("/projects/new")}
                  className="flex-row items-center justify-between gap-3 rounded-2xl border border-hair bg-card p-3.5 shadow-xs active:opacity-85"
                >
                  <View className="size-10 items-center justify-center rounded-xl bg-brand-soft">
                    <Text className="font-instrument-semibold text-[11px] text-brand">
                      {project.tag}
                    </Text>
                  </View>

                  <View className="flex-1 gap-0.5">
                    <Text className="font-instrument-semibold text-[14px] text-ink">
                      {project.title}
                    </Text>
                    <Text className="font-instrument text-ink3 text-xs">
                      {project.meta}
                    </Text>
                  </View>

                  <Text
                    className={`font-instrument-semibold text-[13px] ${
                      project.coverage === 100
                        ? "text-ok"
                        : project.coverage !== null
                          ? "text-ink"
                          : "text-ink3"
                    }`}
                  >
                    {project.coverage !== null ? `${project.coverage}%` : "—"}
                  </Text>
                </Pressable>
              ))}
            </View>
          )}
        </View>
      </ScrollView>
    </View>
  );
}
