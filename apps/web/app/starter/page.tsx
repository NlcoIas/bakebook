"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useState } from "react";
import { SectionLabel } from "@/components/shared/SectionLabel";
import { HandRule } from "@/components/shared/HandRule";

const API = "/api/v1/starters";

interface Starter {
  id: string;
  name: string;
  hydrationPct: number;
  peakBaseHours: number;
  notes: string | null;
}

interface StarterStatus {
  lastFedAt: string | null;
  hoursSinceFed: number | null;
  estimatedPeakAt: string | null;
}

async function fetchJson<T>(url: string, init?: RequestInit): Promise<T> {
  const res = await fetch(url, { ...init, headers: { "Content-Type": "application/json", ...init?.headers } });
  if (!res.ok) throw new Error(`API ${res.status}`);
  return res.json();
}

function StarterCard({ starter }: { starter: Starter }) {
  const queryClient = useQueryClient();

  const { data: status } = useQuery({
    queryKey: ["starter-status", starter.id],
    queryFn: () => fetchJson<StarterStatus>(`${API}/${starter.id}/status`),
    refetchInterval: 60000,
  });

  const [temp, setTemp] = useState("22");
  const [ratio, setRatio] = useState("1:5:5");

  const feedMutation = useMutation({
    mutationFn: () =>
      fetchJson(`${API}/${starter.id}/feedings`, {
        method: "POST",
        body: JSON.stringify({
          ratio,
          kitchenTempC: Number(temp),
        }),
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["starter-status", starter.id] });
    },
  });

  const isPastPeak = status?.estimatedPeakAt && new Date(status.estimatedPeakAt) < new Date();

  return (
    <div className="border border-rule rounded-card p-4 bg-paper">
      <div className="flex items-start justify-between">
        <h3
          className="font-display font-[400] text-[20px] text-ink"
          style={{ fontVariationSettings: '"opsz" 60' }}
        >
          {starter.name}
        </h3>
        <span className="font-mono text-[10px] tracking-[0.14em] text-ink-faint">
          {starter.hydrationPct}% hydration
        </span>
      </div>

      {status && status.lastFedAt && (
        <div className="mt-3 grid grid-cols-2 gap-3">
          <div>
            <span className="font-mono text-[9px] tracking-[0.18em] uppercase text-ink-faint">
              Last fed
            </span>
            <p className="mt-0.5 font-mono text-[12px] text-ink">
              {new Date(status.lastFedAt).toLocaleString("en-CH", {
                month: "short", day: "numeric", hour: "2-digit", minute: "2-digit",
              })}
            </p>
          </div>
          <div>
            <span className="font-mono text-[9px] tracking-[0.18em] uppercase text-ink-faint">
              Hours since
            </span>
            <p
              className={`mt-0.5 font-display italic font-[350] text-[20px] ${
                isPastPeak ? "text-warn" : "text-good"
              }`}
              style={{ fontVariationSettings: '"opsz" 144, "SOFT" 60' }}
            >
              {status.hoursSinceFed?.toFixed(1)}h
            </p>
          </div>
          {status.estimatedPeakAt && (
            <div className="col-span-2">
              <span className="font-mono text-[9px] tracking-[0.18em] uppercase text-ink-faint">
                Estimated peak
              </span>
              <p className={`mt-0.5 font-mono text-[13px] font-[600] ${isPastPeak ? "text-warn" : "text-amber"}`}>
                {new Date(status.estimatedPeakAt).toLocaleTimeString("en-CH", {
                  hour: "2-digit", minute: "2-digit",
                })}
                {isPastPeak && " (past peak)"}
              </p>
            </div>
          )}
        </div>
      )}

      {!status?.lastFedAt && (
        <p className="mt-2 text-[13px] text-ink-faint" style={{ fontVariationSettings: '"opsz" 24' }}>
          No feedings logged yet.
        </p>
      )}

      <HandRule seed={starter.name.charCodeAt(0)} className="mt-4" />

      <SectionLabel>Log feeding</SectionLabel>
      <div className="mt-2 flex gap-2">
        <div className="flex-1">
          <label className="font-mono text-[9px] tracking-[0.18em] uppercase text-ink-faint">Ratio</label>
          <input
            type="text"
            value={ratio}
            onChange={(e) => setRatio(e.target.value)}
            className="mt-1 w-full px-2 py-1.5 bg-cream-deep border border-rule rounded-lg font-mono text-[13px] focus:outline-none focus:ring-1 focus:ring-amber"
          />
        </div>
        <div className="flex-1">
          <label className="font-mono text-[9px] tracking-[0.18em] uppercase text-ink-faint">Temp (°C)</label>
          <input
            type="number"
            inputMode="decimal"
            value={temp}
            onChange={(e) => setTemp(e.target.value)}
            className="mt-1 w-full px-2 py-1.5 bg-cream-deep border border-rule rounded-lg font-mono text-[13px] focus:outline-none focus:ring-1 focus:ring-amber"
          />
        </div>
      </div>
      <button
        type="button"
        onClick={() => feedMutation.mutate()}
        disabled={feedMutation.isPending}
        className="mt-3 w-full py-2.5 font-mono text-[10px] tracking-[0.18em] uppercase bg-amber text-cream rounded-pill font-medium disabled:opacity-50"
      >
        {feedMutation.isPending ? "Logging..." : "Log feeding"}
      </button>
    </div>
  );
}

