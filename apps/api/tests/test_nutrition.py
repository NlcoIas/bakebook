"""Tests for the pure nutrition calculation service."""

from decimal import Decimal

import pytest

from app.services.nutrition import (
    IngredientInput,
    Macros,
    calculate_nutrition,
)

D = Decimal

# ---------------------------------------------------------------------------
# Shared fixtures
# ---------------------------------------------------------------------------

NUTRITION_TABLE: dict[str, dict[str, Decimal]] = {
    "bread_flour": {
        "kcal": D("340"),
        "protein": D("11"),
        "fat": D("1.5"),
        "carbs": D("72"),
        "sugar": D("0.3"),
        "fiber": D("2.4"),
        "salt": D("0"),
    },
    "butter": {
        "kcal": D("717"),
        "protein": D("0.85"),
        "fat": D("81"),
        "carbs": D("0.06"),
        "sugar": D("0.06"),
        "fiber": D("0"),
        "salt": D("0.01"),
    },
    "sugar": {
        "kcal": D("387"),
        "protein": D("0"),
        "fat": D("0"),
        "carbs": D("100"),
        "sugar": D("99.8"),
        "fiber": D("0"),
        "salt": D("0"),
    },
}


def _zero_macros() -> Macros:
    return Macros(
        kcal=D("0.00"),
        protein=D("0.00"),
        fat=D("0.00"),
        carbs=D("0.00"),
        sugar=D("0.00"),
        fiber=D("0.00"),
        salt=D("0.00"),
    )


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


class TestSimpleRecipe:
    """A recipe with known nutrition values looked up from the table."""

    def test_per_recipe_totals(self):
        ingredients = [
            IngredientInput(name="Bread flour", grams=D("500"), pantry_nutrition_ref="bread_flour"),
            IngredientInput(name="Butter", grams=D("100"), pantry_nutrition_ref="butter"),
        ]
        result = calculate_nutrition(ingredients, NUTRITION_TABLE, servings=1)

        # flour: 500/100 * 340 = 1700 kcal; butter: 100/100 * 717 = 717 kcal
        assert result.per_recipe.kcal == D("2417.00")
        # flour protein: 500/100 * 11 = 55; butter: 100/100 * 0.85 = 0.85
        assert result.per_recipe.protein == D("55.85")
        # flour fat: 500/100 * 1.5 = 7.5; butter: 100/100 * 81 = 81
        assert result.per_recipe.fat == D("88.50")
        assert result.warnings == []

    def test_per_serving(self):
        ingredients = [
            IngredientInput(name="Bread flour", grams=D("500"), pantry_nutrition_ref="bread_flour"),
            IngredientInput(name="Butter", grams=D("100"), pantry_nutrition_ref="butter"),
        ]
        result = calculate_nutrition(ingredients, NUTRITION_TABLE, servings=4)

        # 2417 / 4 = 604.25
        assert result.per_serving.kcal == D("604.25")
        # 55.85 / 4 = 13.9625 → 13.96
        assert result.per_serving.protein == D("13.96")

    def test_per_100g(self):
        ingredients = [
            IngredientInput(name="Bread flour", grams=D("500"), pantry_nutrition_ref="bread_flour"),
            IngredientInput(name="Butter", grams=D("100"), pantry_nutrition_ref="butter"),
        ]
        result = calculate_nutrition(ingredients, NUTRITION_TABLE, servings=1)

        assert result.per_100g is not None
        # total grams = 600.  kcal per 100g = 2417 / 600 * 100 = 402.8333… → 402.83
        assert result.per_100g.kcal == D("402.83")
        # fat per 100g = 88.5 / 600 * 100 = 14.75
        assert result.per_100g.fat == D("14.75")


class TestNutritionOverride:
    """Ingredient with a nutrition_override should use that instead of the table."""

    def test_override_takes_precedence(self):
        custom = {
            "kcal": D("400"),
            "protein": D("15"),
            "fat": D("5"),
            "carbs": D("70"),
            "sugar": D("1"),
            "fiber": D("3"),
            "salt": D("0.5"),
        }
        ingredients = [
            IngredientInput(
                name="Special flour",
                grams=D("200"),
                nutrition_override=custom,
                pantry_nutrition_ref="bread_flour",  # should be ignored
            ),
        ]
        result = calculate_nutrition(ingredients, NUTRITION_TABLE, servings=1)

        # 200/100 * 400 = 800 (from override, NOT 340 from table)
        assert result.per_recipe.kcal == D("800.00")
        assert result.per_recipe.protein == D("30.00")
        assert result.warnings == []


