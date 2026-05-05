# M1 Issues

## 1. Nutrition service float/Decimal type mismatch
**Problem**: nutrition.json values are floats (from JSON parsing), but the nutrition service uses Decimal arithmetic. Multiplication fails: `float * Decimal`.
**Fix**: Convert JSON float values to Decimal via `Decimal(str(v))` in the table lookup function.
**Commit**: 7f08089

## 2. BakerRatios field names mismatch
**Problem**: Route code referenced `ratios.salt` but the dataclass field is `salt_pct`.
**Fix**: Updated route to use correct field names: `salt_pct`, `sugar_pct`, `fat_pct`, `prefermented_flour_pct`.
**Commit**: 7f08089

## 3. Recipe list stagger animation hides cards in screenshot
**Problem**: The `animate-in` CSS animation starts at `opacity: 0` with staggered delays. Playwright screenshot may capture before all cards animate in.
**Impact**: Visual only — test counts 8 cards correctly. Will address with a small wait or removing animation for screenshots.

## 4. Port 8003 leftover process
**Problem**: Previous uvicorn process from testing didn't get cleaned up, blocking port 8003.
**Fix**: Kill orphaned process before starting new one.
