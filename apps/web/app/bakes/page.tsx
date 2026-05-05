"use client";

import { useQuery } from "@tanstack/react-query";
import Link from "next/link";
import { api } from "@/lib/api";
import { SectionLabel } from "@/components/shared/SectionLabel";

const OUTCOME_EMOJI: Record<string, string> = {
  disaster: "💥",
  meh: "😐",
  okay: "👌",
  good: "😊",
  best_yet: "🏆",
};

export default function JournalPage() {
  const { data: bakes, isLoading } = useQuery({
    queryKey: ["bakes"],
    queryFn: () => api.bakes.list(),
  });

  return (
    <div className="px-4 pt-6 max-w-lg mx-auto">
      <h1
        className="font-display font-[350] text-[28px] tracking-[-0.02em]"
        style={{ fontVariationSettings: '"opsz" 144, "SOFT" 80' }}
      >
        Journal
      </h1>

      <SectionLabel>{bakes?.length ?? 0} bakes</SectionLabel>

      {isLoading ? (
        <p className="mt-6 text-center font-mono text-[11px] tracking-[0.14em] uppercase text-ink-faint">
          Loading...
        </p>
      ) : bakes?.length === 0 ? (
        <div className="mt-8 text-center">
          <p className="text-[15px] text-ink-faint" style={{ fontVariationSettings: '"opsz" 24' }}>
            No bakes yet. Start one from a recipe!
          </p>
        </div>
      ) : (
        <div className="mt-4 flex flex-col gap-3">
          {bakes?.map((bake, i) => (
            <Link
              key={bake.id}
              href={`/bakes/${bake.id}`}
              className="block border border-rule rounded-card p-4 bg-paper hover:shadow-card transition-shadow"
              style={{ animationDelay: `${i * 60}ms` }}
            >
              <div className="flex items-start justify-between">
                <div>
                  <h3 className="font-display font-[400] text-[16px] text-ink" style={{ fontVariationSettings: '"opsz" 24' }}>
                    {bake.recipeTitle}
                  </h3>
                  <p className="mt-0.5 font-mono text-[10px] tracking-[0.14em] text-ink-faint">
                    {new Date(bake.startedAt).toLocaleDateString("en-CH", {
                      month: "short",
                      day: "numeric",
                      year: "numeric",
                    })}
                  </p>
                </div>
                <div className="flex items-center gap-2">
                  {bake.outcome && (
                    <span className="text-[16px]">{OUTCOME_EMOJI[bake.outcome] || ""}</span>
                  )}
                  {bake.rating && (
                    <span className="font-mono text-[11px] text-amber">
                      {"★".repeat(bake.rating)}
                      {"☆".repeat(5 - bake.rating)}
                    </span>
                  )}
                </div>
              </div>
              <div className="mt-1">
                <span
                  className={`font-mono text-[9px] tracking-[0.18em] uppercase px-2 py-0.5 rounded-full ${
                    bake.status === "active"
                      ? "bg-amber/10 text-amber"
                      : bake.status === "finished"
                        ? "bg-good/10 text-good"
                        : "bg-ink-faint/10 text-ink-faint"
                  }`}
                >
                  {bake.status}
                </span>
              </div>
            </Link>
          ))}
        </div>
      )}
    </div>
  );
}
