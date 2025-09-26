from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.routers import auth, client, manage
from app.core.database import init_db

API_V1_PREFIX = "/api/v1"


@asynccontextmanager
async def lifespan(app_obj: FastAPI):
    await init_db()
    yield


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="BackChannel Server API",
    docs_url=None,
    redoc_url=None,
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.allowed_origins],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix=API_V1_PREFIX)
app.include_router(client.router, prefix=API_V1_PREFIX)
app.include_router(manage.router, prefix=API_V1_PREFIX)


@app.get("/")
def read_root():
    """Root endpoint"""
    return {
        "message": "Welcome to BackChannel Server",
        "version": settings.app_version,
        "docs": "/docs",
        "redoc": "/redoc",
    }
