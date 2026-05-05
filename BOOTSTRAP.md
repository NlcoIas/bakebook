# BOOTSTRAP.md — kickoff prompt for Claude Code

You are Claude Code, working autonomously on the **Bakebook** project. This file is your entry point. Read it once, then execute.

---

## 1. Read these files in order, then stop and ack

1. `CLAUDE.md` — master spec. Data model, API surface, phases, verification protocol.
2. `DESIGN.md` — design tokens, shared components, the "is it on-design" checklist.
3. `design/v1-screens.html` and `design/v2-data.html` — visual ground truth at 380 × 800 viewport. Open them, look at them, internalize the look. These are not specs but they are the target.
4. `phases/M0/task.md` — your first session.

After reading, before writing any code, output a short acknowledgement (≤ 10 lines) that:
- Confirms which phase you are starting (M0).
- Lists the open questions in `CLAUDE.md` §18 and the defaults you will assume (the first option in each).
- States the first three tool calls you intend to make.

Then proceed.

---

## 2. Operating rules

These are absolute. Violating any one of them is a regression:

1. **Phase discipline.** You execute one phase at a time, in order. M0 → M1 → M2 → M3 → M4 → M5. Do not start M{n+1} until M{n}'s exit gate is green and `phases/M{n}/done.md` is written.
2. **Migrations always.** Every schema change is an Alembic migration. Never `Base.metadata.create_all` in app code.
3. **Playwright before "done".** No feature is complete without a passing Playwright test that takes a screenshot and commits it to `test-results/screenshots/{phase}/{feature}.png`.
4. **Compare to design.** For every new screen, after the Playwright screenshot, visually compare to the corresponding HTML in `design/`. Use the §8 checklist in `DESIGN.md`. Note any deviations in the phase's `issues.md`.
5. **Real flow on real phone.** Each phase's exit gate includes a real end-to-end run on the deployed staging URL from a phone. Note kitchen temperature and any timer drift in `phases/M{n}/done.md`.
6. **Honest issues log.** Write down every bug you hit, in `phases/M{n}/issues.md`, with the commit that fixed it. An empty file is suspicious — write down the small ones too.
7. **No LLM-generated content in the app.** No runtime Claude API calls in v1. The pattern detection rules in `services/patterns.py` are hand-coded and reviewed.
8. **Adversarial cross-check at M2 and M3.** Before declaring those phases done, run Codex CLI and Gemini CLI against the active-bake worker (M2) and tweak-application logic (M3) with: *"Find race conditions, timer drift sources, ways the timer can be lost on backgrounding, edge cases in the tweak parser. Be adversarial."* Address every concrete issue raised.
9. **Don't read ahead.** While building M{n}, do not pre-read M{n+2}'s task file. Each phase has decisions that should be made fresh.
10. **Stop and ask** if the spec is genuinely ambiguous or you discover a contradiction. Otherwise default to the spec and the first-option resolutions in `CLAUDE.md` §18.

---

## 3. Verification toolkit

Use these constantly:

- `pnpm --filter web typecheck` — fail fast on TS errors
- `pnpm --filter api ruff check` — fail fast on Python lint
- `pnpm --filter web test` — Vitest unit
- `pnpm --filter api test` — pytest
- `pnpm --filter web e2e` — Playwright (must pass before phase exit)
- `pnpm --filter web build` — make sure prod build works before deploy

CI runs all of these on push. Local pre-commit runs lint + typecheck.

---

## 4. The recommended autonomous loop

Inside each phase:

```
loop:
  read phases/M{n}/task.md (or update it as sub-tasks emerge)
  pick the next unchecked item
  ultrathink: design the smallest meaningful slice
  implement
  write tests (unit + e2e where applicable)
  run all checks
  if red: fix, log in issues.md
  if green: commit with message "M{n}: <slice>"
  check the item off
  if all items checked: write done.md, run the exit-gate flow, ask user to confirm phase complete
```

For overnight tmux sessions: at the top of each iteration, check the time. If you've been running > 3 hours since the last gate, write a checkpoint to `phases/M{n}/checkpoint.md` summarizing state so the next session can resume.

---

## 5. First action

Read `CLAUDE.md`, then `DESIGN.md`, then `phases/M0/task.md`, then ack and begin.

*Welcome to Bakebook. Build it well.*
