"""Comprehensive tests for the scaling service."""

from decimal import Decimal

import pytest

from app.services.scaling import (
    Ingredient,
    ScaleMode,
    ScalingError,
    scale,
)

# ---------------------------------------------------------------------------
# Fixtures / helpers
# ---------------------------------------------------------------------------

def _bread_ingredients() -> list[Ingredient]:
    """A simple bread recipe: flour, water, salt, yeast."""
    return [
        Ingredient(id="1", name="Bread flour", grams=Decimal("500"), role="flour"),
        Ingredient(id="2", name="Water", grams=Decimal("350"), role="water"),
        Ingredient(id="3", name="Salt", grams=Decimal("10"), role="salt"),
        Ingredient(id="4", name="Instant yeast", grams=Decimal("5"), role="leaven"),
    ]


def _no_flour_ingredients() -> list[Ingredient]:
    """Ingredients with no flour role — e.g. a sauce."""
    return [
        Ingredient(id="1", name="Butter", grams=Decimal("100"), role="fat"),
        Ingredient(id="2", name="Sugar", grams=Decimal("50"), role="sugar"),
        Ingredient(id="3", name="Milk", grams=Decimal("200"), role="dairy"),
    ]


def _ingredients_with_none_grams() -> list[Ingredient]:
    """Some ingredients lack gram values (e.g. 'a pinch of')."""
    return [
        Ingredient(id="1", name="Bread flour", grams=Decimal("500"), role="flour"),
        Ingredient(id="2", name="Water", grams=Decimal("350"), role="water"),
        Ingredient(id="3", name="Salt", grams=None, role="salt"),
        Ingredient(id="4", name="Vanilla extract", grams=None, role="other"),
    ]


# ---------------------------------------------------------------------------
# Multiplier mode
# ---------------------------------------------------------------------------

class TestMultiplierMode:
    def test_double(self):
        result = scale(_bread_ingredients(), ScaleMode.MULTIPLIER, Decimal("2"))
        assert result[0].grams == Decimal("1000")  # flour
        assert result[1].grams == Decimal("700")    # water
        assert result[2].grams == Decimal("20")     # salt
        assert result[3].grams == Decimal("10")     # yeast

    def test_half(self):
        result = scale(_bread_ingredients(), ScaleMode.MULTIPLIER, Decimal("0.5"))
        assert result[0].grams == Decimal("250.0")
        assert result[1].grams == Decimal("175.0")
        assert result[2].grams == Decimal("5.0")
        assert result[3].grams == Decimal("2.5")

    def test_identity(self):
        """Multiplier of 1 returns the same gram values."""
        ingredients = _bread_ingredients()
        result = scale(ingredients, ScaleMode.MULTIPLIER, Decimal("1"))
        for orig, scaled in zip(ingredients, result):
            assert scaled.grams == orig.grams
            assert scaled.original_grams == orig.grams

    def test_zero(self):
        """Multiplier of 0 zeros out all gram values."""
        result = scale(_bread_ingredients(), ScaleMode.MULTIPLIER, Decimal("0"))
        for item in result:
            assert item.grams == Decimal("0")

    def test_fractional(self):
        result = scale(_bread_ingredients(), ScaleMode.MULTIPLIER, Decimal("1.5"))
        assert result[0].grams == Decimal("750.0")
        assert result[1].grams == Decimal("525.0")

    def test_preserves_original_grams(self):
        result = scale(_bread_ingredients(), ScaleMode.MULTIPLIER, Decimal("3"))
        assert result[0].original_grams == Decimal("500")
        assert result[0].grams == Decimal("1500")

    def test_preserves_metadata(self):
        """id, name, and role are carried through."""
        result = scale(_bread_ingredients(), ScaleMode.MULTIPLIER, Decimal("2"))
        assert result[0].id == "1"
        assert result[0].name == "Bread flour"
        assert result[0].role == "flour"

    def test_string_mode(self):
        """Mode can be passed as a plain string."""
        result = scale(_bread_ingredients(), "multiplier", Decimal("2"))
        assert result[0].grams == Decimal("1000")

    def test_none_grams_left_as_none(self):
        """Ingredients without gram values are unchanged."""
        result = scale(_ingredients_with_none_grams(), ScaleMode.MULTIPLIER, Decimal("2"))
        assert result[0].grams == Decimal("1000")  # flour scaled
        assert result[2].grams is None              # salt was None, stays None
        assert result[3].grams is None              # vanilla was None, stays None
        assert result[2].original_grams is None


# ---------------------------------------------------------------------------
# Dough weight mode
# ---------------------------------------------------------------------------

