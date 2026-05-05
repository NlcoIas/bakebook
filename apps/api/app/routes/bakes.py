from datetime import UTC, datetime
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.db import get_db
from app.models.bake import Bake, BakePhoto, BakeTweak
from app.models.recipe import Recipe
from app.schemas.bake import (
    BakeCreate,
    BakeListItem,
    BakeOut,
    BakePhotoOut,
    BakePhotoUpdate,
    BakeTweakCreate,
    BakeTweakOut,
    BakeUpdate,
)
from app.services.r2 import delete_object, generate_read_url, generate_upload_url

router = APIRouter(tags=["bakes"])


def _bake_query():
    return select(Bake).options(
        selectinload(Bake.photos),
        selectinload(Bake.tweaks),
        selectinload(Bake.recipe),
    )


def _to_bake_out(bake: Bake) -> BakeOut:
    water_loss = None
    if bake.start_weight_g and bake.final_weight_g and bake.start_weight_g > 0:
        water_loss = float(
            (bake.start_weight_g - bake.final_weight_g) / bake.start_weight_g * 100
        )

    photos = [
        BakePhotoOut(
            id=p.id,
            bake_id=p.bake_id,
            r2_key=p.r2_key,
            url=generate_read_url(p.r2_key),
            caption=p.caption,
            kind=p.kind,
            step_ord=p.step_ord,
            taken_at=p.taken_at,
        )
        for p in bake.photos
    ]

    return BakeOut(
        id=bake.id,
        recipe_id=bake.recipe_id,
        started_at=bake.started_at,
        finished_at=bake.finished_at,
        status=bake.status,
        current_step=bake.current_step,
        scale_multiplier=bake.scale_multiplier,
        kitchen_temp_c=bake.kitchen_temp_c,
        kitchen_humidity=bake.kitchen_humidity,
        flour_brand=bake.flour_brand,
        rating=bake.rating,
        outcome=bake.outcome,
        start_weight_g=bake.start_weight_g,
        final_weight_g=bake.final_weight_g,
        rise_height_cm=bake.rise_height_cm,
        internal_temp_c=bake.internal_temp_c,
        crumb_score=bake.crumb_score,
        crust_score=bake.crust_score,
        notes=bake.notes,
        water_loss_pct=water_loss,
        photos=photos,
        tweaks=[BakeTweakOut.model_validate(t, from_attributes=True) for t in bake.tweaks],
        recipe_title=bake.recipe.title if bake.recipe else None,
        recipe_category=bake.recipe.category if bake.recipe else None,
    )


# --- Bake CRUD ---


@router.post("/api/v1/bakes", response_model=BakeOut, status_code=201)
async def start_bake(data: BakeCreate, db: AsyncSession = Depends(get_db)):
    recipe = await db.get(Recipe, data.recipe_id)
    if not recipe:
        raise HTTPException(404, "Recipe not found")

    bake = Bake(**data.model_dump())
    db.add(bake)
    await db.commit()

    result = await db.execute(_bake_query().where(Bake.id == bake.id))
    bake = result.scalar_one()
    return _to_bake_out(bake)


@router.get("/api/v1/bakes/{bake_id}", response_model=BakeOut)
async def get_bake(bake_id: UUID, db: AsyncSession = Depends(get_db)):
    result = await db.execute(_bake_query().where(Bake.id == bake_id))
    bake = result.scalar_one_or_none()
    if not bake:
        raise HTTPException(404, "Bake not found")
    return _to_bake_out(bake)


@router.patch("/api/v1/bakes/{bake_id}", response_model=BakeOut)
async def update_bake(
    bake_id: UUID, data: BakeUpdate, db: AsyncSession = Depends(get_db)
):
    result = await db.execute(_bake_query().where(Bake.id == bake_id))
    bake = result.scalar_one_or_none()
    if not bake:
        raise HTTPException(404, "Bake not found")

    updates = data.model_dump(exclude_unset=True)
    for key, value in updates.items():
        setattr(bake, key, value)

    if data.status == "finished" and not bake.finished_at:
        bake.finished_at = datetime.now(UTC)

    await db.commit()

    result = await db.execute(_bake_query().where(Bake.id == bake.id))
    bake = result.scalar_one()
    return _to_bake_out(bake)


