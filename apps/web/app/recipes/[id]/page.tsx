"use client";

import { useQuery } from "@tanstack/react-query";
import { useParams } from "next/navigation";
import { Suspense } from "react";
import { api } from "@/lib/api";
import { HandRule } from "@/components/shared/HandRule";
import { SectionLabel } from "@/components/shared/SectionLabel";
import { NutritionPanel } from "@/components/recipe/NutritionPanel";
import { CostPanel } from "@/components/recipe/CostPanel";
import { RatiosPanel } from "@/components/recipe/RatiosPanel";

function formatTime(minutes: number): string {
  if (minutes < 60) return `${minutes} min`;
  const h = Math.floor(minutes / 60);
  const m = minutes % 60;
  return m > 0 ? `${h}h ${m}m` : `${h}h`;
}

function RecipeDetail() {
  const params = useParams();
  const id = params.id as string;

  const { data: recipe, isLoading, error } = useQuery({
    queryKey: ["recipe", id],
    queryFn: () => api.recipes.get(id),
  });

  if (isLoading) {
    return (
      <div className="px-4 pt-12 text-center">
        <p className="font-mono text-[11px] tracking-[0.14em] uppercase text-ink-faint">
          Loading...
        </p>
      </div>
    );
  }

  if (error || !recipe) {
    return (
      <div className="px-4 pt-12 text-center">
        <p className="font-mono text-[11px] tracking-[0.14em] uppercase text-amber">
          Recipe not found
        </p>
      </div>
    );
  }

  // Group ingredients
  const ingredientGroups: { label: string | null; items: typeof recipe.ingredients }[] = [];
  let currentGroup: typeof ingredientGroups[0] | null = null;
  for (const ing of recipe.ingredients) {
    if (!currentGroup || ing.groupLabel !== currentGroup.label) {
      currentGroup = { label: ing.groupLabel, items: [] };
      ingredientGroups.push(currentGroup);
    }
    currentGroup.items.push(ing);
  }

  return (
    <div className="px-4 pt-6 max-w-lg mx-auto">
      {/* Hero */}
      <div className="mb-1">
        <span className="font-mono text-[9px] tracking-[0.22em] uppercase text-ink-faint">
          {recipe.category}
        </span>
      </div>
      <h1
        className="font-display font-[350] text-[32px] tracking-[-0.025em] leading-[0.95]"
        style={{ fontVariationSettings: '"opsz" 144, "SOFT" 80' }}
      >
        {recipe.title}
      </h1>

      {recipe.summary && (
        <p className="mt-3 text-[15px] text-ink-soft leading-relaxed" style={{ fontVariationSettings: '"opsz" 24' }}>
          {recipe.summary}
        </p>
      )}

      {/* Meta row */}
      <div className="mt-3 flex gap-5 flex-wrap font-mono text-[10px] tracking-[0.14em] uppercase text-ink-faint">
        {recipe.totalTimeMin && <span>{formatTime(recipe.totalTimeMin)}</span>}
        {recipe.difficulty && (
          <span>
            {"●".repeat(recipe.difficulty)}
            {"○".repeat(5 - recipe.difficulty)}
          </span>
        )}
        {recipe.yields && <span>{recipe.yields}</span>}
        {recipe.servings > 1 && <span>{recipe.servings} servings</span>}
      </div>

      <div className="mt-4">
        <HandRule seed={recipe.title.charCodeAt(0)} />
      </div>

      {/* Ingredients */}
      <SectionLabel>Ingredients</SectionLabel>
      <div className="mt-3 flex flex-col gap-1">
        {ingredientGroups.map((group, gi) => (
          <div key={gi}>
            {group.label && (
              <p className="mt-2 mb-1 font-mono text-[9px] tracking-[0.18em] uppercase text-amber font-medium">
                {group.label}
              </p>
            )}
            {group.items.map((ing) => (
              <div
                key={ing.id}
                className="flex items-baseline justify-between py-1.5 border-b border-dashed border-rule/50"
              >
                <span
                  className={`text-[14.5px] ${ing.optional ? "text-ink-faint italic" : "text-ink"}`}
                  style={{ fontVariationSettings: '"opsz" 24' }}
                >
                  {ing.name}
                  {ing.optional && <span className="text-[11px]"> (optional)</span>}
                </span>
                <span className="font-mono text-[12px] font-medium text-ink ml-2 whitespace-nowrap">
                  {ing.grams != null ? `${ing.grams} g` : ""}
                  {ing.unitDisplay && ing.unitDisplayQty && (
                    <span className="text-ink-faint ml-1">
                      ({ing.unitDisplayQty} {ing.unitDisplay})
                    </span>
                  )}
                </span>
              </div>
            ))}
          </div>
        ))}
      </div>

      <div className="mt-5">
        <HandRule seed={recipe.title.charCodeAt(1) || 13} />
      </div>

      {/* Steps */}
      <SectionLabel>Method</SectionLabel>
      <div className="mt-3 flex flex-col gap-4">
        {recipe.steps.map((step) => (
          <div key={step.id} className="flex gap-3">
            <div className="flex-shrink-0 w-6 h-6 rounded-full bg-cream-deep flex items-center justify-center">
              <span className="font-mono text-[10px] font-medium text-ink-faint">
                {step.ord}
              </span>
            </div>
            <div className="flex-1 min-w-0">
              <h3 className="font-display font-[500] text-[14.5px] text-ink" style={{ fontVariationSettings: '"opsz" 24' }}>
                {step.title}
              </h3>
              <p className="mt-1 text-[13.5px] text-ink-soft leading-relaxed" style={{ fontVariationSettings: '"opsz" 24' }}>
                {step.body}
              </p>
              <div className="mt-1 flex gap-3">
                {step.timerSeconds && (
                  <span className="font-mono text-[10px] tracking-[0.12em] text-amber">
                    ⏱ {Math.floor(step.timerSeconds / 60)} min
                  </span>
                )}
                {step.targetTempC && (
                  <span className="font-mono text-[10px] tracking-[0.12em] text-ink-faint">
                    {step.targetTempC}°C {step.tempKind && `(${step.tempKind})`}
                  </span>
                )}
              </div>
            </div>
          </div>
        ))}
      </div>

      <div className="mt-6">
        <HandRule seed={recipe.title.charCodeAt(2) || 29} />
      </div>

      {/* Data panels */}
      <div className="mt-4 flex flex-col gap-3">
        {recipe.nutrition && (
          <NutritionPanel nutrition={recipe.nutrition} servings={recipe.servings} />
        )}
        {recipe.cost && (
          <CostPanel cost={recipe.cost} servings={recipe.servings} />
        )}
        {recipe.ratios && (
          <RatiosPanel ratios={recipe.ratios} />
        )}
      </div>

      {/* Equipment */}
      {recipe.equipment.length > 0 && (
        <div className="mt-4">
          <SectionLabel>Equipment</SectionLabel>
          <div className="mt-2 flex flex-wrap gap-2">
            {recipe.equipment.map((eq) => (
              <span
                key={eq}
                className="font-mono text-[10px] tracking-[0.14em] uppercase text-ink-faint border border-rule rounded-full px-2.5 py-1"
              >
                {eq}
              </span>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

export default function RecipePage() {
  return (
    <Suspense>
      <RecipeDetail />
    </Suspense>
  );
}
