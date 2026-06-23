from pydantic import BaseModel
from uuid import UUID

class notifi(BaseModel):
    content: str
    sender_id: UUID