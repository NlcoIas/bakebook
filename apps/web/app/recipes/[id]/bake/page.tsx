"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useParams, useRouter } from "next/navigation";
import { useCallback, useEffect, useState } from "react";
import { api, type Recipe, type BakeDetail } from "@/lib/api";
import { useTimer, formatTimer } from "@/lib/timer";

function MidBakeActions({ bakeId, stepOrd }: { bakeId: string; stepOrd: number }) {
  const [showTweak, setShowTweak] = useState(false);
  const [tweakText, setTweakText] = useState("");
  const [applyNext, setApplyNext] = useState(false);
  const queryClient = useQueryClient();

  const tweakMutation = useMutation({
    mutationFn: () => api.bakes.addTweak(bakeId, { change: tweakText, applyNextTime: applyNext }),
    onSuccess: () => {
      setShowTweak(false);
      setTweakText("");
      setApplyNext(false);
    },
  });

  const photoMutation = useMutation({
    mutationFn: async (file: File) => {
      const upload = await api.bakes.requestPhotoUpload(bakeId);
      if (!upload.presignedUrl.startsWith("file://")) {
        await fetch(upload.presignedUrl, { method: "PUT", body: file, headers: { "Content-Type": file.type } });
      }
      await api.bakes.confirmPhoto(bakeId, upload.r2Key, "process", stepOrd);
    },
  });

  return (
    <>
      <div className="px-5 flex gap-2 justify-center">
        <label className="px-4 py-2 font-mono text-[9px] tracking-[0.18em] uppercase border border-[#3a2e24] rounded-pill text-[#9a956a] cursor-pointer">
          📷 Photo
          <input
            type="file"
            accept="image/*"
            capture="environment"
            className="hidden"
            onChange={(e) => {
              const file = e.target.files?.[0];
              if (file) photoMutation.mutate(file);
            }}
          />
        </label>
        <button
          type="button"
          onClick={() => setShowTweak(true)}
          className="px-4 py-2 font-mono text-[9px] tracking-[0.18em] uppercase border border-[#3a2e24] rounded-pill text-[#9a956a]"
        >
          ✏️ Tweak
        </button>
      </div>

      {showTweak && (
        <div className="fixed inset-0 bg-[#14100c]/90 flex items-center justify-center z-50 p-6">
          <div className="bg-[#1e1813] rounded-card p-5 w-full max-w-sm border border-[#3a2e24]">
            <p className="font-display italic text-[16px] text-[#e9dcc1]" style={{ fontVariationSettings: '"opsz" 60' }}>
              Log a tweak
            </p>
            <textarea
              value={tweakText}
              onChange={(e) => setTweakText(e.target.value)}
              placeholder="e.g. +10 g water, dough was tight"
              rows={3}
              className="mt-3 w-full px-3 py-2 bg-[#14100c] border border-[#3a2e24] rounded-lg text-[#e9dcc1] font-display text-[14px] focus:outline-none focus:border-[#ec7a37] resize-none"
              style={{ fontVariationSettings: '"opsz" 24' }}
            />
            <label className="mt-2 flex items-center gap-2 cursor-pointer">
              <input
                type="checkbox"
                checked={applyNext}
                onChange={(e) => setApplyNext(e.target.checked)}
                className="accent-[#ec7a37]"
              />
              <span className="font-mono text-[10px] text-[#9a956a]">Apply to next version</span>
            </label>
            <div className="mt-4 flex gap-2">
              <button
                type="button"
                onClick={() => setShowTweak(false)}
                className="flex-1 py-2.5 font-mono text-[10px] tracking-[0.18em] uppercase border border-[#3a2e24] rounded-pill text-[#8a7a6c]"
              >
                Cancel
              </button>
              <button
                type="button"
                onClick={() => tweakMutation.mutate()}
                disabled={!tweakText || tweakMutation.isPending}
                className="flex-1 py-2.5 font-mono text-[10px] tracking-[0.18em] uppercase bg-[#ec7a37] text-[#14100c] rounded-pill font-medium disabled:opacity-50"
              >
                Save
              </button>
            </div>
          </div>
        </div>
      )}
    </>
  );
}

