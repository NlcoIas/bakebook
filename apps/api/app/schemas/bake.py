from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict


def _to_camel(s: str) -> str:
    parts = s.split("_")
    return parts[0] + "".join(p.capitalize() for p in parts[1:])


class BakeCreate(BaseModel):
    model_config = ConfigDict(alias_generator=_to_camel, populate_by_name=True)

    recipe_id: UUID
    scale_multiplier: Decimal = Decimal("1")
    kitchen_temp_c: Decimal | None = None
    kitchen_humidity: Decimal | None = None
    flour_brand: str | None = None


class BakeUpdate(BaseModel):
    model_config = ConfigDict(alias_generator=_to_camel, populate_by_name=True)

    current_step: int | None = None
    status: str | None = None
    rating: int | None = None
    outcome: str | None = None
    start_weight_g: Decimal | None = None
    final_weight_g: Decimal | None = None
    rise_height_cm: Decimal | None = None
    internal_temp_c: Decimal | None = None
    crumb_score: int | None = None
    crust_score: int | None = None
    notes: str | None = None


class BakeTweakCreate(BaseModel):
    model_config = ConfigDict(alias_generator=_to_camel, populate_by_name=True)

    change: str
    reason: str | None = None
    ingredient_id: UUID | None = None
    step_id: UUID | None = None
    apply_next_time: bool = False


class BakeTweakOut(BaseModel):
    model_config = ConfigDict(alias_generator=_to_camel, populate_by_name=True)

    id: UUID
    bake_id: UUID
    change: str
    reason: str | None = None
    ingredient_id: UUID | None = None
    step_id: UUID | None = None
    apply_next_time: bool
    resolved_in_recipe_id: UUID | None = None


class BakePhotoOut(BaseModel):
    model_config = ConfigDict(alias_generator=_to_camel, populate_by_name=True)

    id: UUID
    bake_id: UUID
    r2_key: str
    url: str | None = None
    caption: str | None = None
    kind: str | None = None
    step_ord: int | None = None
    taken_at: datetime


class BakePhotoUpdate(BaseModel):
    model_config = ConfigDict(alias_generator=_to_camel, populate_by_name=True)

    caption: str | None = None
    kind: str | None = None
    step_ord: int | None = None


class BakeOut(BaseModel):
    model_config = ConfigDict(alias_generator=_to_camel, populate_by_name=True)

    id: UUID
    recipe_id: UUID
    started_at: datetime
    finished_at: datetime | None = None
    status: str
    current_step: int
    scale_multiplier: Decimal

    kitchen_temp_c: Decimal | None = None
    kitchen_humidity: Decimal | None = None
    flour_brand: str | None = None

    rating: int | None = None
    outcome: str | None = None
    start_weight_g: Decimal | None = None
    final_weight_g: Decimal | None = None
    rise_height_cm: Decimal | None = None
    internal_temp_c: Decimal | None = None
    crumb_score: int | None = None
    crust_score: int | None = None
    notes: str | None = None

    water_loss_pct: float | None = None
    photos: list[BakePhotoOut] = []
    tweaks: list[BakeTweakOut] = []

    # Recipe title for journal list
    recipe_title: str | None = None
    recipe_category: str | None = None


class BakeListItem(BaseModel):
    model_config = ConfigDict(alias_generator=_to_camel, populate_by_name=True)

    id: UUID
    recipe_id: UUID
    recipe_title: str | None = None
    recipe_category: str | None = None
    started_at: datetime
    finished_at: datetime | None = None
    status: str
    rating: int | None = None
    outcome: str | None = None
