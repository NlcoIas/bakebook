"""Cost service — pure computation, no DB access.

For each ingredient:
  1. If cost_override_per_kg is set, use it.
  2. Else if pantry_cost_per_kg is provided, use it.
  3. Else 0 (and flag as missing).

Cost per ingredient = grams / 1000 * cost_per_kg.
Sum for recipe total.  Per serving = total / servings.
"""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from decimal import Decimal

ZERO = Decimal(0)
ONE_THOUSAND = Decimal(1000)


@dataclass(frozen=True)
class CostIngredient:
    """Minimal ingredient representation for cost calculation.

    Only ``grams``, ``cost_override_per_kg``, and ``pantry_cost_per_kg``
    matter to the cost logic.  ``name`` is carried through for warnings.
    """

    name: str
    grams: Decimal | None
    cost_override_per_kg: Decimal | None = None
    pantry_cost_per_kg: Decimal | None = None


@dataclass(frozen=True)
class IngredientCost:
    """Cost result for a single ingredient."""

    name: str
    grams: Decimal | None
    cost_per_kg: Decimal
    cost: Decimal
    source: str  # 'override' | 'pantry' | 'missing'


@dataclass(frozen=True)
class CostResult:
    """Aggregate cost result for a recipe."""

    total_cost: Decimal
    per_serving_cost: Decimal
    ingredient_costs: list[IngredientCost]
    warnings: list[str]
    top_contributors: list[IngredientCost]


def _resolve_cost_per_kg(
    ingredient: CostIngredient,
) -> tuple[Decimal, str]:
    """Return (cost_per_kg, source) for a single ingredient."""
    if ingredient.cost_override_per_kg is not None:
        return ingredient.cost_override_per_kg, "override"
    if ingredient.pantry_cost_per_kg is not None:
        return ingredient.pantry_cost_per_kg, "pantry"
    return ZERO, "missing"


def _ingredient_cost(grams: Decimal | None, cost_per_kg: Decimal) -> Decimal:
    """Compute cost from grams and cost-per-kg."""
    if grams is None or grams == ZERO:
        return ZERO
    return grams / ONE_THOUSAND * cost_per_kg


def calculate_cost(
    ingredients: Sequence[CostIngredient],
    servings: int = 1,
) -> CostResult:
    """Calculate cost for a recipe.

    Parameters
    ----------
    ingredients:
        The ingredient list with gram weights and optional cost sources.
    servings:
        Number of servings the recipe yields (must be >= 1).

    Returns
    -------
    A ``CostResult`` with total, per-serving, per-ingredient costs,
    warnings for ingredients missing cost data, and the top 4 cost
    contributors sorted descending by cost.
    """
    if servings < 1:
        raise ValueError("servings must be >= 1")

    ingredient_costs: list[IngredientCost] = []
    warnings: list[str] = []
    total = ZERO

    for ing in ingredients:
        cost_per_kg, source = _resolve_cost_per_kg(ing)

        if source == "missing" and ing.grams is not None and ing.grams > ZERO:
            warnings.append(f"Missing cost data for '{ing.name}'")

        cost = _ingredient_cost(ing.grams, cost_per_kg)
        total += cost

        ingredient_costs.append(
            IngredientCost(
                name=ing.name,
                grams=ing.grams,
                cost_per_kg=cost_per_kg,
                cost=cost,
                source=source,
            )
        )

    per_serving = total / Decimal(servings)

    # Top contributors: sort by cost descending, take up to 4 non-zero.
    top_contributors = sorted(
        (ic for ic in ingredient_costs if ic.cost > ZERO),
        key=lambda ic: ic.cost,
        reverse=True,
    )[:4]

    return CostResult(
        total_cost=total,
        per_serving_cost=per_serving,
        ingredient_costs=ingredient_costs,
        warnings=warnings,
        top_contributors=top_contributors,
    )
