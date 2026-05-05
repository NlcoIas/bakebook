import uuid
from decimal import Decimal

from sqlalchemy import (
    ARRAY,
    Boolean,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Text,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, SoftDeleteMixin, TimestampMixin, uuid7


class Recipe(Base, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "recipes"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid7)
    version_of_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("recipes.id"), nullable=True
    )
    parent_recipe_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("recipes.id"), nullable=True
    )
    version_number: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    title: Mapped[str] = mapped_column(Text, nullable=False)
    slug: Mapped[str] = mapped_column(Text, nullable=False)
    category: Mapped[str] = mapped_column(Text, nullable=False)
    summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    yields: Mapped[str | None] = mapped_column(Text, nullable=True)
    servings: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    serving_g: Mapped[Decimal | None] = mapped_column(Numeric(7, 2), nullable=True)
    total_time_min: Mapped[int | None] = mapped_column(Integer, nullable=True)
    active_time_min: Mapped[int | None] = mapped_column(Integer, nullable=True)
    difficulty: Mapped[int | None] = mapped_column(Integer, nullable=True)
    equipment: Mapped[list[str]] = mapped_column(ARRAY(String), server_default="{}", default=list)
    hero_photo_key: Mapped[str | None] = mapped_column(Text, nullable=True)
    source: Mapped[str | None] = mapped_column(Text, nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    target_dough_g: Mapped[Decimal | None] = mapped_column(Numeric(7, 2), nullable=True)

    ingredients: Mapped[list["RecipeIngredient"]] = relationship(
        back_populates="recipe",
        cascade="all, delete-orphan",
        order_by="RecipeIngredient.ord",
    )
    steps: Mapped[list["RecipeStep"]] = relationship(
        back_populates="recipe",
        cascade="all, delete-orphan",
        order_by="RecipeStep.ord",
    )


class RecipeIngredient(Base):
    __tablename__ = "recipe_ingredients"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid7)
    recipe_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("recipes.id", ondelete="CASCADE"), nullable=False
    )
    pantry_item_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("pantry_items.id"), nullable=True
    )
    ord: Mapped[int] = mapped_column(Integer, nullable=False)
    group_label: Mapped[str | None] = mapped_column(Text, nullable=True)
    name: Mapped[str] = mapped_column(Text, nullable=False)
    grams: Mapped[Decimal | None] = mapped_column(Numeric(8, 2), nullable=True)
    unit_display: Mapped[str | None] = mapped_column(Text, nullable=True)
    unit_display_qty: Mapped[Decimal | None] = mapped_column(Numeric(8, 2), nullable=True)
    role: Mapped[str | None] = mapped_column(Text, nullable=True)
    leaven_flour_pct: Mapped[Decimal] = mapped_column(
        Numeric(5, 2), nullable=False, server_default="50"
    )
    cost_override_per_kg: Mapped[Decimal | None] = mapped_column(Numeric(7, 2), nullable=True)
    nutrition_override: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    optional: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    recipe: Mapped["Recipe"] = relationship(back_populates="ingredients")
    pantry_item: Mapped["PantryItem | None"] = relationship("PantryItem")  # noqa: F821


class RecipeStep(Base):
    __tablename__ = "recipe_steps"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid7)
    recipe_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("recipes.id", ondelete="CASCADE"), nullable=False
    )
    ord: Mapped[int] = mapped_column(Integer, nullable=False)
    title: Mapped[str] = mapped_column(Text, nullable=False)
    body: Mapped[str] = mapped_column(Text, nullable=False)
    timer_seconds: Mapped[int | None] = mapped_column(Integer, nullable=True)
    min_seconds: Mapped[int | None] = mapped_column(Integer, nullable=True)
    max_seconds: Mapped[int | None] = mapped_column(Integer, nullable=True)
    target_temp_c: Mapped[Decimal | None] = mapped_column(Numeric(5, 1), nullable=True)
    temp_kind: Mapped[str | None] = mapped_column(Text, nullable=True)
    ingredient_ids: Mapped[list[uuid.UUID]] = mapped_column(
        ARRAY(UUID(as_uuid=True)), server_default="{}", default=list
    )
    parallelizable_with: Mapped[list[int]] = mapped_column(
        ARRAY(Integer), server_default="{}", default=list
    )

    recipe: Mapped["Recipe"] = relationship(back_populates="steps")
