"""Pure nutrition calculation service.

For each ingredient:
1. If nutrition_override is set, use it (per 100 g).
2. Else if pantry_nutrition_ref is set, look up in nutrition_table dict.
3. Else zero — and flag the ingredient name in warnings.

Sum per recipe, then divide for per-serving, per-100 g, and daily-value %.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from decimal import ROUND_HALF_UP, Decimal

# Fixed daily-value reference (CLAUDE.md §6.3).
DAILY_VALUE_KCAL = Decimal("2000")
DAILY_VALUE_FAT_G = Decimal("75")
DAILY_VALUE_CARBS_G = Decimal("275")
DAILY_VALUE_PROTEIN_G = Decimal("50")

MACRO_KEYS = ("kcal", "protein", "fat", "carbs", "sugar", "fiber", "salt")

_ZERO = Decimal("0")
_HUNDRED = Decimal("100")


# ---------------------------------------------------------------------------
# Input / output types
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class IngredientInput:
    """One ingredient row fed into the calculator."""

    name: str
    grams: Decimal | None  # None or 0 → contributes nothing
    nutrition_override: dict[str, Decimal] | None = None  # per 100 g
    pantry_nutrition_ref: str | None = None


@dataclass(frozen=True)
class Macros:
    """Nutrient totals for a single view (recipe / serving / 100 g)."""

    kcal: Decimal = _ZERO
    protein: Decimal = _ZERO
    fat: Decimal = _ZERO
    carbs: Decimal = _ZERO
    sugar: Decimal = _ZERO
    fiber: Decimal = _ZERO
    salt: Decimal = _ZERO


@dataclass(frozen=True)
class DailyValuePct:
    """Percentage of the daily-value reference for the *per-serving* macros."""

    kcal: Decimal = _ZERO
    protein: Decimal = _ZERO
    fat: Decimal = _ZERO
    carbs: Decimal = _ZERO


@dataclass(frozen=True)
class NutritionResult:
    per_recipe: Macros
    per_serving: Macros
    per_100g: Macros | None  # None when total recipe weight is 0
    daily_value_pct: DailyValuePct
    warnings: list[str] = field(default_factory=list)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _get_per_100g(
    ingredient: IngredientInput,
    nutrition_table: dict[str, dict[str, Decimal]],
) -> tuple[dict[str, Decimal], bool]:
    """Return (per-100 g dict, has_data).

    ``has_data`` is False when neither override nor table lookup succeeded.
    """
    if ingredient.nutrition_override is not None:
        return ingredient.nutrition_override, True

    if ingredient.pantry_nutrition_ref is not None:
        entry = nutrition_table.get(ingredient.pantry_nutrition_ref)
        if entry is not None:
            # Convert float values from JSON to Decimal
            return {k: Decimal(str(v)) for k, v in entry.items() if k in MACRO_KEYS}, True

    return {k: _ZERO for k in MACRO_KEYS}, False


def _scale(per_100g: dict[str, Decimal], grams: Decimal) -> dict[str, Decimal]:
    """Scale a per-100 g record by actual grams: ``grams / 100 * value``."""
    factor = grams / _HUNDRED
    return {k: per_100g.get(k, _ZERO) * factor for k in MACRO_KEYS}


def _sum_dicts(a: dict[str, Decimal], b: dict[str, Decimal]) -> dict[str, Decimal]:
    return {k: a.get(k, _ZERO) + b.get(k, _ZERO) for k in MACRO_KEYS}


def _dict_to_macros(d: dict[str, Decimal]) -> Macros:
    return Macros(**{k: _q(d.get(k, _ZERO)) for k in MACRO_KEYS})


def _q(value: Decimal) -> Decimal:
    """Quantize to 2 decimal places."""
    return value.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def _dv_pct(value: Decimal, reference: Decimal) -> Decimal:
    """Compute daily-value percentage, quantized to 1 decimal place."""
    if reference == _ZERO:
        return _ZERO
    return (value / reference * _HUNDRED).quantize(
        Decimal("0.1"), rounding=ROUND_HALF_UP
    )


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def calculate_nutrition(
    ingredients: list[IngredientInput],
    nutrition_table: dict[str, dict[str, Decimal]],
    servings: int,
) -> NutritionResult:
    """Compute nutrition totals for a recipe.

    Parameters
    ----------
    ingredients:
        List of ingredient inputs.
    nutrition_table:
        Mapping from ref key to ``{kcal, protein, fat, carbs, sugar, fiber, salt}``
        values per 100 g.  Loaded from ``nutrition.json`` at startup.
    servings:
        Number of servings the recipe yields.  Must be >= 1.

    Returns
    -------
    NutritionResult
        Totals per recipe, per serving, per 100 g, daily-value %, and warnings.
    """
    if servings < 1:
        raise ValueError("servings must be >= 1")

    total: dict[str, Decimal] = {k: _ZERO for k in MACRO_KEYS}
    total_grams = _ZERO
    warnings: list[str] = []

    for ing in ingredients:
        grams = ing.grams if ing.grams is not None else _ZERO
        if grams <= _ZERO:
            continue

        per_100g, has_data = _get_per_100g(ing, nutrition_table)
        if not has_data:
            warnings.append(
                f"No nutrition data for '{ing.name}'; counted as zero."
            )

        contribution = _scale(per_100g, grams)
        total = _sum_dicts(total, contribution)
        total_grams += grams

    per_recipe = _dict_to_macros(total)

    # Per serving
    servings_d = Decimal(servings)
    per_serving_dict = {k: total[k] / servings_d for k in MACRO_KEYS}
    per_serving = _dict_to_macros(per_serving_dict)

    # Per 100 g
    if total_grams > _ZERO:
        per_100g_dict = {k: total[k] / total_grams * _HUNDRED for k in MACRO_KEYS}
        per_100g_macros: Macros | None = _dict_to_macros(per_100g_dict)
    else:
        per_100g_macros = None

    # Daily-value % (based on per-serving values, before quantization)
    daily_value_pct = DailyValuePct(
        kcal=_dv_pct(per_serving_dict["kcal"], DAILY_VALUE_KCAL),
        protein=_dv_pct(per_serving_dict["protein"], DAILY_VALUE_PROTEIN_G),
        fat=_dv_pct(per_serving_dict["fat"], DAILY_VALUE_FAT_G),
        carbs=_dv_pct(per_serving_dict["carbs"], DAILY_VALUE_CARBS_G),
    )

    return NutritionResult(
        per_recipe=per_recipe,
        per_serving=per_serving,
        per_100g=per_100g_macros,
        daily_value_pct=daily_value_pct,
        warnings=warnings,
    )
