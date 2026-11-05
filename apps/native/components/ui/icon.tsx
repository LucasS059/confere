import { SymbolView, type SFSymbol } from "expo-symbols";
import { Ionicons } from "@expo/vector-icons";
import { Platform } from "react-native";

interface IconProps {
  name: SFSymbol;
  fallback?: keyof typeof Ionicons.glyphMap;
  size?: number;
  color?: string;
}

export function Icon({
  name,
  fallback,
  size = 20,
  color = "#141821",
}: IconProps) {
  if (Platform.OS === "ios") {
    return (
      <SymbolView
        name={name}
        size={size}
        tintColor={color}
        resizeMode="scaleAspectFit"
      />
    );
  }

  if (fallback) {
    return <Ionicons name={fallback} size={size} color={color} />;
  }

  return (
    <SymbolView
      name={name}
      size={size}
      tintColor={color}
      resizeMode="scaleAspectFit"
    />
  );
}
