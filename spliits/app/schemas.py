from pydantic import BaseModel, EmailStr, Field, model_validator
from datetime import datetime


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

        


