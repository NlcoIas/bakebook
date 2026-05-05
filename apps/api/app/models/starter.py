import uuid
from datetime import datetime
from decimal import Decimal

from sqlalchemy import DateTime, ForeignKey, Numeric, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, uuid7


class Starter(Base):
    __tablename__ = "starters"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid7)
    name: Mapped[str] = mapped_column(Text, nullable=False)
    hydration_pct: Mapped[Decimal] = mapped_column(
        Numeric(5, 1), nullable=False, server_default="100"
    )
    peak_base_hours: Mapped[Decimal] = mapped_column(
        Numeric(4, 1), nullable=False, server_default="6"
    )
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    feedings: Mapped[list["StarterFeeding"]] = relationship(
        back_populates="starter",
        cascade="all, delete-orphan",
        order_by="StarterFeeding.fed_at.desc()",
    )


class StarterFeeding(Base):
    __tablename__ = "starter_feedings"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid7)
    starter_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("starters.id", ondelete="CASCADE"), nullable=False
    )
    fed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    ratio: Mapped[str | None] = mapped_column(Text, nullable=True)
    flour_mix: Mapped[str | None] = mapped_column(Text, nullable=True)
    kitchen_temp_c: Mapped[Decimal | None] = mapped_column(Numeric(4, 1), nullable=True)
    peak_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    starter: Mapped["Starter"] = relationship(back_populates="feedings")
