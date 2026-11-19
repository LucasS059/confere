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
            1. Compromisso com seus Dados Acadêmicos
          </Text>
          <Text className="font-instrument text-[14px] text-ink2 leading-[22px]">
            No Confere, seus arquivos e trabalhos acadêmicos são tratados com
            sigilo rigoroso. Seus textos, relatórios e documentos{" "}
            <Text className="font-semibold text-ink">
              não são utilizados para treinar modelos públicos de IA
            </Text>
            .
          </Text>
        </View>

        <View className="gap-3 rounded-3xl border border-line-glass bg-glass p-5 shadow-sm">
          <Text className="font-instrument-semibold text-[17px] text-ink">
            2. Informações que Coletamos
          </Text>
          <Text className="font-instrument text-[14px] text-ink2 leading-[22px]">
            Coletamos apenas as informações essenciais para funcionamento da sua
            conta:
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
              Título dos projetos, critérios da rubrica cadastrada e arquivos em
              PDF/DOCX enviados para verificação.
            </Text>
            <Text className="font-instrument text-[13.5px] text-ink2">
              • <Text className="font-semibold text-ink">Resultados:</Text>{" "}
              Notas de cobertura e justificativas de conformidade geradas para
              cada requisito.
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
