import { useRouter } from "expo-router";
import { useState } from "react";
import { Pressable, ScrollView, Text, TextInput, View } from "react-native";
import { useSafeAreaInsets } from "react-native-safe-area-context";
import { Ionicons } from "@expo/vector-icons";
import { Blob } from "@/components/blob";
import { ScreenHeader } from "@/components/screen-header";

interface SelectedDocument {
  name: string;
  size: string;
  pages?: number;
}

export default function NewSubmissionScreen() {
  const router = useRouter();
  const insets = useSafeAreaInsets();

  const [document, setDocument] = useState<SelectedDocument | null>(null);
  const [version, setVersion] = useState("v1");
  const [label, setLabel] = useState("");

  function handlePickFile() {
    setDocument({
      name: "trabalho-academico.pdf",
      size: "2,4 MB",
      pages: 35,
    });
  }

  return (
    <View className="flex-1 overflow-hidden bg-canvas">
      <Blob
        color="#2F6BFF"
        className="-top-[120px] -left-[80px] size-[360px] opacity-[0.16] dark:opacity-[0.28]"
      />
      <Blob
        color="#10B981"
        className="top-[320px] -right-[140px] size-[300px] opacity-[0.12] dark:opacity-[0.20]"
      />

      <ScreenHeader
        title="Nova entrega"
        subtitle="Enviar trabalho para conferência"
      />

      <ScrollView
        showsVerticalScrollIndicator={false}
        contentContainerStyle={{
          paddingHorizontal: 20,
          paddingTop: 16,
          paddingBottom: insets.bottom + 100,
        }}
      >
        {document ? (
          <View className="mb-6 items-center rounded-3xl border border-line-glass bg-glass p-6 text-center shadow-sm">
            <View className="mb-3 size-14 items-center justify-center rounded-2xl bg-err/10">
              <Ionicons name="document-text" size={28} color="#EF4444" />
            </View>

            <Text className="text-[17px] font-bold text-ink">
              {document.name}
            </Text>
            <Text className="mt-1 font-mono text-[13px] text-ink2">
              {document.pages ? `${document.pages} páginas · ` : ""}
              {document.size} · pronto para análise
            </Text>

            <Pressable
              onPress={() => setDocument(null)}
              className="mt-3"
            >
              <Text className="text-[13px] font-semibold text-err">
                Remover arquivo
              </Text>
            </Pressable>
          </View>
        ) : (
          <Pressable
            onPress={handlePickFile}
            className="mb-6 items-center rounded-3xl border-2 border-dashed border-line-glass bg-glass/60 p-8 text-center active:bg-glass"
          >
            <View className="mb-3 size-14 items-center justify-center rounded-2xl bg-brand/10">
              <Ionicons name="cloud-upload-outline" size={28} color="#2F6BFF" />
            </View>
            <Text className="text-[16px] font-bold text-ink">
              Selecionar documento
            </Text>
            <Text className="mt-1 text-center font-mono text-[12px] text-ink3">
              Toque para escolher PDF ou DOCX
            </Text>
          </Pressable>
        )}

        <View className="mb-6 flex-row gap-3">
          <View className="w-28 gap-2">
            <Text className="text-[13px] font-medium text-ink2">Versão</Text>
            <View className="h-12 justify-center rounded-2xl border border-line-glass bg-glass px-3.5">
              <TextInput
                value={version}
                onChangeText={setVersion}
                placeholder="v1"
                placeholderTextColor="#94A3B8"
                className="font-mono text-[14px] text-ink"
              />
            </View>
          </View>

          <View className="flex-1 gap-2">
            <Text className="text-[13px] font-medium text-ink2">Rótulo</Text>
            <View className="h-12 justify-center rounded-2xl border border-line-glass bg-glass px-3.5">
              <TextInput
                value={label}
                onChangeText={setLabel}
                placeholder="Ex: Entrega parcial, Versão final"
                placeholderTextColor="#94A3B8"
                className="text-[14px] text-ink"
              />
            </View>
          </View>
        </View>

        <View className="mb-6 gap-2.5">
          <Text className="text-[14px] font-medium text-ink2">
            Outras formas de enviar
          </Text>
          <View className="flex-row gap-3">
            <Pressable className="flex-1 items-center justify-center rounded-2xl border border-line-glass bg-glass p-3 shadow-sm active:opacity-75">
              <Text className="font-mono text-[11px] font-bold text-brand">
                TXT
              </Text>
              <Text className="mt-0.5 text-[12px] text-ink2">Colar texto</Text>
            </Pressable>

            <Pressable className="flex-1 items-center justify-center rounded-2xl border border-line-glass bg-glass p-3 shadow-sm active:opacity-75">
              <Text className="font-mono text-[11px] font-bold text-brand">
                IMG
              </Text>
              <Text className="mt-0.5 text-[12px] text-ink2">Fotos</Text>
            </Pressable>

            <Pressable className="flex-1 items-center justify-center rounded-2xl border border-line-glass bg-glass p-3 shadow-sm active:opacity-75">
              <Text className="font-mono text-[11px] font-bold text-brand">
                DOC
              </Text>
              <Text className="mt-0.5 text-[12px] text-ink2">Word</Text>
            </Pressable>
          </View>
        </View>

        <View className="rounded-2xl border border-line-glass bg-glass/60 p-3.5">
          <Text className="text-[12px] leading-relaxed text-ink3">
            O arquivo é processado de forma privada e apagado em 30 dias. Ajuste
            em Configurações.
          </Text>
        </View>
      </ScrollView>

      <View
        style={{ paddingBottom: Math.max(insets.bottom, 16) }}
        className="absolute bottom-0 left-0 right-0 border-t border-line-glass bg-canvas/90 px-5 pt-3"
      >
        <Pressable
          onPress={() => router.push("/conferences/review")}
          className="h-13 items-center justify-center rounded-2xl bg-brand shadow-lg shadow-brand/25 active:opacity-90"
        >
          <Text className="text-[16px] font-semibold text-white">Continuar</Text>
        </Pressable>
      </View>
    </View>
  );
}
