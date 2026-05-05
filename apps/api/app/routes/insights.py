from datetime import UTC, datetime, timedelta

from fastapi import APIRouter, Depends, Query
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.db import get_db
from app.models.bake import Bake, BakeTweak
from app.services.patterns import detect_patterns

router = APIRouter(prefix="/api/v1/insights", tags=["insights"])


def _range_filter(range_val: str) -> datetime | None:
    now = datetime.now(UTC)
    if range_val == "month":
        return now - timedelta(days=30)
    if range_val == "year":
        return now - timedelta(days=365)
    return None  # "all"


@router.get("/summary")
async def summary(
    range: str = Query("all", pattern="^(month|year|all)$"),
    db: AsyncSession = Depends(get_db),
):
    since = _range_filter(range)
    query = select(Bake).where(Bake.status == "finished")
    if since:
        query = query.where(Bake.started_at >= since)

    result = await db.execute(query.options(selectinload(Bake.recipe)))
    bakes = list(result.scalars().all())

    count = len(bakes)
    rated = [b.rating for b in bakes if b.rating]
    avg_rating = sum(rated) / max(1, len(rated))

    # Flour kg: sum all flour-role ingredient grams * scale_multiplier
    flour_kg = 0.0
    for bake in bakes:
        if bake.recipe:
            for ing in bake.recipe.ingredients:
                if ing.role == "flour" and ing.grams:
                    flour_kg += float(ing.grams) * float(bake.scale_multiplier) / 1000

    # Total cost
    total_cost = 0.0
    for bake in bakes:
        if bake.recipe:
            for ing in bake.recipe.ingredients:
                if ing.grams and ing.pantry_item and ing.pantry_item.cost_per_kg:
                    total_cost += (
                        float(ing.grams) * float(bake.scale_multiplier) / 1000
                        * float(ing.pantry_item.cost_per_kg)
                    )

    return {
        "bakesCount": count,
        "avgRating": round(avg_rating, 1) if count else None,
        "flourKg": round(flour_kg, 1),
        "totalCostChf": round(total_cost, 2),
    }


@router.get("/bakes-per-month")
async def bakes_per_month(
    months: int = Query(12, ge=1, le=24),
    db: AsyncSession = Depends(get_db),
):
    now = datetime.now(UTC)
    data = []
    for i in range(months - 1, -1, -1):
        month_start = (now - timedelta(days=30 * i)).replace(day=1, hour=0, minute=0, second=0)
        if i > 0:
            month_end = (now - timedelta(days=30 * (i - 1))).replace(
                day=1, hour=0, minute=0, second=0
            )
        else:
            month_end = now

        result = await db.execute(
            select(func.count())
            .select_from(Bake)
            .where(
                Bake.started_at >= month_start,
                Bake.started_at < month_end,
                Bake.status == "finished",
            )
        )
        count = result.scalar() or 0
        data.append({
            "month": month_start.strftime("%Y-%m"),
            "label": month_start.strftime("%b"),
            "count": count,
        })

    return data


@router.get("/top-tweaks")
async def top_tweaks(
    limit: int = Query(10, ge=1, le=50),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(BakeTweak.change, func.count().label("count"))
        .group_by(BakeTweak.change)
        .order_by(func.count().desc())
        .limit(limit)
    )
    rows = result.all()
    return [
        {"rank": i + 1, "change": row[0], "count": row[1]}
        for i, row in enumerate(rows)
    ]


@router.get("/equipment")
async def equipment_stats(db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Bake)
        .options(selectinload(Bake.recipe))
        .where(Bake.status == "finished")
    )
    bakes = result.scalars().all()

    equip_data: dict[str, dict] = {}
    for bake in bakes:
        if not bake.recipe:
            continue
        for eq in bake.recipe.equipment:
            if eq not in equip_data:
                equip_data[eq] = {"ratings": [], "count": 0}
            equip_data[eq]["count"] += 1
            if bake.rating:
                equip_data[eq]["ratings"].append(bake.rating)

    return [
        {
            "name": name,
            "avgRating": round(sum(d["ratings"]) / len(d["ratings"]), 1)
            if d["ratings"]
            else None,
            "count": d["count"],
        }
        for name, d in sorted(equip_data.items(), key=lambda x: x[1]["count"], reverse=True)
    ]


@router.get("/calendar")
async def calendar_heatmap(
    year: int = Query(default=None),
    db: AsyncSession = Depends(get_db),
):
    if year is None:
        year = datetime.now(UTC).year

    start = datetime(year, 1, 1)
    end = datetime(year + 1, 1, 1)

    result = await db.execute(
        select(Bake.started_at)
        .where(Bake.started_at >= start, Bake.started_at < end)
    )
    dates = [row[0] for row in result.all()]

    # Count bakes per day-of-year
    day_counts: dict[int, int] = {}
    for dt in dates:
        day = dt.timetuple().tm_yday - 1  # 0-indexed
        day_counts[day] = day_counts.get(day, 0) + 1

    # Build 365-day array with intensity levels (0-4)
    import calendar
    total_days = 366 if calendar.isleap(year) else 365
    data = []
    for d in range(total_days):
        count = day_counts.get(d, 0)
        if count == 0:
            level = 0
        elif count == 1:
            level = 1
        elif count == 2:
            level = 2
        elif count <= 4:
            level = 3
        else:
            level = 4
        data.append(level)

    return {"year": year, "data": data}


@router.get("/patterns")
async def patterns(db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Bake)
        .options(selectinload(Bake.tweaks), selectinload(Bake.recipe))
        .order_by(Bake.started_at.desc())
        .limit(20)
    )
    bakes = list(result.scalars().all())

    # Add recipe_title as an attribute for the patterns service
    for bake in bakes:
        bake.recipe_title = bake.recipe.title if bake.recipe else None  # type: ignore[attr-defined]

    insights = detect_patterns(bakes)
    return {"patterns": insights}
