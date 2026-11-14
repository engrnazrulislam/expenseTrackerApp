from fastapi import FastAPI, APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from model import User
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from typing import Annotated, Optional
from database import SessionLocal
from fastapi.security import OAuth2PasswordRequestForm

bcrypt_context = CryptContext(schemes=['bcrypt'], deprecated='auto')

router = APIRouter()

class Create_Users(BaseModel):
    username: str
    email: str
    hashed_password: str

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

db_dependency = Annotated[Session, Depends(get_db)]

# Authentication User Registration Endpoint
def authenticate_user(username, password, db):
    user = db.query(User).filter(User.username == username).first()
    if not user:
        return False
    if bcrypt_context.verify(password, user.hashed_password):
        return True
    return False


@router.post("/auth/register")
def register_user(db: db_dependency,new_user: Create_Users):
    # Check if the username or email already exists in the database
    existing_user = db.query(User).filter(User.username == new_user.username).first()
    if existing_user is not None:
        raise HTTPException(status_code=400, detail="Username already exists")
    # Check if the email already exists in the database
    existing_email = db.query(User).filter(User.email == new_user.email).first()
    if existing_email is not None:
        raise HTTPException(status_code=400, detail="Email already exists")
    
    user_model = User(
        username=new_user.username,
        email=new_user.email,
        hashed_password=bcrypt_context.hash(new_user.hashed_password)
    )
    db.add(user_model)
    db.commit()
    return JSONResponse(status_code=201, content={"message": "User created successfully"})

@router.post("/auth/login")
def login_user(db: db_dependency, form_data: Annotated[OAuth2PasswordRequestForm, Depends()]):
    user = authenticate_user(form_data.username, form_data.password, db)
    if user is True:
        return JSONResponse(status_code=200, content={"message": "Login successful"})
    if user is False:
        raise HTTPException(status_code=401, detail="Invalid username or password")