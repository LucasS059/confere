import { cn } from "heroui-native";
import { View } from "react-native";
import Svg, { Circle, Defs, RadialGradient, Stop } from "react-native-svg";

// Design's `radial-gradient(circle, color, transparent 70%)` backdrop glow; SVG
// because uniwind drops radial gradients on native. Opacity comes from className.
export function Blob({
  color,
  className,
}: {
  color: string;
  className: string;
}) {
  const id = `blob-${color.replace(/[^a-zA-Z0-9]/g, "")}`;
  return (
    <View pointerEvents="none" className={cn("absolute", className)}>
      <Svg width="100%" height="100%">
        <Defs>
          <RadialGradient id={id} cx="50%" cy="50%" r="70.71%">
            <Stop offset="0" stopColor={color} stopOpacity={1} />
            <Stop offset="0.7" stopColor={color} stopOpacity={0} />
          </RadialGradient>
        </Defs>
        <Circle cx="50%" cy="50%" r="50%" fill={`url(#${id})`} />
      </Svg>
    </View>
  );
}
