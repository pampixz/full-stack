from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import PlainTextResponse, Response

from .api.v1.routes import router as api_v1
from .api.v1.entries import router as entries_router
from .api.v1.auth import router as auth_router
from .api.v1.meeting import router as meet_router
from .api.v1.admin import router as admin_router
from .api.v1.entry_files import router as entry_files_router
from .api.v1.weather import router as weather_router

from backend.app.db.database import engine, Base

# Импорты моделей нужны, чтобы SQLAlchemy "увидел" таблицы
from backend.app.models.entry import Entry
from backend.app.models.user import User
from backend.app.models.meeting import Meeting
from backend.app.models.refresh_token import RefreshToken
from backend.app.models.entry_file import EntryFile


app = FastAPI(title="Mood Diary API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def root():
    return {"service": "mood-diary", "version": "0.1.0"}


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/robots.txt", response_class=PlainTextResponse)
def robots():
    return """User-agent: *
Allow: /
Disallow: /api/
Disallow: /docs
Disallow: /login
Disallow: /register
Disallow: /entries
Disallow: /entries/new
Disallow: /meetings
Disallow: /meetings/new
Disallow: /rooms

Sitemap: http://127.0.0.1:8080/sitemap.xml
"""


@app.get("/sitemap.xml", response_class=Response)
def sitemap():
    xml = """<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">

  <url>
    <loc>http://localhost:5173/</loc>
    <priority>1.0</priority>
  </url>

</urlset>
"""
    return Response(content=xml, media_type="application/xml")


app.include_router(api_v1, prefix="/api/v1")
app.include_router(entries_router, prefix="/api/v1")
app.include_router(auth_router, prefix="/api/v1")
app.include_router(meet_router, prefix="/api/v1")
app.include_router(admin_router, prefix="/api/v1")
app.include_router(entry_files_router, prefix="/api/v1")
app.include_router(weather_router, prefix="/api/v1")


Base.metadata.create_all(bind=engine)