import uuid
from datetime import datetime
from decimal import Decimal

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, Numeric, Text, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, uuid7


class Bake(Base):
    __tablename__ = "bakes"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid7)
    recipe_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("recipes.id"), nullable=False
    )
    started_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    finished_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    status: Mapped[str] = mapped_column(Text, nullable=False, server_default="active")
    current_step: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    scale_multiplier: Mapped[Decimal] = mapped_column(
        Numeric(6, 3), nullable=False, server_default="1"
    )

    # Environmental context
    kitchen_temp_c: Mapped[Decimal | None] = mapped_column(Numeric(4, 1), nullable=True)
    kitchen_humidity: Mapped[Decimal | None] = mapped_column(Numeric(4, 1), nullable=True)
    flour_brand: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Structured outcomes
    rating: Mapped[int | None] = mapped_column(Integer, nullable=True)
    outcome: Mapped[str | None] = mapped_column(Text, nullable=True)
    start_weight_g: Mapped[Decimal | None] = mapped_column(Numeric(7, 2), nullable=True)
    final_weight_g: Mapped[Decimal | None] = mapped_column(Numeric(7, 2), nullable=True)
    rise_height_cm: Mapped[Decimal | None] = mapped_column(Numeric(4, 1), nullable=True)
    internal_temp_c: Mapped[Decimal | None] = mapped_column(Numeric(4, 1), nullable=True)
    crumb_score: Mapped[int | None] = mapped_column(Integer, nullable=True)
    crust_score: Mapped[int | None] = mapped_column(Integer, nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    context: Mapped[dict] = mapped_column(JSONB, server_default="{}", default=dict)

    # Relationships
    recipe: Mapped["Recipe"] = relationship("Recipe")  # noqa: F821
    photos: Mapped[list["BakePhoto"]] = relationship(
        back_populates="bake", cascade="all, delete-orphan"
    )
    tweaks: Mapped[list["BakeTweak"]] = relationship(
        back_populates="bake", cascade="all, delete-orphan"
    )


class BakePhoto(Base):
    __tablename__ = "bake_photos"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid7)
    bake_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("bakes.id", ondelete="CASCADE"), nullable=False
    )
    r2_key: Mapped[str] = mapped_column(Text, nullable=False)
    caption: Mapped[str | None] = mapped_column(Text, nullable=True)
    kind: Mapped[str | None] = mapped_column(Text, nullable=True)
    step_ord: Mapped[int | None] = mapped_column(Integer, nullable=True)
    taken_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    bake: Mapped["Bake"] = relationship(back_populates="photos")


class BakeTweak(Base):
    __tablename__ = "bake_tweaks"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid7)
    bake_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("bakes.id", ondelete="CASCADE"), nullable=False
    )
    ingredient_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("recipe_ingredients.id"), nullable=True
    )
    step_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("recipe_steps.id"), nullable=True
    )
    change: Mapped[str] = mapped_column(Text, nullable=False)
    reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    apply_next_time: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    resolved_in_recipe_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("recipes.id"), nullable=True
    )

    bake: Mapped["Bake"] = relationship(back_populates="tweaks")
