from pydantic import BaseModel, EmailStr
from typing import Optional

# 1. Define what the Account data should look like
class AccountResponse(BaseModel):
    account_number: str
    initial_balance: float

    class Config:
        from_attributes = True


class UserResponse(BaseModel):
    id: int
    first_name: str
    email: str
    
    account: Optional[AccountResponse] = None 
    
    class Config:
        from_attributes = True


class UserCreate(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    phone_number: int
    pin: str