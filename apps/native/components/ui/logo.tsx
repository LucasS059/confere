import { Image, type ImageStyle, type StyleProp } from "react-native";
import { useAppTheme } from "@/contexts/app-theme-context";

type LogoProps = {
  size: number;
  appearance?: "auto" | "light" | "dark";
  style?: StyleProp<ImageStyle>;
};

export function Logo({ size, appearance = "auto", style }: LogoProps) {
  const { isDark } = useAppTheme();
  const useLightLogo = appearance === "light" || (appearance === "auto" && isDark);

  return (
    <Image
      accessibilityLabel="Confere"
      source={
        useLightLogo
          ? require("../../assets/images/logo/logo_claro.png")
          : require("../../assets/images/logo/logo_escuro.png")
      }
      style={[{ width: size, height: size }, style]}
    />
  );
}
