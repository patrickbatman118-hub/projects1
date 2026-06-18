from pydantic import BaseModel, EmailStr, Field, model_validator
from enum import Enum
from datetime import datetime
from .pools import PoolResponse as pool
from typing import Optional




class user(BaseModel):
    name: str
    email: EmailStr
    pfp: str
    password: str = Field(min_length=8)
    confirm_password: str = Field(min_length=8)
    

    @model_validator(mode='after')
    def check_pass_match(self):
        if self.password == self.confirm_password:
            return self
        else:
            raise ValueError('Password does not match')


class UserResponse(BaseModel):
    name: str
    email: EmailStr
    pfp: str
    hosted_pools:  list[pool] = []


    class Config:
        from_attributes = True

class userupdate(BaseModel):
    name: Optional[str]
    pfp: Optional[str]









    



        


