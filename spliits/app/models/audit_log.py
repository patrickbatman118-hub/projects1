from datetime import datetime
from uuid import UUID

from sqlalchemy import ForeignKey, Text, TIMESTAMP,text
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..db import Base


class AuditLog(Base):
    __tablename__ = "audit_log"

    id: Mapped[int] = mapped_column(primary_key=True)
    actor_id: Mapped[int | None] = mapped_column(ForeignKey("users.user_id", ondelete="SET NULL"),nullable=True)
    jti: Mapped[UUID | None] = mapped_column(PG_UUID(as_uuid=True),nullable=True)
    action: Mapped[str] = mapped_column(Text, nullable=False)
    resource_type: Mapped[str] = mapped_column(Text, nullable=False)
    resource_id: Mapped[str | None] = mapped_column(Text,nullable=True)
    decision: Mapped[str] = mapped_column(Text,nullable=False)
    reason: Mapped[str] = mapped_column(Text,nullable=False)
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), server_default=text('now()'))


    actor = relationship(
        "User",
        back_populates="audit_logs",
    )