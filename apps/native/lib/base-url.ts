import { env } from "@confere/env/native";
import Constants from "expo-constants";

const LOCALHOST = /\/\/(localhost|127\.0\.0\.1)(?=[:/]|$)/;

// On a physical device "localhost" is the phone itself. In dev, swap it for
// the Metro host IP so the .env doesn't need editing on every Wi-Fi change.
// Any other URL (tunnel, remote server) is used as-is.
export function getBaseUrl(): string {
  const devHost = Constants.expoConfig?.hostUri?.split(":")[0];

  if (__DEV__ && devHost) {
    return env.EXPO_PUBLIC_SERVER_URL.replace(LOCALHOST, `//${devHost}`);
  }

  return env.EXPO_PUBLIC_SERVER_URL;
}
