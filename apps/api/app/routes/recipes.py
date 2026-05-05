import json
from datetime import UTC, datetime
from decimal import Decimal
from pathlib import Path
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.db import get_db
from app.models.recipe import Recipe, RecipeIngredient, RecipeStep
from app.schemas.recipe import (
    RecipeCreate,
    RecipeListItem,
    RecipeOut,
    RecipeUpdate,
    ScaleRequest,
)
from app.services.cost import CostIngredient, calculate_cost
from app.services.nutrition import IngredientInput, calculate_nutrition
from app.services.ratios import compute_ratios
from app.services.scaling import Ingredient as ScaleIngredient
from app.services.scaling import scale

router = APIRouter(prefix="/api/v1/recipes", tags=["recipes"])

NUTRITION_JSON = Path(__file__).parent.parent.parent / "data" / "nutrition.json"
_nutrition_table: dict | None = None


def _get_nutrition_table() -> dict:
    global _nutrition_table
    if _nutrition_table is None:
        with open(NUTRITION_JSON) as f:
            _nutrition_table = json.load(f)
    return _nutrition_table


def _compute_recipe_data(recipe: Recipe) -> dict:
    """Compute nutrition, cost, and ratios for a recipe."""
    nutrition_table = _get_nutrition_table()
    result: dict = {}

    # Nutrition
    nutrition_inputs = []
    for ing in recipe.ingredients:
        override = ing.nutrition_override
        ref = None
        if ing.pantry_item:
            ref = ing.pantry_item.nutrition_ref
        nutrition_inputs.append(
            IngredientInput(
                name=ing.name,
                grams=ing.grams or Decimal(0),
                nutrition_override=override,
                pantry_nutrition_ref=ref,
            )
        )
    if nutrition_inputs:
        nr = calculate_nutrition(nutrition_inputs, nutrition_table, recipe.servings)
        result["nutrition"] = {
            "perRecipe": _macros_dict(nr.per_recipe),
            "perServing": _macros_dict(nr.per_serving),
            "per100g": _macros_dict(nr.per_100g) if nr.per_100g else None,
            "dailyValuePct": {
                "kcal": float(nr.daily_value_pct.kcal),
                "protein": float(nr.daily_value_pct.protein),
                "fat": float(nr.daily_value_pct.fat),
                "carbs": float(nr.daily_value_pct.carbs),
            }
            if nr.daily_value_pct
            else None,
            "warnings": nr.warnings,
        }

    # Cost
    cost_inputs = []
    for ing in recipe.ingredients:
        pantry_cost = None
        if ing.pantry_item:
            pantry_cost = ing.pantry_item.cost_per_kg
        cost_inputs.append(
            CostIngredient(
                name=ing.name,
                grams=ing.grams or Decimal(0),
                cost_override_per_kg=ing.cost_override_per_kg,
                pantry_cost_per_kg=pantry_cost,
            )
        )
    if cost_inputs:
        cr = calculate_cost(cost_inputs, recipe.servings)
        result["cost"] = {
            "totalCost": float(cr.total_cost),
            "perServingCost": float(cr.per_serving_cost),
            "currency": "CHF",
            "topContributors": [
                {"name": tc.name, "cost": float(tc.cost)} for tc in cr.top_contributors
            ],
            "warnings": cr.warnings,
        }

    # Ratios
    ratios = compute_ratios(recipe.ingredients)
    if ratios:
        result["ratios"] = {
            "flourTotalG": float(ratios.flour_total_g),
            "hydration": float(ratios.hydration),
            "hydrationWithDairy": float(ratios.hydration_with_dairy),
            "salt": float(ratios.salt_pct),
            "sugar": float(ratios.sugar_pct),
            "fat": float(ratios.fat_pct),
            "prefermentedFlour": float(ratios.prefermented_flour_pct),
            "inoculationRate": float(ratios.inoculation_rate),
        }

    return result


def _macros_dict(m) -> dict:
    return {
        "kcal": float(m.kcal),
        "protein": float(m.protein),
        "fat": float(m.fat),
        "carbs": float(m.carbs),
        "sugar": float(m.sugar),
        "fiber": float(m.fiber),
        "salt": float(m.salt),
    }


def _recipe_query():
    return (
        select(Recipe)
        .options(
            selectinload(Recipe.ingredients).selectinload(RecipeIngredient.pantry_item),
            selectinload(Recipe.steps),
        )
        .where(Recipe.deleted_at.is_(None))
    )


@router.get("", response_model=list[RecipeListItem])
async def list_recipes(
    category: str | None = None,
    q: str | None = None,
    include_versions: bool = Query(False),
    db: AsyncSession = Depends(get_db),
):
    query = select(Recipe).where(Recipe.deleted_at.is_(None))

    if not include_versions:
        query = query.where(Recipe.version_of_id.is_(None))

    if category:
        query = query.where(Recipe.category == category)

    if q:
        query = query.where(Recipe.title.ilike(f"%{q}%"))

    query = query.order_by(Recipe.created_at.desc())
    result = await db.execute(query)
    return result.scalars().all()


