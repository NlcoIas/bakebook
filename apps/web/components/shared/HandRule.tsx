"use client";

function wobblyPath(seed: number): string {
  // Generate a hand-drawn line with seeded jitter
  const rng = (s: number) => {
    s = Math.sin(s * 127.1 + seed * 311.7) * 43758.5453;
    return s - Math.floor(s);
  };

  const points = 5;
  const segWidth = 200 / (points - 1);
  let d = `M 0 ${7 + (rng(0) - 0.5) * 4}`;

  for (let i = 1; i < points; i++) {
    const x = i * segWidth;
    const y = 7 + (rng(i) - 0.5) * 5;
    const cpx1 = (i - 0.6) * segWidth;
    const cpy1 = 7 + (rng(i + 10) - 0.5) * 6;
    const cpx2 = (i - 0.3) * segWidth;
    const cpy2 = 7 + (rng(i + 20) - 0.5) * 6;
    d += ` C ${cpx1} ${cpy1}, ${cpx2} ${cpy2}, ${x} ${y}`;
  }

  return d;
}

interface HandRuleProps {
  seed?: number;
  className?: string;
}

export function HandRule({ seed = 42, className }: HandRuleProps) {
  return (
    <svg
      viewBox="0 0 200 14"
      preserveAspectRatio="none"
      className={className}
      style={{ width: "100%", height: "14px" }}
      aria-hidden="true"
    >
      <path
        d={wobblyPath(seed)}
        stroke="var(--rule)"
        strokeWidth="1"
        fill="none"
        strokeLinecap="round"
      />
    </svg>
  );
}
