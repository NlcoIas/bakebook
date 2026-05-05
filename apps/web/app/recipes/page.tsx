"use client";

import { useQuery } from "@tanstack/react-query";
import Link from "next/link";
import { useState } from "react";
import { api, type RecipeListItem } from "@/lib/api";
import { SectionLabel } from "@/components/shared/SectionLabel";

const CATEGORIES = [
  { value: "", label: "All" },
  { value: "bread", label: "Bread" },
  { value: "sweet", label: "Sweet" },
  { value: "quick", label: "Quick" },
  { value: "pizza", label: "Pizza" },
];

function RecipeCard({ recipe }: { recipe: RecipeListItem }) {
  const categoryColors: Record<string, string> = {
    bread: "bg-amber/10 text-amber",
    sweet: "bg-blush/20 text-ink-soft",
    quick: "bg-olive/10 text-olive",
    pizza: "bg-warn/10 text-warn",
    other: "bg-ink-faint/10 text-ink-faint",
  };

  return (
    <Link
      href={`/recipes/${recipe.id}`}
      className="block border border-rule rounded-card p-4 hover:shadow-card transition-shadow bg-paper"
    >
      <div className="flex items-start justify-between gap-2">
        <h3
          className="font-display font-[400] text-[17px] text-ink leading-tight"
          style={{ fontVariationSettings: '"opsz" 24' }}
        >
          {recipe.title}
        </h3>
        <span
          className={`font-mono text-[9px] tracking-[0.18em] uppercase px-2 py-0.5 rounded-full whitespace-nowrap ${categoryColors[recipe.category] || categoryColors.other}`}
        >
          {recipe.category}
        </span>
      </div>
      {recipe.summary && (
        <p className="mt-2 text-[13px] text-ink-faint leading-relaxed line-clamp-2">
          {recipe.summary}
        </p>
      )}
      <div className="mt-3 flex gap-4 font-mono text-[10px] tracking-[0.14em] uppercase text-ink-faint">
        {recipe.totalTimeMin && <span>{recipe.totalTimeMin} min</span>}
        {recipe.difficulty && <span>{"●".repeat(recipe.difficulty)}{"○".repeat(5 - recipe.difficulty)}</span>}
        {recipe.yields && <span>{recipe.yields}</span>}
      </div>
    </Link>
  );
}

export default function RecipesPage() {
  const [category, setCategory] = useState("");
  const [search, setSearch] = useState("");

  const { data: recipes, isLoading } = useQuery({
    queryKey: ["recipes", category, search],
    queryFn: () => api.recipes.list({ category: category || undefined, q: search || undefined }),
  });

  return (
    <div className="px-4 pt-6 max-w-lg mx-auto">
      <h1
        className="font-display font-[350] text-[28px] tracking-[-0.02em]"
        style={{ fontVariationSettings: '"opsz" 144, "SOFT" 80' }}
      >
        Recipes
      </h1>

      <div className="mt-3">
        <Link
          href="/recipes/new"
          className="inline-block font-mono text-[10px] tracking-[0.18em] uppercase px-4 py-2 bg-amber text-cream rounded-pill font-medium"
        >
          + New recipe
        </Link>
      </div>

      <div className="mt-4 flex gap-2 overflow-x-auto pb-1">
        {CATEGORIES.map((cat) => (
          <button
            key={cat.value}
            type="button"
            onClick={() => setCategory(cat.value)}
            className={`font-mono text-[10px] tracking-[0.18em] uppercase px-3 py-1.5 rounded-full border whitespace-nowrap transition-colors ${
              category === cat.value
                ? "bg-ink text-cream border-ink"
                : "bg-transparent text-ink-faint border-rule hover:border-ink-faint"
            }`}
          >
            {cat.label}
          </button>
        ))}
      </div>

      <input
        type="search"
        placeholder="Search recipes..."
        value={search}
        onChange={(e) => setSearch(e.target.value)}
        className="mt-3 w-full px-3 py-2 bg-cream-deep border border-rule rounded-lg font-display text-[14px] text-ink placeholder:text-ink-faint focus:outline-none focus:ring-2 focus:ring-amber/40"
        style={{ fontVariationSettings: '"opsz" 24' }}
      />

      <SectionLabel>{recipes?.length ?? 0} recipes</SectionLabel>

      {isLoading ? (
        <p className="mt-6 text-center text-ink-faint font-mono text-[11px] tracking-[0.14em] uppercase">
          Loading...
        </p>
      ) : (
        <div className="mt-4 flex flex-col gap-3">
          {recipes?.map((recipe, i) => (
            <div
              key={recipe.id}
              style={{ animationDelay: `${i * 60}ms` }}
              className="animate-in fade-in slide-in-from-bottom-1"
            >
              <RecipeCard recipe={recipe} />
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
