"""Tests for the ready-by schedule service."""

from datetime import UTC, datetime, timedelta

import pytest

from app.services.schedule import ScheduleStep, calculate_schedule

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

# Fixed target time for deterministic assertions.
TARGET = datetime(2026, 5, 5, 18, 0, 0, tzinfo=UTC)


def _sequential_steps(n: int, seconds_each: int) -> list[ScheduleStep]:
    """Create *n* sequential steps each lasting *seconds_each*."""
    return [
        ScheduleStep(ord=i, timer_seconds=seconds_each)
        for i in range(1, n + 1)
    ]


# ---------------------------------------------------------------------------
# Simple sequential steps
# ---------------------------------------------------------------------------


class TestSequentialSteps:
    def test_three_steps_10_min_each(self):
        """3 steps x 600s = 1800s total. Start 30 min before target."""
        steps = _sequential_steps(3, 600)
        result = calculate_schedule(steps, TARGET)

        assert result.expected_total_seconds == 1800
        assert result.start_at == TARGET - timedelta(seconds=1800)
        assert result.expected_end == TARGET

    def test_single_step(self):
        steps = [ScheduleStep(ord=1, timer_seconds=300)]
        result = calculate_schedule(steps, TARGET)

        assert result.expected_total_seconds == 300
        assert result.start_at == TARGET - timedelta(seconds=300)

    def test_durations_add_up(self):
        """Steps with different durations sum correctly."""
        steps = [
            ScheduleStep(ord=1, timer_seconds=120),
            ScheduleStep(ord=2, timer_seconds=300),
            ScheduleStep(ord=3, timer_seconds=60),
        ]
        result = calculate_schedule(steps, TARGET)

        assert result.expected_total_seconds == 480
        assert result.start_at == TARGET - timedelta(seconds=480)


# ---------------------------------------------------------------------------
# Steps with min/max ranges
# ---------------------------------------------------------------------------


class TestMinMaxRanges:
    def test_min_and_max_paths(self):
        """min_seconds and max_seconds produce different range bounds."""
        steps = [
            ScheduleStep(ord=1, timer_seconds=600, min_seconds=480, max_seconds=720),
            ScheduleStep(ord=2, timer_seconds=600, min_seconds=540, max_seconds=660),
        ]
        result = calculate_schedule(steps, TARGET)

        assert result.expected_total_seconds == 1200  # 600 + 600
        assert result.min_total_seconds == 1020  # 480 + 540
        assert result.max_total_seconds == 1380  # 720 + 660

        # range_start_at uses max (earliest you might need to start)
        assert result.range_start_at == TARGET - timedelta(seconds=1380)
        # range_end_at uses min (latest you can start)
        assert result.range_end_at == TARGET - timedelta(seconds=1020)

    def test_partial_min_max(self):
        """Some steps have min/max, others fall back to timer_seconds."""
        steps = [
            ScheduleStep(ord=1, timer_seconds=600, min_seconds=300),
            ScheduleStep(ord=2, timer_seconds=600, max_seconds=900),
        ]
        result = calculate_schedule(steps, TARGET)

        assert result.expected_total_seconds == 1200
        # min: 300 + 600 (step 2 has no min_seconds, falls back to timer)
        assert result.min_total_seconds == 900
        # max: 600 + 900 (step 1 has no max_seconds, falls back to timer)
        assert result.max_total_seconds == 1500

    def test_min_max_same_as_expected(self):
        """When min and max equal timer_seconds, ranges collapse."""
        steps = [
            ScheduleStep(ord=1, timer_seconds=600, min_seconds=600, max_seconds=600),
        ]
        result = calculate_schedule(steps, TARGET)

        assert result.expected_total_seconds == 600
        assert result.min_total_seconds == 600
        assert result.max_total_seconds == 600
        assert result.start_at == result.range_start_at == result.range_end_at


# ---------------------------------------------------------------------------
# Parallelizable steps
# ---------------------------------------------------------------------------


