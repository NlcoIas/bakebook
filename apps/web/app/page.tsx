import { HandRule } from "@/components/shared/HandRule";
import { SectionLabel } from "@/components/shared/SectionLabel";

export default function Home() {
  return (
    <main className="min-h-screen flex flex-col items-center justify-center px-6">
      <h1
        className="font-display font-[350] text-[36px] tracking-[-0.025em] text-center"
        style={{ fontVariationSettings: '"opsz" 144, "SOFT" 80' }}
      >
        <span className="italic font-[300]">Bake</span>
        <span className="text-amber">book</span>
      </h1>
      <p className="mt-3 font-mono text-[10px] tracking-[0.22em] uppercase text-ink-faint">
        Personal baking companion
      </p>
      <div className="w-48 mt-5">
        <HandRule seed={7} />
      </div>
      <div className="w-64 mt-8">
        <SectionLabel>Coming soon</SectionLabel>
      </div>
    </main>
  );
}
