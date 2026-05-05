"use client";

import { useQuery } from "@tanstack/react-query";
import { useEffect, useState } from "react";
import { api } from "@/lib/api";

interface Props {
  recipeId: string;
}

function formatTime(iso: string): string {
  const d = new Date(iso);
  return d.toLocaleTimeString("en-CH", { hour: "2-digit", minute: "2-digit" });
}

export function ReadyByPanel({ recipeId }: Props) {
  const [targetTime, setTargetTime] = useState(() => {
    if (typeof window !== "undefined") {
      return localStorage.getItem(`readyby:${recipeId}`) || "18:00";
    }
    return "18:00";
  });

  useEffect(() => {
    localStorage.setItem(`readyby:${recipeId}`, targetTime);
  }, [targetTime, recipeId]);

  // Build ISO target from today's date + target time
  const today = new Date();
  const [h, m] = targetTime.split(":").map(Number);
  const targetDate = new Date(today.getFullYear(), today.getMonth(), today.getDate(), h, m);
  const targetIso = targetDate.toISOString();

  const { data } = useQuery({
    queryKey: ["ready-by", recipeId, targetIso],
    queryFn: () => api.recipes.readyBy(recipeId, targetIso),
    enabled: !!targetTime,
  });

  return (
    <div className="rounded-card p-4 bg-gradient-to-br from-[#14100c] to-[#1e1813] border border-[#3a2e24]">
      <div className="flex items-center justify-between">
        <span className="font-mono text-[9px] tracking-[0.22em] uppercase text-[#ec7a37] font-medium">
          Ready by
        </span>
        <input
          type="time"
          value={targetTime}
          onChange={(e) => setTargetTime(e.target.value)}
          className="bg-transparent font-mono text-[14px] text-[#e9dcc1] focus:outline-none"
        />
      </div>

      <div className="mt-3">
        <span className="font-display italic font-[300] text-[14px] text-[#9a956a]">
          Out of the oven at
        </span>
        <div className="mt-1">
          <span className="font-mono text-[32px] font-[600] text-[#e9dcc1] tracking-[-0.01em]">
            {targetTime}
          </span>
        </div>
      </div>

      {data && (
        <>
          <div className="mt-3 h-px bg-[#3a2e24]" />
          <div className="mt-3">
            <span className="font-display italic font-[300] text-[14px] text-[#9a956a]">
              Start at
            </span>
            <div className="mt-1">
              <span className="font-mono text-[24px] font-[600] text-[#ec7a37] tracking-[-0.01em]">
                {formatTime(data.startAt)}
              </span>
              <span className="ml-2 font-mono text-[11px] text-[#9a956a]">
                ({formatTime(data.rangeStartAt)} – {formatTime(data.rangeEndAt)})
              </span>
            </div>
          </div>
        </>
      )}
    </div>
  );
}
