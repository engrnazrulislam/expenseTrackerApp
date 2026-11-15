from fastapi import FastAPI, APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from model import User
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from typing import Annotated, Optional
from database import SessionLocal
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from jose import jwt, JWTError
from datetime import timedelta, datetime, timezone

bcrypt_context = CryptContext(schemes=['bcrypt'], deprecated='auto')
OAuth2_bearer = OAuth2PasswordBearer(tokenUrl='login')
SECRET_KEY = "f5aa3f803072b62117bd40efd00db090c0a29247a39ef2b99c7cf486c339ec02"
ALGORITHM = "HS256"
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
    print(user)
    if not user:
        return False
    if bcrypt_context.verify(password, user.hashed_password):
        return user
    return False

# Access Token Creation Function
def create_access_token(username: str, user_id: int, expires_delta: timedelta):
    encode={"sub": username, "id": user_id}
    expire=datetime.now(timezone.utc)+expires_delta
    encode.update({"exp": expire})
    return jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)


# Get Current User Function
def get_current_user(token: Annotated[str, Depends(OAuth2_bearer)], db):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        user_id = payload.get("id")
        if username is None or user_id is None:
            raise HTTPException(status_code=401, detail="User not found")
        return {"username": username, "id": user_id}
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")


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
    if user is False:
        raise HTTPException(status_code=401, detail="Invalid username or password")
    token = create_access_token(user.username, user.id, timedelta(minutes=30))
    return JSONResponse(status_code=200, content={"access_token": token, "token_type": "bearer"})
    