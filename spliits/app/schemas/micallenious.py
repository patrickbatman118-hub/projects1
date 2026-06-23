from pydantic import BaseModel
from uuid import UUID
from typing import List
class NotificationSchema(BaseModel):
    content: str
    sender_id: UUID
    receiver_id: UUID
    pool_id: UUID
    is_read: bool
    id: int

    class Config:
        from_attributes = True

class NotificationResponseSchema(BaseModel):
    unread_count: int
    notifications: List[NotificationSchema]