class TestMissingNutritionData:
    """Ingredients with no override and no table match should be flagged."""

    def test_warning_emitted(self):
        ingredients = [
            IngredientInput(name="Mystery powder", grams=D("50")),
        ]
        result = calculate_nutrition(ingredients, NUTRITION_TABLE, servings=1)

        assert result.per_recipe == _zero_macros()
        assert len(result.warnings) == 1
        assert "Mystery powder" in result.warnings[0]

    def test_missing_ref_not_in_table(self):
        ingredients = [
            IngredientInput(
                name="Rare spice",
                grams=D("10"),
                pantry_nutrition_ref="nonexistent_key",
            ),
        ]
        result = calculate_nutrition(ingredients, NUTRITION_TABLE, servings=1)

        assert result.per_recipe == _zero_macros()
        assert len(result.warnings) == 1
        assert "Rare spice" in result.warnings[0]

    def test_mixed_known_and_unknown(self):
        ingredients = [
            IngredientInput(name="Bread flour", grams=D("500"), pantry_nutrition_ref="bread_flour"),
            IngredientInput(name="Magic dust", grams=D("5")),
        ]
        result = calculate_nutrition(ingredients, NUTRITION_TABLE, servings=1)

        # Only flour contributes: 500/100 * 340 = 1700
        assert result.per_recipe.kcal == D("1700.00")
        assert len(result.warnings) == 1
        assert "Magic dust" in result.warnings[0]


class TestPerServingAndPer100g:
    """Verify per-serving and per-100 g math independently."""

    def test_single_ingredient(self):
        ingredients = [
            IngredientInput(name="Sugar", grams=D("200"), pantry_nutrition_ref="sugar"),
        ]
        result = calculate_nutrition(ingredients, NUTRITION_TABLE, servings=8)

        # total kcal = 200/100 * 387 = 774
        assert result.per_recipe.kcal == D("774.00")

        # per serving = 774 / 8 = 96.75
        assert result.per_serving.kcal == D("96.75")

        # per 100g = 774 / 200 * 100 = 387
        assert result.per_100g is not None
        assert result.per_100g.kcal == D("387.00")

        # per 100g of pure sugar should match the table entry
        assert result.per_100g.carbs == D("100.00")


class TestDailyValuePct:
    """Daily-value percentages computed from per-serving values."""

    def test_known_values(self):
        # Construct a recipe where per-serving values are easy to reason about.
        # 1 serving of 100g bread flour:
        # kcal=340, protein=11, fat=1.5, carbs=72
        ingredients = [
            IngredientInput(name="Bread flour", grams=D("100"), pantry_nutrition_ref="bread_flour"),
        ]
        result = calculate_nutrition(ingredients, NUTRITION_TABLE, servings=1)

        # kcal DV% = 340 / 2000 * 100 = 17.0
        assert result.daily_value_pct.kcal == D("17.0")
        # protein DV% = 11 / 50 * 100 = 22.0
        assert result.daily_value_pct.protein == D("22.0")
        # fat DV% = 1.5 / 75 * 100 = 2.0
        assert result.daily_value_pct.fat == D("2.0")
        # carbs DV% = 72 / 275 * 100 = 26.1818… → 26.2
        assert result.daily_value_pct.carbs == D("26.2")

    def test_multi_serving_dv(self):
        ingredients = [
            IngredientInput(name="Bread flour", grams=D("500"), pantry_nutrition_ref="bread_flour"),
        ]
        result = calculate_nutrition(ingredients, NUTRITION_TABLE, servings=5)

        # per-serving kcal = 1700 / 5 = 340 → DV% = 17.0 (same as 100g single-serving)
        assert result.daily_value_pct.kcal == D("17.0")


class TestZeroGramsIngredient:
    """Ingredients with 0 or None grams should contribute nothing."""

    def test_zero_grams(self):
        ingredients = [
            IngredientInput(name="Bread flour", grams=D("0"), pantry_nutrition_ref="bread_flour"),
            IngredientInput(name="Butter", grams=D("100"), pantry_nutrition_ref="butter"),
        ]
        result = calculate_nutrition(ingredients, NUTRITION_TABLE, servings=1)

        # Only butter contributes
        assert result.per_recipe.kcal == D("717.00")
        assert result.warnings == []

    def test_none_grams(self):
        ingredients = [
            IngredientInput(name="Bread flour", grams=None, pantry_nutrition_ref="bread_flour"),
            IngredientInput(name="Butter", grams=D("100"), pantry_nutrition_ref="butter"),
        ]
        result = calculate_nutrition(ingredients, NUTRITION_TABLE, servings=1)

        assert result.per_recipe.kcal == D("717.00")
        assert result.warnings == []

    def test_negative_grams_ignored(self):
        ingredients = [
            IngredientInput(name="Flour", grams=D("-50"), pantry_nutrition_ref="bread_flour"),
        ]
        result = calculate_nutrition(ingredients, NUTRITION_TABLE, servings=1)

        assert result.per_recipe == _zero_macros()


class TestEmptyRecipe:
    """A recipe with no ingredients."""

    def test_empty_list(self):
        result = calculate_nutrition([], NUTRITION_TABLE, servings=1)

        assert result.per_recipe == _zero_macros()
        assert result.per_serving == _zero_macros()
        assert result.per_100g is None  # total_grams is 0
        assert result.daily_value_pct.kcal == D("0")
        assert result.warnings == []

    def test_invalid_servings(self):
        with pytest.raises(ValueError, match="servings must be >= 1"):
            calculate_nutrition([], NUTRITION_TABLE, servings=0)
