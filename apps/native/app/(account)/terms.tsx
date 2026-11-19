import { ScrollView, Text, View } from "react-native";
import { useSafeAreaInsets } from "react-native-safe-area-context";
import { Blob } from "@/components/ui/blob";
import { ScreenHeader } from "@/components/ui/screen-header";

export default function TermsScreen() {
  const insets = useSafeAreaInsets();

  return (
    <View className="flex-1 overflow-hidden bg-canvas">
      <Blob
        color="#2F6BFF"
        className="-top-[120px] -left-[80px] size-[360px] opacity-[0.16] dark:opacity-[0.28]"
      />

      <ScreenHeader title="Termos de Uso" />

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
            1. Aceitação dos Termos
          </Text>
          <Text className="font-instrument text-[14px] text-ink2 leading-[22px]">
            Ao criar uma conta ou utilizar o aplicativo Confere, você concorda
            com estes termos. O serviço é destinado a estudantes e pesquisadores
            para conferência de relatórios e trabalhos acadêmicos contra editais
            ou rubricas de avaliação informadas.
          </Text>
        </View>

        <View className="gap-3 rounded-3xl border border-line-glass bg-glass p-5 shadow-sm">
          <Text className="font-instrument-semibold text-[17px] text-ink">
            2. Uso do Serviço e Responsabilidades
          </Text>
          <Text className="font-instrument text-[14px] text-ink2 leading-[22px]">
            O Confere é uma ferramenta de apoio ao estudo e validação preliminar
            de conformidade. A análise automática gerada pela inteligência
            artificial serve como orientação e suporte acadêmico, não
            substituindo a avaliação final e critérios do orientador, professor
            ou banca examinadora.
          </Text>
        </View>

        <View className="gap-3 rounded-3xl border border-line-glass bg-glass p-5 shadow-sm">
          <Text className="font-instrument-semibold text-[17px] text-ink">
            3. Conteúdo do Usuário e Propriedade Intelectual
          </Text>
          <Text className="font-instrument text-[14px] text-ink2 leading-[22px]">
            Você mantém todos os direitos autorais e propriedade intelectual
            sobre os arquivos, relatórios, monografias ou editais que envia.
            Você garante possuir os direitos necessários para carregar os
            documentos para análise.
          </Text>
        </View>

        <View className="gap-3 rounded-3xl border border-line-glass bg-glass p-5 shadow-sm">
          <Text className="font-instrument-semibold text-[17px] text-ink">
            4. Disponibilidade e Atualizações
          </Text>
          <Text className="font-instrument text-[14px] text-ink2 leading-[22px]">
            O serviço pode passar por atualizações periódicas para aprimorar o
            desempenho, a precisão da IA e a segurança da plataforma.
            Reservamo-nos o direito de modificar ou descontinuar recursos com
            aviso prévio.
          </Text>
        </View>

        <Text className="pb-4 text-center font-mono text-[12px] text-ink3">
          Última atualização: Novembro de 2026
        </Text>
      </ScrollView>
    </View>
  );
}
