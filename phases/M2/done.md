# M2 — Done

## Status: Gate green. Deployed to production.

## What shipped

### Backend
- **Schema**: bakes, bake_photos, bake_tweaks tables with Alembic migration
- **R2 service**: presigned PUT/GET URLs, local dev fallback, delete support
- **Bake API**: start, get, update, list (journal feed), photo upload/confirm, tweak logging
- **Computed fields**: waterLossPct derived on GET

### Frontend — Active Bake (Kitchen Mode)
- Full-screen espresso dark palette, no site chrome
- Pre-bake context modal (kitchen temp, humidity, flour brand)
- Step-by-step navigation with progress bar
- Timer: Web Worker tick loop (250ms), IndexedDB persistence, wake lock
- Timer recomputes from epoch target on visibility change (backgrounding resilience)
- Notification with vibration pattern on timer complete
- Temperature display per step
- "Start bake" button on recipe detail page

### Frontend — Reflection Screen
- Star rating (1-5)
- Outcome chip selector (disaster → best_yet)
- 4 measurement fields: rise height, internal temp, weight before/after
- Computed water loss % (highlighted, amber)
- Crumb/crust sliders (1-5)
- Free-text notes
- Save & finish → PATCH bake with all fields

### Frontend — Journal
- Timeline of past bakes with recipe title, date, rating, outcome, status

### Verification
- 6 Playwright tests passing
- Screenshots committed: active bake (dark mode), reflection screen
- Production deployed with migration applied

## Deferred
- Photo capture UI (camera input → R2 upload): R2 bucket not configured yet
- Tweak modal during bake: API ready, UI deferred to M3
- Real phone test with screen lock: requires Cloudflare Access to be configured first

## Open questions for M3
- R2 bucket needs creation for photo upload in production
- Tweak application logic (parsing "+10 g water" changes) needs careful design
