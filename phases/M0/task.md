# Phase M0 — Project skeleton

**Goal**: a clean monorepo deployed to staging on Coolify, with the design tokens applied to a placeholder page, and CI passing.

**Estimated**: one focused session (3–5 hours).

**Hard exit gate**: `curl https://bakebook-staging.../api/v1/health` returns 200 from your phone, the web root shows a styled placeholder page in the cookbook palette with Fraunces correctly loaded, and CI is green on `main`.

---

## Tasks

Work top-down. Check off as you go.

### Repo skeleton

- [ ] Initialize git repo. First commit: just `CLAUDE.md`, `DESIGN.md`, `BOOTSTRAP.md`, `README.md`, the design HTML files, and this task file.
- [ ] Create monorepo layout per `CLAUDE.md` §14. `apps/web`, `apps/api`, `packages/types`, `playwright`, `decisions`, `phases`, `design`.
- [ ] Set up pnpm workspaces in `package.json` and `pnpm-workspace.yaml`.
- [ ] `.gitignore` covering `node_modules`, `__pycache__`, `.venv`, `.next`, `dist`, `.env*`, `test-results`, `playwright-report`.
- [ ] `.env.example` with placeholders for: `DATABASE_URL`, `R2_ACCOUNT_ID`, `R2_ACCESS_KEY_ID`, `R2_SECRET_ACCESS_KEY`, `R2_BUCKET`, `AUTH_DEV_EMAIL=dev@local`, `ENV=dev`.
- [ ] Add a `pnpm rename <new-name>` script to allow project renaming later (string replace in package.json files + README + Coolify service names noted in a comment).

### Web app (Next.js 14)

- [ ] `apps/web` initialized with `pnpm dlx create-next-app@latest --ts --app --tailwind --no-eslint --import-alias "@/*"` — then replace ESLint with Biome.
- [ ] Install: `next-pwa`, `@tanstack/react-query`, `zustand`, `clsx`, `tailwind-merge`. shadcn/ui CLI initialized but only install the components you need as you go.
- [ ] Tailwind config extends with the cookbook + kitchen-mode CSS variables from `DESIGN.md` §2. All variables defined as Tailwind colors (`amber: 'var(--amber)'` etc.) so utility classes work.
- [ ] `app/layout.tsx` loads Fraunces (variable, with `opsz` and `SOFT` axes) and JetBrains Mono via `next/font/google`. Sets `--font-display` and `--font-mono` on `<html>`.
- [ ] `app/globals.css` contains the `:root` block, the body grain background, and base typography setting `font-family: var(--display)` on body.
- [ ] `app/page.tsx` is a placeholder home: a centered Fraunces italic title saying "Bakebook" with the amber accent on "book", a sub-line of mono caps text, and a small `<HandRule>` underneath. This page is your design-token smoke test.
- [ ] Build `<HandRule>` and `<SectionLabel>` components in `components/shared/` — they are the design system's foundation.
- [ ] Verify: open at 380 × 800 in Playwright, take a screenshot, eyeball compare to the title treatment in `design/v1-screens.html`. The "Bakebook" should look like a small cousin of the editorial titles in the design.

### API (FastAPI)

- [ ] `apps/api` with `pyproject.toml` using uv. Dependencies: `fastapi`, `uvicorn[standard]`, `sqlalchemy>=2`, `asyncpg`, `alembic`, `pydantic>=2`, `pydantic-settings`, `python-multipart`, `boto3` (for R2), `httpx` (testing).
- [ ] Dev dependencies: `pytest`, `pytest-asyncio`, `pytest-httpx`, `ruff`, `black`, `mypy`.
- [ ] `app/main.py` with FastAPI app, CORS for localhost dev, a single route `GET /api/v1/health` returning `{"status": "ok", "version": "0.0.1"}`.
- [ ] `app/auth.py` — middleware that reads `Cf-Access-Authenticated-User-Email`. In `ENV=dev`, injects `dev@local`. In prod, 401 if missing.
- [ ] `app/db.py` — async SQLAlchemy engine, session factory.
- [ ] Alembic initialized in `apps/api/alembic/`. Empty initial migration.

