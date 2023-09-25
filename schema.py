from pydantic import BaseModel, EmailStr
from fastapi import FastAPI
from fastapi_sqlalchemy import DBSessionMiddleware

import os
from dotenv import load_dotenv

load_dotenv('.env')

app = FastAPI()
app.add_middleware(DBSessionMiddleware, db_url=os.environ['DATABASE_URL'])


class Book(BaseModel):
    title: str
    rating: float
    author_id: int

    class Config:
        orm_mode = True


class Author(BaseModel):
    name: str
    age: int

    class Config:
        orm_more = True


class SignupUser(BaseModel):
    username = str
    email = EmailStr
    hashed_password = str

    class Config:
        orm_more = True


class CreateUser(BaseModel):
    username: str
    email: EmailStr
    password: str

    class Config:
        orm_mode = True


class Login(BaseModel):
    username: str
    password: str

    class Config:
        orm_mode = True


class ChangePassword(BaseModel):
    password: str

    class Config:
        orm_mode = True


class ResetPassword(BaseModel):
    email: str

    class Config:
        orm_mode = True


class ForgetPassword(BaseModel):
    token: int
    password: str

    class Config:
        orm_mode = True