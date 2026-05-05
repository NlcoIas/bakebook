"use client";

import { useQuery } from "@tanstack/react-query";
import { useState } from "react";
import { SectionLabel } from "@/components/shared/SectionLabel";
import { HandRule } from "@/components/shared/HandRule";
import { StatsStrip } from "@/components/insights/StatsStrip";
import { BakesPerMonthChart } from "@/components/insights/BakesPerMonthChart";
import { CalendarHeatmap } from "@/components/insights/CalendarHeatmap";

const API = "/api/v1/insights";

async function fetchJson<T>(url: string): Promise<T> {
  const res = await fetch(url);
  if (!res.ok) throw new Error(`API ${res.status}`);
  return res.json();
}

const RANGES = ["month", "year", "all"] as const;

export default function InsightsPage() {
  const [range, setRange] = useState<string>("all");

  const { data: summary } = useQuery({
    queryKey: ["insights-summary", range],
    queryFn: () =>
      fetchJson<{
        bakesCount: number;
        avgRating: number | null;
        flourKg: number;
        totalCostChf: number;
      }>(`${API}/summary?range=${range}`),
  });

  const { data: monthData } = useQuery({
    queryKey: ["insights-months"],
    queryFn: () =>
      fetchJson<{ label: string; count: number }[]>(`${API}/bakes-per-month`),
  });

  const { data: topTweaks } = useQuery({
    queryKey: ["insights-tweaks"],
    queryFn: () =>
      fetchJson<{ rank: number; change: string; count: number }[]>(
        `${API}/top-tweaks`,
      ),
  });

  const { data: equipment } = useQuery({
    queryKey: ["insights-equipment"],
    queryFn: () =>
      fetchJson<{ name: string; avgRating: number | null; count: number }[]>(
        `${API}/equipment`,
      ),
  });

  const { data: calendar } = useQuery({
    queryKey: ["insights-calendar"],
    queryFn: () =>
      fetchJson<{ year: number; data: number[] }>(`${API}/calendar`),
  });

  const { data: patterns } = useQuery({
    queryKey: ["insights-patterns"],
    queryFn: () =>
      fetchJson<{ patterns: string[] }>(`${API}/patterns`),
  });

  return (
    <div className="px-4 pt-6 max-w-lg mx-auto">
      <h1
        className="font-display font-[350] text-[28px] tracking-[-0.02em]"
        style={{ fontVariationSettings: '"opsz" 144, "SOFT" 80' }}
      >
        Insights
      </h1>

      {/* Range selector */}
      <div className="mt-4 flex gap-2">
        {RANGES.map((r) => (
          <button
            key={r}
            type="button"
            onClick={() => setRange(r)}
            className={`font-mono text-[10px] tracking-[0.18em] uppercase px-3 py-1.5 rounded-full border transition-colors ${
              range === r
                ? "bg-ink text-cream border-ink"
                : "bg-transparent text-ink-faint border-rule"
            }`}
          >
            {r === "all" ? "All time" : r}
          </button>
        ))}
      </div>

      {/* Stats strip */}
      {summary && (
        <div className="mt-4">
          <StatsStrip
            stats={[
              { label: "Bakes", value: String(summary.bakesCount) },
              {
                label: "Avg rating",
                value: summary.avgRating
                  ? `${summary.avgRating.toFixed(1)} ★`
                  : "—",
              },
              { label: "Flour used", value: `${summary.flourKg} kg` },
              { label: "Total cost", value: `CHF ${summary.totalCostChf.toFixed(0)}` },
            ]}
          />
        </div>
      )}

      <HandRule seed={55} className="mt-4" />

      {/* Bakes per month */}
      {monthData && (
        <div className="mt-4">
          <BakesPerMonthChart data={monthData} />
        </div>
      )}

      {/* Top tweaks */}
      {topTweaks && topTweaks.length > 0 && (
        <div className="mt-4">
          <SectionLabel>Top tweaks</SectionLabel>
          <div className="mt-3 flex flex-col gap-2">
            {topTweaks.map((t) => (
              <div key={t.rank} className="flex items-baseline gap-3">
                <span className="font-mono text-[11px] text-ink-faint w-5">
                  {String(t.rank).padStart(2, "0")}
                </span>
                <span
                  className="flex-1 text-[14px] text-ink"
                  style={{ fontVariationSettings: '"opsz" 24' }}
                >
                  {t.change}
                </span>
                <span className="font-mono text-[10px] text-ink-faint">
                  {t.count}x
                </span>
              </div>
            ))}
          </div>

          {/* Pattern callout */}
          {patterns && patterns.patterns.length > 0 && (
            <div className="mt-3 pt-3 border-t border-dashed border-rule">
              {patterns.patterns.map((p, i) => (
                <p
                  key={i}
                  className="text-[14px] italic text-ink-soft"
                  style={{ fontVariationSettings: '"opsz" 24' }}
                >
                  {p}
                </p>
              ))}
            </div>
          )}
        </div>
      )}

      {/* Equipment */}
      {equipment && equipment.length > 0 && (
        <div className="mt-4">
          <SectionLabel>Equipment</SectionLabel>
          <div className="mt-3 flex flex-col">
            {equipment.map((e, i) => (
              <div
                key={e.name}
                className={`flex items-center py-2 ${
                  i < equipment.length - 1 ? "border-b border-dotted border-rule/50" : ""
                }`}
              >
                <span
                  className="flex-1 text-[14px] text-ink"
                  style={{ fontVariationSettings: '"opsz" 24' }}
                >
                  {e.name}
                </span>
                <span className="font-mono text-[11px] text-amber mr-3">
                  {e.avgRating ? "★".repeat(Math.round(e.avgRating)) + "☆".repeat(5 - Math.round(e.avgRating)) : "—"}
                </span>
                <span className="font-mono text-[10px] text-ink-faint">
                  {e.count}
                </span>
              </div>
            ))}
          </div>
        </div>
      )}

      <HandRule seed={77} className="mt-4" />

      {/* Calendar heatmap */}
      {calendar && (
        <div className="mt-4">
          <CalendarHeatmap data={calendar.data} year={calendar.year} />
        </div>
      )}

      {/* Empty state */}
      {summary && summary.bakesCount === 0 && (
        <div className="mt-8 text-center">
          <p
            className="text-[15px] text-ink-faint"
            style={{ fontVariationSettings: '"opsz" 24' }}
          >
            No bakes yet. Start baking to see your insights!
          </p>
        </div>
      )}
    </div>
  );
}
