"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useRouter } from "next/navigation";
import { useState } from "react";
import { api, type Recipe, type PantryItem } from "@/lib/api";
import { SectionLabel } from "@/components/shared/SectionLabel";

const CATEGORIES = ["bread", "sweet", "quick", "pizza", "other"];
const ROLES = ["flour", "water", "salt", "leaven", "fat", "sugar", "egg", "dairy", "other"];

interface IngredientRow {
  key: string;
  name: string;
  grams: string;
  role: string;
  groupLabel: string;
  pantryItemId: string;
  optional: boolean;
}

interface StepRow {
  key: string;
  title: string;
  body: string;
  timerSeconds: string;
  targetTempC: string;
  tempKind: string;
}

function slugify(s: string): string {
  return s.toLowerCase().replace(/[^a-z0-9]+/g, "-").replace(/^-|-$/g, "");
}

let nextKey = 1;
function genKey() {
  return `k${nextKey++}`;
}

interface Props {
  recipe?: Recipe;
}

export function RecipeEditor({ recipe }: Props) {
  const router = useRouter();
  const queryClient = useQueryClient();
  const isEdit = !!recipe;

  const [title, setTitle] = useState(recipe?.title ?? "");
  const [category, setCategory] = useState(recipe?.category ?? "bread");
  const [summary, setSummary] = useState(recipe?.summary ?? "");
  const [yields, setYields] = useState(recipe?.yields ?? "");
  const [servings, setServings] = useState(String(recipe?.servings ?? 8));
  const [servingG, setServingG] = useState(recipe?.servingG ? String(recipe.servingG) : "");
  const [totalTime, setTotalTime] = useState(recipe?.totalTimeMin ? String(recipe.totalTimeMin) : "");
  const [activeTime, setActiveTime] = useState(recipe?.activeTimeMin ? String(recipe.activeTimeMin) : "");
  const [difficulty, setDifficulty] = useState(String(recipe?.difficulty ?? 2));
  const [equipment, setEquipment] = useState(recipe?.equipment?.join(", ") ?? "");
  const [source, setSource] = useState(recipe?.source ?? "");
  const [notes, setNotes] = useState(recipe?.notes ?? "");

  const [ingredients, setIngredients] = useState<IngredientRow[]>(
    recipe?.ingredients?.map((i) => ({
      key: genKey(),
      name: i.name,
      grams: i.grams != null ? String(i.grams) : "",
      role: i.role ?? "other",
      groupLabel: i.groupLabel ?? "",
      pantryItemId: i.pantryItemId ?? "",
      optional: i.optional,
    })) ?? [{ key: genKey(), name: "", grams: "", role: "flour", groupLabel: "", pantryItemId: "", optional: false }],
  );

  const [steps, setSteps] = useState<StepRow[]>(
    recipe?.steps?.map((s) => ({
      key: genKey(),
      title: s.title,
      body: s.body,
      timerSeconds: s.timerSeconds != null ? String(s.timerSeconds) : "",
      targetTempC: s.targetTempC != null ? String(s.targetTempC) : "",
      tempKind: s.tempKind ?? "",
    })) ?? [{ key: genKey(), title: "", body: "", timerSeconds: "", targetTempC: "", tempKind: "" }],
  );

  const { data: pantryItems } = useQuery({
    queryKey: ["pantry"],
    queryFn: () => api.pantry.list(),
  });

  const saveMutation = useMutation({
    mutationFn: () => {
      const slug = slugify(title);
      const data = {
        title,
        slug,
        category,
        summary: summary || null,
        yields: yields || null,
        servings: Number(servings) || 1,
        servingG: servingG ? Number(servingG) : null,
        totalTimeMin: totalTime ? Number(totalTime) : null,
        activeTimeMin: activeTime ? Number(activeTime) : null,
        difficulty: Number(difficulty) || null,
        equipment: equipment ? equipment.split(",").map((s) => s.trim()).filter(Boolean) : [],
        source: source || null,
        notes: notes || null,
        ingredients: ingredients
          .filter((i) => i.name)
          .map((i, idx) => ({
            ord: idx + 1,
            name: i.name,
            grams: i.grams ? Number(i.grams) : null,
            role: i.role || null,
            groupLabel: i.groupLabel || null,
            pantryItemId: i.pantryItemId || null,
            optional: i.optional,
          })),
        steps: steps
          .filter((s) => s.title || s.body)
          .map((s, idx) => ({
            ord: idx + 1,
            title: s.title || `Step ${idx + 1}`,
            body: s.body,
            timerSeconds: s.timerSeconds ? Number(s.timerSeconds) : null,
            targetTempC: s.targetTempC ? Number(s.targetTempC) : null,
            tempKind: s.tempKind || null,
          })),
      };

      return isEdit ? api.recipes.update(recipe.id, data) : api.recipes.create(data);
    },
    onSuccess: (result) => {
      queryClient.invalidateQueries({ queryKey: ["recipes"] });
      queryClient.invalidateQueries({ queryKey: ["recipe"] });
      router.push(`/recipes/${result.id}`);
    },
  });

  const updateIngredient = (idx: number, field: keyof IngredientRow, value: string | boolean) => {
    setIngredients((prev) => prev.map((ing, i) => (i === idx ? { ...ing, [field]: value } : ing)));
  };

  const updateStep = (idx: number, field: keyof StepRow, value: string) => {
    setSteps((prev) => prev.map((s, i) => (i === idx ? { ...s, [field]: value } : s)));
  };

  return (
    <div className="px-4 pt-6 max-w-lg mx-auto">
      <h1
        className="font-display font-[350] text-[28px] tracking-[-0.02em]"
        style={{ fontVariationSettings: '"opsz" 144, "SOFT" 80' }}
      >
        {isEdit ? "Edit recipe" : "New recipe"}
      </h1>

      {/* Metadata */}
      <SectionLabel>Details</SectionLabel>
      <div className="mt-3 flex flex-col gap-3">
        <Field label="Title" value={title} onChange={setTitle} />
        <div className="flex gap-2">
          <div className="flex-1">
            <label className="font-mono text-[9px] tracking-[0.18em] uppercase text-ink-faint">Category</label>
            <select
              value={category}
              onChange={(e) => setCategory(e.target.value)}
              className="mt-1 w-full px-3 py-2 bg-cream-deep border border-rule rounded-lg font-display text-[14px] focus:outline-none focus:ring-1 focus:ring-amber"
            >
              {CATEGORIES.map((c) => (
                <option key={c} value={c}>{c}</option>
              ))}
            </select>
          </div>
          <Field label="Difficulty (1-5)" value={difficulty} onChange={setDifficulty} className="w-24" type="number" />
        </div>
        <Field label="Summary" value={summary} onChange={setSummary} multiline />
        <div className="grid grid-cols-2 gap-2">
          <Field label="Yields" value={yields} onChange={setYields} placeholder="e.g. 1 loaf" />
          <Field label="Servings" value={servings} onChange={setServings} type="number" />
        </div>
        <div className="grid grid-cols-2 gap-2">
          <Field label="Total time (min)" value={totalTime} onChange={setTotalTime} type="number" />
          <Field label="Active time (min)" value={activeTime} onChange={setActiveTime} type="number" />
        </div>
        <Field label="Equipment (comma-separated)" value={equipment} onChange={setEquipment} placeholder="e.g. cast iron skillet, dutch oven" />
        <Field label="Source" value={source} onChange={setSource} placeholder="e.g. mom, URL, book" />
      </div>

      {/* Ingredients */}
      <SectionLabel>Ingredients</SectionLabel>
      <div className="mt-3 flex flex-col gap-2">
        {ingredients.map((ing, idx) => (
          <div key={ing.key} className="border border-rule rounded-card p-3 bg-paper">
            <div className="flex gap-2">
              <input
                value={ing.name}
                onChange={(e) => updateIngredient(idx, "name", e.target.value)}
                placeholder="Ingredient name"
                className="flex-1 px-2 py-1.5 bg-cream-deep border border-rule rounded-lg font-display text-[13px] focus:outline-none focus:ring-1 focus:ring-amber"
                style={{ fontVariationSettings: '"opsz" 24' }}
                list="pantry-items"
              />
              <input
                value={ing.grams}
                onChange={(e) => updateIngredient(idx, "grams", e.target.value)}
                placeholder="g"
                type="number"
                inputMode="decimal"
                className="w-16 px-2 py-1.5 bg-cream-deep border border-rule rounded-lg font-mono text-[13px] focus:outline-none focus:ring-1 focus:ring-amber"
              />
            </div>
            <div className="mt-1.5 flex gap-2 items-center">
              <select
                value={ing.role}
                onChange={(e) => updateIngredient(idx, "role", e.target.value)}
                className="px-2 py-1 bg-cream-deep border border-rule rounded-lg font-mono text-[10px] focus:outline-none"
              >
                {ROLES.map((r) => (
                  <option key={r} value={r}>{r}</option>
                ))}
              </select>
              <input
                value={ing.groupLabel}
                onChange={(e) => updateIngredient(idx, "groupLabel", e.target.value)}
                placeholder="Group"
                className="flex-1 px-2 py-1 bg-cream-deep border border-rule rounded-lg font-mono text-[10px] focus:outline-none"
              />
              <button
                type="button"
                onClick={() => setIngredients((prev) => prev.filter((_, i) => i !== idx))}
                className="text-ink-faint hover:text-amber text-[14px] px-1"
              >
                &times;
              </button>
            </div>
          </div>
        ))}
        <button
          type="button"
          onClick={() => setIngredients((prev) => [...prev, { key: genKey(), name: "", grams: "", role: "other", groupLabel: "", pantryItemId: "", optional: false }])}
          className="py-2 font-mono text-[10px] tracking-[0.18em] uppercase border border-dashed border-rule rounded-card text-ink-faint hover:border-ink-faint"
        >
          + Add ingredient
        </button>
      </div>

      {/* Pantry datalist */}
      <datalist id="pantry-items">
        {pantryItems?.map((p) => (
          <option key={p.id} value={p.name} />
        ))}
      </datalist>

      {/* Steps */}
      <SectionLabel>Steps</SectionLabel>
      <div className="mt-3 flex flex-col gap-2">
        {steps.map((step, idx) => (
          <div key={step.key} className="border border-rule rounded-card p-3 bg-paper">
            <div className="flex gap-2 items-center">
              <span className="font-mono text-[10px] text-ink-faint w-5">{idx + 1}</span>
              <input
                value={step.title}
                onChange={(e) => updateStep(idx, "title", e.target.value)}
                placeholder="Step title"
                className="flex-1 px-2 py-1.5 bg-cream-deep border border-rule rounded-lg font-display text-[13px] font-medium focus:outline-none focus:ring-1 focus:ring-amber"
                style={{ fontVariationSettings: '"opsz" 24' }}
              />
              <button
                type="button"
                onClick={() => setSteps((prev) => prev.filter((_, i) => i !== idx))}
                className="text-ink-faint hover:text-amber text-[14px] px-1"
              >
                &times;
              </button>
            </div>
            <textarea
              value={step.body}
              onChange={(e) => updateStep(idx, "body", e.target.value)}
              placeholder="Instructions..."
              rows={2}
              className="mt-1.5 w-full px-2 py-1.5 bg-cream-deep border border-rule rounded-lg font-display text-[12px] focus:outline-none focus:ring-1 focus:ring-amber resize-none"
              style={{ fontVariationSettings: '"opsz" 24' }}
            />
            <div className="mt-1.5 flex gap-2">
              <input
                value={step.timerSeconds}
                onChange={(e) => updateStep(idx, "timerSeconds", e.target.value)}
                placeholder="Timer (sec)"
                type="number"
                className="w-24 px-2 py-1 bg-cream-deep border border-rule rounded-lg font-mono text-[10px] focus:outline-none"
              />
              <input
                value={step.targetTempC}
                onChange={(e) => updateStep(idx, "targetTempC", e.target.value)}
                placeholder="Temp °C"
                type="number"
                className="w-20 px-2 py-1 bg-cream-deep border border-rule rounded-lg font-mono text-[10px] focus:outline-none"
              />
              <select
                value={step.tempKind}
                onChange={(e) => updateStep(idx, "tempKind", e.target.value)}
                className="px-2 py-1 bg-cream-deep border border-rule rounded-lg font-mono text-[10px] focus:outline-none"
              >
                <option value="">—</option>
                <option value="oven">Oven</option>
                <option value="internal">Internal</option>
                <option value="dough">Dough</option>
                <option value="water">Water</option>
              </select>
            </div>
          </div>
        ))}
        <button
          type="button"
          onClick={() => setSteps((prev) => [...prev, { key: genKey(), title: "", body: "", timerSeconds: "", targetTempC: "", tempKind: "" }])}
          className="py-2 font-mono text-[10px] tracking-[0.18em] uppercase border border-dashed border-rule rounded-card text-ink-faint hover:border-ink-faint"
        >
          + Add step
        </button>
      </div>

      {/* Notes */}
      <SectionLabel>Notes</SectionLabel>
      <Field label="" value={notes} onChange={setNotes} multiline placeholder="Recipe notes..." />

      {/* Save */}
      <button
        type="button"
        onClick={() => saveMutation.mutate()}
        disabled={!title || saveMutation.isPending}
        className="mt-6 w-full py-4 font-mono text-[11px] tracking-[0.18em] uppercase bg-amber text-cream rounded-pill font-medium disabled:opacity-50"
      >
        {saveMutation.isPending ? "Saving..." : isEdit ? "Save changes" : "Create recipe"}
      </button>

      {saveMutation.isError && (
        <p className="mt-2 text-center font-mono text-[10px] text-amber">
          Error: {(saveMutation.error as Error).message}
        </p>
      )}
    </div>
  );
}

