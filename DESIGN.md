# Bakebook — DESIGN.md

The visual contract. `design/v1-screens.html` and `design/v2-data.html` are the *picture*; this file is the *spec*. When in doubt, this file wins. When this file is silent, match the HTML reference at 380 × 800 viewport.

---

## 1. Aesthetic

**Editorial cookbook with a kitchen-mode flip.** Browsing/editing/journaling reads like a well-set cookbook — cream paper, a warm display serif, generous whitespace, hand-drawn rules. The active bake screen flips to espresso-dark with hot amber and a monospace timer because at 5 a.m. you want focus, not paper.

Hard nos: Inter, Roboto, system fonts, Space Grotesk, purple gradients on white, generic AI-mockup look.

---

## 2. Tokens

### 2.1 Cookbook palette (default)

```css
:root {
  --cream: #f4ead4;
  --cream-deep: #ecdfc1;
  --paper: #f8f1dd;
  --ink: #1d1410;
  --ink-soft: #4a3a30;
  --ink-faint: #8a7a6c;
  --amber: #b8501f;
  --amber-bright: #d96826;
  --olive: #6b6939;
  --blush: #d8a892;
  --rule: #b8a98c;
  --good: #4a7d3d;
  --warn: #c08e1f;
}
```

### 2.2 Kitchen-mode palette (active bake only)

```css
.kitchen-mode {
  --espresso: #14100c;
  --espresso-2: #1e1813;
  --cream-dim: #e9dcc1;
  --hot-amber: #ec7a37;
  --hot-amber-glow: rgba(236, 122, 55, 0.18);
  --olive-dim: #9a956a;
}
```

### 2.3 Typography

```css
:root {
  --display: "Fraunces", ui-serif, Georgia, serif;
  --mono: "JetBrains Mono", ui-monospace, monospace;
}
```

Load both from Google Fonts in `app/layout.tsx`:

```tsx
import { Fraunces, JetBrains_Mono } from "next/font/google";
const fraunces = Fraunces({
  subsets: ["latin"],
  axes: ["opsz", "SOFT"],
  display: "swap",
  variable: "--font-display"
});
const jetbrains = JetBrains_Mono({
  subsets: ["latin"],
  display: "swap",
  variable: "--font-mono"
});
```

### 2.4 Type scale & variation rules

| Use | Family | Weight | Size | Letter | Variation |
|---|---|---|---|---|---|
| Hero display | Fraunces | 350 | 32–36px | -0.025em | `opsz 144, SOFT 80` |
| H2 italic accent | Fraunces italic | 300 | inherits | inherits | `opsz 144, SOFT 80` |
| Section title (panel) | Fraunces italic | 400 | 16–18px | -0.005em | `opsz 60` |
| Body | Fraunces | 400 | 14.5–15px, line-height 1.5 | 0 | `opsz 24` |
| Number, large | Fraunces | 350–400 | 24–36px | -0.02em | `opsz 144, SOFT 60` |
| Mono number | JetBrains Mono | 500 | varies | -0.015em | n/a |
| Mono label / caps | JetBrains Mono | 400 | 9–11px | 0.18–0.24em uppercase | n/a |
| Status bar / tiny mono | JetBrains Mono | 600 | 13px | 0 | n/a |

**Rule**: mono is for numbers, labels, and the status bar. Everything else is the serif. No exceptions.

### 2.5 Background grain

Apply once globally as a fixed pseudo-element with `mix-blend-mode: multiply`, opacity 0.5. SVG noise turbulence at `baseFrequency=0.85`. See implementation in `design/v1-screens.html` `body::before`.

### 2.6 Spacing & layout

- Mobile: 16–24 px gutters, design at 375 px width.
- Tap targets ≥ 44 × 44 px.
- Bottom nav 64 px tall, floats with a 16 px gap on each side, `backdrop-filter: blur(20px)`.
- Cards: 14–18 px radius, 1 px border `var(--rule)`.
- Big buttons: 100 px (pill) radius.
- Panels stacked with 12 px gap.

### 2.7 Shadows

Two only:

```css
--shadow-card: 0 1px 0 rgba(255,255,255,.08) inset, 0 30px 60px -20px rgba(48, 32, 18, 0.4), 0 12px 24px -8px rgba(48, 32, 18, 0.25);
--shadow-fab:  0 12px 24px -8px rgba(20, 16, 12, 0.4);
```

---

## 3. Shared components

These live in `apps/web/components/shared/`. Build them in M0 alongside the design tokens, before any feature work.

### 3.1 `<HandRule />`

A single SVG with a wobbly stroke, used as a section divider. Props: `length` (defaults to fill container), `seed` (number, drives wobble path).

