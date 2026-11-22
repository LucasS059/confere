import { ScrollView, Text, View } from "react-native";
import { useSafeAreaInsets } from "react-native-safe-area-context";
import { Blob } from "@/components/ui/blob";
import { ScreenHeader } from "@/components/ui/screen-header";

export default function PrivacyScreen() {
  const insets = useSafeAreaInsets();

  return (
    <View className="flex-1 overflow-hidden bg-canvas">
      <Blob
        color="#1E9E62"
        className="-top-[120px] -right-[80px] size-[360px] opacity-[0.16] dark:opacity-[0.28]"
      />

      <ScreenHeader title="Privacidade" />

      <ScrollView
        showsVerticalScrollIndicator={false}
        contentContainerStyle={{
          paddingHorizontal: 20,
          paddingTop: 16,
          paddingBottom: insets.bottom + 40,
          gap: 20,
        }}
      >
        <View className="gap-3 rounded-3xl border border-line-glass bg-glass p-5 shadow-sm">
          <Text className="font-instrument-semibold text-[17px] text-ink">
            1. Uso dos Dados para Aprimoramento da IA
          </Text>
          <Text className="font-instrument text-[14px] text-ink2 leading-[22px]">
            No Confere, seus arquivos, rubricas e resultados de conferência são
            tratados com segurança e{" "}
            <Text className="font-semibold text-ink">
              podem ser utilizados de forma anonimizada para alimentar, treinar
              e refinar o modelo próprio de inteligência artificial do sistema
            </Text>
            , visando melhorar a precisão na extração de requisitos e na análise
            de entregas acadêmicas.
          </Text>
        </View>

        <View className="gap-3 rounded-3xl border border-line-glass bg-glass p-5 shadow-sm">
          <Text className="font-instrument-semibold text-[17px] text-ink">
            2. Informações que Coletamos
          </Text>
          <Text className="font-instrument text-[14px] text-ink2 leading-[22px]">
            Coletamos as informações necessárias para funcionamento da sua conta
            e evolução das análises:
          </Text>
          <View className="gap-2 pl-2">
            <Text className="font-instrument text-[13.5px] text-ink2">
              • <Text className="font-semibold text-ink">Identificação:</Text>{" "}
              Nome e endereço de e-mail informados no cadastro.
            </Text>
            <Text className="font-instrument text-[13.5px] text-ink2">
              •{" "}
              <Text className="font-semibold text-ink">
                Projetos e Entregas:
              </Text>{" "}
              Título dos projetos, requisitos da rubrica cadastrada e arquivos
              enviados para verificação e treinamento do modelo.
            </Text>
            <Text className="font-instrument text-[13.5px] text-ink2">
              • <Text className="font-semibold text-ink">Resultados:</Text>{" "}
              Notas de cobertura, citações extraídas e justificativas de
              conformidade geradas para cada requisito.
            </Text>
          </View>
        </View>

        <View className="gap-3 rounded-3xl border border-line-glass bg-glass p-5 shadow-sm">
          <Text className="font-instrument-semibold text-[17px] text-ink">
            3. Segurança e Armazenamento
          </Text>
          <Text className="font-instrument text-[14px] text-ink2 leading-[22px]">
            As credenciais e sessões de acesso são armazenadas com criptografia
            de ponta e proteção em hardware (Secure Store / Keychain). As
            conexões com nossos servidores ocorrem de forma segura via
            HTTPS/TLS.
          </Text>
        </View>

        <View className="gap-3 rounded-3xl border border-line-glass bg-glass p-5 shadow-sm">
          <Text className="font-instrument-semibold text-[17px] text-ink">
            4. Seus Direitos (LGPD)
          </Text>
          <Text className="font-instrument text-[14px] text-ink2 leading-[22px]">
            Você tem total controle sobre seus dados. A qualquer momento, você
            pode exportar seus relatórios ou solicitar a exclusão definitiva dos
            seus projetos, conferências e conta.
          </Text>
        </View>

        <Text className="pb-4 text-center font-mono text-[12px] text-ink3">
          Última atualização: Novembro de 2026
        </Text>
      </ScrollView>
    </View>
  );
}
