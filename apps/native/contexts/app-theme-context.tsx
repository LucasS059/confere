import * as SecureStore from "expo-secure-store";
import type React from "react";
import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useState,
} from "react";
import { Uniwind, useUniwind } from "uniwind";

export type ThemeMode = "system" | "light" | "dark";

type AppThemeContextType = {
  mode: ThemeMode;
  currentTheme: string;
  isLight: boolean;
  isDark: boolean;
  setMode: (mode: ThemeMode) => void;
};

const STORAGE_KEY = "confere.theme-mode";

const AppThemeContext = createContext<AppThemeContextType | undefined>(
  undefined,
);

export const AppThemeProvider = ({
  children,
}: {
  children: React.ReactNode;
}) => {
  const { theme } = useUniwind();
  const [mode, setModeState] = useState<ThemeMode>("system");

  // Restaura a escolha salva
  useEffect(() => {
    SecureStore.getItemAsync(STORAGE_KEY)
      .then((saved) => {
        if (saved === "light" || saved === "dark" || saved === "system") {
          setModeState(saved);
          Uniwind.setTheme(saved);
        }
      })
      .catch(() => undefined);
  }, []);

  const setMode = useCallback((next: ThemeMode) => {
    setModeState(next);
    Uniwind.setTheme(next);
    SecureStore.setItemAsync(STORAGE_KEY, next).catch(() => undefined);
  }, []);

  const value = useMemo(
    () => ({
      mode,
      currentTheme: theme,
      isLight: theme === "light",
      isDark: theme === "dark",
      setMode,
    }),
    [mode, theme, setMode],
  );

  return (
    <AppThemeContext.Provider value={value}>
      {children}
    </AppThemeContext.Provider>
  );
};

export function useAppTheme() {
  const context = useContext(AppThemeContext);
  if (!context) {
    throw new Error("useAppTheme must be used within AppThemeProvider");
  }
  return context;
}
