from sqlalchemy.orm import  Mapped, mapped_column, relationship
from sqlalchemy import Integer, String, ForeignKey, Float, Text, Boolean, Computed, Numeric,text,TIMESTAMP,CheckConstraint,UniqueConstraint
from datetime import datetime, timezone
from ..db import Base
from sqlalchemy.dialects.postgresql import UUID
import uuid






class pool(Base):
    __tablename__ = 'pools'


    pool_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, server_default=text('gen_random_uuid()'))
    title: Mapped[str] = mapped_column(String(250), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    total_cost: Mapped[float] = mapped_column(Numeric(10,2), nullable=False)
    max_members: Mapped[int] = mapped_column(Integer, nullable=False)
    category: Mapped[str] = mapped_column(Text, nullable=False)
    cost_per_member: Mapped[float] = mapped_column(Numeric(10,2), Computed("total_cost / max_members"), nullable=False)
    host_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey('users.user_id', ondelete='CASCADE'), index=True)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    created_at : Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True),server_default=text("now()"))
    updated_at : Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True),server_default=text("now()"), onupdate=lambda: datetime.now(timezone.utc))
    

    host = relationship('User', back_populates='hosted_pools')

    __table_args__ = (
        CheckConstraint('total_cost > 0', name='chq_cost'),
        CheckConstraint('max_members > 0', name='chq_maxmembers')
    )