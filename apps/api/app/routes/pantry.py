import json
from pathlib import Path
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_db
from app.models.pantry import PantryItem, PantryPriceHistory
from app.schemas.pantry import (
    PantryItemCreate,
    PantryItemOut,
    PantryItemUpdate,
    PriceHistoryOut,
)

router = APIRouter(prefix="/api/v1/pantry", tags=["pantry"])

NUTRITION_JSON = Path(__file__).parent.parent.parent / "data" / "nutrition.json"


@router.get("", response_model=list[PantryItemOut])
async def list_pantry(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(PantryItem).order_by(PantryItem.name))
    return result.scalars().all()


@router.post("", response_model=PantryItemOut, status_code=201)
async def create_pantry_item(data: PantryItemCreate, db: AsyncSession = Depends(get_db)):
    item = PantryItem(**data.model_dump())
    db.add(item)
    await db.commit()
    await db.refresh(item)
    return item


@router.patch("/{item_id}", response_model=PantryItemOut)
async def update_pantry_item(
    item_id: UUID, data: PantryItemUpdate, db: AsyncSession = Depends(get_db)
):
    item = await db.get(PantryItem, item_id)
    if not item:
        raise HTTPException(404, "Pantry item not found")

    updates = data.model_dump(exclude_unset=True)
    old_cost = item.cost_per_kg

    for key, value in updates.items():
        setattr(item, key, value)

    # Track price history if cost changed
    if "cost_per_kg" in updates and updates["cost_per_kg"] != old_cost and updates["cost_per_kg"]:
        history = PantryPriceHistory(
            pantry_item_id=item.id,
            cost_per_kg=updates["cost_per_kg"],
            source="manual",
        )
        db.add(history)

    await db.commit()
    await db.refresh(item)
    return item


@router.get("/{item_id}/price-history", response_model=list[PriceHistoryOut])
async def price_history(item_id: UUID, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(PantryPriceHistory)
        .where(PantryPriceHistory.pantry_item_id == item_id)
        .order_by(PantryPriceHistory.observed_at.desc())
    )
    return result.scalars().all()


@router.get("/nutrition-table")
async def nutrition_table():
    with open(NUTRITION_JSON) as f:
        return json.load(f)
