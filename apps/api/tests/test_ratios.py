"""Tests for baker's ratio calculations (apps/api/app/services/ratios.py).

Each test constructs lightweight ingredient stubs — no DB required.
"""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal

import pytest

from app.services.ratios import BakerRatios, compute_ratios

# ---------------------------------------------------------------------------
# Stub ingredient that satisfies IngredientLike
# ---------------------------------------------------------------------------

@dataclass
class Ing:
    grams: Decimal | None
    role: str | None = None
    leaven_flour_pct: Decimal | None = None


def _d(v: str | int | float) -> Decimal:
    return Decimal(str(v))


# ---------------------------------------------------------------------------
# 1. Basic bread: flour, water, salt, yeast
# ---------------------------------------------------------------------------

class TestBasicBread:
    """Simple lean dough: 500 g flour, 325 g water, 10 g salt, 5 g yeast (other)."""

    @pytest.fixture()
    def ratios(self) -> BakerRatios:
        ingredients = [
            Ing(grams=_d(500), role="flour"),
            Ing(grams=_d(325), role="water"),
            Ing(grams=_d(10), role="salt"),
            Ing(grams=_d(5), role="other"),  # instant yeast, role='other'
        ]
        result = compute_ratios(ingredients)
        assert result is not None
        return result

    def test_flour_total(self, ratios: BakerRatios) -> None:
        assert ratios.flour_total_g == _d("500.00")

    def test_hydration(self, ratios: BakerRatios) -> None:
        # 325/500 = 65%
        assert ratios.hydration == _d("65.00")

    def test_hydration_with_dairy_equals_hydration(self, ratios: BakerRatios) -> None:
        # No dairy → both values identical
        assert ratios.hydration_with_dairy == _d("65.00")

    def test_salt(self, ratios: BakerRatios) -> None:
        # 10/500 = 2%
        assert ratios.salt_pct == _d("2.00")

    def test_sugar(self, ratios: BakerRatios) -> None:
        assert ratios.sugar_pct == _d("0.00")

    def test_fat(self, ratios: BakerRatios) -> None:
        assert ratios.fat_pct == _d("0.00")

    def test_prefermented_flour(self, ratios: BakerRatios) -> None:
        assert ratios.prefermented_flour_pct == _d("0.00")

    def test_inoculation_rate(self, ratios: BakerRatios) -> None:
        assert ratios.inoculation_rate == _d("0.00")


# ---------------------------------------------------------------------------
# 2. Enriched dough: flour, water, butter, sugar, eggs
# ---------------------------------------------------------------------------

class TestEnrichedDough:
    """Brioche-style: 500 g flour, 150 g water, 125 g butter (fat),
    75 g sugar, 100 g eggs (egg role → treated as 'other' for ratios),
    10 g salt.
    """

    @pytest.fixture()
    def ratios(self) -> BakerRatios:
        ingredients = [
            Ing(grams=_d(500), role="flour"),
            Ing(grams=_d(150), role="water"),
            Ing(grams=_d(125), role="fat"),
            Ing(grams=_d(75), role="sugar"),
            Ing(grams=_d(100), role="egg"),
            Ing(grams=_d(10), role="salt"),
        ]
        result = compute_ratios(ingredients)
        assert result is not None
        return result

    def test_hydration(self, ratios: BakerRatios) -> None:
        # 150/500 = 30%
        assert ratios.hydration == _d("30.00")

    def test_fat(self, ratios: BakerRatios) -> None:
        # 125/500 = 25%
        assert ratios.fat_pct == _d("25.00")

    def test_sugar(self, ratios: BakerRatios) -> None:
        # 75/500 = 15%
        assert ratios.sugar_pct == _d("15.00")

    def test_salt(self, ratios: BakerRatios) -> None:
        # 10/500 = 2%
        assert ratios.salt_pct == _d("2.00")


# ---------------------------------------------------------------------------
# 3. With sourdough leaven (role='leaven', leaven_flour_pct=50)
# ---------------------------------------------------------------------------