```tsx
<svg viewBox="0 0 200 14" preserveAspectRatio="none">
  <path d={wobblyPath(seed)} stroke="var(--rule)" strokeWidth="1" fill="none" strokeLinecap="round"/>
</svg>
```

Generate `wobblyPath(seed)` by sampling 4 control points with seeded jitter. Each `<HandRule>` should look slightly different — that's the point. Use `seed = recipeId.charCodeAt(0)` or similar to keep them stable per content but varied across the page.

### 3.2 `<SectionLabel>`

A mono-caps label with a dotted line filling the rest of the width.

```tsx
<div className="section-label">
  <span>{children}</span>
</div>
```

```css
.section-label {
  margin-top: 18px;
  display: flex; align-items: center; gap: 12px;
  font-family: var(--mono);
  font-size: 10px; letter-spacing: 0.22em; text-transform: uppercase;
  color: var(--ink-faint);
}
.section-label::after {
  content: ""; flex: 1; height: 1px;
  background: repeating-linear-gradient(to right, var(--rule) 0 4px, transparent 4px 8px);
}
```

### 3.3 `<NutritionPanel recipe={...} per="serving"|"100g" />`

Cream paper card. Header: mono "Nutrition" label + a 2-segment toggle between "per slice/serving" and "per 100 g". State lives in URL hash.

Big kcal number in italic Fraunces (36 px). To the right: "of 2,000 daily · 16%" in mono.

Below: 4-color stacked bar (carbs warn-yellow, fat amber, protein olive, fiber ink-faint), heights proportional to gram weights.

Below: 4-column macro grid. Each column: a 8 × 8 px swatch matching the bar, mono-caps name, big italic number with a small "g" unit.

Bottom: dotted divider, then "Contains" mono label and allergen pills (yellow tint, see HTML reference).

If the recipe has any ingredient with `nutrition_warning` flag (no nutrition data found), show a small warning row.

### 3.4 `<CostPanel recipe={...} />`

Cream paper card, two-column. Left: mono "Cost" label, then italic "CHF 2.40" total in big Fraunces, then mono per-serving sub. Right: small breakdown rows (mono label + bold number) — top 4 cost contributors.

### 3.5 `<RatiosPanel recipe={...} />`

Cream paper card. Mono "Baker's ratios" header. Each row: mono-caps label (80 px column), a 4 px progress track showing percentage with a colored fill, mono percentage value.

Colors:
- Hydration: `--amber`
- Hyd + dairy: `--blush`
- Fat: `--olive`
- Sugar: `--warn`
- Salt: `--ink-faint`
- Yeast/leaven: `--good`

If recipe has no flour-roled ingredients → render nothing (panel hidden).

### 3.6 `<ReadyByPanel recipe={...} />`

Espresso-gradient card (the only dark element on cookbook screens — earns attention). Hot-amber "Ready by" header. Two rows: target out-of-oven time (italic Fraunces label, big white mono time). Below: dim divider, then "Start at" with hot-amber bold mono time.

Tap to open a target-time picker. Persist last-used target per recipe in localStorage.

### 3.7 `<TweakBanner tweaks={...} />`

Yellow-ish banner (`#f5e6c4` bg, `#d8b66c` border, 14 px radius). Star icon, "Pending tweak from last bake" mono-caps heading, body in serif. "Apply to v3 →" amber underlined text triggers `POST /recipes/{id}/tweaks/apply`.

### 3.8 `<MeasurementGrid bake={...} editable />`

2-column grid of small cards. Each card: mono-caps label, then a number input that displays as italic Fraunces 24 px when not focused, mono unit suffix.

Computed cards (water loss, oven spring) use a different background tint (linear-gradient cream-deep variant) and italic amber numbers. Read-only.

### 3.9 `<CrumbCrustSlider label="..." min="..." max="..." value={...} />`

White-paper card with a 6 px gradient track (olive → amber), 18 px ink knob with cream border. Labels at the ends in mono.

Rounds to 1–5 internally; visual position is `(value-1)/4`.

### 3.10 `<StatsStrip stats={[{label, value, delta}, ...]} />`

2 × 2 grid of paper cards. Each: mono-caps label, big italic number, optional mono delta with up/down arrow color-coded green/amber.

### 3.11 `<BakesPerMonthChart data={[number, number, ...]} />`

SVG bar chart, 12 bars, no library. Last bar is `var(--amber-bright)`, others `var(--amber)`. Below: 12 single-letter month labels (D J F M A M J J A S O N) in mono. Current month label is amber.

