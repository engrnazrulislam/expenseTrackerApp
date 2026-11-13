from fastapi import FastAPI

app = FastAPI()

@app.get('/')
def read_main():
    return {"message": "Hello, World!"}


@app.get("/about")
def about():
    return "This is the about page"