class TestSourdoughLeaven:
    """500 g flour, 325 g water, 10 g salt, 100 g sourdough starter at 100% hydration
    (leaven_flour_pct=50 → 50 g flour from leaven).
    """

    @pytest.fixture()
    def ratios(self) -> BakerRatios:
        ingredients = [
            Ing(grams=_d(500), role="flour"),
            Ing(grams=_d(325), role="water"),
            Ing(grams=_d(10), role="salt"),
            Ing(grams=_d(100), role="leaven", leaven_flour_pct=_d(50)),
        ]
        result = compute_ratios(ingredients)
        assert result is not None
        return result

    def test_flour_total_includes_leaven_flour(self, ratios: BakerRatios) -> None:
        # 500 + 100*0.50 = 550
        assert ratios.flour_total_g == _d("550.00")

    def test_hydration(self, ratios: BakerRatios) -> None:
        # 325 / 550 ≈ 59.09%
        assert ratios.hydration == _d("59.09")

    def test_prefermented_flour(self, ratios: BakerRatios) -> None:
        # 50 / 550 ≈ 9.09%
        assert ratios.prefermented_flour_pct == _d("9.09")

    def test_inoculation_rate(self, ratios: BakerRatios) -> None:
        # 100 / 550 ≈ 18.18%
        assert ratios.inoculation_rate == _d("18.18")

    def test_salt(self, ratios: BakerRatios) -> None:
        # 10 / 550 ≈ 1.82%
        assert ratios.salt_pct == _d("1.82")


# ---------------------------------------------------------------------------
# 4. With dairy (buttermilk)
# ---------------------------------------------------------------------------

class TestWithDairy:
    """500 g flour, 200 g water, 200 g buttermilk (dairy), 10 g salt."""

    @pytest.fixture()
    def ratios(self) -> BakerRatios:
        ingredients = [
            Ing(grams=_d(500), role="flour"),
            Ing(grams=_d(200), role="water"),
            Ing(grams=_d(200), role="dairy"),
            Ing(grams=_d(10), role="salt"),
        ]
        result = compute_ratios(ingredients)
        assert result is not None
        return result

    def test_hydration_without_dairy(self, ratios: BakerRatios) -> None:
        # 200/500 = 40%
        assert ratios.hydration == _d("40.00")

    def test_hydration_with_dairy(self, ratios: BakerRatios) -> None:
        # (200 + 200*0.90) / 500 = (200 + 180) / 500 = 76%
        assert ratios.hydration_with_dairy == _d("76.00")


# ---------------------------------------------------------------------------
# 5. No flour ingredients → returns None
# ---------------------------------------------------------------------------

class TestNoFlour:
    """Recipes with no flour role should return None."""

    def test_all_other_roles(self) -> None:
        ingredients = [
            Ing(grams=_d(200), role="water"),
            Ing(grams=_d(100), role="sugar"),
            Ing(grams=_d(50), role="fat"),
        ]
        assert compute_ratios(ingredients) is None

    def test_empty_list(self) -> None:
        assert compute_ratios([]) is None

    def test_none_roles(self) -> None:
        ingredients = [
            Ing(grams=_d(500), role=None),
            Ing(grams=_d(300), role=None),
        ]
        assert compute_ratios(ingredients) is None

    def test_flour_with_zero_grams(self) -> None:
        """Flour role present but 0 g → still None (avoid division by zero)."""
        ingredients = [
            Ing(grams=_d(0), role="flour"),
            Ing(grams=_d(300), role="water"),
        ]
        assert compute_ratios(ingredients) is None

    def test_flour_with_none_grams(self) -> None:
        """Flour role present but grams=None → still None."""
        ingredients = [
            Ing(grams=None, role="flour"),
            Ing(grams=_d(300), role="water"),
        ]
        assert compute_ratios(ingredients) is None


# ---------------------------------------------------------------------------
# 6. Multiple flour types (bread flour + whole wheat)
# ---------------------------------------------------------------------------

