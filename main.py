from fastapi import FastAPI
import model
from database import engine

# Create the database tables
model.Base.metadata.create_all(bind=engine)

app = FastAPI()


@app.get('/')
def read_main():
    return {"message": "Welcome to the FastAPI application!"}


@app.get("/about")
def about():
    return "This is the about page"