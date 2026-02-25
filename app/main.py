from fastapi import FastAPI
from app.api.auth import router as auth_router
from app.api.rooms import router as rooms_router
from app.api.bookings import router as bookings_router
from app.api.users_admin import router as users_admin_router
from app.api.admin_metrics import router as admin_metrics_router
from fastapi.staticfiles import StaticFiles
from app.web.pages import router as web_router

app = FastAPI(title="Campus Booking System API", version="1.0.0")
app.include_router(auth_router)
app.include_router(rooms_router)
app.include_router(bookings_router)
app.include_router(users_admin_router)

app.include_router(web_router)
app.mount("/static", StaticFiles(directory="app/web/static"), name="static")
app.include_router(admin_metrics_router)

@app.get("/health")
def health():
    return {"status": "ok"}