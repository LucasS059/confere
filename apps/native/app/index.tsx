import { Redirect } from "expo-router";
import { useEffect, useState } from "react";
import { ActivityIndicator, View } from "react-native";
import { authClient } from "@/lib/auth/client";
import { isOnboardingCompleted } from "@/lib/onboarding";

export default function Index() {
  const { data: session, isPending } = authClient.useSession();
  const [onboardingCompleted, setOnboardingCompleted] = useState<
    boolean | null
  >(null);

  useEffect(() => {
    isOnboardingCompleted().then(setOnboardingCompleted);
  }, []);

  if (isPending || onboardingCompleted === null) {
    return (
      <View className="flex-1 items-center justify-center bg-canvas">
        <ActivityIndicator />
      </View>
    );
  }

  return (
    <Redirect
      href={
        session ? "/(tabs)" : onboardingCompleted ? "/login" : "/onboarding"
      }
    />
  );
}
