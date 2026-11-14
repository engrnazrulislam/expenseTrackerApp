from fastapi import FastAPI
import model
from database import engine
from router import auth

# Create the database tables
model.Base.metadata.create_all(bind=engine)
app = FastAPI()

# Include the authentication routes
app.include_router(auth.router)

@app.get('/')
def read_main():
    return {"message": "Welcome to the FastAPI application!"}


@app.get("/about")
def about():
    return "This is the about page"