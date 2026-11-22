import { Text, View } from "react-native";
import { KeyboardAwareScrollView } from "react-native-keyboard-controller";
import { useSafeAreaInsets } from "react-native-safe-area-context";
import { ProjectForm } from "@/components/projects/project-form";
import { Blob } from "@/components/ui/blob";

export default function NewProjectTabScreen() {
  const insets = useSafeAreaInsets();

  return (
    <View className="flex-1 overflow-hidden bg-canvas">
      <Blob
        color="#2F6BFF"
        className="-top-[120px] -right-[100px] size-[360px] opacity-[0.16] dark:opacity-[0.28]"
      />
      <Blob
        color="#10B981"
        className="top-[320px] -left-[120px] size-[300px] opacity-[0.12] dark:opacity-[0.20]"
      />

      <KeyboardAwareScrollView
        bottomOffset={24}
        keyboardShouldPersistTaps="handled"
        showsVerticalScrollIndicator={false}
        contentContainerStyle={{
          gap: 16,
          paddingHorizontal: 20,
          paddingTop: Math.max(insets.top + 16, 48),
          paddingBottom: insets.bottom + 110,
        }}
      >
        <View className="rounded-3xl border border-line-glass bg-glass p-5 shadow-sm">
          <Text className="font-bold text-[22px] text-ink">Novo projeto</Text>
          <Text className="mt-0.5 text-[13px] text-ink2">
            Cadastre o trabalho e a rubrica para conferir suas entregas
          </Text>
        </View>

        <ProjectForm />
      </KeyboardAwareScrollView>
    </View>
  );
}
