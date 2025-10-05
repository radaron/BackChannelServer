from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app.core.config import settings
from app.core.database import init_db
from app.routers import auth, client, manage

templates = Jinja2Templates(directory="app/templates")

API_V1_PREFIX = "/api/v1"


@asynccontextmanager
async def lifespan(app_obj: FastAPI) -> AsyncGenerator[None, None]:
    await init_db()
    yield


app = FastAPI(
    title="BackChannel Server",
    description="BackChannel Server API",
    docs_url=None,
    redoc_url=None,
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.allowed_origins],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix=API_V1_PREFIX)
app.include_router(client.router, prefix=API_V1_PREFIX)
app.include_router(manage.router, prefix=API_V1_PREFIX)
app.mount("/assets", StaticFiles(directory="app/assets"), name="assets")


@app.get("/")
@app.get("/manage")
@app.get("/login")
async def serve_frontend(request: Request) -> Response:
    return templates.TemplateResponse("index.html", {"request": request})
