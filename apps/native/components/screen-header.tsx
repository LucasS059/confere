import { useRouter } from "expo-router";
import type { ReactNode } from "react";
import { Pressable, Text, View } from "react-native";
import { useCSSVariable } from "uniwind";
import { Icon } from "@/components/icon";

type ScreenHeaderProps = {
  title: string;
  subtitle?: string;
  onBack?: () => void;
  rightSlot?: ReactNode;
  rightElement?: ReactNode;
};

export function ScreenHeader({
  title,
  subtitle,
  onBack,
  rightSlot,
  rightElement,
}: ScreenHeaderProps) {
  const router = useRouter();
  const inkColor = (useCSSVariable("--ink") as string) || "#141821";

  const handleBack = () => {
    if (onBack) {
      onBack();
      return;
    }
    if (router.canGoBack()) {
      router.back();
    } else {
      router.replace("/(tabs)" as any);
    }
  };

  return (
    <View className="flex-row items-center justify-between gap-3">
      <Pressable
        accessibilityRole="button"
        accessibilityLabel="Voltar"
        onPress={handleBack}
        className="size-10 items-center justify-center rounded-full border-[0.5px] border-glass-bd bg-glass shadow-glass backdrop-blur-[18px] backdrop-saturate-[180%] active:opacity-75"
      >
        <Icon name="chevron.backward" fallback="chevron-back" size={18} color={inkColor} />
      </Pressable>

      <View className="min-w-[148px] items-center justify-center rounded-full border-[0.5px] border-glass-bd bg-glass px-6 py-2.5 shadow-glass backdrop-blur-[18px] backdrop-saturate-[180%]">
        <Text className="font-instrument-semibold text-[13px] text-ink">
          {title}
        </Text>
        {subtitle ? (
          <Text className="font-instrument text-[11px] text-ink2">
            {subtitle}
          </Text>
        ) : null}
      </View>

      {rightSlot || rightElement ? rightSlot || rightElement : <View className="size-10" />}
    </View>
  );
}
