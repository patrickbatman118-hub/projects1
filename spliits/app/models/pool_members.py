from sqlalchemy.orm import  Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey, Text, UUID, text, TIMESTAMP, CheckConstraint,UniqueConstraint,Enum
from datetime import datetime,timezone
from ..db import Base
import uuid
from ..utils.enum import request_status,pool_role

class pool_members(Base):
    __tablename__ = 'pool_members'

    member_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, server_default=text('gen_random_uuid()'))
    pool_id: Mapped[UUID] = mapped_column(UUID, ForeignKey('pools.pool_id', ondelete='CASCADE'), index=True)
    user_id: Mapped[UUID] = mapped_column(UUID, ForeignKey('users.user_id', ondelete='SET NULL'), index=True)
    host_id: Mapped[UUID] = mapped_column(UUID, ForeignKey('users.user_id', ondelete='SET NULL'), index=True)
    status: Mapped[request_status] = mapped_column(Enum(request_status,values_callable=lambda enum: [e.value for e in enum],name='pool_status_enum'),nullable=False, server_default=request_status.REQUESTED.value)
    role: Mapped[pool_role] = mapped_column(Enum(pool_role,values_callable=lambda enum: [e.value for e in enum],name='pool_role_enum'), nullable=False, server_default=pool_role.MEMBER.value)
    joined_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), server_default=text('now()'))


    __table_args__ = (
        UniqueConstraint('pool_id','user_id', name='unq_pool_user'),
    )
