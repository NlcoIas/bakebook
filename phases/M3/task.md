# Phase M3 — Versioning + Tweaks + Scaling + Ready-by

**Goal**: Recipe versioning via tweaks, scaling UI, ready-by time calculation, allergen badges.

**Estimated**: 1 focused session.

**Hard exit gate**: Bake focaccia, log "+15 g water" tweak with apply_next_time, apply to v2, verify v2 ingredient list shows the change. Set ready-by to 18:00, verify computed start time.

---

## Tasks

### 1. Ready-by service (`schedule.py`)
- [ ] Pure computation: critical path from steps with timer_seconds, min_seconds, max_seconds
- [ ] Handle parallelizable_with
- [ ] Return {startAt, expectedEnd, rangeStartAt, rangeEndAt}
- [ ] Unit tests

### 2. Tweak application logic
- [ ] Parse tweak change strings (e.g. "+10 g water" → find ingredient by name/role, add 10 to grams)
- [ ] `POST /recipes/{recipeId}/tweaks/apply` — create new version with tweaks applied
- [ ] Mark applied tweaks as resolved

### 3. API endpoints
- [ ] `GET /recipes/{id}/pending-tweaks` — unresolved apply_next_time tweaks
- [ ] `GET /recipes/{id}/ready-by?target=ISO8601` — ready-by calculation
- [ ] `GET /recipes/{id}/bakes` — bake history for a recipe
- [ ] Allergen computation on recipe GET (gluten, dairy, egg)

### 4. Frontend — recipe view enhancements
- [ ] `<TweakBanner>` — pending tweak banner with "Apply to v{n}" action
- [ ] `<ReadyByPanel>` — espresso-gradient card with target time picker
- [ ] Scale UI — slider/input for multiplier or target dough weight
- [ ] Allergen badges on recipe view
- [ ] Version indicator showing lineage

### 5. Verification
- [ ] Playwright test: apply tweak creates new version with updated ingredient
- [ ] Playwright test: ready-by panel shows computed start time
- [ ] Screenshots committed
- [ ] Deploy and verify

---