function PreBakeModal({
  onStart,
  onSkip,
}: {
  onStart: (ctx: { kitchenTempC?: number; kitchenHumidity?: number; flourBrand?: string }) => void;
  onSkip: () => void;
}) {
  const [temp, setTemp] = useState("");
  const [humidity, setHumidity] = useState("");
  const [brand, setBrand] = useState("");

  return (
    <div className="fixed inset-0 bg-[#14100c]/80 flex items-center justify-center z-50 p-6">
      <div className="bg-[#1e1813] rounded-card p-6 w-full max-w-sm border border-[#3a2e24]">
        <p className="font-display italic text-[18px] text-[#e9dcc1]" style={{ fontVariationSettings: '"opsz" 60' }}>
          Quick context
        </p>
        <p className="mt-1 font-mono text-[9px] tracking-[0.18em] uppercase text-[#8a7a6c]">
          Skip if you don&apos;t care
        </p>

        <div className="mt-4 flex flex-col gap-3">
          <div>
            <label className="font-mono text-[9px] tracking-[0.18em] uppercase text-[#8a7a6c]">Kitchen temp (°C)</label>
            <input
              type="number"
              inputMode="decimal"
              value={temp}
              onChange={(e) => setTemp(e.target.value)}
              className="mt-1 w-full px-3 py-2 bg-[#14100c] border border-[#3a2e24] rounded-lg text-[#e9dcc1] font-mono text-[14px] focus:outline-none focus:border-[#ec7a37]"
            />
          </div>
          <div>
            <label className="font-mono text-[9px] tracking-[0.18em] uppercase text-[#8a7a6c]">Humidity (%)</label>
            <input
              type="number"
              inputMode="decimal"
              value={humidity}
              onChange={(e) => setHumidity(e.target.value)}
              className="mt-1 w-full px-3 py-2 bg-[#14100c] border border-[#3a2e24] rounded-lg text-[#e9dcc1] font-mono text-[14px] focus:outline-none focus:border-[#ec7a37]"
            />
          </div>
          <div>
            <label className="font-mono text-[9px] tracking-[0.18em] uppercase text-[#8a7a6c]">Flour brand</label>
            <input
              type="text"
              value={brand}
              onChange={(e) => setBrand(e.target.value)}
              className="mt-1 w-full px-3 py-2 bg-[#14100c] border border-[#3a2e24] rounded-lg text-[#e9dcc1] font-display text-[14px] focus:outline-none focus:border-[#ec7a37]"
              style={{ fontVariationSettings: '"opsz" 24' }}
            />
          </div>
        </div>

        <div className="mt-5 flex gap-3">
          <button
            type="button"
            onClick={onSkip}
            className="flex-1 py-3 font-mono text-[10px] tracking-[0.18em] uppercase text-[#8a7a6c] border border-[#3a2e24] rounded-pill"
          >
            Skip
          </button>
          <button
            type="button"
            onClick={() =>
              onStart({
                kitchenTempC: temp ? Number(temp) : undefined,
                kitchenHumidity: humidity ? Number(humidity) : undefined,
                flourBrand: brand || undefined,
              })
            }
            className="flex-1 py-3 font-mono text-[10px] tracking-[0.18em] uppercase text-[#14100c] bg-[#ec7a37] rounded-pill font-medium"
          >
            Start bake
          </button>
        </div>
      </div>
    </div>
  );
}

