"""
DocuForge — API principal
"""
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware

from app.core.config import settings
from app.core.logging import setup_logging

from app.api.routes import convert
from app.api.routes import health
from app.api.routes import tools
from app.api.routes import jobs

@asynccontextmanager
async def lifespan(app: FastAPI):
    setup_logging()
    yield


app = FastAPI(
    title="DocuForge API",
    description="Plataforma de conversión de documentos — PDF, Office, OCR",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# ── Middlewares ────────────────────────────────────────────────────────────────
app.add_middleware(GZipMiddleware, minimum_size=1000)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Routers ───────────────────────────────────────────────────────────────────
app.include_router(health.router,  prefix="/api/v1",         tags=["health"])
app.include_router(convert.router, prefix="/api/v1/convert", tags=["conversión"])
app.include_router(tools.router,   prefix="/api/v1/tools",   tags=["herramientas PDF"])
app.include_router(jobs.router,    prefix="/api/v1/jobs",    tags=["trabajos async"])