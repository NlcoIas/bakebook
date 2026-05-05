import { SectionLabel } from "@/components/shared/SectionLabel";
import type { RecipeRatios } from "@/lib/api";

const RATIO_ROWS: { key: keyof RecipeRatios; label: string; color: string; max: number }[] = [
  { key: "hydration", label: "Hydration", color: "var(--amber)", max: 100 },
  { key: "hydrationWithDairy", label: "Hyd + dairy", color: "var(--blush)", max: 100 },
  { key: "fat", label: "Fat", color: "var(--olive)", max: 30 },
  { key: "sugar", label: "Sugar", color: "var(--warn)", max: 20 },
  { key: "salt", label: "Salt", color: "var(--ink-faint)", max: 5 },
  { key: "inoculationRate", label: "Yeast/leaven", color: "var(--good)", max: 30 },
];

interface Props {
  ratios: RecipeRatios;
}

export function RatiosPanel({ ratios }: Props) {
  return (
    <div className="border border-rule rounded-card p-4 bg-paper">
      <SectionLabel>Baker&apos;s ratios</SectionLabel>

      <div className="mt-4 flex flex-col gap-3">
        {RATIO_ROWS.map((row) => {
          const value = ratios[row.key] as number;
          if (value === 0 && row.key !== "hydration") return null;
          const pct = Math.min((value / row.max) * 100, 100);

          return (
            <div key={row.key} className="flex items-center gap-3">
              <span className="w-20 font-mono text-[9px] tracking-[0.18em] uppercase text-ink-faint shrink-0">
                {row.label}
              </span>
              <div className="flex-1 h-1 rounded-full bg-cream-deep overflow-hidden">
                <div
                  className="h-full rounded-full"
                  style={{ width: `${pct}%`, backgroundColor: row.color }}
                />
              </div>
              <span className="w-12 text-right font-mono text-[11px] font-medium text-ink">
                {value.toFixed(1)}%
              </span>
            </div>
          );
        })}
      </div>
    </div>
  );
}
