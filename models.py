from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Float, BigInteger
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
from passlib.context import CryptContext
import bcrypt

Base = declarative_base()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class BaseTimeStemp(Base):
    __abstract__ = True
    id = Column(BigInteger, primary_key=True, index=True)
    time_created = Column(DateTime(timezone=True), server_default=func.now())
    time_update = Column(DateTime, onupdate=datetime.now(), default=datetime.now())


class Book(BaseTimeStemp):
    __tablename__ = "book"
    title = Column(String)
    rating = Column(Float)
    author_id = Column(Integer, ForeignKey('author.id'))

    author = relationship('Author')


class Author(BaseTimeStemp):
    __tablename__ = "author"
    name = Column(String)
    age = Column(Integer)


class User(BaseTimeStemp):
    __tablename__ = "user"
    username = Column(String, unique=True)
    email = Column(String, unique=True)
    hashed_password = Column(String)


class Token(BaseTimeStemp):
    __tablename__ = 'token'
    user_id = Column(Integer, ForeignKey('user.id'))
    token = Column(String, unique=True)

    user = relationship('User')


class ResetPasswordToken(BaseTimeStemp):
    __tablename__ = 'password_reset_token'
    user_id = Column(Integer, ForeignKey('user.id'))
    token = Column(String, unique=True)

    user = relationship('User')



