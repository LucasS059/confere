import { StatusBar } from "expo-status-bar";
import { Text, View } from "react-native";
import Animated, { FadeOut } from "react-native-reanimated";
import { CheckMark } from "@/components/check-mark";

export function Splash({ fontsLoaded }: { fontsLoaded: boolean }) {
  return (
    <Animated.View
      exiting={FadeOut.duration(300)}
      className="absolute inset-0 items-center justify-center gap-[18px] bg-splash-gradient"
    >
      <StatusBar style="light" />
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
    </Animated.View>
  );
}
