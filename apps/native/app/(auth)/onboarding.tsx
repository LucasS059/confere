import { useRouter } from "expo-router";
import { useState } from "react";
import { Alert, Pressable, Text, View } from "react-native";
import { useSafeAreaInsets } from "react-native-safe-area-context";
import { Blob } from "@/components/ui/blob";
import { CheckMark } from "@/components/ui/check-mark";
import { completeOnboarding } from "@/lib/onboarding";

const SAMPLE_REQUIREMENTS = [
  {
    text: "Artigo entre 15 e 25 páginas",
    code: "3.1",
    checked: true,
    strikethrough: false,
  },
  {
    text: "Resumo em PT e EN, até 250\npalavras",
    code: "3.2",
    checked: true,
    strikethrough: false,
  },
  {
    text: "Referências em ABNT, mínimo 20",
    code: "4.1",
    checked: true,
    strikethrough: false,
  },
  {
    text: "Inscrição até 30/10",
    code: "prazo",
    checked: false,
    strikethrough: true,
  },
];

export default function OnboardingScreen() {
  const router = useRouter();
  const insets = useSafeAreaInsets();

  const [isContinuing, setIsContinuing] = useState(false);

  async function continueToLogin() {
    if (isContinuing) return;

    setIsContinuing(true);
    try {
      await completeOnboarding();
      router.replace("/login");
    } catch (error) {
      console.warn("Unable to save onboarding state.", error);
      setIsContinuing(false);
      Alert.alert(
        "Não foi possível continuar",
        "Tente novamente para salvar esta etapa.",
      );
    }
  }

  return (
    <View
      className="flex-1 justify-between overflow-hidden bg-canvas px-6"
      style={{
        paddingTop: Math.max(insets.top + 12, 56),
        paddingBottom: Math.max(insets.bottom + 20, 36),
      }}
    >
      <Blob
        color="#2F6BFF"
        className="-top-[100px] -left-[80px] size-[380px] opacity-[0.22] dark:opacity-[0.36]"
      />
      <Blob
        color="#1E9E62"
        className="top-[240px] -right-[120px] size-[320px] opacity-[0.16] dark:opacity-[0.28]"
      />

      <View className="flex-1 items-center justify-center gap-3.5 px-2">
        <View className="flex-row items-center gap-2">
          <View className="flex-row items-center gap-1.5 rounded-full border border-hair bg-card px-3.5 py-2 shadow-xs">
            <Text className="font-mono-medium text-[11px] text-brand">TXT</Text>
            <Text className="font-instrument-medium text-ink text-xs">
              Texto
            </Text>
          </View>
          <View className="flex-row items-center gap-1.5 rounded-full border border-hair bg-card px-3.5 py-2 shadow-xs">
            <Text className="font-mono-medium text-[11px] text-err">PDF</Text>
            <Text className="font-instrument-medium text-ink text-xs">
              Edital
            </Text>
          </View>
          <View className="flex-row items-center gap-1.5 rounded-full border border-hair bg-card px-3.5 py-2 shadow-xs">
            <View className="size-2 rounded-full bg-err" />
            <Text className="font-instrument-medium text-ink text-xs">
              Áudio
            </Text>
          </View>
        </View>

        <Text className="font-instrument text-brand text-lg">↓</Text>

        <View className="w-full rounded-[22px] border border-hair bg-card px-4 py-2 shadow-xs">
          {SAMPLE_REQUIREMENTS.map((req, index) => (
            <View
              key={req.code}
              className={`flex-row items-center justify-between gap-3 py-3 ${
                index < SAMPLE_REQUIREMENTS.length - 1
                  ? "border-hair border-b"
                  : ""
              }`}
            >
              <View className="flex-1 flex-row items-center gap-2.5">
                <View
                  className={`size-5 items-center justify-center ${
                    req.checked
                      ? "rounded-[6px] bg-brand"
                      : "rounded-full border border-hair bg-canvas"
                  }`}
                >
                  {req.checked ? <CheckMark size={12} /> : null}
                </View>
                <Text
                  className={`flex-1 font-instrument-medium text-[13px] leading-[17.5px] ${
                    req.strikethrough
                      ? "font-instrument text-ink3 line-through"
                      : "text-ink"
                  }`}
                >
                  {req.text}
                </Text>
              </View>
              <Text className="font-mono text-[11px] text-ink3">
                {req.code}
              </Text>
            </View>
          ))}
        </View>
      </View>

      <View className="gap-6">
        <View className="gap-2">
          <Text className="font-instrument-semibold text-[26px] text-ink leading-[30px] tracking-[-0.65px]">
            Seus requisitos, organizados.
          </Text>
          <Text className="font-instrument text-[14.5px] text-ink2 leading-[21.5px]">
            Cole o edital, envie o PDF, fotografe ou dite. O Confere separa cada
            requisito e você confirma a lista.
          </Text>
        </View>

        <View className="items-end">
          <Pressable
            accessibilityRole="button"
            disabled={isContinuing}
            onPress={continueToLogin}
            className="h-[50px] flex-row items-center justify-center rounded-full bg-brand px-6 shadow-brand-button active:opacity-85 disabled:opacity-60"
          >
            <Text className="font-instrument-semibold text-[15px] text-white">
              Continuar →
            </Text>
          </Pressable>
        </View>
      </View>
    </View>
  );
}
