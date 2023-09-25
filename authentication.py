from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext
from datetime import datetime, timedelta
from typing import Optional
from jose import jwt
from passlib.hash import pbkdf2_sha256 as sha256

from models import User, Token
from fastapi_sqlalchemy import db
from dotenv import load_dotenv
load_dotenv('.env')

ALGORITHM = "HS256"
SECRET_KEY = "your-secret-key"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def get_user_by_username(username: str):
    return db.session.query(User).filter((User.username == username) | (User.email == username)).first()
#
#
def authenticate_user(username: str, password: str):
    user = get_user_by_username(username)
    if not user:
        return False
    if not sha256.verify(password, user.hashed_password):
        return False
    return user

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")
oauth2_scheme_user = OAuth2PasswordBearer(tokenUrl="token")


async def get_current_user(token: str = Depends(oauth2_scheme_user)):
    token = db.session.query(Token).filter(Token.token == token).first()
    if token:
        user = db.session.query(User).filter(User.id == token.user_id).first()
        if not user:
            raise HTTPException(status_code=401, detail="Invalid authentication credentials")
        return user
    raise HTTPException(status_code=400, detail="Invalid Token")