### Shared types

- [ ] `packages/types` with a script that runs `datamodel-code-generator` against the FastAPI OpenAPI spec to produce `index.ts`. Add it to web's `pnpm dev` so types refresh on api restart.

### Local dev

- [ ] `docker-compose.yml` at repo root with a `postgres:16` service, named volume, exposed on 5432.
- [ ] `pnpm dev` runs both apps concurrently (use `concurrently` or `turbo`). API on 8000, web on 3000. Web dev proxies `/api/*` to api.
- [ ] Verify `pnpm install && docker compose up -d postgres && pnpm dev` works clean from a fresh clone. Document this in `README.md`.

### CI

- [ ] `.github/workflows/ci.yml` with jobs for: typecheck, biome, ruff, pytest (with a service postgres), vitest, playwright (headless, install-deps step).
- [ ] All jobs run on PR and on push to `main`.

### Coolify deploy

- [ ] Create the Coolify project `bakebook` with two services (`web`, `api`) and a Postgres.
- [ ] `apps/web/Dockerfile` — multi-stage, Next.js standalone output.
- [ ] `apps/api/Dockerfile` — python:3.12-slim, `uv sync --frozen`, `uvicorn`.
- [ ] `apps/api/entrypoint.sh` — runs `alembic upgrade head` then `exec "$@"`. Marked executable.
- [ ] Configure Coolify routes: `/api/*` → api service, everything else → web service. Auto-deploy from `main`.
- [ ] Configure Cloudflare Tunnel route: `bakebook.nicolasschaerer.ch` → Coolify proxy. Cloudflare Access policy: single allowed email.
- [ ] Set env vars in Coolify: production R2 creds, `ENV=prod`, `DATABASE_URL` (Coolify-generated).

### Decisions to record

- [ ] Write `decisions/0001-deployment.md` documenting: chose Coolify over plain docker-compose because we already run it; if we hit annoyance, fallback is plain compose, here's roughly what would change.
- [ ] Write `decisions/0002-auth.md` documenting: Cloudflare Access is sole auth perimeter in v1; api blindly trusts header; Coolify network policy restricts api ingress to web service + tunnel only.

### Verification (the gate)

- [ ] `curl https://bakebook-staging.../api/v1/health` returns 200 from your phone (not just laptop).
- [ ] Open the staging URL on the phone, take a screenshot, verify Fraunces loaded (title looks soft and warm, not blocky) and the cream background grain is visible.
- [ ] CI green on `main`.
- [ ] Write `phases/M0/done.md` with: the staging URL, the kitchen temperature when you tested (for the future-trends-archive), three things that took longer than expected, and any open questions for M1.
- [ ] Write `phases/M0/issues.md` with every bug encountered, even small ones, and the commit that fixed each.

---

## Notes for this phase

- Don't build feature components. Resist. M0 is foundation only.
- Don't seed any data. M1 owns seeding.
- Don't write API routes beyond `/health` and `/me`. They'll come in M1.
- The placeholder home page exists for one reason: to verify Fraunces and JetBrains Mono load correctly and the cream palette is applied. If the title doesn't look right, fix the font loading before moving on.
- If `next/font/google` doesn't expose the `SOFT` axis directly, fall back to `<link>` tags in the document head with the full `https://fonts.googleapis.com/css2?...&SOFT=...` URL. Do not silently drop the axis.

---

## When complete

After M0's gate is green and the two `done.md` / `issues.md` files are written, ask the user to confirm the phase. Then read `phases/M1/task.md` (which doesn't exist yet — write it from `CLAUDE.md` §12 M1 first, in dialog with the user if anything's unclear).
