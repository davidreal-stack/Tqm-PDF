"""
Schemas Pydantic para request / response de la API
"""
from __future__ import annotations

from enum import Enum
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, Field


# ── Formatos soportados ────────────────────────────────────────────────────────

class OutputFormat(str, Enum):
    # PDF
    PDF = "pdf"
    # Office
    DOCX = "docx"
    XLSX = "xlsx"
    PPTX = "pptx"
    # Texto / Web
    TXT = "txt"
    HTML = "html"
    MARKDOWN = "md"
    # Imagen
    PNG = "png"
    JPG = "jpg"


class ToolAction(str, Enum):
    COMPRESS = "compress"
    MERGE = "merge"
    SPLIT = "split"
    ROTATE = "rotate"
    WATERMARK = "watermark"
    PROTECT = "protect"
    UNLOCK = "unlock"
    OCR = "ocr"
    METADATA = "metadata"


class JobStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    DONE = "done"
    FAILED = "failed"


# ── Conversión ────────────────────────────────────────────────────────────────

class ConvertRequest(BaseModel):
    output_format: OutputFormat
    ocr_enabled: bool = False
    ocr_lang: str = "spa+eng"
    preserve_layout: bool = True
    dpi: int = Field(default=150, ge=72, le=600)


class ConvertResponse(BaseModel):
    job_id: UUID
    status: JobStatus
    download_url: Optional[str] = None
    filename: Optional[str] = None
    size_bytes: Optional[int] = None
    pages: Optional[int] = None
    processing_time_ms: Optional[int] = None
    error: Optional[str] = None


# ── Herramientas PDF ───────────────────────────────────────────────────────────

class CompressOptions(BaseModel):
    quality: str = Field(default="ebook", description="screen | ebook | printer | prepress")


class SplitOptions(BaseModel):
    pages: Optional[str] = Field(None, description="Ej: '1-3,5,7-9' o None para una página por archivo")


class RotateOptions(BaseModel):
    degrees: int = Field(90, description="90 | 180 | 270")
    pages: Optional[str] = Field(None, description="Ej: '1,3,5' o None para todas")


class WatermarkOptions(BaseModel):
    text: str = Field(..., description="Texto de la marca de agua")
    opacity: float = Field(default=0.3, ge=0.05, le=1.0)
    angle: int = Field(default=45, ge=0, le=360)
    font_size: int = Field(default=48, ge=12, le=120)


class ProtectOptions(BaseModel):
    user_password: str
    owner_password: Optional[str] = None
    allow_printing: bool = True
    allow_copying: bool = False


class OcrOptions(BaseModel):
    lang: str = "spa+eng"
    dpi: int = Field(default=300, ge=150, le=600)


class MergeOptions(BaseModel):
    order: Optional[List[int]] = Field(None, description="Índices en el orden deseado")


# ── Jobs ──────────────────────────────────────────────────────────────────────

class JobResponse(BaseModel):
    job_id: UUID
    status: JobStatus
    progress: int = Field(default=0, ge=0, le=100)
    result: Optional[ConvertResponse] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None