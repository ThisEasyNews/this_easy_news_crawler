from fastapi import FastAPI
from app.api.v1 import batch

from dotenv import load_dotenv

load_dotenv()
app = FastAPI()

app.include_router(
    batch.router, 
    prefix="/api/v1/batch", 
    tags=["Batch Operations"]
)

@app.get("/")
def read_root():
    return {"message": "This Easy News API is running!"}