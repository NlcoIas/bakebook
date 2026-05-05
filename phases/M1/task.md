# Phase M1 — Recipes + Pantry + Nutrition + Ratios + Cost

**Goal**: Full recipe data model, CRUD API, pure computation services (scaling, ratios, nutrition, cost), seed data, and the recipe browse/view/edit frontend with all data panels.

**Estimated**: 2 focused sessions.

**Hard exit gate**: Playwright opens the cornbread recipe at 380x800, screenshots show:
- Macros panel with 4 non-zero macro cards
- Cost panel with non-zero CHF
- Ratios panel renders for bread recipes, hidden for cornbread
- All styled per DESIGN.md

---

## Tasks

### 1. Database schema (migrations)

- [ ] Alembic migration for `recipes` table (§4.1)
- [ ] Alembic migration for `pantry_items` + `pantry_price_history` (§4.2)
- [ ] Alembic migration for `recipe_ingredients` + `recipe_steps` (§4.3)
- [ ] All IDs are UUID v7 (time-ordered). All timestamps `timestamptz`. Soft-delete via `deleted_at`.

### 2. SQLAlchemy models

- [ ] `app/models/recipe.py` — Recipe, RecipeIngredient, RecipeStep
- [ ] `app/models/pantry.py` — PantryItem, PantryPriceHistory
- [ ] `app/models/base.py` — Base class with UUID v7 primary key, timestamps

### 3. API routes — Recipes (§5.1)

- [ ] `GET /recipes` — list with `?category=&q=&include_versions=false`
- [ ] `GET /recipes/{id}` — full recipe with computed nutrition, cost, ratios
- [ ] `GET /recipes/by-slug/{slug}` — latest non-deleted version
- [ ] `POST /recipes` — create
- [ ] `PUT /recipes/{id}` — edit in place (409 if bakes reference)
- [ ] `POST /recipes/{id}/version` — new version
- [ ] `POST /recipes/{id}/fork` — fork
- [ ] `DELETE /recipes/{id}` — soft delete
- [ ] `POST /recipes/{id}/scale` — pure function, scaled ingredient list
- [ ] Pydantic schemas for all request/response models (camelCase JSON, snake_case Python)

### 4. API routes — Pantry (§5.2)

- [ ] `GET /pantry` — list with current cost + nutrition_ref
- [ ] `POST /pantry` — create
- [ ] `PATCH /pantry/{id}` — update (triggers price-history if cost changed)
- [ ] `GET /pantry/{id}/price-history` — time series
- [ ] `GET /nutrition-table` — returns bundled JSON

### 5. Pure computation services with unit tests

- [ ] `services/scaling.py` — 3 modes: multiplier, doughWeight, flourWeight (§6.1)
- [ ] `services/ratios.py` — baker's ratios: hydration, hydration+dairy, salt, sugar, fat, prefermented flour, inoculation (§6.2)
- [ ] `services/nutrition.py` — per-recipe, per-serving, per-100g macros with DV% (§6.3)
- [ ] `services/cost.py` — per-recipe and per-serving cost (§6.4)
- [ ] Full pytest suite for each service

### 6. Nutrition data

- [ ] `scripts/build-nutrition-table.py` — build from USDA FoodData Central data
- [ ] Commit `data/nutrition.json` (~80 baking ingredients, per-100g macros)

### 7. Seed data

- [ ] `seed/pantry.py` — ~30 pantry items with Swiss-realistic cost_per_kg
- [ ] `seed/recipes/` — 8 recipes (cornbread, Butterzopf, no-knead loaf, focaccia, cinnamon rolls, toastbread, bagels, banana bread)
- [ ] Each recipe: 6-14 steps with timers, ingredients with roles, servings, serving_g, equipment
- [ ] Idempotent (ON CONFLICT DO NOTHING)

### 8. Frontend — Recipe list

- [ ] `/recipes` route — grid/list of recipe cards with category filter, search
- [ ] Recipe card: hero photo placeholder, title, category chip, summary
- [ ] Bottom nav component (Home, Recipes, Journal, Insights)
- [ ] Stagger reveal animation on list

### 9. Frontend — Recipe view

- [ ] `/recipes/[id]` route — full recipe display
- [ ] Hero section: title, category, meta (time, difficulty, yields)
- [ ] Ingredients list with group labels and roles
- [ ] Steps list with timer indicators and temperatures
- [ ] `<NutritionPanel>` — per-serving / per-100g toggle (URL hash state), kcal hero, macro bar + grid, allergen pills
- [ ] `<CostPanel>` — total CHF, per-serving, top 4 cost contributors
- [ ] `<RatiosPanel>` — baker's ratios with progress bars (hidden if no flour roles)
- [ ] `<HandRule>` dividers between sections

### 10. Frontend — Recipe editor

- [ ] `/recipes/new` and `/recipes/[id]/edit` routes
- [ ] Form for recipe metadata (title, category, summary, yields, servings, etc.)
- [ ] Ingredient editor: add/remove/reorder, pantry item autocomplete, role picker
- [ ] Step editor: add/remove/reorder, timer/temp fields
- [ ] Save → POST or PUT

### 11. Frontend — Pantry

- [ ] `/pantry` route — list of pantry items with cost and nutrition ref
- [ ] Add/edit pantry item form

### 12. TanStack Query + API client

- [ ] API client module (`lib/api.ts`) with typed fetch helpers
- [ ] TanStack Query hooks for recipes, pantry, nutrition-table

### 13. Verification

- [ ] Playwright test: open cornbread recipe, assert macros panel has 4 non-zero values
- [ ] Playwright test: assert cost panel shows non-zero CHF
- [ ] Playwright test: open a bread recipe, assert ratios panel renders
- [ ] Playwright test: cornbread has NO ratios panel (chemical leavening)
- [ ] Screenshot at 380x800 committed to `test-results/screenshots/M1/`
- [ ] Compare to `design/v1-screens.html` and `design/v2-data.html` per §8 checklist
- [ ] All lint + typecheck + pytest + vitest passing
- [ ] Write `phases/M1/done.md` and `phases/M1/issues.md`

---

## Notes

- Start with the backend (schema + API + services + seed) before touching the frontend. The pure services can be fully tested without any frontend.
- The nutrition.json build script only runs once; output is committed. No external API at runtime.
- shadcn/ui: initialize and install components as needed (Button, Input, Select, etc.)
- The recipe view is the most design-heavy screen. Match the design HTML references closely.
- camelCase in JSON responses, snake_case in Python. Use Pydantic `model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)`.
