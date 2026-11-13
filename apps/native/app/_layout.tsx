import "@/global.css";

import {
  DMMono_400Regular,
  DMMono_500Medium,
} from "@expo-google-fonts/dm-mono";
import {
  Inter_400Regular,
  Inter_500Medium,
  Inter_600SemiBold,
  Inter_700Bold,
  useFonts,
} from "@expo-google-fonts/inter";
import { QueryClientProvider } from "@tanstack/react-query";
import { Stack } from "expo-router";
import { HeroUINativeProvider } from "heroui-native";
import { useEffect, useState } from "react";
import { GestureHandlerRootView } from "react-native-gesture-handler";
import { KeyboardProvider } from "react-native-keyboard-controller";
import { Splash } from "@/components/ui/splash";
import { AppThemeProvider } from "@/contexts/app-theme-context";
import { authClient } from "@/lib/auth/client";
import { queryClient } from "@/lib/trpc";

const SPLASH_MIN_MS = 1000;

function StackLayout({ isAuthenticated }: { isAuthenticated: boolean }) {
  return (
    <Stack screenOptions={{ headerShown: false }}>
      <Stack.Protected guard={isAuthenticated}>
        <Stack.Screen name="(tabs)" />
        <Stack.Screen name="projects/new" />
        <Stack.Screen name="projects/review" />
        <Stack.Screen name="projects/details" />
        <Stack.Screen name="projects/submission" />
        <Stack.Screen name="projects/check-review" />
        <Stack.Screen name="projects/checking" />
        <Stack.Screen name="projects/result" />
        <Stack.Screen name="projects/requirement-detail" />
        <Stack.Screen name="(account)/settings" />
      </Stack.Protected>
      <Stack.Protected guard={!isAuthenticated}>
        <Stack.Screen name="(auth)/onboarding" />
        <Stack.Screen name="(auth)/login" />
        <Stack.Screen name="(auth)/sign-up" />
        <Stack.Screen name="(auth)/forgot-password" />
      </Stack.Protected>
      <Stack.Screen name="(auth)/reset-password" />
    </Stack>
  );
}

export default function Layout() {
  const [fontsLoaded, fontsError] = useFonts({
    Inter_400Regular,
    Inter_500Medium,
    Inter_600SemiBold,
    Inter_700Bold,
    DMMono_400Regular,
    DMMono_500Medium,
  });
  const [minTimeElapsed, setMinTimeElapsed] = useState(false);

  useEffect(() => {
    const timer = setTimeout(() => setMinTimeElapsed(true), SPLASH_MIN_MS);
    return () => clearTimeout(timer);
  }, []);

  const { data: session, isPending: isSessionPending } =
    authClient.useSession();

  const isReady =
    (fontsLoaded || !!fontsError) && minTimeElapsed && !isSessionPending;

  return (
    <QueryClientProvider client={queryClient}>
      <GestureHandlerRootView style={{ flex: 1 }}>
        <KeyboardProvider>
          <AppThemeProvider>
            <HeroUINativeProvider>
              <StackLayout isAuthenticated={Boolean(session)} />
              <Splash fontsLoaded={fontsLoaded} hidden={isReady} />
            </HeroUINativeProvider>
          </AppThemeProvider>
        </KeyboardProvider>
      </GestureHandlerRootView>
    </QueryClientProvider>
  );
}
