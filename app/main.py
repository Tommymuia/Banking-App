from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import engine, BASE, get_db
from app.models import User, Account
from app import crud, schemas, security
from fastapi.security import OAuth2PasswordBearer
from jose import jwt

# 1. SECURITY CONSTANTS (Must match app/security.py)
SECRET_KEY = "BANK_PROJECT_2024_SECRET" 
ALGORITHM = "HS256"

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

# 2. DATABASE SYNC
print("--- DATABASE SYNC STARTING ---")
try:
    BASE.metadata.create_all(bind=engine)
    print("--- DATABASE TABLES VERIFIED ---")
except Exception as e:
    print(f"--- ERROR CREATING TABLES: {e} ---")

app = FastAPI(title="Money Transfer API")

# 3. AUTHENTICATION DEPENDENCY
def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        print(f"DEBUG: Token Payload -> {payload}")
    except Exception as e:
        print(f"DEBUG: Decode Failed -> {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user_id = payload.get("sub")
    user = db.query(User).filter(User.id == int(user_id)).first()
    
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    
    return user

# --- AUTH ROUTES ---

@app.post("/signup", response_model=schemas.UserResponse)
def signup(user: schemas.UserCreate, db: Session = Depends(get_db)):
    return crud.create_user_with_account(db=db, user=user)

@app.post("/login")
def login(user_credentials: schemas.UserLogin, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == user_credentials.email).first()

    if not user or not security.verify_pin(user_credentials.pin, user.hashed_pin):
        raise HTTPException(status_code=401, detail="Invalid email or PIN")

    access_token = security.create_access_token(data={"sub": str(user.id)})
    return {"access_token": access_token, "token_type": "bearer"}

# --- BANKING ROUTES ---

@app.post("/deposit")
def deposit(deposit_data: schemas.DepositCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if deposit_data.amount <= 0:
        raise HTTPException(status_code=400, detail="Deposit amount must be positive")
    
    account = crud.deposit_funds(db, current_user.id, deposit_data.amount)
    
    return {
        "message": "Deposit successful", 
        "new_balance": account.initial_balance,
        "account_number": account.account_number
    }

@app.post("/transfer")
def transfer(transfer_data: schemas.TransferCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """
    Uses the TransferCreate schema to read the receiver account and amount 
    from the JSON body in Thunder Client.
    """
    # 1. We need the sender's actual account ID for the CRUD function
    sender_account = db.query(Account).filter(Account.user_id == current_user.id).first()
    
    if not sender_account:
        raise HTTPException(status_code=404, detail="Sender account not found")

    # 2. Execute transfer logic
    result = crud.transfer_money(
        db=db, 
        sender_account_id=sender_account.id, 
        receiver_acc_number=transfer_data.receiver_acc_number, 
        amount=transfer_data.amount
    )
    
    return result

@app.get("/my-transactions", response_model=list[schemas.TransactionBase])
def read_transactions(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    # Note: Ensure crud.get_user_transactions is updated to return receiver_id/sender_id
    return crud.get_user_transactions(db, user_id=current_user.id)