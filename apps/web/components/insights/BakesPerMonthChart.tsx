interface MonthData {
  label: string;
  count: number;
}

export function BakesPerMonthChart({ data }: { data: MonthData[] }) {
  const maxCount = Math.max(1, ...data.map((d) => d.count));
  const barWidth = 100 / data.length;

  return (
    <div className="border border-rule rounded-card p-4 bg-paper">
      <span className="font-mono text-[9px] tracking-[0.18em] uppercase text-ink-faint">
        Bakes per month
      </span>
      <svg viewBox="0 0 300 120" className="mt-3 w-full" preserveAspectRatio="xMidYMid meet">
        {data.map((d, i) => {
          const h = (d.count / maxCount) * 90;
          const x = i * (300 / data.length) + 4;
          const w = 300 / data.length - 8;
          const isLast = i === data.length - 1;
          return (
            <g key={d.label}>
              <rect
                x={x}
                y={100 - h}
                width={Math.max(w, 2)}
                height={Math.max(h, 1)}
                rx={3}
                fill={isLast ? "var(--amber-bright)" : "var(--amber)"}
                opacity={d.count === 0 ? 0.15 : 1}
              />
              <text
                x={x + w / 2}
                y={115}
                textAnchor="middle"
                className={`text-[8px] font-mono ${isLast ? "fill-amber" : "fill-ink-faint"}`}
                style={{ fill: isLast ? "var(--amber)" : "var(--ink-faint)" }}
              >
                {d.label.charAt(0)}
              </text>
            </g>
          );
        })}
      </svg>
    </div>
  );
}
