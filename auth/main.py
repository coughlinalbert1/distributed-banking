from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel
from redis_om import get_redis_connection, HashModel
import os, logging, asyncio
from hash import Hash
from typing import Optional
from dotenv import load_dotenv



load_dotenv()
ACCOUNT= os.getenv('ACCOUNT')
TRANSACTION= os.getenv('TRANSACTION')
AUTHENTICATION= os.getenv('AUTHENTICATION')
SECRET_KEY = os.getenv('SECRET_KEY')
ALGORITHM = os.getenv('ALGORITHM')
ACCESS_TOKEN_EXPIRE_MINUTES = os.getenv('ACCESS_TOKEN_EXPIRE_MINUTES')
PORT = os.getenv('REDIS_PORT')
PASSWORD = os.getenv('REDIS_PASSWORD')
HOST = os.getenv('REDIS_HOST')

app = FastAPI(
    title="User Authentication Service", 
    version="1.0", 
    description="User Authentication Service using FastAPI and Redis"
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

'''
Data models for requests, response, and redis schema
'''
class User(BaseModel):
    username: str
    password: str
    
class UserModel(HashModel):
    username: str
    password: str
    class Meta:
        database = redis

class UserResponse(HashModel):
    user_ID: str
    username: str
    password: str
    access: str = ""
    time_expires: Optional[str] = None
    class Meta:
        database = redis

#####################################################################

'''
Utility Functions
'''
def get_user(username: str):
    all_keys = redis.scan_iter("*")
    keys = [key.split(":")[-1] for key in all_keys if "UserResponse" in key]
    if not keys:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No user found")
    for key in keys:
        user = UserResponse.get(key.split(":")[-1])
        if user.username == username:
            return user
    return None

def authenticate_user(username: str, password: str):
    user = get_user(username)
    if not user:
        return False  # Here consider throwing an exception or returning None
    if not Hash.verify(user.password, password):
        return False
    return user

def format(pk: str):
    user_response = UserResponse.get(pk)
    return {
        "user_ID": user_response.user_ID,
        "username": user_response.username,
        "password": user_response.password
    }

#####################################################################

'''
API Endpoints
'''

@app.post("/register/", response_model=None)
async def register(user_request: User):
    user = UserModel(username=user_request.username, password=user_request.password)

    # Check if user already exists
    if get_user(user.username):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Username already registered")
    
    hashed_password = Hash.bcrypt(user.password)
    # Store user in Redis
    user_response = UserResponse(
        user_ID=user.pk,
        username=user.username,
        password=hashed_password
    )
    try:
        await asyncio.to_thread(user_response.save)
        logging.info(f'Account saved for {user_response.username}')
    except Exception as e:
        logging.error(f'Failed to save account for {user_response.username}: {str(e)}')
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to create account")
    
    return format(user_response.pk)

@app.post("/login/", response_model=None)
async def verify(form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return {"success": "User authenticated successfully"}
