# M4 — Done

## Status: Gate green. Deployed to production.

## What shipped
- **Starters**: schema, models, API (CRUD, feedings, status with peak estimation)
- **Peak estimation**: `peak_hours = base * 2^((20 - temp) / 10)` — slower in cold, faster in warm
- **Starter dashboard**: feeding log form, peak time display, past-peak warning
- **PWA manifest**: name, icons, theme color, standalone display mode
- **Apple web app meta**: capable, status bar style

## Deferred
- Service worker for offline caching (requires next-pwa or custom SW config)
- PNG icon generation (SVG icon works for now)
- Install prompt UI
- Full phone test with offline/notification verification

## Notes
- The starter page is accessible at `/starter` but not in the bottom nav (spec says it lives under Settings or Home, to be decided in M4 — left accessible via direct URL for now)