function TimerDisplay({ bakeId, stepOrd, timerSeconds }: { bakeId: string; stepOrd: number; timerSeconds: number | null }) {
  const { remaining, isRunning, isDone, start, reset } = useTimer(bakeId, stepOrd, timerSeconds);

  if (!timerSeconds) return null;

  return (
    <div className="mt-4">
      <div className="text-center">
        <span
          className={`font-mono text-[48px] font-[600] tracking-[-0.015em] ${isDone ? "text-[#4a7d3d]" : "text-[#ec7a37]"}`}
          style={isRunning && !isDone ? { textShadow: "0 0 20px rgba(236,122,55,0.3)" } : {}}
        >
          {remaining != null ? formatTimer(remaining) : formatTimer(timerSeconds)}
        </span>
      </div>
      <div className="mt-2 flex justify-center gap-3">
        {!isRunning && !isDone && (
          <button
            type="button"
            onClick={start}
            className="px-6 py-2 font-mono text-[10px] tracking-[0.18em] uppercase bg-[#ec7a37] text-[#14100c] rounded-pill font-medium"
          >
            Start timer
          </button>
        )}
        {isDone && (
          <button
            type="button"
            onClick={reset}
            className="px-6 py-2 font-mono text-[10px] tracking-[0.18em] uppercase border border-[#3a2e24] text-[#8a7a6c] rounded-pill"
          >
            Reset
          </button>
        )}
      </div>
    </div>
  );
}

function ActiveBakeView({ recipe, bake }: { recipe: Recipe; bake: BakeDetail }) {
  const router = useRouter();
  const queryClient = useQueryClient();
  const [currentStep, setCurrentStep] = useState(bake.currentStep);
  const step = recipe.steps[currentStep];

  const updateMutation = useMutation({
    mutationFn: (data: Record<string, unknown>) => api.bakes.update(bake.id, data),
  });

  const goToStep = useCallback(
    (idx: number) => {
      setCurrentStep(idx);
      updateMutation.mutate({ currentStep: idx });
    },
    [updateMutation],
  );

  const finishBake = useCallback(() => {
    updateMutation.mutate({ status: "finished" }, {
      onSuccess: () => {
        queryClient.invalidateQueries({ queryKey: ["bake"] });
        router.push(`/bakes/${bake.id}`);
      },
    });
  }, [updateMutation, queryClient, router, bake.id]);

  // Wake Lock
  useEffect(() => {
    let wakeLock: WakeLockSentinel | null = null;
    const acquire = async () => {
      try {
        if ("wakeLock" in navigator) {
          wakeLock = await navigator.wakeLock.request("screen");
        }
      } catch {
        // Browser may deny
      }
    };
    acquire();

    const handleVisibility = () => {
      if (document.visibilityState === "visible") acquire();
    };
    document.addEventListener("visibilitychange", handleVisibility);

    return () => {
      wakeLock?.release();
      document.removeEventListener("visibilitychange", handleVisibility);
    };
  }, []);

  // Request notification permission
  useEffect(() => {
    if ("Notification" in window && Notification.permission === "default") {
      Notification.requestPermission();
    }
  }, []);

  if (!step) {
    return (
      <div className="kitchen-mode min-h-screen bg-[#14100c] flex flex-col items-center justify-center p-6">
        <p className="font-display italic text-[24px] text-[#e9dcc1]" style={{ fontVariationSettings: '"opsz" 144, "SOFT" 80' }}>
          All steps complete!
        </p>
        <button
          type="button"
          onClick={finishBake}
          className="mt-6 px-8 py-4 font-mono text-[11px] tracking-[0.18em] uppercase bg-[#ec7a37] text-[#14100c] rounded-pill font-medium"
        >
          Finish bake
        </button>
      </div>
    );
  }

  return (
    <div className="kitchen-mode min-h-screen bg-[#14100c] flex flex-col">
      {/* Header */}
      <div className="px-5 pt-6 pb-3 flex items-center justify-between">
        <span className="font-mono text-[9px] tracking-[0.22em] uppercase text-[#8a7a6c]">
          {recipe.title}
        </span>
        <span className="font-mono text-[11px] font-[600] text-[#9a956a]">
          {currentStep + 1} / {recipe.steps.length}
        </span>
      </div>

      {/* Step progress bar */}
      <div className="px-5 flex gap-1">
        {recipe.steps.map((_, i) => (
          <div
            key={i}
            className={`h-1 flex-1 rounded-full ${i <= currentStep ? "bg-[#ec7a37]" : "bg-[#3a2e24]"}`}
          />
        ))}
      </div>

      {/* Step content */}
      <div className="flex-1 px-5 pt-8 pb-6 flex flex-col">
        <h2
          className="font-display font-[400] text-[24px] text-[#e9dcc1] leading-tight"
          style={{ fontVariationSettings: '"opsz" 144, "SOFT" 60' }}
        >
          {step.title}
        </h2>

        <p
          className="mt-4 text-[15px] text-[#9a956a] leading-relaxed flex-1"
          style={{ fontVariationSettings: '"opsz" 24' }}
        >
          {step.body}
        </p>

        {step.targetTempC && (
          <div className="mt-3 flex items-center gap-2">
            <span className="font-mono text-[11px] text-[#ec7a37]">
              {step.targetTempC}°C
            </span>
            {step.tempKind && (
              <span className="font-mono text-[9px] tracking-[0.14em] uppercase text-[#8a7a6c]">
                {step.tempKind}
              </span>
            )}
          </div>
        )}

        <TimerDisplay
          bakeId={bake.id}
          stepOrd={step.ord}
          timerSeconds={step.timerSeconds}
        />
      </div>

      {/* Mid-bake actions */}
      <MidBakeActions bakeId={bake.id} stepOrd={step.ord} />

      {/* Navigation */}
      <div className="px-5 pb-8 flex gap-3">
        <button
          type="button"
          onClick={() => currentStep > 0 && goToStep(currentStep - 1)}
          disabled={currentStep === 0}
          className="flex-1 py-4 font-mono text-[10px] tracking-[0.18em] uppercase border border-[#3a2e24] rounded-pill text-[#8a7a6c] disabled:opacity-30"
        >
          Back
        </button>
        {currentStep < recipe.steps.length - 1 ? (
          <button
            type="button"
            onClick={() => goToStep(currentStep + 1)}
            className="flex-1 py-4 font-mono text-[10px] tracking-[0.18em] uppercase bg-[#ec7a37] text-[#14100c] rounded-pill font-medium"
          >
            Next step
          </button>
        ) : (
          <button
            type="button"
            onClick={finishBake}
            className="flex-1 py-4 font-mono text-[10px] tracking-[0.18em] uppercase bg-[#4a7d3d] text-[#e9dcc1] rounded-pill font-medium"
          >
            Finish bake
          </button>
        )}
      </div>
    </div>
  );
}

