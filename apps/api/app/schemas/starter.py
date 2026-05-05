from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict


def _to_camel(s: str) -> str:
    parts = s.split("_")
    return parts[0] + "".join(p.capitalize() for p in parts[1:])


class StarterCreate(BaseModel):
    model_config = ConfigDict(alias_generator=_to_camel, populate_by_name=True)
    name: str
    hydration_pct: Decimal = Decimal("100")
    peak_base_hours: Decimal = Decimal("6")
    notes: str | None = None


class StarterUpdate(BaseModel):
    model_config = ConfigDict(alias_generator=_to_camel, populate_by_name=True)
    name: str | None = None
    hydration_pct: Decimal | None = None
    peak_base_hours: Decimal | None = None
    notes: str | None = None


class StarterOut(BaseModel):
    model_config = ConfigDict(alias_generator=_to_camel, populate_by_name=True)
    id: UUID
    name: str
    hydration_pct: Decimal
    peak_base_hours: Decimal
    notes: str | None = None
    created_at: datetime


class FeedingCreate(BaseModel):
    model_config = ConfigDict(alias_generator=_to_camel, populate_by_name=True)
    ratio: str | None = None
    flour_mix: str | None = None
    kitchen_temp_c: Decimal | None = None
    notes: str | None = None


class FeedingOut(BaseModel):
    model_config = ConfigDict(alias_generator=_to_camel, populate_by_name=True)
    id: UUID
    starter_id: UUID
    fed_at: datetime
    ratio: str | None = None
    flour_mix: str | None = None
    kitchen_temp_c: Decimal | None = None
    peak_at: datetime | None = None
    notes: str | None = None


class StarterStatus(BaseModel):
    model_config = ConfigDict(alias_generator=_to_camel, populate_by_name=True)
    last_fed_at: datetime | None = None
    hours_since_fed: float | None = None
    estimated_peak_at: datetime | None = None
