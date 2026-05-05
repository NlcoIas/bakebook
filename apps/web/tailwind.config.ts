import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./app/**/*.{ts,tsx}",
    "./components/**/*.{ts,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        cream: "var(--cream)",
        "cream-deep": "var(--cream-deep)",
        paper: "var(--paper)",
        ink: "var(--ink)",
        "ink-soft": "var(--ink-soft)",
        "ink-faint": "var(--ink-faint)",
        amber: "var(--amber)",
        "amber-bright": "var(--amber-bright)",
        olive: "var(--olive)",
        blush: "var(--blush)",
        rule: "var(--rule)",
        good: "var(--good)",
        warn: "var(--warn)",
        espresso: "var(--espresso)",
        "espresso-2": "var(--espresso-2)",
        "cream-dim": "var(--cream-dim)",
        "hot-amber": "var(--hot-amber)",
        "olive-dim": "var(--olive-dim)",
      },
      fontFamily: {
        display: ["var(--font-display)", "ui-serif", "Georgia", "serif"],
        mono: ["var(--font-mono)", "ui-monospace", "monospace"],
      },
      borderRadius: {
        card: "16px",
        pill: "100px",
        nav: "22px",
      },
      boxShadow: {
        card: "0 1px 0 rgba(255,255,255,.08) inset, 0 30px 60px -20px rgba(48, 32, 18, 0.4), 0 12px 24px -8px rgba(48, 32, 18, 0.25)",
        fab: "0 12px 24px -8px rgba(20, 16, 12, 0.4)",
      },
    },
  },
  plugins: [],
};

export default config;
