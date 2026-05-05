# Bakebook

A personal baking PWA. This folder is the project handoff — drop it into a fresh git repo and point Claude Code at `BOOTSTRAP.md`.

## What's in this folder

| File | What it is |
|---|---|
| `CLAUDE.md` | The master spec. Read this to understand what's being built. |
| `DESIGN.md` | The design system — tokens, components, the "is it on-design" checklist. |
| `BOOTSTRAP.md` | The kickoff prompt for Claude Code. Self-contained operating rules. |
| `phases/M0/task.md` | The first concrete session: project skeleton + design tokens + Coolify deploy. |
| `design/v1-screens.html` | Visual reference: Home, Recipe, Active Bake, Journal screens. |
| `design/v2-data.html` | Visual reference: Recipe (data-dense), Reflection, Insights. |
| `README.md` | This file. |

## How to start (you, the human)

1. Drop this folder into your factory location, e.g. `~/claude/websites/bakebook/`.
2. `cd` into it. `git init && git add . && git commit -m "M0 handoff"`.
3. Open Claude Code in this directory.
4. First message:

   ```
   Read BOOTSTRAP.md and follow it.
   ```

That's it. Claude Code will read the bootstrap, then `CLAUDE.md`, then `DESIGN.md`, then `phases/M0/task.md`, ack, and start.

## How to start (alternative — autonomous overnight)

If running with `--dangerously-skip-permissions` in a tmux session:

```bash
cd ~/claude/websites/bakebook
claude --dangerously-skip-permissions <<EOF
Read BOOTSTRAP.md and follow it. Execute M0 to completion.
Stop only at the M0 exit gate (or if a genuine spec contradiction blocks you).
EOF
```

The bootstrap rules require Claude Code to write `phases/M0/done.md` and `phases/M0/issues.md` before declaring done — so when you wake up, those files tell you the truth about what shipped.

## Phases at a glance

- **M0** — Skeleton, design tokens, Coolify deploy. *(concrete task file included)*
- **M1** — Recipes + pantry + nutrition + ratios + cost.
- **M2** — Active bake + photos + reflection screen.
- **M3** — Versioning + tweaks + scaling + ready-by.
- **M4** — Starter + PWA polish (offline, install, push).
- **M5** — Insights screen.

Phases beyond M0 don't have task files yet; Claude Code writes them at the start of each phase, in dialog with you if anything's unclear in the spec.

## When the design HTML disagrees with DESIGN.md

DESIGN.md wins. The HTML is a picture; the markdown is the contract. If you spot a divergence, fix DESIGN.md and note it in a decision record.

## Open questions before M0

See `CLAUDE.md` §18. Defaults are: domain = `bakebook.nicolasschaerer.ch`, R2 = new dedicated bucket, notification = generic chime, kitchen temp = manual entry, daily-value = 2000 kcal. Override any of these by replying to Claude Code's first ack message.
