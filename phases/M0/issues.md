# M0 Issues

## 1. pnpm onlyBuiltDependencies required interactive approval
**Problem**: `pnpm approve-builds` launches an interactive TUI selector, which doesn't work in non-interactive sessions.
**Fix**: Added `pnpm.onlyBuiltDependencies` to root `package.json` to declaratively approve `@biomejs/biome` and `esbuild`.

## 2. Port 5432 already in use
**Problem**: Host already has a PostgreSQL instance on port 5432.
**Fix**: Changed docker-compose to map container port 5432 to host port 5433. Updated `.env.example` accordingly.

## 3. Port 8000 already in use (Coolify)
**Problem**: Coolify is running on port 8000 on this host.
**Fix**: Changed API dev port to 8001. Updated `next.config.js` proxy and CORS origin.

## 4. Port 3000 already in use
**Problem**: Another app ("PredictionsHub") was running on port 3000, causing Playwright to hit the wrong app.
**Fix**: Changed Next.js dev port to 3001. Updated Playwright config accordingly.

## 5. Playwright tried to use WebKit (not installed)
**Problem**: Using `devices["iPhone 13"]` defaults to WebKit browser engine, which wasn't installed.
**Fix**: Changed Playwright project to use Chromium with mobile viewport (380x800) instead of WebKit device preset.

## 6. Playwright test dir module resolution
**Problem**: Tests in `../../playwright/` couldn't resolve `@playwright/test` from outside `node_modules` scope.
**Fix**: Moved tests to `apps/web/e2e/` within the web package's module resolution scope.

## 7. uv `tool.uv.dev-dependencies` deprecated
**Problem**: `[tool.uv] dev-dependencies` emits a deprecation warning.
**Fix**: Changed to `[dependency-groups] dev` in pyproject.toml.

## 8. ruff import sorting
**Problem**: ruff flagged unsorted imports in `alembic/env.py` and `app/auth.py`.
**Fix**: Ran `ruff check --fix .` to auto-sort.
