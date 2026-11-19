import * as SecureStore from "expo-secure-store";

export const ONBOARDING_COMPLETED_KEY = "confere.onboarding-completed";

export async function isOnboardingCompleted() {
  try {
    return (
      (await SecureStore.getItemAsync(ONBOARDING_COMPLETED_KEY)) === "true"
    );
  } catch (error) {
    console.warn("Unable to read onboarding state.", error);
    return false;
  }
}

export function completeOnboarding() {
  return SecureStore.setItemAsync(ONBOARDING_COMPLETED_KEY, "true");
}