class TestDoughWeightMode:
    def test_basic(self):
        """Scale so total dough weight equals the target."""
        ingredients = _bread_ingredients()
        total = sum(i.grams for i in ingredients if i.grams is not None)
        assert total == Decimal("865")  # sanity check

        target = Decimal("1730")  # double
        result = scale(ingredients, ScaleMode.DOUGH_WEIGHT, target)

        scaled_total = sum(r.grams for r in result if r.grams is not None)
        assert scaled_total == target

    def test_scale_down(self):
        """Scale to half the original dough weight."""
        ingredients = _bread_ingredients()
        target = Decimal("432.5")
        result = scale(ingredients, ScaleMode.DOUGH_WEIGHT, target)

        scaled_total = sum(r.grams for r in result if r.grams is not None)
        assert scaled_total == target

    def test_same_weight(self):
        """Target equals current weight — no change."""
        ingredients = _bread_ingredients()
        total = sum(i.grams for i in ingredients if i.grams is not None)
        result = scale(ingredients, ScaleMode.DOUGH_WEIGHT, total)

        for orig, scaled in zip(ingredients, result):
            assert scaled.grams == orig.grams

    def test_preserves_ratios(self):
        """Internal ratios stay the same after scaling."""
        ingredients = _bread_ingredients()
        result = scale(ingredients, ScaleMode.DOUGH_WEIGHT, Decimal("1730"))

        # Hydration ratio should be preserved
        original_hydration = Decimal("350") / Decimal("500")
        scaled_hydration = result[1].grams / result[0].grams
        assert scaled_hydration == original_hydration

    def test_with_none_grams(self):
        """None-gram ingredients are excluded from the total and left unchanged."""
        ingredients = _ingredients_with_none_grams()
        # Only flour (500) + water (350) = 850 count toward total
        target = Decimal("1700")  # double
        result = scale(ingredients, ScaleMode.DOUGH_WEIGHT, target)

        assert result[0].grams == Decimal("1000")  # flour doubled
        assert result[1].grams == Decimal("700")    # water doubled
        assert result[2].grams is None              # still None
        assert result[3].grams is None              # still None

    def test_zero_total_weight_raises(self):
        """If all grams are None or zero, cannot compute multiplier."""
        ingredients = [
            Ingredient(id="1", name="Salt", grams=None, role="salt"),
            Ingredient(id="2", name="Pepper", grams=None, role="other"),
        ]
        with pytest.raises(ScalingError, match="total ingredient weight is zero"):
            scale(ingredients, ScaleMode.DOUGH_WEIGHT, Decimal("500"))

    def test_all_zero_grams_raises(self):
        ingredients = [
            Ingredient(id="1", name="Flour", grams=Decimal("0"), role="flour"),
            Ingredient(id="2", name="Water", grams=Decimal("0"), role="water"),
        ]
        with pytest.raises(ScalingError, match="total ingredient weight is zero"):
            scale(ingredients, ScaleMode.DOUGH_WEIGHT, Decimal("500"))

    def test_string_mode(self):
        result = scale(_bread_ingredients(), "doughWeight", Decimal("1730"))
        scaled_total = sum(r.grams for r in result if r.grams is not None)
        assert scaled_total == Decimal("1730")


# ---------------------------------------------------------------------------
# Flour weight mode
# ---------------------------------------------------------------------------

