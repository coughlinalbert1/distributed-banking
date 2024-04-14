from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel
from redis_om import get_redis_connection, HashModel
import os
from hash import Hash
from typing import Optional
from jose import jwt
from datetime import datetime, timedelta
from dotenv import load_dotenv


load_dotenv()
SECRET_KEY = os.getenv('SECRET_KEY')
ALGORITHM = os.getenv('ALGORITHM')
ACCESS_TOKEN_EXPIRE_MINUTES = os.getenv('ACCESS_TOKEN_EXPIRE_MINUTES')
PORT = os.getenv('REDIS_PORT')
PASSWORD = os.getenv('REDIS_PASSWORD')
HOST = os.getenv('REDIS_HOST')

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

app = FastAPI()

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
        raise HTTPException(status_code=404, detail="No user found")
    for key in keys:
        user = UserResponse.get(key.split(":")[-1])
        if user.username == username:
            return user
    return None

def authenticate_user(username: str, password: str):
    user = get_user(username)
    if not user:
        return False
    if not Hash.verify(user.password, password):
        return False
    return user

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({'exp': expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

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
    user_response.save()
    return format(user_response.pk)

@app.post("/token", response_model=None)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=timedelta(minutes=eval(ACCESS_TOKEN_EXPIRE_MINUTES))
    )
    return {"access_token": access_token, "token_type": "bearer"}

