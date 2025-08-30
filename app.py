from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

# Simple GET endpoint
@app.get("/ping")
def ping():
    return {"message": "pong"}

# Data model for POST
class Message(BaseModel):
    user: str
    text: str

# Simple POST endpoint
@app.post("/message")
def create_message(msg: Message):
    return {"status": "success", "data": msg.dict()}
