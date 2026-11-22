// Gera sigla curta (ex: TCC ou iniciais das 3 primeiras palavras relevantes) para o ícone do projeto.
export function getProjectBadge(name: string): string {
  const words = name
    .trim()
    .split(/\s+/)
    .filter((w) => w.length > 2 || w.toUpperCase() === "TCC");
  if (words.length === 0) return name.slice(0, 3).toUpperCase() || "PRJ";
  if (words[0].toUpperCase() === "TCC") return "TCC";
  if (words.length >= 3) {
    return (words[0][0] + words[1][0] + words[2][0]).toUpperCase();
  }
  return words[0].slice(0, 3).toUpperCase();
}

export function formatShortDate(dateInput?: Date | string | null): string {
  if (!dateInput) return "";
  const d = typeof dateInput === "string" ? new Date(dateInput) : dateInput;
  if (Number.isNaN(d.getTime())) return "";

  const now = new Date();
  const isToday =
    d.getDate() === now.getDate() &&
    d.getMonth() === now.getMonth() &&
    d.getFullYear() === now.getFullYear();

  const hours = String(d.getHours()).padStart(2, "0");
  const mins = String(d.getMinutes()).padStart(2, "0");

  if (isToday) {
    return `Hoje, ${hours}:${mins}`;
  }

  const day = String(d.getDate()).padStart(2, "0");
  const month = String(d.getMonth() + 1).padStart(2, "0");
  return `${day}/${month}/${d.getFullYear()}`;
}

export function getCoverageColor(coverage: number | null): string {
  if (coverage === null) return "text-ink3";
  if (coverage >= 80) return "text-ok";
  if (coverage >= 50) return "text-warn";
  return "text-err";
}

const RESULT_STATUS: Record<
  string,
  {
    label: string;
    dot: string;
    bg: string;
    text: string;
  }
> = {
  atendido: {
    label: "Atendido",
    dot: "bg-ok",
    bg: "bg-ok/12",
    text: "text-ok",
  },
  revisar: {
    label: "Revisar",
    dot: "bg-warn",
    bg: "bg-warn/15",
    text: "text-warn",
  },
  faltando: {
    label: "Faltando",
    dot: "bg-err",
    bg: "bg-err/12",
    text: "text-err",
  },
};

export function getResultStatusStyle(status: string) {
  return (
    RESULT_STATUS[status] ?? {
      label: status,
      dot: "bg-ink3",
      bg: "bg-card",
      text: "text-ink2",
    }
  );
}
