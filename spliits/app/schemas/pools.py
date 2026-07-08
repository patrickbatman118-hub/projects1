from pydantic import BaseModel, Field
from ..utils.enum import PoolCategory
from typing import Optional
from uuid import UUID





class pool(BaseModel):
    title: str
    description: str
    total_cost: float = Field(gt=0)
    max_members: int = Field(gte=2)
    category: PoolCategory

class UserResponsePool(BaseModel):
    name: str
    email: str
    pfp: str
    role: str

class PoolResponseBase(BaseModel):
    pool_id: UUID
    host_id: UUID
    title: str
    description: str
    total_cost: float
    max_members: int
    category: PoolCategory
    is_active: bool

    class Config:
        from_attributes = True

class PoolResponse(BaseModel):
    pool: PoolResponseBase
    member_count: int


class updatepool(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    total_cost: Optional[float] = None
    max_members: Optional[int] = None