@router.get("/{recipe_id}", response_model=RecipeOut)
async def get_recipe(recipe_id: UUID, db: AsyncSession = Depends(get_db)):
    result = await db.execute(_recipe_query().where(Recipe.id == recipe_id))
    recipe = result.scalar_one_or_none()
    if not recipe:
        raise HTTPException(404, "Recipe not found")

    computed = _compute_recipe_data(recipe)
    out = RecipeOut.model_validate(recipe, from_attributes=True)
    out.nutrition = computed.get("nutrition")
    out.cost = computed.get("cost")
    out.ratios = computed.get("ratios")
    return out


@router.get("/by-slug/{slug}", response_model=RecipeOut)
async def get_recipe_by_slug(slug: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        _recipe_query()
        .where(Recipe.slug == slug)
        .order_by(Recipe.version_number.desc())
        .limit(1)
    )
    recipe = result.scalar_one_or_none()
    if not recipe:
        raise HTTPException(404, "Recipe not found")

    computed = _compute_recipe_data(recipe)
    out = RecipeOut.model_validate(recipe, from_attributes=True)
    out.nutrition = computed.get("nutrition")
    out.cost = computed.get("cost")
    out.ratios = computed.get("ratios")
    return out


@router.post("", response_model=RecipeOut, status_code=201)
async def create_recipe(data: RecipeCreate, db: AsyncSession = Depends(get_db)):
    recipe_data = data.model_dump(exclude={"ingredients", "steps"})
    recipe = Recipe(**recipe_data)

    for ing_data in data.ingredients:
        recipe.ingredients.append(RecipeIngredient(**ing_data.model_dump()))

    for step_data in data.steps:
        recipe.steps.append(RecipeStep(**step_data.model_dump()))

    db.add(recipe)
    await db.commit()

    # Reload with relationships
    result = await db.execute(_recipe_query().where(Recipe.id == recipe.id))
    recipe = result.scalar_one()
    computed = _compute_recipe_data(recipe)
    out = RecipeOut.model_validate(recipe, from_attributes=True)
    out.nutrition = computed.get("nutrition")
    out.cost = computed.get("cost")
    out.ratios = computed.get("ratios")
    return out


@router.put("/{recipe_id}", response_model=RecipeOut)
async def update_recipe(
    recipe_id: UUID, data: RecipeUpdate, db: AsyncSession = Depends(get_db)
):
    result = await db.execute(_recipe_query().where(Recipe.id == recipe_id))
    recipe = result.scalar_one_or_none()
    if not recipe:
        raise HTTPException(404, "Recipe not found")

    updates = data.model_dump(exclude_unset=True, exclude={"ingredients", "steps"})
    for key, value in updates.items():
        setattr(recipe, key, value)

    if data.ingredients is not None:
        recipe.ingredients.clear()
        for ing_data in data.ingredients:
            recipe.ingredients.append(RecipeIngredient(**ing_data.model_dump()))

    if data.steps is not None:
        recipe.steps.clear()
        for step_data in data.steps:
            recipe.steps.append(RecipeStep(**step_data.model_dump()))

    await db.commit()

    result = await db.execute(_recipe_query().where(Recipe.id == recipe.id))
    recipe = result.scalar_one()
    computed = _compute_recipe_data(recipe)
    out = RecipeOut.model_validate(recipe, from_attributes=True)
    out.nutrition = computed.get("nutrition")
    out.cost = computed.get("cost")
    out.ratios = computed.get("ratios")
    return out


@router.post("/{recipe_id}/version", response_model=RecipeOut, status_code=201)
async def create_version(recipe_id: UUID, db: AsyncSession = Depends(get_db)):
    result = await db.execute(_recipe_query().where(Recipe.id == recipe_id))
    original = result.scalar_one_or_none()
    if not original:
        raise HTTPException(404, "Recipe not found")

    # Get the root recipe ID for version tracking
    root_id = original.version_of_id or original.id

    # Get max version number
    max_ver = await db.execute(
        select(func.max(Recipe.version_number)).where(
            (Recipe.version_of_id == root_id) | (Recipe.id == root_id)
        )
    )
    next_ver = (max_ver.scalar() or 1) + 1

    new_recipe = Recipe(
        version_of_id=root_id,
        version_number=next_ver,
        title=original.title,
        slug=original.slug,
        category=original.category,
        summary=original.summary,
        yields=original.yields,
        servings=original.servings,
        serving_g=original.serving_g,
        total_time_min=original.total_time_min,
        active_time_min=original.active_time_min,
        difficulty=original.difficulty,
        equipment=list(original.equipment),
        hero_photo_key=original.hero_photo_key,
        source=original.source,
        notes=original.notes,
        target_dough_g=original.target_dough_g,
    )

    for ing in original.ingredients:
        new_recipe.ingredients.append(
            RecipeIngredient(
                pantry_item_id=ing.pantry_item_id,
                ord=ing.ord,
                group_label=ing.group_label,
                name=ing.name,
                grams=ing.grams,
                unit_display=ing.unit_display,
                unit_display_qty=ing.unit_display_qty,
                role=ing.role,
                leaven_flour_pct=ing.leaven_flour_pct,
                cost_override_per_kg=ing.cost_override_per_kg,
                nutrition_override=ing.nutrition_override,
                notes=ing.notes,
                optional=ing.optional,
            )
        )

    for step in original.steps:
        new_recipe.steps.append(
            RecipeStep(
                ord=step.ord,
                title=step.title,
                body=step.body,
                timer_seconds=step.timer_seconds,
                min_seconds=step.min_seconds,
                max_seconds=step.max_seconds,
                target_temp_c=step.target_temp_c,
                temp_kind=step.temp_kind,
                parallelizable_with=list(step.parallelizable_with),
            )
        )

    db.add(new_recipe)
    await db.commit()

    result = await db.execute(_recipe_query().where(Recipe.id == new_recipe.id))
    recipe = result.scalar_one()
    computed = _compute_recipe_data(recipe)
    out = RecipeOut.model_validate(recipe, from_attributes=True)
    out.nutrition = computed.get("nutrition")
    out.cost = computed.get("cost")
    out.ratios = computed.get("ratios")
    return out


