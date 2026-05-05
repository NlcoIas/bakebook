"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { api } from "@/lib/api";

interface Props {
  recipeId: string;
  versionNumber: number;
}

export function TweakBanner({ recipeId, versionNumber }: Props) {
  const queryClient = useQueryClient();

  const { data: tweaks } = useQuery({
    queryKey: ["pending-tweaks", recipeId],
    queryFn: () => api.recipes.pendingTweaks(recipeId),
  });

  const applyMutation = useMutation({
    mutationFn: () => {
      const ids = tweaks?.map((t) => t.id) ?? [];
      return api.recipes.applyTweaks(recipeId, ids);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["recipe"] });
      queryClient.invalidateQueries({ queryKey: ["recipes"] });
      queryClient.invalidateQueries({ queryKey: ["pending-tweaks"] });
    },
  });

  if (!tweaks || tweaks.length === 0) return null;

  return (
    <div className="border border-[#d8b66c] rounded-[14px] bg-[#f5e6c4] p-4">
      <div className="flex items-start gap-2">
        <span className="text-[16px]">&#9733;</span>
        <div className="flex-1">
          <p className="font-mono text-[9px] tracking-[0.18em] uppercase text-ink-soft font-medium">
            Pending tweak{tweaks.length > 1 ? "s" : ""} from last bake
          </p>
          {tweaks.map((t) => (
            <p
              key={t.id}
              className="mt-1 text-[14px] text-ink"
              style={{ fontVariationSettings: '"opsz" 24' }}
            >
              {t.change}
              {t.reason && (
                <span className="text-ink-faint"> — {t.reason}</span>
              )}
            </p>
          ))}
          <button
            type="button"
            onClick={() => applyMutation.mutate()}
            disabled={applyMutation.isPending}
            className="mt-2 font-mono text-[11px] tracking-[0.1em] text-amber underline"
          >
            {applyMutation.isPending
              ? "Applying..."
              : `Apply to v${versionNumber + 1} \u2192`}
          </button>
        </div>
      </div>
    </div>
  );
}
