import { SectionLabel } from "@/components/shared/SectionLabel";
import type { RecipeCost } from "@/lib/api";

interface Props {
  cost: RecipeCost;
  servings: number;
}

export function CostPanel({ cost, servings }: Props) {
  return (
    <div className="border border-rule rounded-card p-4 bg-paper">
      <div className="flex gap-4">
        <div className="flex-1">
          <SectionLabel>Cost</SectionLabel>
          <div className="mt-3">
            <span
              className="font-display italic font-[350] text-[28px] tracking-[-0.02em] text-ink"
              style={{ fontVariationSettings: '"opsz" 144, "SOFT" 60' }}
            >
              {cost.currency} {cost.totalCost.toFixed(2)}
            </span>
          </div>
          <span className="font-mono text-[10px] tracking-[0.14em] text-ink-faint">
            {cost.currency} {cost.perServingCost.toFixed(2)} / serving
          </span>
        </div>

        <div className="flex-1">
          <div className="mt-7 flex flex-col gap-1.5">
            {cost.topContributors.slice(0, 4).map((item) => (
              <div key={item.name} className="flex justify-between items-center">
                <span className="font-mono text-[9px] tracking-[0.12em] uppercase text-ink-faint truncate mr-2">
                  {item.name}
                </span>
                <span className="font-mono text-[10px] font-medium text-ink whitespace-nowrap">
                  {item.cost.toFixed(2)}
                </span>
              </div>
            ))}
          </div>
        </div>
      </div>

      {cost.warnings.length > 0 && (
        <p className="mt-3 font-mono text-[9px] text-warn tracking-[0.1em]">
          Missing cost for: {cost.warnings.join(", ")}
        </p>
      )}
    </div>
  );
}
