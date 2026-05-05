# M0 — Done

## Status: Gate green. Deployed to production.

## Staging URL
- Web: https://bakebook.nicolasschaerer.ch
- API health: https://bakebook.nicolasschaerer.ch/api/v1/health → `{"status":"ok","version":"0.0.1"}`
- GitHub: https://github.com/NlcoIas/bakebook (public)
- Coolify app UUID: `p13bvj4ysc9oolk7yhnl18zi`

## What shipped
- Monorepo skeleton: `apps/web` (Next.js 14), `apps/api` (FastAPI), `packages/types`
- Design tokens applied: Fraunces (variable, opsz+SOFT axes) + JetBrains Mono loaded via `next/font/google`
- Cookbook palette in CSS variables, Tailwind config extended
- Background grain (SVG noise turbulence) applied globally
- `<HandRule>` and `<SectionLabel>` shared components built
- Placeholder home page with italic "Bake" + amber "book" title treatment
- FastAPI with `/api/v1/health` and `/api/v1/me`, auth middleware, async SQLAlchemy, Alembic
- Deployed to Coolify with docker-compose (web + api + postgres)
- DNS: `bakebook.nicolasschaerer.ch` → Cloudflare Tunnel
- Playwright test at 380x800 viewport — screenshot committed
- GitHub Actions CI configured (typecheck, biome, ruff, pytest, vitest, playwright)
- Dockerfiles for both services
- ADRs: deployment (Coolify) and auth (Cloudflare Access)

## Local dev ports (this machine)
- Web: `localhost:3001` (port 3000 in use by PredictionsHub)
- API: `localhost:8001` (port 8000 in use by Coolify)
- Postgres: `localhost:5433` (port 5432 in use by existing postgres)

## Remaining
- [ ] Cloudflare Access policy: restrict to single email (requires Zero Trust dashboard — DNS token insufficient)
- [ ] Verify Fraunces loads on phone via staging URL (user to confirm)

## Things that took longer than expected
1. Port conflicts — three services (postgres, API, web) all had port collisions with existing services
2. Docker build issues — 5 deploy attempts: private repo, COPY syntax, empty public dir, Next.js rewrites not baked
3. Next.js standalone rewrites requiring build-time env vars was the trickiest deployment issue

## Open questions for M1
1. Should the API dev port (8001) and web dev port (3001) be documented in a `.env` or are they fine hardcoded?
2. shadcn/ui needs to be initialized when first needed — should we do it at M1 start or lazily?