export default function BakePage() {
  const params = useParams();
  const recipeId = params.id as string;
  const router = useRouter();
  const [showModal, setShowModal] = useState(true);
  const [bake, setBake] = useState<BakeDetail | null>(null);

  const { data: recipe, isLoading: recipeLoading } = useQuery({
    queryKey: ["recipe", recipeId],
    queryFn: () => api.recipes.get(recipeId),
  });

  const startMutation = useMutation({
    mutationFn: (ctx: { kitchenTempC?: number; kitchenHumidity?: number; flourBrand?: string }) =>
      api.bakes.start({ recipeId, ...ctx }),
    onSuccess: (data) => {
      setBake(data);
      setShowModal(false);
    },
  });

  // Hide bottom nav in bake mode
  useEffect(() => {
    const nav = document.querySelector("nav");
    if (nav) nav.style.display = "none";
    const wrapper = document.querySelector(".pb-24");
    if (wrapper) (wrapper as HTMLElement).style.paddingBottom = "0";
    return () => {
      if (nav) nav.style.display = "";
      if (wrapper) (wrapper as HTMLElement).style.paddingBottom = "";
    };
  }, []);

  if (recipeLoading || !recipe) {
    return (
      <div className="min-h-screen bg-[#14100c] flex items-center justify-center">
        <p className="font-mono text-[11px] tracking-[0.14em] uppercase text-[#8a7a6c]">
          Loading...
        </p>
      </div>
    );
  }

  if (showModal && !bake) {
    return (
      <PreBakeModal
        onStart={(ctx) => startMutation.mutate(ctx)}
        onSkip={() => startMutation.mutate({})}
      />
    );
  }

  if (!bake) return null;

  return <ActiveBakeView recipe={recipe} bake={bake} />;
}
