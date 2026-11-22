import { useRouter } from "expo-router";
import type { ReactNode } from "react";
import { Pressable, Text, View } from "react-native";
import { useSafeAreaInsets } from "react-native-safe-area-context";
import { useCSSVariable } from "uniwind";
import { Icon } from "@/components/ui/icon";

type ScreenHeaderProps = {
  title: string;
  subtitle?: string;
  onBack?: () => void;
  rightSlot?: ReactNode;
  safeTop?: boolean;
};

export function ScreenHeader({
  title,
  subtitle,
  onBack,
  rightSlot,
  safeTop = true,
}: ScreenHeaderProps) {
  const router = useRouter();
  const insets = useSafeAreaInsets();
  const inkColor = (useCSSVariable("--ink") as string) || "#141821";

  const handleBack = () => {
    if (onBack) {
      onBack();
      return;
    }
    if (router.canGoBack()) {
      router.back();
    } else {
      router.replace("/(tabs)");
    }
  };

  return (
    <View
      className={`flex-row items-center justify-between gap-3 ${safeTop ? "px-5 pb-2" : ""}`}
      style={safeTop ? { paddingTop: Math.max(insets.top + 8, 44) } : undefined}
    >
      <Pressable
        accessibilityRole="button"
        accessibilityLabel="Voltar"
        onPress={handleBack}
        hitSlop={8}
        className="size-10 items-center justify-center rounded-full border border-line-glass bg-glass shadow-sm active:opacity-75"
      >
        <Icon
          name="chevron.backward"
          fallback="chevron-back"
          size={18}
          color={inkColor}
        />
      </Pressable>

      <View className="min-w-[160px] max-w-[240px] items-center justify-center rounded-full border border-line-glass bg-glass px-5 py-2 shadow-sm">
        <Text numberOfLines={1} className="font-semibold text-[14px] text-ink">
          {title}
        </Text>
        {subtitle ? (
          <Text numberOfLines={1} className="text-[11px] text-ink3">
            {subtitle}
          </Text>
        ) : null}
      </View>

      {rightSlot ?? <View className="size-10" />}
    </View>
  );
}
