from sqlalchemy.orm import declarative_base, Mapped, mapped_column
from sqlalchemy import Integer, String, ForeignKey, DateTime
from datetime import datetime

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'

    id : Mapped[int] = mapped_column(Integer, primary_key=True, index = True)
    name : Mapped[str] = mapped_column(String(250), nullable=False)
    email : Mapped[str] = mapped_column(String(250), nullable=False, unique=True)
    password : Mapped[str] = mapped_column(String(250), nullable=False)
    pfp : Mapped[str] = mapped_column(String(250), nullable=False)
    created_at : Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at : Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)