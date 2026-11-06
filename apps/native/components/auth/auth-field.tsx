import {
  Text,
  TextInput,
  type TextInputInstance,
  type TextInputProps,
  View,
} from "react-native";
import { useCSSVariable } from "uniwind";

interface AuthFieldProps extends TextInputProps {
  label: string;
  ref?: React.Ref<TextInputInstance>;
  focused?: boolean;
  trailing?: React.ReactNode;
}

export function AuthField({
  label,
  ref,
  focused,
  trailing,
  className,
  ...props
}: AuthFieldProps) {
  const placeholderColor = useCSSVariable("--ink3") as string | undefined;

  return (
    <View
      className={`h-[54px] flex-row items-center gap-2.5 rounded-2xl bg-card px-4 ${
        focused ? "border-[1.5px] border-brand" : "border border-hair"
      }`}
    >
      <Text className="w-[52px] font-instrument text-ink3 text-xs">
        {label}
      </Text>
      <TextInput
        ref={ref}
        className={`h-full flex-1 font-instrument text-[15px] text-ink web:outline-none ${className ?? ""}`}
        placeholderTextColor={placeholderColor}
        accessibilityLabel={label}
        {...props}
      />
      {trailing}
    </View>
  );
}
