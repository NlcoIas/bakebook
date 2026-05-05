from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict


def _to_camel(s: str) -> str:
    parts = s.split("_")
    return parts[0] + "".join(p.capitalize() for p in parts[1:])


# --- Ingredient schemas ---


class IngredientBase(BaseModel):
    model_config = ConfigDict(alias_generator=_to_camel, populate_by_name=True)

    pantry_item_id: UUID | None = None
    ord: int
    group_label: str | None = None
    name: str
    grams: Decimal | None = None
    unit_display: str | None = None
    unit_display_qty: Decimal | None = None
    role: str | None = None
    leaven_flour_pct: Decimal = Decimal("50")
    cost_override_per_kg: Decimal | None = None
    nutrition_override: dict | None = None
    notes: str | None = None
    optional: bool = False


class IngredientCreate(IngredientBase):
    pass


class IngredientOut(IngredientBase):
    id: UUID


# --- Step schemas ---


class StepBase(BaseModel):
    model_config = ConfigDict(alias_generator=_to_camel, populate_by_name=True)

    ord: int
    title: str
    body: str
    timer_seconds: int | None = None
    min_seconds: int | None = None
    max_seconds: int | None = None
    target_temp_c: Decimal | None = None
    temp_kind: str | None = None
    ingredient_ids: list[UUID] = []
    parallelizable_with: list[int] = []


class StepCreate(StepBase):
    pass


class StepOut(StepBase):
    id: UUID


# --- Recipe schemas ---


class RecipeBase(BaseModel):
    model_config = ConfigDict(alias_generator=_to_camel, populate_by_name=True)

    title: str
    slug: str
    category: str
    summary: str | None = None
    yields: str | None = None
    servings: int = 1
    serving_g: Decimal | None = None
    total_time_min: int | None = None
    active_time_min: int | None = None
    difficulty: int | None = None
    equipment: list[str] = []
    hero_photo_key: str | None = None
    source: str | None = None
    notes: str | None = None
    target_dough_g: Decimal | None = None


class RecipeCreate(RecipeBase):
    ingredients: list[IngredientCreate] = []
    steps: list[StepCreate] = []


class RecipeUpdate(BaseModel):
    model_config = ConfigDict(alias_generator=_to_camel, populate_by_name=True)

    title: str | None = None
    slug: str | None = None
    category: str | None = None
    summary: str | None = None
    yields: str | None = None
    servings: int | None = None
    serving_g: Decimal | None = None
    total_time_min: int | None = None
    active_time_min: int | None = None
    difficulty: int | None = None
    equipment: list[str] | None = None
    hero_photo_key: str | None = None
    source: str | None = None
    notes: str | None = None
    target_dough_g: Decimal | None = None
    ingredients: list[IngredientCreate] | None = None
    steps: list[StepCreate] | None = None


class RecipeListItem(RecipeBase):
    id: UUID
    version_number: int
    created_at: datetime
    updated_at: datetime


class RecipeOut(RecipeBase):
    id: UUID
    version_of_id: UUID | None = None
    parent_recipe_id: UUID | None = None
    version_number: int
    created_at: datetime
    updated_at: datetime
    ingredients: list[IngredientOut] = []
    steps: list[StepOut] = []
    nutrition: dict | None = None
    cost: dict | None = None
    ratios: dict | None = None


# --- Scale schemas ---


class ScaleRequest(BaseModel):
    model_config = ConfigDict(alias_generator=_to_camel, populate_by_name=True)

    mode: str  # 'multiplier' | 'doughWeight' | 'flourWeight'
    value: Decimal
