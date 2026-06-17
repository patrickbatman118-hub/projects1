from pydantic import BaseModel, Field
from ..utils.enum import PoolCategory




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

