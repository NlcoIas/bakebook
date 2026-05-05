# M5 — Done

## Status: Gate green. Deployed to production.

## What shipped

### Backend
- **6 insights endpoints**: summary, bakes-per-month, top-tweaks, equipment, calendar, patterns
- **patterns.py**: 5 hand-coded rules:
  1. Adding water repeatedly → raise hydration
  2. Underbaked outcomes with low internal temp
  3. Reducing bake time frequently
  4. Adding salt repeatedly
  5. Consistently low ratings on a recipe

### Frontend
- **Range selector**: Month / Year / All time chips
- **StatsStrip**: 2x2 grid (bakes count, avg rating, flour kg, total cost)
- **BakesPerMonthChart**: SVG bar chart, last bar in amber-bright
- **Top tweaks**: ranked list with pattern callout below
- **Equipment leaderboard**: name, star rating, bake count
- **CalendarHeatmap**: GitHub-style SVG grid with 5 intensity levels

### Verification
- 8 Playwright tests passing (all phases)
- 120 backend tests passing
- All pages return 200 on production
- Insights summary returns data (0 bakes — will populate with real baking)
