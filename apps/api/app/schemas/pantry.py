from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict


def _to_camel(s: str) -> str:
    parts = s.split("_")
    return parts[0] + "".join(p.capitalize() for p in parts[1:])


class PantryItemBase(BaseModel):
    model_config = ConfigDict(alias_generator=_to_camel, populate_by_name=True)

    name: str
    cost_per_kg: Decimal | None = None
    cost_currency: str = "CHF"
    nutrition_ref: str | None = None
    default_role: str | None = None


class PantryItemCreate(PantryItemBase):
    pass


class PantryItemUpdate(BaseModel):
    model_config = ConfigDict(alias_generator=_to_camel, populate_by_name=True)

    name: str | None = None
    cost_per_kg: Decimal | None = None
    cost_currency: str | None = None
    nutrition_ref: str | None = None
    default_role: str | None = None


class PantryItemOut(PantryItemBase):
    id: UUID
    created_at: datetime
    updated_at: datetime


class PriceHistoryOut(BaseModel):
    model_config = ConfigDict(alias_generator=_to_camel, populate_by_name=True)

    id: UUID
    pantry_item_id: UUID
    cost_per_kg: Decimal
    observed_at: datetime
    source: str | None = None
