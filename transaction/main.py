from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel
from redis_om import get_redis_connection, HashModel
import os, requests, httpx, logging, asyncio
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
    title="Account Service", 
    version="1.0", 
    description="Account Service API using FastAPI and Redis"
)
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

class Account(BaseModel):
    username: str
    email: str
    password: str
    phone_num: Optional[str] = None
    first_name: str
    last_name: str

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
    time_expires: Optional[str] = None

    class Meta: 
        database = redis

class AccountResponse(BaseModel):
    user_id: int
    username: str
    email: str
    hashed_password: str

def format_response(account: AccountModel):
    return {
        'user_id': account.user_id,
        'username': account.username,
        'email': account.email,
        'phone_num': account.phone_num,
        'first_name': account.first_name,
        'last_name': account.last_name,
        'balance': account.balance
    }

def get_user(user_id: str):
    all_keys = redis.scan_iter("*")
    keys = [key.split(":")[-1] for key in all_keys if "AccountModel" in key]
    if not keys:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No user found")
    for key in keys:
        user = AccountModel.get(key.split(":")[-1])
        if user.user_id == user_id:
            return user
    return None

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


@app.post("/create/")
async def account(request: Account):
    url = f'{AUTHENTICATION}/register/'
    headers = {'Content-Type': 'application/json'}
    data = {
        'username': request.username,
        'password': request.password
    }
    req = requests.post(url, json=data, headers=headers)

    if req.status_code == status.HTTP_400_BAD_REQUEST:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="username is taken")
    elif req.status_code == status.HTTP_404_NOT_FOUND:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User registration failed")
    
    response = req.json()
    user_id = response.get('user_ID')
    hashed_password = response.get('password')

    if not user_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User ID is missing in the response")
    if not hashed_password:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Hashed password is missing in the response")
    
    account = AccountModel(
        user_id=user_id,
        username=request.username,
        hashed_password=hashed_password,
        email=request.email,
        phone_num=request.phone_num,
        first_name=request.first_name,
        last_name=request.last_name
    )
    try:
        await asyncio.to_thread(account.save)
        logging.info(f'Account saved for {account.username}')
    except Exception as e:
        logging.error(f'Failed to save account for {account.username}: {str(e)}')
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to create account")
    
    return format_response(account)

@app.get("/account/{user_id}")
async def get_account(user_id: str):
    account = get_user(user_id)
    if not account:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Account not found")
    return format_response(account)


@app.post("/login/")
async def login(account: OAuth2PasswordRequestForm = Depends()):
    url = f'{AUTHENTICATION}/login/'
    headers = {'Content-Type': 'application/json'}
    data = {
        'username': account.username,
        'password': account.password
    }
    req = requests.post(url, json=data, headers=headers)

    if req.status_code == status.HTTP_404_NOT_FOUND:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    elif req.status_code == status.HTTP_401_UNAUTHORIZED:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid password")
    
    response = req.json()
    
    account = get_user_by_name(response['username'])
    if not account:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Account not found")

    account.access = response['access_token']
    try:
        await asyncio.to_thread(account.save)
        logging.info(f'Access token saved for {account.username}')
    except Exception as e:
        logging.error(f'Failed to save access token for {account.username}: {str(e)}')
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to update account")
    
    account_info = format_response(account)
    
    return {
        'access_token': response['access_token'],
        'token_type': response['token_type'],
        'username': account_info['username'],
        'user_id': account_info['user_id'],
        'email': account_info['email'],
        'phone_num': account_info['phone_num'],
        'first_name': account_info['first_name'],
        'last_name': account_info['last_name'],
        'balance': account_info['balance']
    }


