from datetime import UTC, datetime
from decimal import Decimal
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.db import get_db
from app.models.starter import Starter, StarterFeeding
from app.schemas.starter import (
    FeedingCreate,
    FeedingOut,
    StarterCreate,
    StarterOut,
    StarterStatus,
    StarterUpdate,
)
from app.services.starter import estimate_peak

router = APIRouter(prefix="/api/v1/starters", tags=["starters"])


@router.get("", response_model=list[StarterOut])
async def list_starters(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Starter).order_by(Starter.created_at))
    return result.scalars().all()


@router.post("", response_model=StarterOut, status_code=201)
async def create_starter(data: StarterCreate, db: AsyncSession = Depends(get_db)):
    starter = Starter(**data.model_dump())
    db.add(starter)
    await db.commit()
    await db.refresh(starter)
    return starter


@router.patch("/{starter_id}", response_model=StarterOut)
async def update_starter(
    starter_id: UUID, data: StarterUpdate, db: AsyncSession = Depends(get_db)
):
    starter = await db.get(Starter, starter_id)
    if not starter:
        raise HTTPException(404, "Starter not found")
    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(starter, key, value)
    await db.commit()
    await db.refresh(starter)
    return starter


@router.post("/{starter_id}/feedings", response_model=FeedingOut, status_code=201)
async def add_feeding(
    starter_id: UUID, data: FeedingCreate, db: AsyncSession = Depends(get_db)
):
    starter = await db.get(Starter, starter_id)
    if not starter:
        raise HTTPException(404, "Starter not found")

    feeding = StarterFeeding(starter_id=starter_id, **data.model_dump())

    # Auto-compute peak if temperature provided
    if data.kitchen_temp_c:
        feeding.peak_at = estimate_peak(
            starter.peak_base_hours,
            data.kitchen_temp_c,
            feeding.fed_at,
        )

    db.add(feeding)
    await db.commit()
    await db.refresh(feeding)
    return feeding


@router.get("/{starter_id}/status", response_model=StarterStatus)
async def starter_status(starter_id: UUID, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Starter)
        .options(selectinload(Starter.feedings))
        .where(Starter.id == starter_id)
    )
    starter = result.scalar_one_or_none()
    if not starter:
        raise HTTPException(404, "Starter not found")

    if not starter.feedings:
        return StarterStatus()

    last_feeding = starter.feedings[0]  # ordered desc
    now = datetime.now(UTC)
    hours_since = (now - last_feeding.fed_at).total_seconds() / 3600

    peak_at = last_feeding.peak_at
    if not peak_at and last_feeding.kitchen_temp_c:
        peak_at = estimate_peak(
            starter.peak_base_hours,
            last_feeding.kitchen_temp_c,
            last_feeding.fed_at,
        )
    elif not peak_at:
        peak_at = estimate_peak(
            starter.peak_base_hours,
            Decimal("20"),
            last_feeding.fed_at,
        )

    return StarterStatus(
        last_fed_at=last_feeding.fed_at,
        hours_since_fed=round(hours_since, 1),
        estimated_peak_at=peak_at,
    )
