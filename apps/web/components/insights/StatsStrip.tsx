interface Stat {
  label: string;
  value: string;
}

export function StatsStrip({ stats }: { stats: Stat[] }) {
  return (
    <div className="grid grid-cols-2 gap-3">
      {stats.map((s) => (
        <div key={s.label} className="border border-rule rounded-card p-3 bg-paper">
          <span className="font-mono text-[9px] tracking-[0.18em] uppercase text-ink-faint">
            {s.label}
          </span>
          <p
            className="mt-1 font-display italic font-[350] text-[24px] text-ink"
            style={{ fontVariationSettings: '"opsz" 144, "SOFT" 60' }}
          >
            {s.value}
          </p>
        </div>
      ))}
    </div>
  );
}
