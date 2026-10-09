import { StatusBar } from "expo-status-bar";
import { useEffect, useState } from "react";
import { Animated, StyleSheet, Text, View } from "react-native";
import { CheckMark } from "@/components/check-mark";

type SplashProps = {
  fontsLoaded: boolean;
  /** Flip to true once the app is ready; the splash fades out and unmounts. */
  hidden: boolean;
};

// Fades with React Native's own Animated: Reanimated's `exiting` layout
// animation crashes natively on the Reanimated build bundled in Expo Go.
export function Splash({ fontsLoaded, hidden }: SplashProps) {
  const [opacity] = useState(() => new Animated.Value(1));
  const [isGone, setIsGone] = useState(false);

  useEffect(() => {
    if (!hidden) return;
    Animated.timing(opacity, {
      toValue: 0,
      duration: 300,
      useNativeDriver: true,
    }).start(() => setIsGone(true));
  }, [hidden, opacity]);

  if (isGone) return null;

  return (
    <Animated.View
      pointerEvents={hidden ? "none" : "auto"}
      style={[StyleSheet.absoluteFill, { opacity }]}
    >
      <StatusBar style="light" />
      <View className="flex-1 items-center justify-center gap-[18px] bg-splash-gradient">
        <View className="size-24 items-center justify-center rounded-[28px] border-[0.5px] border-white/40 bg-white/18 shadow-splash-tile backdrop-blur-[18px] backdrop-saturate-[180%]">
          <CheckMark size={52} />
        </View>
        {/* Text waits for the font so it never flashes in the system face. */}
        <View
          className="items-center gap-[18px]"
          style={{ opacity: fontsLoaded ? 1 : 0 }}
        >
          <Text className="font-instrument-semibold text-[34px] text-white tracking-[-1.02px]">
            Confere
          </Text>
          <Text className="font-instrument text-sm text-white/80">
            Entregue com evidência.
          </Text>
        </View>
      </View>
    </Animated.View>
  );
}
