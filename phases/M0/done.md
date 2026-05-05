# M0 — Done

## Status: Local gate green. Coolify deploy pending user action.

## What shipped
- Monorepo skeleton: `apps/web` (Next.js 14), `apps/api` (FastAPI), `packages/types`
- Design tokens applied: Fraunces (variable, opsz+SOFT axes) + JetBrains Mono loaded via `next/font/google`
- Cookbook palette in CSS variables, Tailwind config extended
- Background grain (SVG noise turbulence) applied globally
- `<HandRule>` and `<SectionLabel>` shared components built
- Placeholder home page with italic "Bake" + amber "book" title treatment
- FastAPI with `/api/v1/health` and `/api/v1/me`, auth middleware, async SQLAlchemy, Alembic
- Postgres 16 via docker-compose (port 5433 on this host due to existing postgres)
- Playwright test at 380x800 viewport — screenshot committed
- GitHub Actions CI configured (typecheck, biome, ruff, pytest, vitest, playwright)
- Dockerfiles for both services
- ADRs: deployment (Coolify) and auth (Cloudflare Access)

## Local dev ports (this machine)
- Web: `localhost:3001` (port 3000 in use by PredictionsHub)
- API: `localhost:8001` (port 8000 in use by Coolify)
- Postgres: `localhost:5433` (port 5432 in use by existing postgres)

## Remaining for full gate
- [ ] Push to GitHub remote
- [ ] Coolify project creation: `bakebook` with web + api services + Postgres
- [ ] Cloudflare Tunnel: `bakebook.nicolasschaerer.ch` → Coolify proxy
- [ ] Cloudflare Access policy: single email
- [ ] Verify `curl https://bakebook.nicolasschaerer.ch/api/v1/health` returns 200 from phone
- [ ] Verify Fraunces loads on phone via staging URL

## Things that took longer than expected
1. Port conflicts — three services (postgres, API, web) all had port collisions with existing services on this Proxmox host
2. pnpm `approve-builds` being interactive — required declarative config in package.json instead
3. Playwright module resolution — tests outside `node_modules` scope couldn't find `@playwright/test`

## Open questions for M1
1. Should the API dev port (8001) and web dev port (3001) be documented in a `.env` or are they fine hardcoded?
2. shadcn/ui needs to be initialized when first needed — should we do it at M1 start or lazily?