class TestParallelizableSteps:
    def test_parallel_step_absorbed(self):
        """Step 2 runs during step 1 and is shorter — no extra time."""
        steps = [
            ScheduleStep(ord=1, timer_seconds=600),
            ScheduleStep(ord=2, timer_seconds=300, parallelizable_with=[1]),
        ]
        result = calculate_schedule(steps, TARGET)

        # Step 2 (300s) fits within step 1 (600s), so total is just 600s.
        assert result.expected_total_seconds == 600

    def test_parallel_step_exceeds_reference(self):
        """Step 2 runs during step 1 but is longer — excess adds to path."""
        steps = [
            ScheduleStep(ord=1, timer_seconds=300),
            ScheduleStep(ord=2, timer_seconds=600, parallelizable_with=[1]),
        ]
        result = calculate_schedule(steps, TARGET)

        # Step 2 (600s) overlaps with step 1 (300s), excess = 300s.
        # Total = 300 + 300 = 600.
        assert result.expected_total_seconds == 600

    def test_parallel_step_equal_duration(self):
        """When parallel step has same duration as reference, no excess."""
        steps = [
            ScheduleStep(ord=1, timer_seconds=600),
            ScheduleStep(ord=2, timer_seconds=600, parallelizable_with=[1]),
        ]
        result = calculate_schedule(steps, TARGET)

        assert result.expected_total_seconds == 600

    def test_mixed_parallel_and_sequential(self):
        """Some steps parallel, some sequential."""
        steps = [
            ScheduleStep(ord=1, timer_seconds=600),  # sequential: 600
            ScheduleStep(ord=2, timer_seconds=300, parallelizable_with=[1]),  # absorbed
            ScheduleStep(ord=3, timer_seconds=600),  # sequential: 600
        ]
        result = calculate_schedule(steps, TARGET)

        # 600 (step 1, step 2 absorbed) + 600 (step 3) = 1200
        assert result.expected_total_seconds == 1200

    def test_parallel_with_min_max(self):
        """Parallelizable logic applies to min and max modes too."""
        steps = [
            ScheduleStep(ord=1, timer_seconds=600, min_seconds=480, max_seconds=720),
            ScheduleStep(
                ord=2,
                timer_seconds=300,
                min_seconds=200,
                max_seconds=400,
                parallelizable_with=[1],
            ),
        ]
        result = calculate_schedule(steps, TARGET)

        # Expected: step 1 = 600, step 2 = 300 (absorbed). Total = 600.
        assert result.expected_total_seconds == 600
        # Min: step 1 = 480, step 2 = 200 (absorbed). Total = 480.
        assert result.min_total_seconds == 480
        # Max: step 1 = 720, step 2 = 400 (absorbed). Total = 720.
        assert result.max_total_seconds == 720

    def test_parallel_references_nonexistent_step(self):
        """Referencing a step ord that doesn't exist is silently ignored."""
        steps = [
            ScheduleStep(ord=1, timer_seconds=600),
            ScheduleStep(ord=2, timer_seconds=300, parallelizable_with=[99]),
        ]
        result = calculate_schedule(steps, TARGET)

        # Step 2 references ord 99 which doesn't exist, treated as sequential.
        assert result.expected_total_seconds == 900


# ---------------------------------------------------------------------------
# Steps with no timer (0 duration)
# ---------------------------------------------------------------------------


class TestNoTimerSteps:
    def test_none_timer_is_zero_duration(self):
        """A step with timer_seconds=None contributes 0 seconds."""
        steps = [
            ScheduleStep(ord=1, timer_seconds=600),
            ScheduleStep(ord=2, timer_seconds=None),
            ScheduleStep(ord=3, timer_seconds=600),
        ]
        result = calculate_schedule(steps, TARGET)

        assert result.expected_total_seconds == 1200

    def test_all_none_timers(self):
        """All steps with no timer → 0 total."""
        steps = [
            ScheduleStep(ord=1),
            ScheduleStep(ord=2),
        ]
        result = calculate_schedule(steps, TARGET)

        assert result.expected_total_seconds == 0
        assert result.start_at == TARGET


# ---------------------------------------------------------------------------
# Empty step list
# ---------------------------------------------------------------------------


class TestEmptySteps:
    def test_no_steps(self):
        """Empty step list → 0 duration, start_at == target."""
        result = calculate_schedule([], TARGET)

        assert result.expected_total_seconds == 0
        assert result.min_total_seconds == 0
        assert result.max_total_seconds == 0
        assert result.start_at == TARGET
        assert result.expected_end == TARGET
        assert result.range_start_at == TARGET
        assert result.range_end_at == TARGET


