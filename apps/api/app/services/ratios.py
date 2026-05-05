"""Baker's ratio calculations.

Pure computation — no DB access. All arithmetic uses Decimal for precision.

Reference: CLAUDE.md §6.2.
"""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from decimal import ROUND_HALF_UP, Decimal
from typing import Protocol

# ---------------------------------------------------------------------------
# Input protocol — any object with these fields is accepted
# ---------------------------------------------------------------------------

class IngredientLike(Protocol):
    grams: Decimal | None
    role: str | None
    leaven_flour_pct: Decimal | None


# ---------------------------------------------------------------------------
# Output
# ---------------------------------------------------------------------------

@dataclass(frozen=True, slots=True)
class BakerRatios:
    """All values are percentages (e.g. 65.0 means 65 %)."""

    flour_total_g: Decimal
    hydration: Decimal
    hydration_with_dairy: Decimal
    salt_pct: Decimal
    sugar_pct: Decimal
    fat_pct: Decimal
    prefermented_flour_pct: Decimal
    inoculation_rate: Decimal


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

_ZERO = Decimal("0")
_HUNDRED = Decimal("100")
_DAIRY_WATER_FACTOR = Decimal("0.90")


def _safe_grams(ingredient: IngredientLike) -> Decimal:
    """Return ingredient grams as Decimal, defaulting to 0 if None."""
    if ingredient.grams is None:
        return _ZERO
    return Decimal(str(ingredient.grams))


def _sum_by_role(ingredients: Sequence[IngredientLike], role: str) -> Decimal:
    return sum(
        (_safe_grams(i) for i in ingredients if i.role == role),
        _ZERO,
    )


def _q(value: Decimal) -> Decimal:
    """Quantise to two decimal places."""
    return value.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def compute_ratios(
    ingredients: Sequence[IngredientLike],
) -> BakerRatios | None:
    """Compute baker's ratios from a list of ingredients.

    Returns ``None`` when no ingredient has ``role='flour'``, meaning the
    recipe is not flour-based and the ratios panel should be hidden.
    """

    flour_direct = _sum_by_role(ingredients, "flour")

    # If there is no flour at all (neither direct nor via leaven), bail out.
    has_flour_role = any(i.role == "flour" for i in ingredients)
    if not has_flour_role:
        return None

    # Flour contributed by leaven: leaven_grams * (leaven_flour_pct / 100).
    leaven_flour = _ZERO
    leaven_total = _ZERO
    for i in ingredients:
        if i.role == "leaven":
            g = _safe_grams(i)
            leaven_total += g
            raw = i.leaven_flour_pct if i.leaven_flour_pct is not None else Decimal("50")
            pct = Decimal(str(raw))
            leaven_flour += g * pct / _HUNDRED

    flour_total = flour_direct + leaven_flour

    # Guard against division by zero (e.g. flour roles present but all 0 g).
    if flour_total == _ZERO:
        return None

    water = _sum_by_role(ingredients, "water")
    dairy = _sum_by_role(ingredients, "dairy")
    salt = _sum_by_role(ingredients, "salt")
    sugar = _sum_by_role(ingredients, "sugar")
    fat = _sum_by_role(ingredients, "fat")

    hydration = water / flour_total * _HUNDRED
    hydration_with_dairy = (water + dairy * _DAIRY_WATER_FACTOR) / flour_total * _HUNDRED

    return BakerRatios(
        flour_total_g=_q(flour_total),
        hydration=_q(hydration),
        hydration_with_dairy=_q(hydration_with_dairy),
        salt_pct=_q(salt / flour_total * _HUNDRED),
        sugar_pct=_q(sugar / flour_total * _HUNDRED),
        fat_pct=_q(fat / flour_total * _HUNDRED),
        prefermented_flour_pct=_q(leaven_flour / flour_total * _HUNDRED),
        inoculation_rate=_q(leaven_total / flour_total * _HUNDRED),
    )
