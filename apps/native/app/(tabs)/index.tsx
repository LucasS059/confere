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
import Svg, { Circle } from "react-native-svg";
import { useCSSVariable } from "uniwind";
import { Blob } from "@/components/blob";
import { Icon } from "@/components/icon";
import { authClient } from "@/lib/auth-client";
import { trpc } from "@/utils/trpc";

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

  const { data: projects = [], isLoading } = useQuery(
    trpc.project.list.queryOptions(),
  );

  const firstName = session?.user?.name
    ? session.user.name.trim().split(" ")[0]
    : "Estudante";

  const initials = session?.user?.name
    ? session.user.name
        .trim()
        .split(" ")
        .map((n) => n[0])
        .filter(Boolean)
        .slice(0, 2)
        .join("")
        .toUpperCase()
    : "ES";

  const filtered = projects.filter((p) =>
    p.name.toLowerCase().includes(search.toLowerCase()),
  );

  return (
    <View className="flex-1 overflow-hidden bg-canvas">
      <Blob
        color="#2F6BFF"
        className="-top-[120px] -left-[100px] size-[420px] opacity-[0.20] dark:opacity-[0.35]"
      />
      <Blob
        color="#1E9E62"
        className="top-[320px] -right-[160px] size-[380px] opacity-[0.16] dark:opacity-[0.26]"
      />

      <ScrollView
        showsVerticalScrollIndicator={false}
        contentContainerStyle={{
          gap: 20,
          paddingTop: Math.max(insets.top + 16, 44),
          paddingHorizontal: 20,
          paddingBottom: insets.bottom + 90,
        }}
      >
        {/* Cabeçalho */}
        <View className="flex-row items-center justify-between">
          <View className="flex-row items-center gap-3">
            <View className="size-11 items-center justify-center rounded-full bg-brand-gradient shadow-brand-tile">
              <Text className="font-instrument-bold text-sm text-white">
                {initials}
              </Text>
            </View>
            <View>
              <Text className="font-instrument text-ink3 text-xs">
                Bem-vindo de volta
              </Text>
              <Text className="font-instrument-semibold text-[17px] text-ink leading-tight">
                {firstName}
              </Text>
            </View>
          </View>

          <Pressable
            onPress={() => router.push("/projects/new")}
            className="flex-row items-center gap-1.5 rounded-full bg-brand px-3.5 py-2 shadow-brand-button active:opacity-85"
          >
            <Icon name="plus" fallback="add" size={14} color="#ffffff" />
            <Text className="font-instrument-semibold text-xs text-white">
              Novo projeto
            </Text>
          </Pressable>
        </View>

        {/* Barra de Busca */}
        <View className="h-11 flex-row items-center gap-2 rounded-2xl border border-hair bg-card px-3.5 shadow-xs">
          <Icon name="magnifyingglass" fallback="search" size={15} color="#94A3B8" />
          <TextInput
            value={search}
            onChangeText={setSearch}
            placeholder="Buscar entre meus projetos..."
            placeholderTextColor={placeholderColor}
            className="flex-1 font-instrument text-sm text-ink web:outline-none"
          />
        </View>

        {/* Lista de Projetos */}
        <View className="gap-2.5">
          <Text className="px-1 font-instrument text-ink2 text-xs uppercase tracking-wider">
            Meus Projetos Cadastrados
          </Text>

          {isLoading ? (
            <ActivityIndicator className="my-10" color="#2F6BFF" />
          ) : filtered.length === 0 ? (
            <View className="items-center justify-center rounded-3xl border border-line-glass bg-glass p-8 text-center my-4">
              <Icon
                name="folder.badge.plus"
                fallback="folder-open-outline"
                size={40}
                color="#94A3B8"
              />
              <Text className="mt-3 text-[16px] font-bold text-ink">
                Nenhum projeto cadastrado ainda
              </Text>
              <Text className="mt-1 text-center text-[13px] text-ink2 leading-relaxed">
                Crie seu primeiro projeto colando a rubrica ou critérios informados pelo seu professor.
              </Text>
              <Pressable
                onPress={() => router.push("/projects/new")}
                className="mt-4 rounded-full bg-brand px-5 py-2.5 shadow-brand-button active:opacity-85"
              >
                <Text className="font-instrument-semibold text-[13px] text-white">
                  Cadastrar primeiro projeto
                </Text>
              </Pressable>
            </View>
          ) : (
            filtered.map((item) => (
              <Pressable
                key={item.id}
                onPress={() => {
                  router.push({
                    pathname: "/projects/details",
                    params: { projectId: item.id },
                  });
                }}
                className="rounded-3xl border border-line-glass bg-glass p-4 shadow-sm active:bg-card/60"
              >
                <View className="flex-row items-start justify-between gap-3">
                  <View className="flex-1 gap-1">
                    <View className="flex-row items-center gap-2">
                      <View className="rounded-md bg-brand/10 px-2 py-0.5">
                        <Text className="font-mono text-[10px] font-bold text-brand uppercase">
                          {item.sourceType}
                        </Text>
                      </View>
                      <Text className="text-[12px] text-ink3">
                        {item.requirementsCount} requisitos
                      </Text>
                    </View>

                    <Text className="text-[17px] font-bold text-ink">
                      {item.name}
                    </Text>

                    {item.latestSubmission ? (
                      <Text className="text-[13px] text-ink2">
                        Última entrega: {item.latestSubmission.filename} (
                        {item.latestSubmission.version})
                      </Text>
                    ) : (
                      <Text className="text-[13px] text-ink3">
                        Nenhuma entrega em PDF realizada ainda
                      </Text>
                    )}
                  </View>

                  {item.latestSubmission?.coverage != null ? (
                    <CoverageRing coverage={item.latestSubmission.coverage} />
                  ) : (
                    <View className="size-11 items-center justify-center rounded-2xl bg-brand/5">
                      <Icon
                        name="chevron.forward"
                        fallback="chevron-forward"
                        size={16}
                        color="#94A3B8"
                      />
                    </View>
                  )}
                </View>
              </Pressable>
            ))
          )}
        </View>
      </ScrollView>
    </View>
  );
}
