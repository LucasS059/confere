import { Ionicons } from "@expo/vector-icons";
import { Tabs } from "expo-router";
import type React from "react";
import { Pressable, Text, View } from "react-native";
import { useSafeAreaInsets } from "react-native-safe-area-context";
import { useCSSVariable } from "uniwind";

type BottomTabBarProps = Parameters<
  NonNullable<React.ComponentProps<typeof Tabs>["tabBar"]>
>[0];

const TAB_ITEMS: Array<{
  name: string;
  label: string;
  icon: keyof typeof Ionicons.glyphMap;
}> = [
  { name: "index", label: "Início", icon: "home-outline" },
  { name: "conferir", label: "Conferir", icon: "checkmark-circle-outline" },
  { name: "historico", label: "Histórico", icon: "time-outline" },
  { name: "perfil", label: "Perfil", icon: "person-outline" },
];

function LiquidGlassTabBar({
  state,
  descriptors,
  navigation,
}: BottomTabBarProps) {
  const insets = useSafeAreaInsets();
  const brandColor = (useCSSVariable("--color-brand") as string) || "#2F6BFF";
  const inactiveColor = (useCSSVariable("--ink2") as string) || "#5B6270";

  return (
    <View
      pointerEvents="box-none"
      style={{ paddingBottom: Math.max(insets.bottom, 16) }}
      className="absolute right-0 bottom-0 left-0 px-5"
    >
      <View className="h-[62px] flex-row items-center justify-around rounded-[31px] border-[0.5px] border-glass-bd bg-glass px-2 shadow-glass backdrop-blur-[18px] backdrop-saturate-[180%]">
        {TAB_ITEMS.map((item) => {
          const routeIndex = state.routes.findIndex(
            (r: { name: string }) => r.name === item.name,
          );
          if (routeIndex === -1) return null;

          const route = state.routes[routeIndex];
          const { options } = descriptors[route.key];
          const isFocused = state.index === routeIndex;
          const tintColor = isFocused ? brandColor : inactiveColor;

          const onPress = () => {
            const event = navigation.emit({
              type: "tabPress",
              target: route.key,
              canPreventDefault: true,
            });
            if (!isFocused && !event.defaultPrevented) {
              navigation.navigate(route.name, route.params);
            }
          };

          return (
            <Pressable
              key={item.name}
              accessibilityRole="button"
              accessibilityState={isFocused ? { selected: true } : {}}
              accessibilityLabel={options.tabBarAccessibilityLabel ?? item.label}
              onPress={onPress}
              className="flex-1 items-center justify-center gap-1 py-1.5 active:opacity-75"
            >
              <Ionicons name={item.icon} size={19} color={tintColor} />
              <Text
                className={
                  isFocused
                    ? "font-instrument-semibold text-[11px] text-brand"
                    : "font-instrument text-[11px] text-ink2"
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
      tabBar={(props) => <LiquidGlassTabBar {...props} />}
      screenOptions={{
        headerShown: false,
      }}
    >
      <Tabs.Screen name="index" options={{ title: "Início" }} />
      <Tabs.Screen name="conferir" options={{ title: "Conferir" }} />
      <Tabs.Screen name="historico" options={{ title: "Histórico" }} />
      <Tabs.Screen name="perfil" options={{ title: "Perfil" }} />
    </Tabs>
  );
}
