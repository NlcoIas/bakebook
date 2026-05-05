# Phase M4 — Starter + PWA Polish

**Goal**: Sourdough starter tracking, PWA manifest/icons/install, offline caching.

**Estimated**: 1 focused session.

**Hard exit gate**: Install on phone, force-quit Safari, open icon, view cornbread offline. Start bake, lock phone, get timer notification.

---

## Tasks

### 1. Starter backend
- [ ] Alembic migration: starters, starter_feedings
- [ ] SQLAlchemy models
- [ ] `services/starter.py`: peak estimation `peak_hours = peak_base_hours * 2^((20 - temp) / 10)`
- [ ] API: GET/POST/PATCH starters, POST feedings, GET status

### 2. Starter frontend
- [ ] `/starter` route: starter dashboard
- [ ] Feeding log form
- [ ] Status display: last fed, hours since, estimated peak

### 3. PWA manifest + icons
- [ ] `public/manifest.json` with app name, icons, theme colors
- [ ] App icons (192px, 512px) — generate simple ones
- [ ] `next-pwa` or manual service worker setup
- [ ] Install prompt

### 4. Offline caching
- [ ] Service worker: cache static shell + last-viewed recipes
- [ ] Network-first for /api/*, stale-while-revalidate for recipe GETs

### 5. Verification
- [ ] Playwright tests
- [ ] Deploy and test on phone
