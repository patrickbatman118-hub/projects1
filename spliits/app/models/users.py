from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Integer, String, ForeignKey, DateTime, Float, Text, Boolean, Computed
from datetime import datetime
from sqlalchemy.dialects.postgresql import UUID
from ..db import Base



class User(Base):
    __tablename__ = 'users'

    id : Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name : Mapped[str] = mapped_column(String(250), nullable=False)
    email : Mapped[str] = mapped_column(String(250), nullable=False, unique=True)
    password : Mapped[str] = mapped_column(String(250), nullable=False)
    pfp : Mapped[str] = mapped_column(String(250), nullable=False)
    created_at : Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at : Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    disabled: Mapped[bool] = mapped_column(Boolean,  nullable=True, default=False)

    hosted_pools = relationship('pool', back_populates='host')

  
