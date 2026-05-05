# Bakebook

Personal baking PWA. Self-hosted on Proxmox + Coolify + Cloudflare Tunnel.

## Quick start

```bash
# Prerequisites: Node.js 20+, Docker
cp .env.example apps/api/.env  # then edit as needed
pnpm install
docker compose -f docker-compose.dev.yml up -d postgres
cd apps/api && uv sync && uv run alembic upgrade head && cd ../..
pnpm dev  # web on :3001, api on :8001
```

## Stack

- **Frontend**: Next.js 14 (App Router) + TypeScript + Tailwind + shadcn/ui
- **Backend**: FastAPI (Python 3.12) + SQLAlchemy 2.0 + Alembic
- **Database**: PostgreSQL 16
- **Package managers**: pnpm (web), uv (api)

## Monorepo structure

```
apps/web/     # Next.js PWA
apps/api/     # FastAPI
packages/types/  # Shared TS types
```

## Commands

| Command | Description |
|---|---|
| `pnpm dev` | Run web + api concurrently |
| `pnpm build` | Build web for production |
| `pnpm typecheck` | TypeScript check |
| `pnpm --filter web lint` | Biome lint (web) |
| `pnpm --filter api lint` | Ruff lint (api) |
| `pnpm --filter web test` | Vitest unit tests |
| `pnpm --filter api test` | Pytest |
| `pnpm --filter web e2e` | Playwright tests |

## Phases

- **M0** — Skeleton, design tokens, Coolify deploy
- **M1** — Recipes + pantry + nutrition + ratios + cost
- **M2** — Active bake + photos + reflection screen
- **M3** — Versioning + tweaks + scaling + ready-by
- **M4** — Starter + PWA polish
- **M5** — Insights screen
