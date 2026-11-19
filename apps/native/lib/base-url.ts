import { env } from "@confere/env/native";
import Constants from "expo-constants";

export function getBaseUrl(): string {
  const debuggerHost = Constants.expoConfig?.hostUri;
  const localhost = debuggerHost?.split(":")[0];

  if (localhost) {
    return `http://${localhost}:3000`;
  }

  return env.EXPO_PUBLIC_SERVER_URL;
}
