"use client";

import { useQuery } from "@tanstack/react-query";
import Link from "next/link";
import { api } from "@/lib/api";
import { HandRule } from "@/components/shared/HandRule";
import { SectionLabel } from "@/components/shared/SectionLabel";

export default function Home() {
  const { data: recipes } = useQuery({
    queryKey: ["recipes"],
    queryFn: () => api.recipes.list(),
  });

  const { data: bakes } = useQuery({
    queryKey: ["bakes"],
    queryFn: () => api.bakes.list(),
  });

  const activeBake = bakes?.find((b) => b.status === "active");
  const recentRecipes = recipes?.slice(0, 4);

  return (
    <div className="px-4 pt-8 max-w-lg mx-auto">
      {/* Header */}
      <h1
        className="font-display font-[350] text-[36px] tracking-[-0.025em]"
        style={{ fontVariationSettings: '"opsz" 144, "SOFT" 80' }}
      >
        <span className="italic font-[300]">Bake</span>
        <span className="text-amber">book</span>
      </h1>
      <p className="mt-1 font-mono text-[10px] tracking-[0.22em] uppercase text-ink-faint">
        Personal baking companion
      </p>

      <div className="mt-4">
        <HandRule seed={7} />
      </div>

      {/* Active bake */}
      {activeBake && (
        <div className="mt-4">
          <SectionLabel>Active bake</SectionLabel>
          <Link
            href={`/bakes/${activeBake.id}`}
            className="mt-2 block border border-amber rounded-card p-4 bg-paper"
          >
            <div className="flex items-center gap-3">
              <div className="relative">
                <div className="w-3 h-3 rounded-full bg-amber" />
                <div className="absolute inset-0 w-3 h-3 rounded-full bg-amber animate-pulse" />
              </div>
              <div>
                <p className="font-display font-[400] text-[16px] text-ink" style={{ fontVariationSettings: '"opsz" 24' }}>
                  {activeBake.recipeTitle}
                </p>
                <p className="font-mono text-[10px] tracking-[0.14em] text-amber uppercase">
                  In progress
                </p>
              </div>
            </div>
          </Link>
        </div>
      )}

      {/* Recent recipes */}
      {recentRecipes && recentRecipes.length > 0 && (
        <div className="mt-4">
          <SectionLabel>Recent recipes</SectionLabel>
          <div className="mt-2 flex flex-col gap-2">
            {recentRecipes.map((r) => (
              <Link
                key={r.id}
                href={`/recipes/${r.id}`}
                className="flex items-center justify-between py-2.5 border-b border-dashed border-rule/50"
              >
                <span className="font-display text-[14.5px] text-ink" style={{ fontVariationSettings: '"opsz" 24' }}>
                  {r.title}
                </span>
                <span className="font-mono text-[9px] tracking-[0.14em] uppercase text-ink-faint">
                  {r.category}
                </span>
              </Link>
            ))}
          </div>
        </div>
      )}

      {/* Quick actions */}
      <div className="mt-6 flex gap-3">
        <Link
          href="/recipes/new"
          className="flex-1 py-3 text-center font-mono text-[10px] tracking-[0.18em] uppercase bg-amber text-cream rounded-pill font-medium"
        >
          New recipe
        </Link>
        <Link
          href="/recipes"
          className="flex-1 py-3 text-center font-mono text-[10px] tracking-[0.18em] uppercase border border-rule text-ink-faint rounded-pill"
        >
          All recipes
        </Link>
      </div>

      {/* Recent bakes */}
      {bakes && bakes.length > 0 && (
        <div className="mt-4">
          <SectionLabel>Recent bakes</SectionLabel>
          <div className="mt-2 flex flex-col gap-2">
            {bakes.slice(0, 3).map((b) => (
              <Link
                key={b.id}
                href={`/bakes/${b.id}`}
                className="flex items-center justify-between py-2.5 border-b border-dashed border-rule/50"
              >
                <span className="font-display text-[14.5px] text-ink" style={{ fontVariationSettings: '"opsz" 24' }}>
                  {b.recipeTitle}
                </span>
                <span className="font-mono text-[10px] text-amber">
                  {b.rating ? "★".repeat(b.rating) : ""}
                </span>
              </Link>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