### 3.12 `<TopTweaksList items={[{rank, label, count}, ...]} pattern={"..."} />`

Plain rows: mono "01" rank, serif label with italic amber for the variable part, small mono count. Below the list: optional pattern callout in italic serif body, no border, just dotted divider above.

### 3.13 `<EquipmentLeaderboard items={[{name, avgRating, count}, ...]} />`

Three-column rows separated by dotted dividers. Serif name, amber star rating (filled and dim mixed), mono bake count.

### 3.14 `<CalendarHeatmap data={Array<0|1|2|3|4>} />`

CSS grid, 26 columns × N rows depending on year length. Each cell `aspect-ratio: 1`, `border-radius: 1px`. Five intensity levels:

```css
.hm-cell    { background: var(--cream-deep); }
.hm-cell.l1 { background: #e3c992; }
.hm-cell.l2 { background: #d8a55c; }
.hm-cell.l3 { background: var(--amber); }
.hm-cell.l4 { background: #8a3812; }
```

Below: row with "Jan" / legend / "Dec" labels in mono.

---

## 4. Bottom nav

Four tabs: Home, Recipes, Journal, Insights. Starter and Settings live inside Settings or under Home (decide in M4).

```css
.nav {
  position: absolute;
  bottom: 16px; left: 16px; right: 16px;
  height: 64px;
  background: rgba(255, 248, 230, 0.92);
  backdrop-filter: blur(20px);
  border: 1px solid var(--rule);
  border-radius: 22px;
  display: flex; align-items: center; justify-content: space-around;
  padding: 0 8px;
  z-index: 5;
}
.nav .item { color: var(--ink-faint); }
.nav .item.active { color: var(--amber); }
```

Icons are 22 × 22 px stroked SVG (1.6 stroke), see HTML reference for exact paths. Below each: mono 9 px caps label, 0.18em letter spacing.

Active bake mode hides the nav (full-screen only).

---

## 5. Animation

Restrained. Three approved patterns:

1. **Pulsing dot** on "bake in progress" cards: opacity 1 → 0.3, 1.6s ease infinite.
2. **Stagger reveal** on first paint of any list (recipes, journal, insights panels): each item `animation-delay: calc(var(--i) * 60ms)`, opacity 0 → 1, translateY 8px → 0, 400ms ease-out. Use Motion library for React when available.
3. **Page transitions** between routes: fade only, 200ms. No slides, no flips.

Anything else needs justification.

---

## 6. Photography

Real food photography is the visual centerpiece of the journal. Establish the style early:

- Overhead, natural light.
- Slightly desaturated, warm tones.
- No props, no plated styling, no garnish theater. The bread itself.
- Crumb shots are mandatory for breads — show interior, lit from the side.

For seed recipes, until real photos exist, use the SVG illustration approach from the design HTML. They're good enough placeholders and read as "intentional" rather than "missing."

---

## 7. Accessibility

- All tap targets ≥ 44 × 44 px.
- Color contrast: ink on cream is fine (~14:1). Ink-faint on cream is ~5:1, ok for non-essential mono labels. Don't drop below.
- All interactive elements have visible focus rings (`outline: 2px solid var(--amber); outline-offset: 2px`).
- Decorative SVG (HandRule, illustrations) needs `aria-hidden="true"`.
- Number inputs use `inputmode="decimal"`.
- The active bake screen must respect `prefers-reduced-motion` — disable the pulsing dot, the timer text-shadow glow, and any reveals.

---

## 8. The "is it on-design" checklist

Before declaring any screen done, verify:

- [ ] Fraunces is loaded and rendering with optical sizing (large titles look soft and warm; body looks crisp). If it looks "blocky" the variable axes aren't being applied.
- [ ] JetBrains Mono is rendering for all numbers, labels, and the status bar.
- [ ] No Inter, no Roboto, no system fonts anywhere.
- [ ] Background grain is visible (look closely at any flat cream area).
- [ ] At least one `<HandRule>` per long screen. Two screens shouldn't have identical wobbles — verify the seed varies.
- [ ] Hot amber is only used in kitchen mode. Cookbook mode uses regular amber `#b8501f`.
- [ ] All cards have 1 px `var(--rule)` border, not `0`.
- [ ] Mono labels use uppercase + 0.18em+ letter spacing.
- [ ] Ratios panel renders for breads but not for cornbread / quick breads.
- [ ] At 380 × 800 viewport, the screen matches the corresponding HTML reference within ±5% on critical dimensions (hero photo height, panel padding, font sizes).

---

*End of DESIGN.md. The HTML files in `design/` are the visual ground truth. This file is the contract for tokens, components, and rules.*
