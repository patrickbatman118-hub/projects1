from sqlalchemy.orm import  Mapped, mapped_column, relationship
from sqlalchemy import Integer, String, ForeignKey, Float, Text, Boolean, Computed, Numeric,text,TIMESTAMP,CheckConstraint,UniqueConstraint
from datetime import datetime, timezone
from ..db import Base
from sqlalchemy.dialects.postgresql import UUID
import uuid


class revoked_tokens(Base):
    __tablename__ = 'revoked_tokens'

    jti: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True)
    user_id: Mapped[UUID] = mapped_column(UUID, ForeignKey('users.user_id', ondelete='CASCADE'), index=True)
    revoked_at : Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True),server_default=text("now()"))
    reason : Mapped[str] = mapped_column(Text,nullable=False)