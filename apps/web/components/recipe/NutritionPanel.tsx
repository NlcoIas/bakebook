"use client";

import { useSearchParams, useRouter, usePathname } from "next/navigation";
import { SectionLabel } from "@/components/shared/SectionLabel";
import type { RecipeNutrition } from "@/lib/api";

const MACRO_COLORS: Record<string, string> = {
  carbs: "var(--warn)",
  fat: "var(--amber)",
  protein: "var(--olive)",
  fiber: "var(--ink-faint)",
};

interface Props {
  nutrition: RecipeNutrition;
  servings: number;
}

export function NutritionPanel({ nutrition, servings }: Props) {
  const searchParams = useSearchParams();
  const router = useRouter();
  const pathname = usePathname();
  const per = searchParams.get("per") === "100g" ? "100g" : "serving";

  const macros = per === "100g" && nutrition.per100g
    ? nutrition.per100g
    : nutrition.perServing;

  const togglePer = () => {
    const next = per === "serving" ? "100g" : "serving";
    const params = new URLSearchParams(searchParams.toString());
    params.set("per", next);
    router.replace(`${pathname}?${params.toString()}`, { scroll: false });
  };

  const dv = nutrition.dailyValuePct;

  return (
    <div className="border border-rule rounded-card p-4 bg-paper">
      <div className="flex items-center justify-between">
        <SectionLabel>Nutrition</SectionLabel>
        <button
          type="button"
          onClick={togglePer}
          className="font-mono text-[9px] tracking-[0.18em] uppercase text-ink-faint border border-rule rounded-full px-2 py-0.5 hover:border-ink-faint transition-colors"
        >
          {per === "serving" ? `per serving` : "per 100g"}
        </button>
      </div>

      <div className="mt-4 flex items-baseline gap-3">
        <span
          className="font-display italic font-[350] text-[36px] tracking-[-0.02em] text-ink"
          style={{ fontVariationSettings: '"opsz" 144, "SOFT" 60' }}
        >
          {Math.round(macros.kcal)}
        </span>
        <div className="font-mono text-[10px] tracking-[0.14em] text-ink-faint leading-tight">
          <span>kcal</span>
          {dv && per === "serving" && (
            <span className="block">of 2,000 daily · {Math.round(dv.kcal)}%</span>
          )}
        </div>
      </div>

      {/* Macro bar */}
      <div className="mt-4 flex gap-0.5 h-3 rounded-full overflow-hidden">
        {(["carbs", "fat", "protein", "fiber"] as const).map((key) => {
          const total = macros.carbs + macros.fat + macros.protein + macros.fiber;
          const pct = total > 0 ? (macros[key] / total) * 100 : 25;
          return (
            <div
              key={key}
              style={{ width: `${pct}%`, backgroundColor: MACRO_COLORS[key] }}
              className="min-w-[4px]"
            />
          );
        })}
      </div>

      {/* Macro grid */}
      <div className="mt-4 grid grid-cols-4 gap-3">
        {(["carbs", "fat", "protein", "fiber"] as const).map((key) => (
          <div key={key} className="flex flex-col items-center">
            <div
              className="w-2 h-2 rounded-sm"
              style={{ backgroundColor: MACRO_COLORS[key] }}
            />
            <span className="mt-1 font-mono text-[9px] tracking-[0.18em] uppercase text-ink-faint">
              {key}
            </span>
            <span
              className="font-display italic font-[350] text-[18px] tracking-[-0.01em]"
              style={{ fontVariationSettings: '"opsz" 144, "SOFT" 60' }}
            >
              {macros[key].toFixed(0)}
            </span>
            <span className="font-mono text-[9px] text-ink-faint">g</span>
          </div>
        ))}
      </div>

      {nutrition.warnings.length > 0 && (
        <p className="mt-3 font-mono text-[9px] text-warn tracking-[0.1em]">
          Missing nutrition data for: {nutrition.warnings.join(", ")}
        </p>
      )}
    </div>
  );
}
