import { useRouter } from "expo-router";
import { useToast } from "heroui-native";
import { useState } from "react";
import { Pressable, Text, TextInput, View } from "react-native";
import { KeyboardAwareScrollView } from "react-native-keyboard-controller";
import { useSafeAreaInsets } from "react-native-safe-area-context";
import { useCSSVariable } from "uniwind";
import { Blob } from "@/components/blob";
import { ScreenHeader } from "@/components/screen-header";

const SOURCES = ["Texto", "PDF/DOCX", "Foto", "Áudio"] as const;

export default function NewProjectScreen() {
  const router = useRouter();
  const insets = useSafeAreaInsets();
  const { toast } = useToast();
  const placeholderColor = useCSSVariable("--ink3") as string | undefined;

  const [name, setName] = useState("");
  const [source, setSource] = useState<(typeof SOURCES)[number]>("Texto");
  const [rawText, setRawText] = useState("");
  const [isExtracting, setIsExtracting] = useState(false);

  function handleExtract() {
    if (!name.trim()) {
      toast.show({
        variant: "danger",
        label: "Dê um nome para o seu projeto",
      });
      return;
    }
    if (!rawText.trim()) {
      toast.show({
        variant: "danger",
        label: "Cole o texto dos requisitos ou do edital",
      });
      return;
    }
    setIsExtracting(true);
    toast.show({
      label: "Extraindo requisitos...",
    });
    setTimeout(() => {
      setIsExtracting(false);
      router.push("/projects/review-requirements");
    }, 600);
  }

  return (
    <View className="flex-1 overflow-hidden bg-canvas">
      <Blob
        color="#2F6BFF"
        className="-top-[120px] -left-[80px] size-[360px] opacity-[0.18] dark:opacity-[0.30]"
      />
      <Blob
        color="#1E9E62"
        className="top-[340px] -right-[140px] size-[320px] opacity-[0.14] dark:opacity-[0.24]"
      />

      <KeyboardAwareScrollView
        bottomOffset={24}
        keyboardShouldPersistTaps="handled"
        contentContainerStyle={{
          flexGrow: 1,
          gap: 18,
          paddingTop: Math.max(insets.top + 12, 56),
          paddingHorizontal: 20,
          paddingBottom: Math.max(insets.bottom + 24, 40),
        }}
      >
        <ScreenHeader title="Novo projeto" />

        <View className="gap-1.5">
          <Text className="px-1 font-instrument text-ink2 text-xs">
            Nome do projeto
          </Text>
          <View className="h-[52px] justify-center rounded-2xl border border-hair bg-card px-4 shadow-xs">
            <TextInput
              value={name}
              onChangeText={setName}
              placeholder="Ex: TCC Pedagogia, Artigo PIBIC..."
              placeholderTextColor={placeholderColor}
              className="font-instrument-medium text-[15px] text-ink web:outline-none"
            />
          </View>
        </View>

        <View className="gap-1.5">
          <Text className="px-1 font-instrument text-ink2 text-xs">
            Requisitos — de onde vêm?
          </Text>
          <View className="flex-row rounded-full border-[0.5px] border-glass-bd bg-glass p-1 shadow-glass backdrop-blur-[18px] backdrop-saturate-[180%]">
            {SOURCES.map((item) => {
              const active = source === item;
              return (
                <Pressable
                  key={item}
                  onPress={() => setSource(item)}
                  className={`flex-1 items-center justify-center rounded-full py-2 ${
                    active ? "bg-ink" : ""
                  }`}
                >
                  <Text
                    className={`font-instrument-semibold text-xs ${
                      active ? "text-canvas" : "text-ink2"
                    }`}
                  >
                    {item}
                  </Text>
                </Pressable>
              );
            })}
          </View>
        </View>

        <View className="flex-1 gap-3 rounded-[22px] border border-hair bg-card p-4 shadow-xs">
          <View className="flex-row items-start justify-between gap-3">
            <Text className="flex-1 font-instrument text-ink3 text-xs leading-[16px]">
              Cole o edital, a rubrica ou o e-mail do{"\n"}orientador
            </Text>
            <Text className="text-right font-mono text-[11px] text-ink3 leading-[14px]">
              {rawText.length.toLocaleString("pt-BR")}
              {"\n"}car.
            </Text>
          </View>

          <TextInput
            value={rawText}
            onChangeText={setRawText}
            placeholder="Cole aqui o texto contendo os requisitos, prazos e orientações da entrega..."
            placeholderTextColor={placeholderColor}
            multiline
            textAlignVertical="top"
            className="min-h-[220px] flex-1 font-instrument text-[13.5px] text-ink leading-[21px] web:outline-none"
          />
        </View>

        <Pressable
          onPress={handleExtract}
          disabled={isExtracting}
          className="h-[54px] items-center justify-center rounded-[27px] bg-brand shadow-brand-button active:opacity-85"
        >
          <Text className="font-instrument-semibold text-[15px] text-white">
            {isExtracting ? "Extraindo..." : "Extrair requisitos com IA"}
          </Text>
        </Pressable>
      </KeyboardAwareScrollView>
    </View>
  );
}
