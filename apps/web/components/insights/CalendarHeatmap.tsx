const COLORS = [
  "var(--cream-deep)",
  "#e3c992",
  "#d8a55c",
  "var(--amber)",
  "#8a3812",
];

export function CalendarHeatmap({ data, year }: { data: number[]; year: number }) {
  const cols = 53;
  const cellSize = 10;
  const gap = 2;

  return (
    <div className="border border-rule rounded-card p-4 bg-paper">
      <span className="font-mono text-[9px] tracking-[0.18em] uppercase text-ink-faint">
        {year} baking calendar
      </span>
      <div className="mt-3 overflow-x-auto">
        <svg
          width={cols * (cellSize + gap)}
          height={7 * (cellSize + gap)}
          className="block"
        >
          {data.map((level, i) => {
            const week = Math.floor(i / 7);
            const day = i % 7;
            return (
              <rect
                key={i}
                x={week * (cellSize + gap)}
                y={day * (cellSize + gap)}
                width={cellSize}
                height={cellSize}
                rx={1}
                fill={COLORS[level] || COLORS[0]}
              />
            );
          })}
        </svg>
      </div>
      <div className="mt-2 flex justify-between font-mono text-[8px] text-ink-faint">
        <span>Jan</span>
        <div className="flex gap-1 items-center">
          <span>Less</span>
          {COLORS.map((c, i) => (
            <span
              key={i}
              className="w-2 h-2 rounded-sm inline-block"
              style={{ backgroundColor: c }}
            />
          ))}
          <span>More</span>
        </div>
        <span>Dec</span>
      </div>
    </div>
  );
}
