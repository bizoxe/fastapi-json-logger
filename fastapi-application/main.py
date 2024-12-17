import uvicorn
from fastapi import FastAPI

app = FastAPI()


@app.get("/")
def greeting():
    return {"message": "hello from fastapi"}


if __name__ == "__main__":
    uvicorn.run(app)
