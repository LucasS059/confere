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
import { Stack, useRouter, useSegments } from "expo-router";
import { HeroUINativeProvider } from "heroui-native";
import { useEffect, useState } from "react";
import { GestureHandlerRootView } from "react-native-gesture-handler";
import { KeyboardProvider } from "react-native-keyboard-controller";
import { Splash } from "@/components/ui/splash";
import { AppThemeProvider } from "@/contexts/app-theme-context";
import { authClient } from "@/lib/auth/client";
import { queryClient } from "@/lib/trpc";

const SPLASH_MIN_MS = 1000;

// Screens reachable without a session; everything else bounces to login.
// Terms/privacy are public so sign-up can link to them.
const PUBLIC_ROUTES = new Set(["(account)/terms", "(account)/privacy"]);

function isPublicRoute(segments: string[]) {
  const [first] = segments;
  return (
    first === undefined || // root index (redirector)
    first === "(auth)" ||
    first === "+not-found" ||
    PUBLIC_ROUTES.has(segments.join("/"))
  );
}

// Replaces Stack.Protected (crashed on sign-out in Expo Go): only redirects
// away from protected screens, never toward them, so login/sign-up keep
// navigating themselves and a session refetch can't reset the login form.
function useAuthGuard() {
  const router = useRouter();
  // Typed as non-empty, but the root index route yields [].
  const isPublic = isPublicRoute(useSegments() as string[]);
  const { data: session, isPending } = authClient.useSession();

  useEffect(() => {
    if (!isPending && !session && !isPublic) {
      router.replace("/login");
    }
  }, [isPending, session, isPublic, router]);
}

function StackLayout() {
  useAuthGuard();

  return (
    <Stack screenOptions={{ headerShown: false }}>
      <Stack.Screen name="index" />
      <Stack.Screen name="(tabs)" />
      <Stack.Screen name="(auth)/onboarding" />
      <Stack.Screen name="(auth)/login" />
      <Stack.Screen name="(auth)/sign-up" />
      <Stack.Screen name="(auth)/forgot-password" />
      <Stack.Screen name="(auth)/reset-password" />
      <Stack.Screen name="projects/new" />
      <Stack.Screen name="projects/review" />
      <Stack.Screen name="projects/details" />
      <Stack.Screen name="projects/submission" />
      <Stack.Screen name="projects/check-review" />
      <Stack.Screen name="projects/checking" />
      <Stack.Screen name="projects/result" />
      <Stack.Screen name="projects/requirement-detail" />
      <Stack.Screen name="(account)/settings" />
      <Stack.Screen name="(account)/terms" />
      <Stack.Screen name="(account)/privacy" />
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

  const { isPending: isSessionPending } = authClient.useSession();

  const isReady =
    (fontsLoaded || !!fontsError) && minTimeElapsed && !isSessionPending;

  return (
    <QueryClientProvider client={queryClient}>
      <GestureHandlerRootView style={{ flex: 1 }}>
        <KeyboardProvider>
          <AppThemeProvider>
            <HeroUINativeProvider>
              <StackLayout />
              <Splash fontsLoaded={fontsLoaded} hidden={isReady} />
            </HeroUINativeProvider>
          </AppThemeProvider>
        </KeyboardProvider>
      </GestureHandlerRootView>
    </QueryClientProvider>
  );
}
