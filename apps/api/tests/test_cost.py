"""Tests for the cost calculation service."""

from decimal import Decimal

import pytest

from app.services.cost import CostIngredient, calculate_cost

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

D = Decimal


def _ing(
    name: str,
    grams: Decimal | None,
    *,
    override: Decimal | None = None,
    pantry: Decimal | None = None,
) -> CostIngredient:
    return CostIngredient(
        name=name,
        grams=grams,
        cost_override_per_kg=override,
        pantry_cost_per_kg=pantry,
    )


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


class TestSimpleRecipe:
    """A straightforward recipe where every ingredient has a known cost."""

    def test_total_and_per_ingredient(self):
        ingredients = [
            _ing("Bread flour", D("500"), pantry=D("2.00")),   # 500/1000 * 2 = 1.00
            _ing("Water", D("350"), pantry=D("0.00")),          # 0
            _ing("Salt", D("10"), pantry=D("1.50")),            # 10/1000 * 1.5 = 0.015
            _ing("Yeast", D("5"), pantry=D("20.00")),           # 5/1000 * 20 = 0.10
        ]
        result = calculate_cost(ingredients, servings=1)

        assert result.total_cost == D("1.115")
        assert len(result.ingredient_costs) == 4
        assert result.ingredient_costs[0].cost == D("1.000")
        assert result.ingredient_costs[0].source == "pantry"
        assert result.ingredient_costs[1].cost == D("0.000")
        assert result.ingredient_costs[2].cost == D("0.015")
        assert result.ingredient_costs[3].cost == D("0.100")
        assert result.warnings == []


class TestOverridePrecedence:
    """cost_override_per_kg takes precedence over pantry_cost_per_kg."""

    def test_override_wins(self):
        ing = _ing("Fancy flour", D("500"), override=D("5.00"), pantry=D("2.00"))
        result = calculate_cost([ing], servings=1)

        # 500/1000 * 5 = 2.50  (not 1.00)
        assert result.ingredient_costs[0].cost == D("2.500")
        assert result.ingredient_costs[0].source == "override"
        assert result.total_cost == D("2.500")

    def test_override_only_no_pantry(self):
        ing = _ing("Custom mix", D("200"), override=D("8.00"))
        result = calculate_cost([ing], servings=1)

        assert result.ingredient_costs[0].cost == D("1.600")
        assert result.ingredient_costs[0].source == "override"


class TestMissingCost:
    """Ingredients with no cost data are flagged and counted as zero."""

    def test_warning_emitted(self):
        ingredients = [
            _ing("Bread flour", D("500"), pantry=D("2.00")),
            _ing("Mystery ingredient", D("100")),
        ]
        result = calculate_cost(ingredients, servings=1)

        assert len(result.warnings) == 1
        assert "Mystery ingredient" in result.warnings[0]
        assert result.ingredient_costs[1].cost == D("0")
        assert result.ingredient_costs[1].source == "missing"
        # Total should only reflect flour
        assert result.total_cost == D("1.000")

    def test_multiple_missing(self):
        ingredients = [
            _ing("Unknown A", D("50")),
            _ing("Unknown B", D("100")),
        ]
        result = calculate_cost(ingredients, servings=1)

        assert len(result.warnings) == 2
        assert result.total_cost == D("0")

    def test_no_warning_for_zero_gram_missing_cost(self):
        """An ingredient with zero grams and no cost data should not warn."""
        ing = _ing("Garnish", D("0"))
        result = calculate_cost([ing], servings=1)

        assert result.warnings == []
        assert result.ingredient_costs[0].source == "missing"
        assert result.ingredient_costs[0].cost == D("0")

    def test_no_warning_for_none_gram_missing_cost(self):
        """An ingredient with None grams and no cost data should not warn."""
        ing = _ing("A pinch of magic", None)
        result = calculate_cost([ing], servings=1)

        assert result.warnings == []


class TestPerServing:
    """Per-serving cost divides total by servings count."""

    def test_even_division(self):
        ing = _ing("Flour", D("1000"), pantry=D("2.00"))  # cost = 2.00
        result = calculate_cost([ing], servings=4)

        assert result.total_cost == D("2.000")
        assert result.per_serving_cost == D("0.500")

    def test_single_serving(self):
        ing = _ing("Flour", D("500"), pantry=D("2.00"))
        result = calculate_cost([ing], servings=1)

        assert result.per_serving_cost == result.total_cost

    def test_many_servings(self):
        ing = _ing("Flour", D("500"), pantry=D("3.00"))  # cost = 1.50
        result = calculate_cost([ing], servings=12)

        assert result.per_serving_cost == D("1.500") / D("12")

    def test_invalid_servings(self):
        ing = _ing("Flour", D("500"), pantry=D("2.00"))
        with pytest.raises(ValueError, match="servings must be >= 1"):
            calculate_cost([ing], servings=0)


class TestZeroGrams:
    """Ingredients with zero or None grams should produce zero cost."""

    def test_zero_grams(self):
        ing = _ing("Decoration", D("0"), pantry=D("50.00"))
        result = calculate_cost([ing], servings=1)

        assert result.ingredient_costs[0].cost == D("0")
        assert result.total_cost == D("0")

    def test_none_grams(self):
        ing = _ing("A splash of vanilla", None, pantry=D("120.00"))
        result = calculate_cost([ing], servings=1)

        assert result.ingredient_costs[0].cost == D("0")
        assert result.total_cost == D("0")


class TestTopContributors:
    """Top 4 cost contributors, sorted descending by cost."""

    def test_top_4_sorted(self):
        ingredients = [
            _ing("Flour", D("500"), pantry=D("2.00")),       # 1.00
            _ing("Butter", D("200"), pantry=D("16.00")),      # 3.20
            _ing("Sugar", D("100"), pantry=D("1.50")),        # 0.15
            _ing("Eggs", D("150"), pantry=D("6.00")),         # 0.90
            _ing("Vanilla", D("5"), pantry=D("400.00")),      # 2.00
            _ing("Salt", D("10"), pantry=D("1.50")),          # 0.015
        ]
        result = calculate_cost(ingredients, servings=1)

        top = result.top_contributors
        assert len(top) == 4
        assert top[0].name == "Butter"
        assert top[0].cost == D("3.200")
        assert top[1].name == "Vanilla"
        assert top[1].cost == D("2.000")
        assert top[2].name == "Flour"
        assert top[2].cost == D("1.000")
        assert top[3].name == "Eggs"
        assert top[3].cost == D("0.900")

    def test_fewer_than_4_nonzero(self):
        ingredients = [
            _ing("Flour", D("500"), pantry=D("2.00")),       # 1.00
            _ing("Water", D("300"), pantry=D("0.00")),        # 0
            _ing("Salt", D("10"), pantry=D("1.50")),          # 0.015
        ]
        result = calculate_cost(ingredients, servings=1)

        top = result.top_contributors
        assert len(top) == 2
        assert top[0].name == "Flour"
        assert top[1].name == "Salt"

    def test_empty_ingredients(self):
        result = calculate_cost([], servings=1)

        assert result.total_cost == D("0")
        assert result.per_serving_cost == D("0")
        assert result.ingredient_costs == []
        assert result.top_contributors == []
        assert result.warnings == []
