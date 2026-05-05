"""Hand-coded pattern detection rules over bake data.

These rules are written by hand and reviewed. They surface actionable
insights from real baking data. Do not LLM-generate these at runtime.

Each rule function receives a list of recent bakes (with tweaks loaded)
and returns a list of insight strings, or an empty list.
"""

import re
from collections import defaultdict

WATER_ADD = re.compile(r"\+\s*\d+\s*g?\s*water", re.IGNORECASE)
REDUCE_TIME = re.compile(r"reduce.*bake|less.*time|shorter.*bake", re.IGNORECASE)
MORE_SALT = re.compile(r"\+\s*\d+\s*g?\s*salt|more\s+salt", re.IGNORECASE)


def detect_patterns(bakes: list) -> list[str]:
    """Run all pattern rules and return insights.

    Each bake should have: recipe_title (str), outcome (str|None),
    internal_temp_c (Decimal|None), tweaks (list with .change attr).
    """
    insights: list[str] = []

    insights.extend(_rule_adding_water(bakes))
    insights.extend(_rule_underbaked(bakes))
    insights.extend(_rule_reduce_time(bakes))
    insights.extend(_rule_salt_adjustments(bakes))
    insights.extend(_rule_low_ratings(bakes))

    return insights


def _rule_adding_water(bakes: list) -> list[str]:
    """If adding water >=3 times in last 10 bakes for any recipe."""
    recipe_counts: dict[str, int] = defaultdict(int)
    for bake in bakes[:10]:
        for tweak in getattr(bake, "tweaks", []):
            if WATER_ADD.search(tweak.change):
                title = getattr(bake, "recipe_title", None)
                if not title:
                    recipe = getattr(bake, "recipe", None)
                    title = recipe.title if recipe else "a recipe"
                recipe_counts[title] += 1

    return [
        f"You've been adding water to {recipe}; consider raising default hydration"
        for recipe, count in recipe_counts.items()
        if count >= 3
    ]


def _rule_underbaked(bakes: list) -> list[str]:
    """If meh/disaster outcomes with low internal temp."""
    bad_and_cold = 0
    for bake in bakes[:10]:
        if bake.outcome in ("meh", "disaster"):
            temp = bake.internal_temp_c
            if temp is not None and float(temp) < 92:
                bad_and_cold += 1

    if bad_and_cold >= 2:
        return ["Underbaked outcomes recently \u2014 internal temp under 92\u00b0C"]
    return []


def _rule_reduce_time(bakes: list) -> list[str]:
    """If reducing bake time keeps coming up."""
    count = 0
    for bake in bakes[:10]:
        for tweak in getattr(bake, "tweaks", []):
            if REDUCE_TIME.search(tweak.change):
                count += 1

    if count >= 3:
        return ["Reducing bake time keeps coming up \u2014 lower the default"]
    return []


def _rule_salt_adjustments(bakes: list) -> list[str]:
    """If adding salt frequently across recipes."""
    count = 0
    for bake in bakes[:15]:
        for tweak in getattr(bake, "tweaks", []):
            if MORE_SALT.search(tweak.change):
                count += 1

    if count >= 3:
        return ["You keep adding salt \u2014 consider bumping the base amount"]
    return []


def _rule_low_ratings(bakes: list) -> list[str]:
    """If a recipe consistently gets low ratings."""
    recipe_ratings: dict[str, list[int]] = defaultdict(list)
    for bake in bakes[:20]:
        if bake.rating:
            title = getattr(bake, "recipe_title", None)
            if not title:
                recipe = getattr(bake, "recipe", None)
                title = recipe.title if recipe else None
            if title:
                recipe_ratings[title].append(bake.rating)

    return [
        f"{recipe} averages {sum(ratings)/len(ratings):.1f} stars \u2014 time to tweak the recipe?"
        for recipe, ratings in recipe_ratings.items()
        if len(ratings) >= 3 and sum(ratings) / len(ratings) < 3.0
    ]
