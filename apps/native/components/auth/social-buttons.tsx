import { Pressable, Text, View } from "react-native";

const GOOGLE_COLORS = ["#EA4335", "#4285F4", "#FBBC05", "#34A853"];

const BUTTON_CLASS =
  "flex-row items-center justify-center gap-2.5 rounded-[26px] border-[0.5px] border-glass-bd bg-glass shadow-glass backdrop-blur-[18px] backdrop-saturate-[180%] active:opacity-80";

interface SocialButtonsProps {
  onPress: () => void;
  compact?: boolean;
}

export function SocialButtons({ onPress, compact }: SocialButtonsProps) {
  const prefix = compact ? "" : "Continuar com ";
  const size = compact ? "h-[50px] flex-1" : "h-[52px]";

  return (
    <View className={compact ? "flex-row gap-2.5" : "gap-2.5"}>
      <Pressable
        className={`${BUTTON_CLASS} ${size}`}
        accessibilityRole="button"
        onPress={onPress}
      >
        <View className="size-[18px] rounded-full bg-ink" />
        <Text className="font-instrument-semibold text-ink text-sm">
          {prefix}Apple
        </Text>
      </Pressable>
      <Pressable
        className={`${BUTTON_CLASS} ${size}`}
        accessibilityRole="button"
        onPress={onPress}
      >
        <View className="size-[18px] flex-row flex-wrap overflow-hidden rounded-full">
          {GOOGLE_COLORS.map((color) => (
            <View
              key={color}
              className="size-[9px]"
              style={{ backgroundColor: color }}
            />
          ))}
        </View>
        <Text className="font-instrument-semibold text-ink text-sm">
          {prefix}Google
        </Text>
      </Pressable>
    </View>
  );
}
