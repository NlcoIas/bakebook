# Phase M2 — Active Bake + Photos + Reflection

**Goal**: The full bake lifecycle — start a bake, run through steps with timers in a dark kitchen-mode screen, capture photos, finish with a structured reflection, and browse past bakes in a journal.

**Estimated**: 2 focused sessions.

**Hard exit gate**: Run a real cornbread bake end-to-end on phone. Timer fires after screen lock. Photo uploads. Reflection screen shows 4 measurements + computed water loss.

---

## Tasks

### 1. Database schema

- [ ] Alembic migration for `bakes` (§4.4) — with env-context columns, structured outcomes
- [ ] Alembic migration for `bake_photos` (§4.5) — R2 key, caption, kind, step_ord
- [ ] Alembic migration for `bake_tweaks` (§4.5) — change, reason, apply_next_time
- [ ] SQLAlchemy models for all three tables

### 2. R2 integration

- [ ] `services/r2.py` — presigned PUT URL generation, presigned GET URL generation
- [ ] Configure R2 bucket (or stub for dev with local file storage)
- [ ] Test presigned URL generation

### 3. Bake API routes (§5.3)

- [ ] `POST /bakes` — start bake with recipe, scale, env context
- [ ] `GET /bakes/{id}` — includes computed waterLossPct
- [ ] `PATCH /bakes/{id}` — update step, status, all outcome fields
- [ ] `POST /bakes/{id}/photos` — generate presigned upload URL
- [ ] `POST /bakes/{id}/photos/{r2Key}/confirm` — create DB row after upload
- [ ] `PATCH /bake-photos/{id}` — update caption/kind
- [ ] `DELETE /bake-photos/{id}` — delete from DB + R2
- [ ] `POST /bakes/{id}/tweaks` — add tweak
- [ ] `GET /bakes` — journal feed with filters (from, to, category, minRating, hasTweaks)
- [ ] Pydantic schemas with camelCase

### 4. Active bake frontend — kitchen mode (§8)

- [ ] `/recipes/[id]/bake` route — full-screen, espresso dark palette
- [ ] Pre-bake context modal (kitchen temp, humidity, flour brand) — skippable
- [ ] Step-by-step navigation with large tap targets
- [ ] Timer display: big monospace countdown, amber accent
- [ ] Timer worker (`workers/timer.ts`) — Web Worker posting tick every 250ms
- [ ] Timer state in IndexedDB: `bake:{bakeId}:timers`
- [ ] Wake Lock API — acquire on entry, release on exit/pause
- [ ] Backgrounding resilience: recompute from targetEpochMs on visibilitychange
- [ ] Notification on timer done (with vibration pattern, sound)
- [ ] Resume: detect active bake for recipe, restore current_step
- [ ] Photo capture mid-bake (camera input → preview → background upload)
- [ ] Tweak modal mid-bake (change text, apply_next_time checkbox)
- [ ] Exit flow: pause/abandon/cancel confirmation
- [ ] "Finish bake" button → navigate to reflection
- [ ] Bottom nav hidden in bake mode

### 5. Reflection screen (§9)

- [ ] `/bakes/[id]` route — triggered after finishing bake
- [ ] Star rating (1-5 tap input)
- [ ] Outcome chip selector (disaster | meh | okay | good | best_yet)
- [ ] Photo grid (4 tiles with kind chips + add tile)
- [ ] Measurement grid (rise height, internal temp, weight before/after)
- [ ] Computed: water loss % (highlighted, derived)
- [ ] Crumb/crust sliders (1-5, tight↔open, pale↔blistered)
- [ ] Tweaks list (from in-bake tweaks, editable)
- [ ] Free-text notes
- [ ] Save & finish → PATCH bake, set status='finished'

### 6. Journal timeline

- [ ] `/bakes` route — timeline of past bakes
- [ ] Each entry: recipe title, date, rating stars, outcome chip, thumbnail
- [ ] Filters: date range, category, min rating

### 7. Verification

- [ ] Playwright test: start bake, advance steps, verify timer renders
- [ ] Playwright test: reflection screen with measurement fields
- [ ] Screenshots at 380x800 for active bake (dark mode) and reflection
- [ ] Compare to design HTML references
- [ ] All tests passing (pytest 98+, vitest, playwright)
- [ ] Deploy to production, verify on phone
- [ ] Write done.md and issues.md

---

## Notes

- Kitchen mode uses the espresso palette — completely different visual from cookbook mode
- Timer must survive: tab refresh, backgrounding, screen lock. Use IndexedDB + epoch targets.
- R2 can be stubbed for local dev (store files locally). Wire real R2 for production.
- The reflection screen is a form — most fields optional, only rating required.
- Photos use presigned PUT URLs — client uploads directly to R2, then confirms to API.
