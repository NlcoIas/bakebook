"""Ready-by schedule service — pure computation, no DB access.

Given a recipe's steps and a target end time, computes when to start baking
so the recipe finishes on time.

Algorithm:
  1. Build a dependency chain: each step depends on the previous unless
     ``parallelizable_with`` is set (those steps run concurrently with others).
  2. For sequential steps, the expected duration is ``timer_seconds`` (0 if null).
  3. Compute the critical path for expected, min, and max durations.
  4. Return start times and ranges relative to the target end time.

Parallelizable simplification: if step N has ``parallelizable_with = [M]``,
step N can run during step M, so only the longer of the two counts toward the
critical path — step N's duration does not add independently.
"""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass, field
from datetime import datetime, timedelta


@dataclass(frozen=True)
class ScheduleStep:
    """Minimal step representation for schedule calculation.

    Fields mirror ``recipe_steps`` columns relevant to timing.
    """

    ord: int
    timer_seconds: int | None = None
    min_seconds: int | None = None
    max_seconds: int | None = None
    parallelizable_with: list[int] = field(default_factory=list)


@dataclass(frozen=True)
class ScheduleResult:
    """Result of the ready-by calculation."""

    start_at: datetime
    expected_end: datetime
    range_start_at: datetime  # earliest you might need to start (uses max durations)
    range_end_at: datetime  # latest you can start (uses min durations)
    expected_total_seconds: int
    min_total_seconds: int
    max_total_seconds: int


def _effective_duration(step: ScheduleStep, mode: str) -> int:
    """Return the effective duration for a step in the given mode.

    Parameters
    ----------
    step:
        The step to evaluate.
    mode:
        One of ``'expected'``, ``'min'``, ``'max'``.

    For ``'expected'``, use ``timer_seconds`` (or 0).
    For ``'min'``, use ``min_seconds`` if set, else fall back to ``timer_seconds`` (or 0).
    For ``'max'``, use ``max_seconds`` if set, else fall back to ``timer_seconds`` (or 0).
    """
    base = step.timer_seconds or 0

    if mode == "expected":
        return base
    if mode == "min":
        return step.min_seconds if step.min_seconds is not None else base
    if mode == "max":
        return step.max_seconds if step.max_seconds is not None else base

    raise ValueError(f"Unknown mode: {mode!r}")


def _compute_critical_path(steps: Sequence[ScheduleStep], mode: str) -> int:
    """Compute the critical-path duration in seconds for the given mode.

    Steps are processed in ``ord`` order. A step whose
    ``parallelizable_with`` list includes another step's ord means it can
    run concurrently with that step — only the longer of the two contributes
    to the total duration.

    The algorithm tracks which step ords have already been "consumed" (added
    to the critical path). When a parallelizable step references a consumed
    step, we adjust: instead of adding the full parallel step duration, we
    only add the excess beyond what the referenced step already contributed.
    """
    if not steps:
        return 0

    sorted_steps = sorted(steps, key=lambda s: s.ord)

    # Map ord → duration for lookup.
    duration_by_ord: dict[int, int] = {}
    for step in sorted_steps:
        duration_by_ord[step.ord] = _effective_duration(step, mode)

    # Track the contribution each step ord has made to the critical path.
    # For parallelizable resolution we need to know how much time each step
    # originally contributed.
    contribution: dict[int, int] = {}
    total = 0

    for step in sorted_steps:
        dur = _effective_duration(step, mode)
        parallel_targets = [
            o for o in step.parallelizable_with if o in duration_by_ord
        ]

        if parallel_targets:
            # This step runs concurrently with the referenced steps.
            # Find the maximum duration already contributed by any of the
            # referenced steps. This step only adds time if it's longer.
            max_ref_contribution = max(
                contribution.get(o, 0) for o in parallel_targets
            )
            # Also consider the raw duration of the referenced steps in case
            # the referenced step hasn't been processed yet (unusual but safe).
            max_ref_duration = max(
                duration_by_ord.get(o, 0) for o in parallel_targets
            )
            ref = max(max_ref_contribution, max_ref_duration)

            excess = max(0, dur - ref)
            total += excess
            contribution[step.ord] = excess
        else:
            # Sequential step: adds its full duration.
            total += dur
            contribution[step.ord] = dur

    return total


def calculate_schedule(
    steps: Sequence[ScheduleStep],
    target: datetime,
) -> ScheduleResult:
    """Calculate when to start baking to finish by ``target``.

    Parameters
    ----------
    steps:
        The recipe's steps with timing metadata.
    target:
        The desired finish time.

    Returns
    -------
    A ``ScheduleResult`` with computed start times and duration totals.
    """
    expected_total = _compute_critical_path(steps, "expected")
    min_total = _compute_critical_path(steps, "min")
    max_total = _compute_critical_path(steps, "max")

    return ScheduleResult(
        start_at=target - timedelta(seconds=expected_total),
        expected_end=target,
        range_start_at=target - timedelta(seconds=max_total),
        range_end_at=target - timedelta(seconds=min_total),
        expected_total_seconds=expected_total,
        min_total_seconds=min_total,
        max_total_seconds=max_total,
    )
