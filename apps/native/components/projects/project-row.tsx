import { Pressable, Text, View } from "react-native";
import { Icon } from "@/components/ui/icon";
import { getCoverageColor, getProjectBadge } from "@/lib/format";

export type ProjectSummary = {
  id: string;
  name: string;
  requirementsCount: number;
  submissionsCount?: number;
  latestSubmission: {
    coverage: number | null;
  } | null;
};

type ProjectRowProps = {
  project: ProjectSummary;
  showDivider: boolean;
  onPress: () => void;
};

export function ProjectRow({ project, showDivider, onPress }: ProjectRowProps) {
  const cov = project.latestSubmission?.coverage ?? null;
  const subCount =
    project.submissionsCount ?? (project.latestSubmission ? 1 : 0);

  return (
    <Pressable
      onPress={onPress}
      className={`flex-row items-center justify-between gap-3 px-4 py-4 active:bg-card/50 ${
        showDivider ? "border-line-glass border-b" : ""
      }`}
    >
      <View className="flex-1 flex-row items-center gap-3">
        <View className="size-10 items-center justify-center rounded-xl bg-brand/10">
          <Text className="font-bold text-[11px] text-brand">
            {getProjectBadge(project.name)}
          </Text>
        </View>

        <View className="flex-1">
          <Text
            numberOfLines={1}
            className="font-semibold text-[15px] text-ink"
          >
            {project.name}
          </Text>
          <Text numberOfLines={1} className="mt-0.5 text-[12.5px] text-ink2">
            {project.requirementsCount}{" "}
            {project.requirementsCount === 1 ? "requisito" : "requisitos"} ·{" "}
            {subCount === 0
              ? "sem entrega"
              : `${subCount} ${subCount === 1 ? "entrega" : "entregas"}`}
          </Text>
        </View>
      </View>

      <View className="flex-row items-center gap-2">
        <Text className={`font-bold text-[14px] ${getCoverageColor(cov)}`}>
          {cov !== null ? `${cov}%` : "—"}
        </Text>
        <Icon
          name="chevron.forward"
          fallback="chevron-forward"
          size={15}
          color="#94A3B8"
        />
      </View>
    </Pressable>
  );
}
