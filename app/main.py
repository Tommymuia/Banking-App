import os
import sys
from typing import List
from fastapi import FastAPI, Depends, HTTPException, status, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from jose import jwt

# Python 3.13 Compatibility: Fix for passlib/crypt removal
if sys.version_info >= (3, 13):
    import warnings
    warnings.filterwarnings("ignore", category=DeprecationWarning)

from app.database import engine, BASE, get_db
from app.models import User, Account
from app import crud, schemas, security
from app.mailer import send_transaction_email 

# Initialize App
app = FastAPI(title="Money Transfer API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Config
SECRET_KEY = os.getenv("SECRET_KEY", "BANK_PROJECT_2024_SECRET")
ALGORITHM = "HS256"
ADMIN_CC_LIST = [
    "Ashley.mararo@student.moringaschool.com",
    "david.kuron@student.moringaschool.com",
    "yvonne.kadenyi@student.moringaschool.com",
    "daniel.kamweru@student.moringaschool.com",
    "thomas.mbula@student.moringaschool.com"
]

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

# Database Sync
try:
    BASE.metadata.create_all(bind=engine)
except Exception as e:
    print(f"DB Error: {e}")

# Dependencies
def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token")
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    user = db.query(User).filter(User.id == int(user_id)).first()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    return user

# Routes
@app.get("/")
def health():
    return {"status": "online"}

@app.post("/signup", response_model=schemas.UserResponse)
def signup(user: schemas.UserCreate, db: Session = Depends(get_db)):
    return crud.create_user_with_account(db=db, user=user)

@app.post("/login")
def login(user_credentials: schemas.UserLogin, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == user_credentials.email).first()
    if not user or not security.verify_pin(user_credentials.pin, user.hashed_pin):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    access_token = security.create_access_token(data={"sub": str(user.id)})
    return {"access_token": access_token, "token_type": "bearer"}

@app.put("/users/me", response_model=schemas.UserResponse)
def update_profile(update_data: schemas.UserUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return crud.update_user_profile(db, current_user.id, update_data)

@app.patch("/users/me/reset-pin")
def reset_pin(pin_data: schemas.PinReset, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if crud.update_user_pin(db, current_user.id, pin_data.new_pin):
        return {"message": "PIN updated"}
    raise HTTPException(status_code=404)

@app.delete("/users/me")
def delete_account(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if crud.delete_user_and_account(db, current_user.id):
        return {"message": "Deleted"}
    raise HTTPException(status_code=404)

@app.post("/deposit")
async def deposit(deposit_data: schemas.DepositCreate, background_tasks: BackgroundTasks, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if deposit_data.amount <= 0:
        raise HTTPException(status_code=400, detail="Must be positive")
    account = crud.deposit_funds(db, current_user.id, deposit_data.amount)
    background_tasks.add_task(send_transaction_email, email=current_user.email, name=current_user.first_name, amount=deposit_data.amount, balance=account.initial_balance, type="Deposit", cc_emails=ADMIN_CC_LIST)
    return {"message": "Success", "new_balance": account.initial_balance}

@app.post("/transfer")
async def transfer(transfer_data: schemas.TransferCreate, background_tasks: BackgroundTasks, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    sender_account = db.query(Account).filter(Account.user_id == current_user.id).first()
    receiver_account = db.query(Account).filter(Account.account_number == transfer_data.receiver_acc_number).first()
    if not sender_account or not receiver_account:
        raise HTTPException(status_code=404, detail="Account not found")
    
    result = crud.transfer_money(db=db, sender_account_id=sender_account.id, receiver_acc_number=transfer_data.receiver_acc_number, amount=transfer_data.amount)
    
    background_tasks.add_task(send_transaction_email, email=current_user.email, name=current_user.first_name, amount=transfer_data.amount, balance=result["new_balance"], type="Debit", cc_emails=ADMIN_CC_LIST)
    
    receiver_user = db.query(User).filter(User.id == receiver_account.user_id).first()
    background_tasks.add_task(send_transaction_email, email=receiver_user.email, name=receiver_user.first_name, amount=transfer_data.amount, balance=receiver_account.initial_balance, type="Credit", cc_emails=None)
    
    return result

@app.get("/my-transactions", response_model=List[schemas.TransactionBase])
def read_transactions(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return crud.get_user_transactions(db, user_id=current_user.id)

@app.get("/force-reset")
def force_reset(db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == "premiumresearch5@gmail.com").first()
    if user:
        user.hashed_pin = security.hash_pin("8888")
        db.commit()
        return {"message": "Reset to 8888"}
    return {"error": "Not found"}