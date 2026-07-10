from pydantic import BaseModel, Field
from ..utils.enum import PoolCategory
from typing import Optional


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

    class Config:
        from_attributes = True


class PoolResponse(BaseModel):
    title: str
    description: str
    total_cost: float
    max_members: int
    category: PoolCategory
    is_active: bool
    host: UserResponsePool

    class Config:
        from_attributes = True


class updatepool(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    total_cost: Optional[float] = None
    max_members: Optional[int] = None
