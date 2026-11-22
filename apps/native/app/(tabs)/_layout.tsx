import type { Ionicons } from "@expo/vector-icons";
import { Tabs, useRouter } from "expo-router";
import type { SFSymbol } from "expo-symbols";
import type React from "react";
import { Pressable, Text, View } from "react-native";
import { useSafeAreaInsets } from "react-native-safe-area-context";
import { useCSSVariable } from "uniwind";
import { Icon } from "@/components/ui/icon";

type BottomTabBarProps = Parameters<
  NonNullable<React.ComponentProps<typeof Tabs>["tabBar"]>
>[0];

const TAB_ITEMS: Array<{
  name: string;
  href: "/(tabs)" | "/projects" | "/check" | "/profile";
  label: string;
  icon: SFSymbol;
  activeIcon: SFSymbol;
  fallback: keyof typeof Ionicons.glyphMap;
}> = [
  {
    name: "index",
    href: "/(tabs)",
    label: "Início",
    icon: "house",
    activeIcon: "house.fill",
    fallback: "home-outline",
  },
  {
    name: "projects",
    href: "/projects",
    label: "Projetos",
    icon: "folder",
    activeIcon: "folder.fill",
    fallback: "folder-outline",
  },
  {
    name: "check",
    href: "/check",
    label: "Novo projeto",
    icon: "plus.circle",
    activeIcon: "plus.circle.fill",
    fallback: "add-circle-outline",
  },
  {
    name: "profile",
    href: "/profile",
    label: "Perfil",
    icon: "person",
    activeIcon: "person.fill",
    fallback: "person-outline",
  },
];

function BottomPillTabBar({ state, descriptors }: BottomTabBarProps) {
  const router = useRouter();
  const insets = useSafeAreaInsets();
  const brandColor = (useCSSVariable("--color-brand") as string) || "#2F6BFF";
  const inactiveColor = (useCSSVariable("--ink2") as string) || "#5B6270";

  return (
    <View
      pointerEvents="box-none"
      style={{ paddingBottom: Math.max(insets.bottom, 16) }}
      className="absolute right-0 bottom-0 left-0 px-5"
    >
      <View className="h-[62px] flex-row items-center justify-around rounded-full border border-line-glass bg-card px-2 shadow-black/10 shadow-md">
        {TAB_ITEMS.map((item) => {
          const routeIndex = state.routes.findIndex(
            (r) => r.name === item.name,
          );
          if (routeIndex === -1) return null;

          const route = state.routes[routeIndex];
          const { options } = descriptors[route.key];
          const isFocused = state.index === routeIndex;
          const tintColor = isFocused ? brandColor : inactiveColor;

          const onPress = () => {
            if (!isFocused) {
              router.navigate(item.href);
            }
          };

          return (
            <Pressable
              key={item.name}
              accessibilityRole="button"
              accessibilityState={isFocused ? { selected: true } : {}}
              accessibilityLabel={
                options.tabBarAccessibilityLabel ?? item.label
              }
              onPress={onPress}
              className="flex-1 items-center justify-center gap-1 py-1.5 active:opacity-75"
            >
              <Icon
                name={isFocused ? item.activeIcon : item.icon}
                fallback={item.fallback}
                size={19}
                color={tintColor}
              />
              <Text
                numberOfLines={1}
                className={
                  isFocused
                    ? "font-semibold text-[11px] text-brand"
                    : "text-[11px] text-ink2"
                }
              >
                {item.label}
              </Text>
            </Pressable>
          );
        })}
      </View>
    </View>
  );
}

export default function TabsLayout() {
  return (
    <Tabs
      tabBar={(props) => <BottomPillTabBar {...props} />}
      screenOptions={{
        headerShown: false,
      }}
    >
      <Tabs.Screen name="index" options={{ title: "Início" }} />
      <Tabs.Screen name="projects" options={{ title: "Projetos" }} />
      <Tabs.Screen name="check" options={{ title: "Novo projeto" }} />
      <Tabs.Screen name="profile" options={{ title: "Perfil" }} />
    </Tabs>
  );
}
