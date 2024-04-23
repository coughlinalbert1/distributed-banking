import asyncio, datetime, logging, os, requests
from datetime import timedelta, datetime
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import jwt, JWTError
from pydantic import BaseModel
from redis_om import get_redis_connection, HashModel
from typing import Optional
from dotenv import load_dotenv


load_dotenv()
AUTHENTICATION = os.getenv('AUTHENTICATION')
ACCOUNT = os.getenv('ACCOUNT')
TRANSACTION = os.getenv('TRANSACTION')
SECRET_KEY = os.getenv('SECRET_KEY')
ALGORITHM = os.getenv('ALGORITHM')
ACCESS_TOKEN_EXPIRE_MINUTES = os.getenv('ACCESS_TOKEN_EXPIRE_MINUTES')
PORT = os.getenv('REDIS_PORT')
PASSWORD = os.getenv('REDIS_PASSWORD')
HOST = os.getenv('REDIS_HOST')

app = FastAPI(
    title="Transaction Service", 
    version="1.0", 
    description="Transaction Service using FastAPI and Redis"
)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

origins = [
    ACCOUNT,
    TRANSACTION,
    AUTHENTICATION
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

redis = get_redis_connection(
    host=HOST,
    port=PORT,
    password=PASSWORD,
    decode_responses=True
)

'''
Data models for requests, response, and redis schema
'''
class AccountModel(HashModel):
    user_id: str
    username: str
    email: str
    hashed_password: str
    phone_num: Optional[str] = None
    first_name: str
    last_name: str
    balance: Optional[float] = 0.0
    access: str = ""

    class Meta: 
        database = redis

class TransferRequest(BaseModel):
    receiver_username: str
    amount: float

class DepositRequest(BaseModel):
    amount: float

class WithdrawRequest(BaseModel):
    amount: float


#####################################################################
'''
Utility Functions
'''

def get_user_by_name(username: str):
    all_keys = redis.scan_iter("*")
    keys = [key.split(":")[-1] for key in all_keys if "AccountModel" in key]
    if not keys:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No user found")
    for key in keys:
        user = AccountModel.get(key.split(":")[-1])
        if user.username == username:
            return user
    return None

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({'exp': expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def call_authentication_service(username: str, password: str):
    url = f'{AUTHENTICATION}/login/'
    data = {
        'username': username,
        'password': password
    }
    req = requests.post(url, data=data)

    if req.status_code == status.HTTP_404_NOT_FOUND:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    elif req.status_code == status.HTTP_401_UNAUTHORIZED:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid password")
    
    response = req.json()
    print(response)
    return response

def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    user = get_user_by_name(username)
    if user is None:
        raise credentials_exception
    return user

#####################################################################

'''
API Endpoints
'''

@app.post("/token/", response_model=None)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    if not call_authentication_service(form_data.username, form_data.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    user = get_user_by_name(form_data.username)
    access_token_expires = timedelta(minutes=int(ACCESS_TOKEN_EXPIRE_MINUTES))
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/deposit", response_model=None)
async def deposit_funds(deposit_request: DepositRequest, current_user: AccountModel = Depends(get_current_user)):
    user = get_user_by_name(current_user.username)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    if user.username != current_user.username:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Unauthorized user")
    user.balance += deposit_request.amount

    try:
        await asyncio.to_thread(user.save)
        logging.info(f'Account saved for {user.username}')
    except Exception as e:
        logging.error(f'Failed to save account for {user.username}: {str(e)}')
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to create account")
    return {
        "message": "Deposit successful",
        "username": user.username,
        "account": user.user_id,
        "balance": user.balance
    }

@app.post("/withdraw", response_model=None)
async def withdraw_funds(withdraw_request: WithdrawRequest, current_user: dict = Depends(get_current_user)):
    user = get_user_by_name(current_user.username)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    if user.username != current_user.username:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Unauthorized user")
    user.balance -= withdraw_request.amount

    try:
        await asyncio.to_thread(user.save)
        logging.info(f'Account update for {user.username}')
    except Exception as e:
        logging.error(f'Failed to update account for {user.username}: {str(e)}')
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to update account")
    return {
        "message": f"Withdrawl successful: {withdraw_request.amount}",
        "username": user.username,
        "account": user.user_id,
        "balance": user.balance
    }

@app.post("/transfer", response_model=None)
async def transfer_funds(transfer_request: TransferRequest, current_user: dict = Depends(get_current_user)):
    sender = get_user_by_name(current_user.username)
    if not sender:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    if sender.username != current_user.username:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Unauthorized user")
    receiver = get_user_by_name(transfer_request.receiver_username)
    if not sender or not receiver:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    if sender.balance < transfer_request.amount:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Insufficient funds")
    sender.balance -= transfer_request.amount
    receiver.balance += transfer_request.amount

    try:
        await asyncio.to_thread(sender.save)
        logging.info(f'Account update for {sender.username}')
    except Exception as e:
        logging.error(f'Failed to update account for {sender.username}: {str(e)}')
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to update account")
    
    try:
        await asyncio.to_thread(receiver.save)
        logging.info(f'Account update for {sender.username}')
    except Exception as e:
        logging.error(f'Failed to update account for {receiver.username}: {str(e)}')
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to update account")
    return {
        "message": f"Withdrawl successful: {transfer_request.amount}",
        "username": sender.username,
        "account": sender.user_id,
        "balance": sender.balance
    }