@router.get("/api/v1/bakes", response_model=list[BakeListItem])
async def list_bakes(
    from_date: str | None = Query(None, alias="from"),
    to_date: str | None = Query(None, alias="to"),
    category: str | None = None,
    min_rating: int | None = Query(None, alias="minRating"),
    db: AsyncSession = Depends(get_db),
):
    query = select(Bake).options(selectinload(Bake.recipe)).order_by(Bake.started_at.desc())

    if from_date:
        query = query.where(Bake.started_at >= from_date)
    if to_date:
        query = query.where(Bake.started_at <= to_date)
    if min_rating:
        query = query.where(Bake.rating >= min_rating)
    if category:
        query = query.where(Bake.recipe.has(Recipe.category == category))

    result = await db.execute(query)
    bakes = result.scalars().all()
    return [
        BakeListItem(
            id=b.id,
            recipe_id=b.recipe_id,
            recipe_title=b.recipe.title if b.recipe else None,
            recipe_category=b.recipe.category if b.recipe else None,
            started_at=b.started_at,
            finished_at=b.finished_at,
            status=b.status,
            rating=b.rating,
            outcome=b.outcome,
        )
        for b in bakes
    ]


# --- Photos ---


@router.post("/api/v1/bakes/{bake_id}/photos")
async def request_photo_upload(
    bake_id: UUID,
    filename: str = Query("photo.jpg"),
    db: AsyncSession = Depends(get_db),
):
    bake = await db.get(Bake, bake_id)
    if not bake:
        raise HTTPException(404, "Bake not found")
    return generate_upload_url(str(bake_id), filename)


@router.post("/api/v1/bakes/{bake_id}/photos/{r2_key:path}/confirm", response_model=BakePhotoOut)
async def confirm_photo(
    bake_id: UUID,
    r2_key: str,
    caption: str | None = None,
    kind: str | None = None,
    step_ord: int | None = None,
    db: AsyncSession = Depends(get_db),
):
    bake = await db.get(Bake, bake_id)
    if not bake:
        raise HTTPException(404, "Bake not found")

    photo = BakePhoto(
        bake_id=bake_id,
        r2_key=r2_key,
        caption=caption,
        kind=kind,
        step_ord=step_ord,
    )
    db.add(photo)
    await db.commit()
    await db.refresh(photo)

    return BakePhotoOut(
        id=photo.id,
        bake_id=photo.bake_id,
        r2_key=photo.r2_key,
        url=generate_read_url(photo.r2_key),
        caption=photo.caption,
        kind=photo.kind,
        step_ord=photo.step_ord,
        taken_at=photo.taken_at,
    )


@router.patch("/api/v1/bake-photos/{photo_id}", response_model=BakePhotoOut)
async def update_photo(
    photo_id: UUID, data: BakePhotoUpdate, db: AsyncSession = Depends(get_db)
):
    photo = await db.get(BakePhoto, photo_id)
    if not photo:
        raise HTTPException(404, "Photo not found")

    updates = data.model_dump(exclude_unset=True)
    for key, value in updates.items():
        setattr(photo, key, value)

    await db.commit()
    await db.refresh(photo)

    return BakePhotoOut(
        id=photo.id,
        bake_id=photo.bake_id,
        r2_key=photo.r2_key,
        url=generate_read_url(photo.r2_key),
        caption=photo.caption,
        kind=photo.kind,
        step_ord=photo.step_ord,
        taken_at=photo.taken_at,
    )


@router.delete("/api/v1/bake-photos/{photo_id}", status_code=204)
async def delete_photo(photo_id: UUID, db: AsyncSession = Depends(get_db)):
    photo = await db.get(BakePhoto, photo_id)
    if not photo:
        raise HTTPException(404, "Photo not found")

    delete_object(photo.r2_key)
    await db.delete(photo)
    await db.commit()


# --- Tweaks ---


@router.post("/api/v1/bakes/{bake_id}/tweaks", response_model=BakeTweakOut, status_code=201)
async def add_tweak(
    bake_id: UUID, data: BakeTweakCreate, db: AsyncSession = Depends(get_db)
):
    bake = await db.get(Bake, bake_id)
    if not bake:
        raise HTTPException(404, "Bake not found")

    tweak = BakeTweak(bake_id=bake_id, **data.model_dump())
    db.add(tweak)
    await db.commit()
    await db.refresh(tweak)
    return BakeTweakOut.model_validate(tweak, from_attributes=True)