function Field({
  label,
  value,
  onChange,
  placeholder,
  type = "text",
  multiline = false,
  className = "",
}: {
  label: string;
  value: string;
  onChange: (v: string) => void;
  placeholder?: string;
  type?: string;
  multiline?: boolean;
  className?: string;
}) {
  return (
    <div className={className}>
      {label && (
        <label className="font-mono text-[9px] tracking-[0.18em] uppercase text-ink-faint">{label}</label>
      )}
      {multiline ? (
        <textarea
          value={value}
          onChange={(e) => onChange(e.target.value)}
          placeholder={placeholder}
          rows={3}
          className="mt-1 w-full px-3 py-2 bg-cream-deep border border-rule rounded-lg font-display text-[14px] focus:outline-none focus:ring-1 focus:ring-amber resize-none"
          style={{ fontVariationSettings: '"opsz" 24' }}
        />
      ) : (
        <input
          type={type}
          value={value}
          onChange={(e) => onChange(e.target.value)}
          placeholder={placeholder}
          inputMode={type === "number" ? "decimal" : undefined}
          className="mt-1 w-full px-3 py-2 bg-cream-deep border border-rule rounded-lg font-display text-[14px] focus:outline-none focus:ring-1 focus:ring-amber"
          style={{ fontVariationSettings: '"opsz" 24' }}
        />
      )}
    </div>
  );
}