class TestFlourWeightMode:
    def test_basic(self):
        """Scale so total flour weight equals the target."""
        ingredients = _bread_ingredients()
        target = Decimal("1000")  # double the flour
        result = scale(ingredients, ScaleMode.FLOUR_WEIGHT, target)

        assert result[0].grams == Decimal("1000")  # flour
        assert result[1].grams == Decimal("700")    # water doubles too
        assert result[2].grams == Decimal("20")     # salt
        assert result[3].grams == Decimal("10")     # yeast

    def test_scale_down(self):
        target = Decimal("250")  # half the flour
        result = scale(_bread_ingredients(), ScaleMode.FLOUR_WEIGHT, target)
        assert result[0].grams == Decimal("250.0")
        assert result[1].grams == Decimal("175.0")

    def test_multiple_flours(self):
        """When multiple ingredients have role='flour', all are summed."""
        ingredients = [
            Ingredient(id="1", name="Bread flour", grams=Decimal("400"), role="flour"),
            Ingredient(id="2", name="Whole wheat", grams=Decimal("100"), role="flour"),
            Ingredient(id="3", name="Water", grams=Decimal("350"), role="water"),
            Ingredient(id="4", name="Salt", grams=Decimal("10"), role="salt"),
        ]
        # Flour total = 400 + 100 = 500
        target = Decimal("1000")  # double
        result = scale(ingredients, ScaleMode.FLOUR_WEIGHT, target)

        assert result[0].grams == Decimal("800")   # bread flour
        assert result[1].grams == Decimal("200")   # whole wheat
        assert result[2].grams == Decimal("700")   # water
        assert result[3].grams == Decimal("20")    # salt

    def test_no_flour_raises(self):
        """If no ingredient has role='flour', raise ScalingError."""
        with pytest.raises(ScalingError, match="no ingredients with role 'flour'"):
            scale(_no_flour_ingredients(), ScaleMode.FLOUR_WEIGHT, Decimal("500"))

    def test_flour_with_zero_grams_raises(self):
        """Flour ingredients with zero grams are effectively absent."""
        ingredients = [
            Ingredient(id="1", name="Flour", grams=Decimal("0"), role="flour"),
            Ingredient(id="2", name="Water", grams=Decimal("350"), role="water"),
        ]
        with pytest.raises(ScalingError, match="no ingredients with role 'flour'"):
            scale(ingredients, ScaleMode.FLOUR_WEIGHT, Decimal("500"))

    def test_with_none_grams(self):
        """None-gram ingredients are left unchanged; flour with grams is used."""
        ingredients = _ingredients_with_none_grams()
        # Flour = 500
        target = Decimal("1000")
        result = scale(ingredients, ScaleMode.FLOUR_WEIGHT, target)

        assert result[0].grams == Decimal("1000")  # flour doubled
        assert result[1].grams == Decimal("700")    # water doubled
        assert result[2].grams is None              # salt None
        assert result[3].grams is None              # vanilla None

    def test_string_mode(self):
        result = scale(_bread_ingredients(), "flourWeight", Decimal("1000"))
        assert result[0].grams == Decimal("1000")


# ---------------------------------------------------------------------------
# Edge cases
# ---------------------------------------------------------------------------

class TestEdgeCases:
    def test_empty_ingredient_list_multiplier(self):
        """Empty list produces empty result."""
        result = scale([], ScaleMode.MULTIPLIER, Decimal("2"))
        assert result == []

    def test_empty_ingredient_list_dough_weight_raises(self):
        with pytest.raises(ScalingError):
            scale([], ScaleMode.DOUGH_WEIGHT, Decimal("500"))

    def test_empty_ingredient_list_flour_weight_raises(self):
        with pytest.raises(ScalingError):
            scale([], ScaleMode.FLOUR_WEIGHT, Decimal("500"))

    def test_invalid_mode_string(self):
        with pytest.raises(ValueError):
            scale(_bread_ingredients(), "badMode", Decimal("2"))

    def test_very_large_multiplier(self):
        result = scale(_bread_ingredients(), ScaleMode.MULTIPLIER, Decimal("1000"))
        assert result[0].grams == Decimal("500000")

    def test_very_small_multiplier(self):
        result = scale(_bread_ingredients(), ScaleMode.MULTIPLIER, Decimal("0.001"))
        assert result[0].grams == Decimal("0.500")

    def test_single_ingredient(self):
        ingredients = [Ingredient(id="1", name="Flour", grams=Decimal("500"), role="flour")]
        result = scale(ingredients, ScaleMode.FLOUR_WEIGHT, Decimal("750"))
        assert result[0].grams == Decimal("750.0")

    def test_result_is_new_list(self):
        """Scaling returns a new list; original ingredients are not mutated."""
        ingredients = _bread_ingredients()
        original_grams = [i.grams for i in ingredients]
        scale(ingredients, ScaleMode.MULTIPLIER, Decimal("3"))
        for orig, expected in zip(ingredients, original_grams):
            assert orig.grams == expected

    def test_all_none_grams_multiplier(self):
        """Multiplier mode with all-None grams just passes through."""
        ingredients = [
            Ingredient(id="1", name="Salt", grams=None, role="salt"),
            Ingredient(id="2", name="Pepper", grams=None, role="other"),
        ]
        result = scale(ingredients, ScaleMode.MULTIPLIER, Decimal("5"))
        assert all(r.grams is None for r in result)

    def test_frozen_dataclasses(self):
        """Ingredient and ScaledIngredient are immutable."""
        ing = Ingredient(id="1", name="Flour", grams=Decimal("500"), role="flour")
        with pytest.raises(AttributeError):
            ing.grams = Decimal("600")  # type: ignore[misc]

        result = scale([ing], ScaleMode.MULTIPLIER, Decimal("2"))
        with pytest.raises(AttributeError):
            result[0].grams = Decimal("999")  # type: ignore[misc]
