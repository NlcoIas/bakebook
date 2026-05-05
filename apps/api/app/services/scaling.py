"""Scaling service — pure computation, no DB access.

Three modes:
  multiplier   — multiply every ingredient gram by `value`.
  doughWeight  — multiplier = value / sum(grams), then apply multiplier mode.
  flourWeight  — multiplier = value / sum(grams where role='flour'). Error if no flour.
"""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from decimal import Decimal
from enum import StrEnum


class ScaleMode(StrEnum):
    MULTIPLIER = "multiplier"
    DOUGH_WEIGHT = "doughWeight"
    FLOUR_WEIGHT = "flourWeight"


@dataclass(frozen=True)
class Ingredient:
    """Minimal ingredient representation for scaling.

    Only `grams` and `role` matter to the scaling logic.
    All other recipe-ingredient fields are passed through unchanged.
    """

    id: str
    name: str
    grams: Decimal | None
    role: str | None = None


@dataclass(frozen=True)
class ScaledIngredient:
    """Result of scaling a single ingredient."""

    id: str
    name: str
    grams: Decimal | None
    original_grams: Decimal | None
    role: str | None = None


class ScalingError(Exception):
    """Raised when scaling cannot be performed."""


def _compute_multiplier(
    ingredients: Sequence[Ingredient],
    mode: ScaleMode,
    value: Decimal,
) -> Decimal:
    """Resolve the effective multiplier for any mode."""
    if mode is ScaleMode.MULTIPLIER:
        return value

    # Sum the relevant grams, skipping None.
    if mode is ScaleMode.DOUGH_WEIGHT:
        total = sum(
            (ing.grams for ing in ingredients if ing.grams is not None),
            Decimal(0),
        )
        if total == 0:
            raise ScalingError(
                "Cannot scale to dough weight: total ingredient weight is zero."
            )
        return value / total

    # ScaleMode.FLOUR_WEIGHT
    flour_total = sum(
        (
            ing.grams
            for ing in ingredients
            if ing.grams is not None and ing.role == "flour"
        ),
        Decimal(0),
    )
    if flour_total == 0:
        raise ScalingError(
            "Cannot scale to flour weight: no ingredients with role 'flour'."
        )
    return value / flour_total


def scale(
    ingredients: Sequence[Ingredient],
    mode: ScaleMode | str,
    value: Decimal,
) -> list[ScaledIngredient]:
    """Scale a list of ingredients.

    Parameters
    ----------
    ingredients:
        The ingredient list to scale.
    mode:
        One of 'multiplier', 'doughWeight', 'flourWeight' (or a ScaleMode enum).
    value:
        The numeric value for the chosen mode — a raw multiplier, a target
        dough weight in grams, or a target flour weight in grams.

    Returns
    -------
    A new list of ScaledIngredient with updated gram values.  Ingredients
    whose grams are None are passed through unchanged.
    """
    if isinstance(mode, str):
        mode = ScaleMode(mode)

    multiplier = _compute_multiplier(ingredients, mode, value)

    result: list[ScaledIngredient] = []
    for ing in ingredients:
        if ing.grams is None:
            scaled_grams = None
        else:
            scaled_grams = ing.grams * multiplier

        result.append(
            ScaledIngredient(
                id=ing.id,
                name=ing.name,
                grams=scaled_grams,
                original_grams=ing.grams,
                role=ing.role,
            )
        )

    return result
