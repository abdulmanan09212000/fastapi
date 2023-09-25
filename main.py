from datetime import timedelta
import random

import uvicorn
from fastapi import FastAPI, HTTPException, status, Depends, APIRouter
from fastapi_sqlalchemy import DBSessionMiddleware, db
from passlib.context import CryptContext

from authentication import ACCESS_TOKEN_EXPIRE_MINUTES, create_access_token, authenticate_user, get_current_user, \
    SECRET_KEY, ALGORITHM
from schema import Book as SchemaBook, CreateUser, Login, ChangePassword, ResetPassword, ForgetPassword
from schema import Author as SchemaAuthor
from passlib.hash import pbkdf2_sha256 as sha256
from fastapi.security import OAuth2PasswordRequestForm
from fastapi_mail import FastMail, MessageSchema

from models import Book, Author, User, Token, ResetPasswordToken
import os
from dotenv import load_dotenv
from sendgrid import SendGridAPIClient

from sendgrid.helpers.mail import Mail

load_dotenv('.env')

app = FastAPI()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/hello/{name}")
async def say_hello(name: str):
    return {"message": f"Hello {name}"}


student_names = [{"student_name": "Sauvik"}, {"student_name": "Mathew"}, {"student_name": "Peter"}]


@app.get("/courses/")
async def get_students(start: int, end: int):
    return student_names[start: start + end]


app.add_middleware(DBSessionMiddleware, db_url=os.environ['DATABASE_URL'])


@app.post('/book/', response_model=SchemaBook)
async def book(book: SchemaBook):
    db_book = Book(title=book.title, rating=book.rating, author_id=book.author_id)
    db.session.add(db_book)
    db.session.commit()
    return db_book


@app.get('/book/')
async def book():
    book = db.session.query(Book).all()
    return book


@app.post('/author/', response_model=SchemaAuthor)
async def author(author: SchemaAuthor):
    db_author = Author(name=author.name, age=author.age)
    db.session.add(db_author)
    db.session.commit()
    return db_author


@app.get('/author/')
async def author():
    author = db.session.query(Author).all()
    return author


@app.delete('/author/{id}/')
async def author(id: int):
    author = db.session.get(Author, id)
    db.session.delete(author)
    db.session.commit()
    return {'msg': "SuccessFully Delete"}


@app.get('/author/{id}/')
async def author(id: int):
    author = db.session.get(Author, id)
    return author


import string

def check_password(password):
    if len(password) < 8:
        return False
    has_uppercase = any(char in string.ascii_uppercase for char in password)
    has_lowercase = any(char in string.ascii_lowercase for char in password)
    has_special = any(char in string.punctuation for char in password)
    has_number = any(char in string.digits for char in password)
    return has_uppercase and has_lowercase and has_special and has_number


@app.post('/signup/', response_model=CreateUser)
async def signup(createuser: CreateUser):
    email = createuser.email
    check = check_password(createuser.password)
    if not check:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password at least 8 character 1 uppercase 1 lowercase 1 special case 1 number"
        )
    hashed_password = sha256.hash(createuser.password)
    user_db = db.session.query(User).filter(User.email == email.lower()).first()
    if user_db:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this email already exist"
        )
    db_user = User(username=createuser.username, email=createuser.email, hashed_password=hashed_password)
    db.session.add(db_user)
    db.session.commit()
    return createuser


@app.post("/login/")
async def login_for_access_token(form_data: Login):
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        return {'msg': "Your username and password is wrong"}
    id = user.id
    email = user.email
    username = user.username
    if not user:
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    if db.session.query(Token).filter(Token.user_id == id).first():
        token = db.session.query(Token).filter(Token.user_id == id).first().token
    else:
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": user.username}, expires_delta=access_token_expires
        )
        db_token = Token()
        db_token.user_id = id
        db_token.token = access_token
        db.session.add(db_token)
        db.session.commit()
        db.session.close()
        token = access_token
    data = {}
    data["id"] = id
    data["email"] = email
    data["username"] = username
    context = {"access_token": token, "token_type": "bearer", "user": data}
    return context


@app.get('/logout/')
async def logout(current_user: User = Depends(get_current_user)):
    token = db.session.query(Token).filter(Token.user_id == current_user.id).first()
    db.session.delete(token)
    db.session.commit()
    return {'msg': "Successfully Logout"}


@app.put('/change_password/')
async def change_password(form_data: ChangePassword, current_user: User = Depends(get_current_user)):
    token = db.session.query(Token).filter(Token.user_id == current_user.id).first()
    hashed_password = sha256.hash(form_data.password)
    user = db.session.query(User).filter(User.id == token.user_id).first()
    user.hashed_password = hashed_password
    db.session.add(user)
    db.session.commit()
    return {"msg": "Your password successfully changed"}


@app.get('/user/')
async def user():
    user = db.session.query(User).all()
    return user


@app.get("/items/")
async def read_items(current_user: User = Depends(get_current_user)):
    return {"username": current_user.username}


async def send_password_reset_email(email: str, reset_url: str):
    message = Mail(
        from_email=os.environ["FORM_MAIL"],
        to_emails=email.email,
        subject='Password reset',
        html_content=f'Click <a href="{reset_url}">here</a> to reset your password'
    )
    try:
        sg = SendGridAPIClient(api_key=os.environ['API_KEY'])
        response = sg.send(message)
        print(response.status_code)
        print(response.body)
        print(response.headers)
    except Exception as e:
        print(e.message)

@app.post("/forgot-password/")
async def forgot_password(email: ResetPassword):
    user = db.session.query(User).filter(User.email == email.email).first()
    if not user:
        raise HTTPException(status_code=400, detail="Email not found")
    reset_token = db.session.query(ResetPasswordToken).filter(ResetPasswordToken.user_id == user.id).first()
    if reset_token:
        token = reset_token.token
    else:
        token = random.randint(100000, 999999)
        reset_password_token = ResetPasswordToken()
        reset_password_token.user_id = user.id
        reset_password_token.token = token
        db.session.add(reset_password_token)
        db.session.commit()
    reset_url = f"https://example.com/reset-password/{token}"
    await send_password_reset_email(email=email, reset_url=reset_url)

    return {"message": "Password reset email sent"}

@app.post("/forgot-password/confirm/")
async def confirm_password(token: ForgetPassword):
    token_password = db.session.query(ResetPasswordToken).filter(token == token.token).first()
    if token_password:
        hashed_password = sha256.hash(token.password)
        user = db.session.query(User).filter(User.id == token_password.user_id).first()
        user.hashed_password = hashed_password
        db.session.add(user)
        db.session.commit()

if __name__ == '__main__':
    uvicorn.run(app, host='127.0.0.1', port=8000)
