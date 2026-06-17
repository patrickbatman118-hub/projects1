from sqlalchemy.orm import  Mapped, mapped_column, relationship
from sqlalchemy import Integer, String, ForeignKey, DateTime, Float, Text, Boolean, Computed
from datetime import datetime
from ..db import Base





class pool(Base):
    __tablename__ = 'pools'


    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String(250), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    total_cost: Mapped[float] = mapped_column(Float, nullable=False)
    max_members: Mapped[int] = mapped_column(Integer, nullable=False)
    category: Mapped[str] = mapped_column(String(250), nullable=False)
    cost_per_member: Mapped[float] = mapped_column(Float, Computed("total_cost / max_members"), nullable=False)
    host_id: Mapped[int] = mapped_column(Integer, ForeignKey('users.id', ondelete='CASCADE'), index=True)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    created_at : Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at : Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    

    host = relationship('User', back_populates='hosted_pools')