# ---------------------------------------------------------------------------
# Target time calculation
# ---------------------------------------------------------------------------


class TestTargetTimeCalculation:
    def test_start_at_is_target_minus_expected(self):
        steps = _sequential_steps(2, 900)  # 2 x 900 = 1800s = 30 min
        result = calculate_schedule(steps, TARGET)

        assert result.start_at == datetime(2026, 5, 5, 17, 30, 0, tzinfo=UTC)

    def test_range_start_uses_max(self):
        """range_start_at = target - max_total (earliest you might need to begin)."""
        steps = [
            ScheduleStep(ord=1, timer_seconds=600, max_seconds=900),
        ]
        result = calculate_schedule(steps, TARGET)

        assert result.range_start_at == TARGET - timedelta(seconds=900)

    def test_range_end_uses_min(self):
        """range_end_at = target - min_total (latest you can begin)."""
        steps = [
            ScheduleStep(ord=1, timer_seconds=600, min_seconds=300),
        ]
        result = calculate_schedule(steps, TARGET)

        assert result.range_end_at == TARGET - timedelta(seconds=300)

    def test_different_target_time(self):
        """Verify with a non-standard target time."""
        target = datetime(2026, 12, 25, 12, 0, 0, tzinfo=UTC)
        steps = [ScheduleStep(ord=1, timer_seconds=3600)]  # 1 hour
        result = calculate_schedule(steps, target)

        assert result.start_at == datetime(2026, 12, 25, 11, 0, 0, tzinfo=UTC)
        assert result.expected_end == target

    def test_result_is_frozen(self):
        """ScheduleResult is immutable."""
        result = calculate_schedule([], TARGET)
        with pytest.raises(AttributeError):
            result.expected_total_seconds = 999  # type: ignore[misc]


# ---------------------------------------------------------------------------
# Real-world-ish scenario
# ---------------------------------------------------------------------------


class TestRealisticBread:
    """A simplified bread recipe schedule."""

    def test_bread_schedule(self):
        steps = [
            ScheduleStep(ord=1, timer_seconds=600, min_seconds=600, max_seconds=600),
            ScheduleStep(ord=2, timer_seconds=3600, min_seconds=2700, max_seconds=5400),
            ScheduleStep(ord=3, timer_seconds=300, min_seconds=300, max_seconds=300),
            ScheduleStep(ord=4, timer_seconds=2700, min_seconds=1800, max_seconds=3600),
            ScheduleStep(ord=5, timer_seconds=0),
            ScheduleStep(ord=6, timer_seconds=2400, min_seconds=2100, max_seconds=2700),
            ScheduleStep(ord=7, timer_seconds=3600, min_seconds=1800, max_seconds=3600),
        ]
        result = calculate_schedule(steps, TARGET)

        # Expected: 600 + 3600 + 300 + 2700 + 0 + 2400 + 3600 = 13200s = 3h40m
        assert result.expected_total_seconds == 13200
        assert result.start_at == TARGET - timedelta(hours=3, minutes=40)

        # Min: 600 + 2700 + 300 + 1800 + 0 + 2100 + 1800 = 9300s = 2h35m
        assert result.min_total_seconds == 9300

        # Max: 600 + 5400 + 300 + 3600 + 0 + 2700 + 3600 = 16200s = 4h30m
        assert result.max_total_seconds == 16200

    def test_bread_with_parallel_preheat(self):
        """Oven preheating runs during final proof (parallelizable)."""
        steps = [
            ScheduleStep(ord=1, timer_seconds=600),   # Mix
            ScheduleStep(ord=2, timer_seconds=3600),   # Bulk ferment
            ScheduleStep(ord=3, timer_seconds=300),    # Shape
            ScheduleStep(ord=4, timer_seconds=2700),   # Final proof
            # Preheat during proof
            ScheduleStep(ord=5, timer_seconds=1800, parallelizable_with=[4]),
            ScheduleStep(ord=6, timer_seconds=2400),   # Bake
            ScheduleStep(ord=7, timer_seconds=3600),   # Cool
        ]
        result = calculate_schedule(steps, TARGET)

        # Preheat (1800s) is shorter than final proof (2700s), so absorbed.
        # Total = 600 + 3600 + 300 + 2700 + 0 + 2400 + 3600 = 13200
        assert result.expected_total_seconds == 13200
