from app.db.session import engine
from fastapi import FastAPI

app = FastAPI(
    title="Campus Booking System API",
    version="1.0.0",
)

@app.get("/health")
def health():
    return {"status": "ok"}