import uuid
from datetime import datetime
from decimal import Decimal

from sqlalchemy import DateTime, ForeignKey, Numeric, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, uuid7


class PantryItem(Base, TimestampMixin):
    __tablename__ = "pantry_items"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid7)
    name: Mapped[str] = mapped_column(Text, unique=True, nullable=False)
    cost_per_kg: Mapped[Decimal | None] = mapped_column(Numeric(7, 2), nullable=True)
    cost_currency: Mapped[str] = mapped_column(Text, nullable=False, server_default="CHF")
    nutrition_ref: Mapped[str | None] = mapped_column(Text, nullable=True)
    default_role: Mapped[str | None] = mapped_column(Text, nullable=True)

    price_history: Mapped[list["PantryPriceHistory"]] = relationship(
        back_populates="pantry_item",
        cascade="all, delete-orphan",
        order_by="PantryPriceHistory.observed_at.desc()",
    )


class PantryPriceHistory(Base):
    __tablename__ = "pantry_price_history"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid7)
    pantry_item_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("pantry_items.id", ondelete="CASCADE"),
        nullable=False,
    )
    cost_per_kg: Mapped[Decimal] = mapped_column(Numeric(7, 2), nullable=False)
    observed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    source: Mapped[str | None] = mapped_column(Text, nullable=True)

    pantry_item: Mapped["PantryItem"] = relationship(back_populates="price_history")