class TestMultipleFlours:
    """400 g bread flour + 100 g whole wheat = 500 g total flour."""

    @pytest.fixture()
    def ratios(self) -> BakerRatios:
        ingredients = [
            Ing(grams=_d(400), role="flour"),   # bread flour
            Ing(grams=_d(100), role="flour"),   # whole wheat
            Ing(grams=_d(350), role="water"),
            Ing(grams=_d(10), role="salt"),
        ]
        result = compute_ratios(ingredients)
        assert result is not None
        return result

    def test_flour_total_sums_all_flours(self, ratios: BakerRatios) -> None:
        assert ratios.flour_total_g == _d("500.00")

    def test_hydration(self, ratios: BakerRatios) -> None:
        # 350/500 = 70%
        assert ratios.hydration == _d("70.00")

    def test_salt(self, ratios: BakerRatios) -> None:
        # 10/500 = 2%
        assert ratios.salt_pct == _d("2.00")


# ---------------------------------------------------------------------------
# Edge cases
# ---------------------------------------------------------------------------

class TestEdgeCases:
    """Various boundary conditions."""

    def test_leaven_defaults_to_50_pct_when_none(self) -> None:
        """leaven_flour_pct=None should default to 50 (per schema default)."""
        ingredients = [
            Ing(grams=_d(500), role="flour"),
            Ing(grams=_d(300), role="water"),
            Ing(grams=_d(100), role="leaven", leaven_flour_pct=None),
        ]
        result = compute_ratios(ingredients)
        assert result is not None
        # flour_total = 500 + 100*0.50 = 550
        assert result.flour_total_g == _d("550.00")

    def test_multiple_leavens(self) -> None:
        """Two leaven entries with different flour percentages."""
        ingredients = [
            Ing(grams=_d(500), role="flour"),
            Ing(grams=_d(300), role="water"),
            Ing(grams=_d(80), role="leaven", leaven_flour_pct=_d(50)),   # 40 g flour
            # 20 g flour (stiff starter)
            Ing(grams=_d(20), role="leaven", leaven_flour_pct=_d(100)),
        ]
        result = compute_ratios(ingredients)
        assert result is not None
        # flour_total = 500 + 40 + 20 = 560
        assert result.flour_total_g == _d("560.00")
        # inoculation = 100/560 ≈ 17.86%
        assert result.inoculation_rate == _d("17.86")
        # prefermented = 60/560 ≈ 10.71%
        assert result.prefermented_flour_pct == _d("10.71")

    def test_ingredients_with_none_grams_skipped(self) -> None:
        """Ingredients with grams=None should contribute 0."""
        ingredients = [
            Ing(grams=_d(500), role="flour"),
            Ing(grams=None, role="water"),
            Ing(grams=_d(10), role="salt"),
        ]
        result = compute_ratios(ingredients)
        assert result is not None
        assert result.hydration == _d("0.00")

    def test_combined_enriched_sourdough_dairy(self) -> None:
        """Full-featured recipe: flour, water, leaven, dairy, fat, sugar, salt."""
        ingredients = [
            Ing(grams=_d(450), role="flour"),
            Ing(grams=_d(200), role="water"),
            Ing(grams=_d(100), role="leaven", leaven_flour_pct=_d(50)),  # 50 g flour
            Ing(grams=_d(150), role="dairy"),     # buttermilk
            Ing(grams=_d(50), role="fat"),        # butter
            Ing(grams=_d(30), role="sugar"),
            Ing(grams=_d(9), role="salt"),
        ]
        result = compute_ratios(ingredients)
        assert result is not None
        # flour_total = 450 + 50 = 500
        assert result.flour_total_g == _d("500.00")
        # hydration = 200/500 = 40%
        assert result.hydration == _d("40.00")
        # hydration_with_dairy = (200 + 150*0.90)/500 = (200+135)/500 = 335/500 = 67%
        assert result.hydration_with_dairy == _d("67.00")
        # fat = 50/500 = 10%
        assert result.fat_pct == _d("10.00")
        # sugar = 30/500 = 6%
        assert result.sugar_pct == _d("6.00")
        # salt = 9/500 = 1.80%
        assert result.salt_pct == _d("1.80")
        # prefermented = 50/500 = 10%
        assert result.prefermented_flour_pct == _d("10.00")
        # inoculation = 100/500 = 20%
        assert result.inoculation_rate == _d("20.00")
