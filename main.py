from fastapi import FastAPI
import model
from database import engine
from router import auth
from fastapi.responses import JSONResponse
from fastapi import Depends, HTTPException
from typing import Annotated
from router.auth import get_current_user, get_db
from pydantic import BaseModel, Field
from model import User
from router.auth import bcrypt_context
from typing import Optional, Annotated
from sqlalchemy.orm import Session


# Create the database tables
model.Base.metadata.create_all(bind=engine)
app = FastAPI()

# Include the authentication routes
app.include_router(auth.router)

db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_current_user)]

class UpdateUsers(BaseModel):
    username: Optional[str]=Field(default=None)
    email: Optional[str]=Field(default=None)

class updatePassword(BaseModel):
    current_password: str
    new_password: str
    confirm_password: str


@app.get('/')
def read_main():
    return {"message": "Welcome to the expenseTracker API!"}


@app.get("/about")
def about():
    return "expenseTracker API is developed by Md. Nazrul Islam. It is a simple API for tracking expenses for users."

@app.get("/user_profile")
def get_user(user:user_dependency, db: db_dependency):
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication required")
    return db.query(User).filter(User.id==user.get('id')).first()
    

@app.put("/edit_profile")
def editProfile(user: user_dependency, db: db_dependency, updateUser: UpdateUsers):
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication required")
    user = db.query(User).filter(User.id==user.get('id')).first()
    
    user_data = updateUser.model_dump(exclude_unset=True)
    
    for key, value in user_data.items():
        setattr(user, key, value)
    
    db.commit()
    
    return JSONResponse(status_code=200, content={"message": "User updated successfully"})

@app.put("/password_update")
def updatePassword(user: user_dependency, db: db_dependency, update_password: updatePassword):
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication required")
    user = db.query(User).filter(User.id==user.get('id')).first()
    
    if not bcrypt_context.verify(update_password.current_password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Wrong Password")
    
    if update_password.new_password != update_password.confirm_password:
        raise HTTPException(status_code=400, detail="Password does not match")
    
    user.hashed_password = bcrypt_context.hash(update_password.new_password)
    db.add(user)
    db.commit()
    
    return JSONResponse(status_code=200, content={"message": "Password updated successfully"})