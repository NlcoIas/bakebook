import uuid
from datetime import datetime

from sqlalchemy import DateTime, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


def uuid7() -> uuid.UUID:
    """Generate a UUID v7 (time-ordered)."""
    import time

    timestamp_ms = int(time.time() * 1000)
    rand_bytes = uuid.uuid4().bytes

    # UUID v7: timestamp in first 48 bits, version=7, variant=2
    uuid_bytes = bytearray(16)
    uuid_bytes[0] = (timestamp_ms >> 40) & 0xFF
    uuid_bytes[1] = (timestamp_ms >> 32) & 0xFF
    uuid_bytes[2] = (timestamp_ms >> 24) & 0xFF
    uuid_bytes[3] = (timestamp_ms >> 16) & 0xFF
    uuid_bytes[4] = (timestamp_ms >> 8) & 0xFF
    uuid_bytes[5] = timestamp_ms & 0xFF
    uuid_bytes[6] = 0x70 | (rand_bytes[6] & 0x0F)  # version 7
    uuid_bytes[7] = rand_bytes[7]
    uuid_bytes[8] = 0x80 | (rand_bytes[8] & 0x3F)  # variant 2
    uuid_bytes[9:] = rand_bytes[9:]

    return uuid.UUID(bytes=bytes(uuid_bytes))


class Base(DeclarativeBase):
    pass


class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )


class SoftDeleteMixin:
    deleted_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        default=None,
    )
