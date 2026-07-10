from sqlalchemy.orm import  Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey, Text, UUID, text, TIMESTAMP, CheckConstraint,UniqueConstraint, INTEGER, Boolean, Index
from datetime import datetime,timezone
from ..db import Base
import uuid


class notifications(Base):
    __tablename__ = 'notifications'

    id: Mapped[int] = mapped_column(INTEGER, primary_key=True)
    receiver_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey('users.user_id', ondelete='CASCADE'))
    sender_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey('users.user_id', ondelete='CASCADE'))
    content: Mapped[str] = mapped_column(Text,nullable=False)
    pool_id: Mapped[UUID] = mapped_column(UUID, ForeignKey('pools.pool_id', ondelete='CASCADE'))
    is_read: Mapped[bool] = mapped_column(Boolean,nullable=False,default=False)
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), server_default=text('now()'))

    __table_args__ = (
        Index('idx_receiver_id_created_at', receiver_id, created_at.desc()),
        Index('idx_notifications_unread_by_user','receiver_id',postgresql_where=(is_read == False) ),
    )