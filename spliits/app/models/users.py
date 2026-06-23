from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Integer, String, ForeignKey, DateTime, Float, Text, Boolean, Computed, TIMESTAMP,text
from datetime import datetime, timezone
from sqlalchemy.dialects.postgresql import UUID
from ..db import Base
import uuid



class User(Base):
    __tablename__ = 'users'

    user_id : Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, server_default=text('gen_random_uuid()'))
    name : Mapped[str] = mapped_column(String(250), nullable=False)
    email : Mapped[str] = mapped_column(String(250), nullable=False, unique=True)
    password : Mapped[str] = mapped_column(String(250), nullable=False)
    pfp : Mapped[str] = mapped_column(String(250), nullable=False)
    created_at : Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True),server_default=text("now()"))
    updated_at : Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True),server_default=text("now()"), onupdate=lambda: datetime.now(timezone.utc))
    disabled: Mapped[bool] = mapped_column(Boolean,  nullable=True, default=False)
    is_admin: Mapped[bool] = mapped_column(Boolean,  nullable=True, default=False)

    hosted_pools = relationship('pool', back_populates='host')