export default function StarterPage() {
  const queryClient = useQueryClient();

  const { data: starters, isLoading } = useQuery({
    queryKey: ["starters"],
    queryFn: () => fetchJson<Starter[]>(API),
  });

  const [showCreate, setShowCreate] = useState(false);
  const [name, setName] = useState("");

  const createMutation = useMutation({
    mutationFn: () =>
      fetchJson(API, {
        method: "POST",
        body: JSON.stringify({ name, hydrationPct: 100, peakBaseHours: 6 }),
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["starters"] });
      setShowCreate(false);
      setName("");
    },
  });

  return (
    <div className="px-4 pt-6 max-w-lg mx-auto">
      <h1
        className="font-display font-[350] text-[28px] tracking-[-0.02em]"
        style={{ fontVariationSettings: '"opsz" 144, "SOFT" 80' }}
      >
        Starters
      </h1>

      <SectionLabel>{starters?.length ?? 0} starters</SectionLabel>

      {isLoading ? (
        <p className="mt-6 text-center font-mono text-[11px] tracking-[0.14em] uppercase text-ink-faint">Loading...</p>
      ) : (
        <div className="mt-4 flex flex-col gap-4">
          {starters?.map((s) => <StarterCard key={s.id} starter={s} />)}
        </div>
      )}

      {!showCreate ? (
        <button
          type="button"
          onClick={() => setShowCreate(true)}
          className="mt-4 w-full py-3 font-mono text-[10px] tracking-[0.18em] uppercase border border-rule text-ink-faint rounded-pill hover:border-ink-faint"
        >
          + Add starter
        </button>
      ) : (
        <div className="mt-4 border border-rule rounded-card p-4 bg-paper">
          <input
            type="text"
            value={name}
            onChange={(e) => setName(e.target.value)}
            placeholder="Starter name"
            className="w-full px-3 py-2 bg-cream-deep border border-rule rounded-lg font-display text-[14px] focus:outline-none focus:ring-1 focus:ring-amber"
            style={{ fontVariationSettings: '"opsz" 24' }}
          />
          <div className="mt-2 flex gap-2">
            <button
              type="button"
              onClick={() => setShowCreate(false)}
              className="flex-1 py-2 font-mono text-[10px] tracking-[0.18em] uppercase border border-rule rounded-pill text-ink-faint"
            >
              Cancel
            </button>
            <button
              type="button"
              onClick={() => createMutation.mutate()}
              disabled={!name || createMutation.isPending}
              className="flex-1 py-2 font-mono text-[10px] tracking-[0.18em] uppercase bg-amber text-cream rounded-pill font-medium disabled:opacity-50"
            >
              Create
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
