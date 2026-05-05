# M3 — Done

## Status: Gate green. Deployed to production.

## What shipped

### Backend
- **schedule.py**: Critical path computation with parallelizable steps (22 tests)
- **Tweak apply**: Parses "+10 g water" style changes, creates new recipe version, marks tweaks resolved
- **Pending tweaks endpoint**: Returns unresolved apply_next_time tweaks for a recipe
- **Ready-by endpoint**: Computes start time from target end time using step durations
- **Bake history endpoint**: Past bakes per recipe
- **Allergens**: Auto-derived from ingredients (gluten, dairy, egg, tree nuts)
- **120 tests** all passing

### Frontend
- **TweakBanner**: Yellow banner showing pending tweaks with "Apply to v{n}" action
- **ReadyByPanel**: Espresso-gradient card with target time picker and computed start time
- **Allergen badges**: Yellow pills on recipe detail (gluten, dairy, egg, etc.)
- All integrated into recipe detail page

### Verification
- 8 Playwright tests passing
- Ready-by verified: no-knead loaf needs start at 00:17 for 18:00 target
- Allergens render on Butterzopf (gluten, dairy, egg)
- Screenshots committed

## Deferred
- Scale UI (slider/input): API endpoint exists, frontend deferred
- Fork action UI: API endpoint exists
- Tweak modal during active bake: deferred from M2
