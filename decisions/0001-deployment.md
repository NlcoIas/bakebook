# ADR 0001: Deployment on Coolify

## Status
Accepted

## Context
We need to deploy the Bakebook PWA (Next.js frontend + FastAPI backend + PostgreSQL) to a self-hosted environment. The existing infrastructure runs Proxmox with Coolify already provisioned and managing other services.

## Decision
Deploy on Coolify with:
- Two services: `web` (Next.js standalone) and `api` (FastAPI via uvicorn)
- One Coolify-managed PostgreSQL 16 instance
- Cloudflare Tunnel for ingress at `bakebook.nicolasschaerer.ch`
- Auto-deploy from `main` branch

## Alternatives Considered
**Plain docker-compose on a Proxmox VM**: viable fallback. Would require:
- Manual Traefik/Caddy setup for routing
- Manual SSL (or rely on Cloudflare Tunnel anyway)
- Manual restart/health-check config
- No built-in deploy-on-push

## Consequences
- Coolify handles container orchestration, health checks, and zero-downtime deploys
- If Coolify becomes annoying (resource overhead, bugs), migration to plain compose is straightforward — same Dockerfiles, same Tunnel config, just add a compose file with routing
- Database backups use Coolify's built-in pg_dump schedule
