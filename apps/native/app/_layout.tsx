import "@/global.css";

import {
  InstrumentSans_400Regular,
  InstrumentSans_500Medium,
  InstrumentSans_600SemiBold,
  useFonts,
} from "@expo-google-fonts/instrument-sans";
import { QueryClientProvider } from "@tanstack/react-query";

import { Stack } from "expo-router";
import { HeroUINativeProvider } from "heroui-native";
import { useEffect, useState } from "react";
import { GestureHandlerRootView } from "react-native-gesture-handler";
import { KeyboardProvider } from "react-native-keyboard-controller";
import { Splash } from "@/components/splash";
import { AppThemeProvider } from "@/contexts/app-theme-context";
import { authClient } from "@/lib/auth-client";

import { queryClient } from "@/utils/trpc";

// Keeps the branded splash readable instead of flashing by on fast starts.
const SPLASH_MIN_MS = 1200;

export const unstable_settings = {
  initialRouteName: "(drawer)",
};

function StackLayout({ isSignedIn }: { isSignedIn: boolean }) {
  return (
    <Stack screenOptions={{}}>
      <Stack.Protected guard={isSignedIn}>
        <Stack.Screen name="(drawer)" options={{ headerShown: false }} />
        <Stack.Screen
          name="modal"
          options={{ title: "Modal", presentation: "modal" }}
        />
      </Stack.Protected>
      <Stack.Protected guard={!isSignedIn}>
        <Stack.Screen name="login" options={{ headerShown: false }} />
        <Stack.Screen name="sign-up" options={{ title: "Criar conta" }} />
      </Stack.Protected>
    </Stack>
  );
}

export default function Layout() {
  const [fontsLoaded, fontsError] = useFonts({
    InstrumentSans_400Regular,
    InstrumentSans_500Medium,
    InstrumentSans_600SemiBold,
  });
  const { data: session, isPending } = authClient.useSession();
  const [minTimeElapsed, setMinTimeElapsed] = useState(false);

  useEffect(() => {
    const timer = setTimeout(() => setMinTimeElapsed(true), SPLASH_MIN_MS);
    return () => clearTimeout(timer);
  }, []);

  // A font failure must not trap the user on the splash.
  const isReady = (fontsLoaded || !!fontsError) && !isPending && minTimeElapsed;

  return (
    <QueryClientProvider client={queryClient}>
      <GestureHandlerRootView style={{ flex: 1 }}>
        <KeyboardProvider>
          <AppThemeProvider>
            <HeroUINativeProvider>
              <StackLayout isSignedIn={!!session} />
              {!isReady && <Splash fontsLoaded={fontsLoaded} />}
            </HeroUINativeProvider>
          </AppThemeProvider>
        </KeyboardProvider>
      </GestureHandlerRootView>
    </QueryClientProvider>
  );
}