@router.post("/{recipe_id}/fork", response_model=RecipeOut, status_code=201)
async def fork_recipe(recipe_id: UUID, db: AsyncSession = Depends(get_db)):
    result = await db.execute(_recipe_query().where(Recipe.id == recipe_id))
    original = result.scalar_one_or_none()
    if not original:
        raise HTTPException(404, "Recipe not found")

    new_recipe = Recipe(
        parent_recipe_id=original.id,
        version_number=1,
        title=f"{original.title} (fork)",
        slug=f"{original.slug}-fork",
        category=original.category,
        summary=original.summary,
        yields=original.yields,
        servings=original.servings,
        serving_g=original.serving_g,
        total_time_min=original.total_time_min,
        active_time_min=original.active_time_min,
        difficulty=original.difficulty,
        equipment=list(original.equipment),
        source=original.source,
        notes=original.notes,
        target_dough_g=original.target_dough_g,
    )

    for ing in original.ingredients:
        new_recipe.ingredients.append(
            RecipeIngredient(
                pantry_item_id=ing.pantry_item_id,
                ord=ing.ord,
                group_label=ing.group_label,
                name=ing.name,
                grams=ing.grams,
                unit_display=ing.unit_display,
                unit_display_qty=ing.unit_display_qty,
                role=ing.role,
                leaven_flour_pct=ing.leaven_flour_pct,
                cost_override_per_kg=ing.cost_override_per_kg,
                nutrition_override=ing.nutrition_override,
                notes=ing.notes,
                optional=ing.optional,
            )
        )

    for step in original.steps:
        new_recipe.steps.append(
            RecipeStep(
                ord=step.ord,
                title=step.title,
                body=step.body,
                timer_seconds=step.timer_seconds,
                min_seconds=step.min_seconds,
                max_seconds=step.max_seconds,
                target_temp_c=step.target_temp_c,
                temp_kind=step.temp_kind,
                parallelizable_with=list(step.parallelizable_with),
            )
        )

    db.add(new_recipe)
    await db.commit()

    result = await db.execute(_recipe_query().where(Recipe.id == new_recipe.id))
    recipe = result.scalar_one()
    computed = _compute_recipe_data(recipe)
    out = RecipeOut.model_validate(recipe, from_attributes=True)
    out.nutrition = computed.get("nutrition")
    out.cost = computed.get("cost")
    out.ratios = computed.get("ratios")
    return out


@router.delete("/{recipe_id}", status_code=204)
async def delete_recipe(recipe_id: UUID, db: AsyncSession = Depends(get_db)):
    recipe = await db.get(Recipe, recipe_id)
    if not recipe:
        raise HTTPException(404, "Recipe not found")
    recipe.deleted_at = datetime.now(UTC)
    await db.commit()


@router.post("/{recipe_id}/scale")
async def scale_recipe(
    recipe_id: UUID, data: ScaleRequest, db: AsyncSession = Depends(get_db)
):
    result = await db.execute(_recipe_query().where(Recipe.id == recipe_id))
    recipe = result.scalar_one_or_none()
    if not recipe:
        raise HTTPException(404, "Recipe not found")

    ingredients = [
        ScaleIngredient(
            id=str(ing.id),
            name=ing.name,
            grams=ing.grams,
            role=ing.role,
        )
        for ing in recipe.ingredients
    ]

    try:
        scaled = scale(ingredients, data.mode, data.value)
    except Exception as e:
        raise HTTPException(400, str(e))

    return [
        {
            "id": s.id,
            "name": s.name,
            "grams": float(s.grams) if s.grams is not None else None,
            "originalGrams": float(s.original_grams) if s.original_grams is not None else None,
            "role": s.role,
        }
        for s in scaled
    ]
