from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime

# --- ACCOUNT SCHEMAS ---
class AccountResponse(BaseModel):
    account_number: str
    initial_balance: float

    class Config:
        from_attributes = True

# --- USER SCHEMAS ---
class UserCreate(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    pin: str

class UserResponse(BaseModel):
    id: int
    first_name: str
    email: str
    account: Optional[AccountResponse] = None 
    
    class Config:
        from_attributes = True

class UserLogin(BaseModel):
    email: EmailStr
    pin: str

# --- AUTH SCHEMAS ---
class Token(BaseModel):
    access_token: str
    token_type: str

# --- BANKING ACTION SCHEMAS ---
# This fixes the "Field required" error you got!
class TransferCreate(BaseModel):
    receiver_acc_number: str
    amount: float

class DepositCreate(BaseModel):
    amount: float

# --- TRANSACTION SCHEMAS ---
class TransactionBase(BaseModel):
    id: int
    reference_code: str
    sender_id: Optional[int] = None
    receiver_id: Optional[int] = None  
    amount: float
    transaction_type: str
    timestamp: datetime

    class Config:
        from_attributes = True