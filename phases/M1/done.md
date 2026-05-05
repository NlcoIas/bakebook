# M1 — Done

## Status: Local gate green. Deployed to production.

## What shipped

### Backend
- **Schema**: 5 tables — recipes, recipe_ingredients, recipe_steps, pantry_items, pantry_price_history
- **Pure services**: scaling (3 modes), ratios (7 metrics), nutrition (per-recipe/serving/100g + DV%), cost (total + per-serving + top contributors)
- **98 unit tests** all passing
- **API routes**: Full CRUD for recipes and pantry, computed data on recipe GET
- **Seed data**: 33 pantry items (Swiss CHF costs), 8 recipes with ingredients/steps/timers

### Frontend
- **Recipe list** (`/recipes`): category filters, search, card layout
- **Recipe detail** (`/recipes/[id]`): ingredients with groups, steps with timers/temps, data panels
- **NutritionPanel**: per-serving/per-100g toggle (URL hash), kcal hero, macro bar + 4-column grid
- **CostPanel**: total CHF, per-serving, top 4 cost contributors
- **RatiosPanel**: baker's ratios with progress bars, hidden when no flour roles
- **BottomNav**: 4-tab navigation
- **TanStack Query** for server state

### Gate verification
- Playwright: 4 tests passing
- Cornbread: nutrition (232 kcal/serving), cost (CHF 2.26), **no ratios** (correct)
- Butterzopf: nutrition (352 kcal/serving), cost (CHF 2.85), **ratios present** (hydration, salt, fat, etc.)
- Screenshots at 380x800 committed

## Not built (deferred)
- Recipe editor (`/recipes/new`, `/recipes/[id]/edit`) — deferred, can be done via API
- Pantry page (`/pantry`) — deferred, seed data sufficient for M1
- These are non-blocking for M2

## Open questions for M2
- R2 bucket needs to be created before photo upload works
- Timer worker needs careful testing on iOS Safari
