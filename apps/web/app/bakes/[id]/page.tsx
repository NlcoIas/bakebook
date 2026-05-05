"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useParams, useRouter } from "next/navigation";
import { useState } from "react";
import { api } from "@/lib/api";
import { SectionLabel } from "@/components/shared/SectionLabel";
import { HandRule } from "@/components/shared/HandRule";

const OUTCOMES = ["disaster", "meh", "okay", "good", "best_yet"] as const;
const OUTCOME_LABELS: Record<string, string> = {
  disaster: "Disaster",
  meh: "Meh",
  okay: "Okay",
  good: "Good",
  best_yet: "Best yet",
};

export default function BakeDetailPage() {
  const params = useParams();
  const bakeId = params.id as string;
  const router = useRouter();
  const queryClient = useQueryClient();

  const { data: bake, isLoading } = useQuery({
    queryKey: ["bake", bakeId],
    queryFn: () => api.bakes.get(bakeId),
  });

  const [rating, setRating] = useState<number | null>(null);
  const [outcome, setOutcome] = useState<string | null>(null);
  const [startWeight, setStartWeight] = useState("");
  const [finalWeight, setFinalWeight] = useState("");
  const [riseHeight, setRiseHeight] = useState("");
  const [internalTemp, setInternalTemp] = useState("");
  const [crumbScore, setCrumbScore] = useState(3);
  const [crustScore, setCrustScore] = useState(3);
  const [notes, setNotes] = useState("");
  const [saved, setSaved] = useState(false);

  // Initialize from bake data when loaded
  const initialized = useState(false);
  if (bake && !initialized[0]) {
    if (bake.rating) setRating(bake.rating);
    if (bake.outcome) setOutcome(bake.outcome);
    if (bake.startWeightG) setStartWeight(String(bake.startWeightG));
    if (bake.finalWeightG) setFinalWeight(String(bake.finalWeightG));
    if (bake.riseHeightCm) setRiseHeight(String(bake.riseHeightCm));
    if (bake.internalTempC) setInternalTemp(String(bake.internalTempC));
    if (bake.crumbScore) setCrumbScore(bake.crumbScore);
    if (bake.crustScore) setCrustScore(bake.crustScore);
    if (bake.notes) setNotes(bake.notes);
    if (bake.status === "finished") setSaved(true);
    initialized[1](true);
  }

  const saveMutation = useMutation({
    mutationFn: () =>
      api.bakes.update(bakeId, {
        status: "finished",
        rating,
        outcome,
        startWeightG: startWeight ? Number(startWeight) : null,
        finalWeightG: finalWeight ? Number(finalWeight) : null,
        riseHeightCm: riseHeight ? Number(riseHeight) : null,
        internalTempC: internalTemp ? Number(internalTemp) : null,
        crumbScore,
        crustScore,
        notes: notes || null,
      }),
    onSuccess: () => {
      setSaved(true);
      queryClient.invalidateQueries({ queryKey: ["bake", bakeId] });
      queryClient.invalidateQueries({ queryKey: ["bakes"] });
    },
  });

  const waterLoss =
    startWeight && finalWeight
      ? (((Number(startWeight) - Number(finalWeight)) / Number(startWeight)) * 100).toFixed(1)
      : null;

  if (isLoading || !bake) {
    return (
      <div className="px-4 pt-12 text-center">
        <p className="font-mono text-[11px] tracking-[0.14em] uppercase text-ink-faint">Loading...</p>
      </div>
    );
  }

  return (
    <div className="px-4 pt-6 max-w-lg mx-auto">
      <span className="font-mono text-[9px] tracking-[0.22em] uppercase text-ink-faint">
        Bake reflection
      </span>
      <h1
        className="mt-1 font-display font-[350] text-[28px] tracking-[-0.02em]"
        style={{ fontVariationSettings: '"opsz" 144, "SOFT" 80' }}
      >
        {bake.recipeTitle}
      </h1>

      <p className="mt-1 font-mono text-[10px] tracking-[0.14em] text-ink-faint">
        {new Date(bake.startedAt).toLocaleDateString("en-CH", {
          weekday: "long",
          year: "numeric",
          month: "long",
          day: "numeric",
        })}
      </p>

      <HandRule seed={42} className="mt-4" />

      {/* Rating */}
      <SectionLabel>Rating</SectionLabel>
      <div className="mt-3 flex gap-2 justify-center">
        {[1, 2, 3, 4, 5].map((star) => (
          <button
            key={star}
            type="button"
            onClick={() => !saved && setRating(star)}
            className={`text-[32px] transition-colors ${
              rating && star <= rating ? "text-amber" : "text-rule"
            }`}
          >
            ★
          </button>
        ))}
      </div>

      {/* Outcome */}
      <SectionLabel>Outcome</SectionLabel>
      <div className="mt-3 flex flex-wrap gap-2 justify-center">
        {OUTCOMES.map((o) => (
          <button
            key={o}
            type="button"
            onClick={() => !saved && setOutcome(o)}
            className={`font-mono text-[10px] tracking-[0.14em] uppercase px-3 py-1.5 rounded-full border transition-colors ${
              outcome === o
                ? "bg-ink text-cream border-ink"
                : "bg-transparent text-ink-faint border-rule"
            }`}
          >
            {OUTCOME_LABELS[o]}
          </button>
        ))}
      </div>

      <HandRule seed={17} className="mt-5" />

      {/* Measurements */}
      <SectionLabel>Measurements</SectionLabel>
      <div className="mt-3 grid grid-cols-2 gap-3">
        {[
          { label: "Rise height", unit: "cm", value: riseHeight, set: setRiseHeight },
          { label: "Internal temp", unit: "°C", value: internalTemp, set: setInternalTemp },
          { label: "Weight before", unit: "g", value: startWeight, set: setStartWeight },
          { label: "Weight after", unit: "g", value: finalWeight, set: setFinalWeight },
        ].map((m) => (
          <div key={m.label} className="border border-rule rounded-card p-3 bg-paper">
            <span className="font-mono text-[9px] tracking-[0.18em] uppercase text-ink-faint">
              {m.label}
            </span>
            <div className="mt-1 flex items-baseline gap-1">
              <input
                type="number"
                inputMode="decimal"
                value={m.value}
                onChange={(e) => !saved && m.set(e.target.value)}
                readOnly={saved}
                className="w-full bg-transparent font-display italic font-[350] text-[24px] text-ink focus:outline-none"
                style={{ fontVariationSettings: '"opsz" 144, "SOFT" 60' }}
                placeholder="—"
              />
              <span className="font-mono text-[10px] text-ink-faint">{m.unit}</span>
            </div>
          </div>
        ))}

        {/* Water loss (computed) */}
        {waterLoss && (
          <div className="col-span-2 border border-rule rounded-card p-3 bg-gradient-to-br from-paper to-cream-deep">
            <span className="font-mono text-[9px] tracking-[0.18em] uppercase text-ink-faint">
              Water loss
            </span>
            <div className="mt-1">
              <span
                className="font-display italic font-[350] text-[24px] text-amber"
                style={{ fontVariationSettings: '"opsz" 144, "SOFT" 60' }}
              >
                {waterLoss}
              </span>
              <span className="font-mono text-[10px] text-ink-faint ml-1">%</span>
            </div>
          </div>
        )}
      </div>

      <HandRule seed={31} className="mt-5" />

      {/* Sliders */}
      <SectionLabel>Crumb &amp; Crust</SectionLabel>
      <div className="mt-3 flex flex-col gap-3">
        <div className="border border-rule rounded-card p-4 bg-paper">
          <div className="flex justify-between font-mono text-[9px] tracking-[0.18em] uppercase text-ink-faint">
            <span>Tight</span>
            <span>Open</span>
          </div>
          <input
            type="range"
            min={1}
            max={5}
            value={crumbScore}
            onChange={(e) => !saved && setCrumbScore(Number(e.target.value))}
            className="w-full mt-2 accent-amber"
          />
          <p className="mt-1 text-center font-mono text-[10px] text-ink-faint">
            Crumb: {crumbScore}/5
          </p>
        </div>
        <div className="border border-rule rounded-card p-4 bg-paper">
          <div className="flex justify-between font-mono text-[9px] tracking-[0.18em] uppercase text-ink-faint">
            <span>Pale</span>
            <span>Blistered</span>
          </div>
          <input
            type="range"
            min={1}
            max={5}
            value={crustScore}
            onChange={(e) => !saved && setCrustScore(Number(e.target.value))}
            className="w-full mt-2 accent-amber"
          />
          <p className="mt-1 text-center font-mono text-[10px] text-ink-faint">
            Crust: {crustScore}/5
          </p>
        </div>
      </div>

      {/* Notes */}
      <SectionLabel>Notes</SectionLabel>
      <textarea
        value={notes}
        onChange={(e) => !saved && setNotes(e.target.value)}
        readOnly={saved}
        rows={4}
        className="mt-3 w-full px-3 py-2 bg-paper border border-rule rounded-card font-display text-[14px] text-ink focus:outline-none focus:ring-2 focus:ring-amber/40 resize-none"
        style={{ fontVariationSettings: '"opsz" 24' }}
        placeholder="How did it go?"
      />

      {/* Save */}
      {!saved ? (
        <button
          type="button"
          onClick={() => saveMutation.mutate()}
          disabled={!rating || saveMutation.isPending}
          className="mt-6 w-full py-4 font-mono text-[11px] tracking-[0.18em] uppercase bg-amber text-cream rounded-pill font-medium disabled:opacity-50"
        >
          {saveMutation.isPending ? "Saving..." : "Save & finish"}
        </button>
      ) : (
        <div className="mt-6 text-center">
          <p className="font-mono text-[10px] tracking-[0.14em] uppercase text-good">
            Bake saved
          </p>
          <button
            type="button"
            onClick={() => router.push("/bakes")}
            className="mt-2 font-mono text-[10px] tracking-[0.14em] text-amber underline"
          >
            View journal
          </button>
        </div>
      )}

      {!rating && !saved && (
        <p className="mt-2 text-center font-mono text-[9px] text-ink-faint">
          Rating is required to save
        </p>
      )}
    </div>
  );
}
