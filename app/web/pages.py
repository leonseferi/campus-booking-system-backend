from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

router = APIRouter()
templates = Jinja2Templates(directory="app/web/templates")


@router.get("/", response_class=HTMLResponse)
def root(request: Request):
    # redirect-ish landing: just show dashboard
    return templates.TemplateResponse("index.html", {"request": request})


@router.get("/portal", response_class=HTMLResponse)
def portal_home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@router.get("/portal/login", response_class=HTMLResponse)
def portal_login(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})


@router.get("/portal/rooms", response_class=HTMLResponse)
def portal_rooms(request: Request):
    return templates.TemplateResponse("rooms.html", {"request": request})


@router.get("/portal/bookings", response_class=HTMLResponse)
def portal_bookings(request: Request):
    return templates.TemplateResponse("bookings.html", {"request": request})


@router.get("/portal/admin", response_class=HTMLResponse)
def portal_admin(request: Request):
    return templates.TemplateResponse("admin.html", {"request": request})