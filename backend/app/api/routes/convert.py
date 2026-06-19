"""
/api/v1/convert — Endpoints de conversión de documentos
"""
from __future__ import annotations

import uuid
from pathlib import Path
from typing import List

from fastapi import APIRouter, File, Form, HTTPException, UploadFile
from fastapi.responses import FileResponse

from app.core.config import settings
from app.core.logging import logger
from app.schemas.documents import ConvertResponse, JobStatus, OutputFormat
from app.services.conversion_service import ConversionService

router = APIRouter()
service = ConversionService()

# Tipos MIME permitidos
ALLOWED_MIME = {
    "application/pdf",
    "application/msword",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "application/vnd.ms-excel",
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    "application/vnd.ms-powerpoint",
    "application/vnd.openxmlformats-officedocument.presentationml.presentation",
    "image/jpeg", "image/png", "image/webp", "image/tiff", "image/gif", "image/bmp",
    "text/html", "text/plain",
}


@router.post("/", response_model=ConvertResponse, summary="Convertir un documento")
async def convert_document(
    file: UploadFile = File(..., description="Archivo a convertir"),
    output_format: OutputFormat = Form(..., description="Formato de salida deseado"),
    ocr_enabled: bool = Form(False),
    preserve_layout: bool = Form(True),
    dpi: int = Form(150),
):
    """
    Convierte un documento al formato solicitado.

    **Combinaciones soportadas:**
    - PDF → DOCX, XLSX, TXT, HTML, PNG, JPG
    - DOCX / XLSX / PPTX → PDF
    - Imagen (PNG/JPG/WEBP) → PDF
    """
    # ── Validaciones ──────────────────────────────────────────────────────────
    if file.content_type not in ALLOWED_MIME:
        raise HTTPException(
            status_code=415,
            detail=f"Tipo de archivo no soportado: {file.content_type}"
        )

    max_bytes = settings.MAX_FILE_SIZE_MB * 1024 * 1024
    content = await file.read()
    if len(content) > max_bytes:
        raise HTTPException(
            status_code=413,
            detail=f"El archivo supera el límite de {settings.MAX_FILE_SIZE_MB} MB"
        )

    # ── Guardar archivo temporal ───────────────────────────────────────────────
    job_id = str(uuid.uuid4())
    upload_dir = settings.get_upload_dir() / job_id
    upload_dir.mkdir(parents=True, exist_ok=True)

    input_path = upload_dir / file.filename
    input_path.write_bytes(content)

    log = logger.bind(job_id=job_id, filename=file.filename, output_format=output_format)
    log.info("Conversión recibida")

    # ── Convertir ──────────────────────────────────────────────────────────────
    try:
        result = await service.convert(
            input_path=input_path,
            output_format=output_format,
            job_id=job_id,
            preserve_layout=preserve_layout,
            dpi=dpi,
        )
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except RuntimeError as e:
        log.error("Error en conversión", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        log.error("Error inesperado", error=str(e))
        raise HTTPException(status_code=500, detail="Error interno al procesar el archivo")
    finally:
        input_path.unlink(missing_ok=True)

    download_url = f"/api/v1/convert/download/{job_id}/{result.filename}"

    return ConvertResponse(
        job_id=uuid.UUID(job_id),
        status=JobStatus.DONE,
        download_url=download_url,
        filename=result.filename,
        size_bytes=result.size_bytes,
        processing_time_ms=result.processing_time_ms,
    )


@router.post("/batch", response_model=List[ConvertResponse], summary="Conversión por lotes")
async def convert_batch(
    files: List[UploadFile] = File(...),
    output_format: OutputFormat = Form(...),
):
    """Convierte múltiples archivos en una sola llamada."""
    if len(files) > settings.MAX_BATCH_FILES:
        raise HTTPException(
            status_code=422,
            detail=f"Máximo {settings.MAX_BATCH_FILES} archivos por lote"
        )

    results = []
    for file in files:
        content = await file.read()
        job_id = str(uuid.uuid4())
        upload_dir = settings.get_upload_dir() / job_id
        upload_dir.mkdir(parents=True, exist_ok=True)
        input_path = upload_dir / file.filename
        input_path.write_bytes(content)

        try:
            result = await service.convert(input_path, output_format, job_id=job_id)
            results.append(ConvertResponse(
                job_id=uuid.UUID(job_id),
                status=JobStatus.DONE,
                download_url=f"/api/v1/convert/download/{job_id}/{result.filename}",
                filename=result.filename,
                size_bytes=result.size_bytes,
                processing_time_ms=result.processing_time_ms,
            ))
        except Exception as e:
            results.append(ConvertResponse(
                job_id=uuid.UUID(job_id),
                status=JobStatus.FAILED,
                error=str(e),
            ))
        finally:
            input_path.unlink(missing_ok=True)

    return results


@router.get("/download/{job_id}/{filename}", summary="Descargar resultado")
async def download_result(job_id: str, filename: str):
    """Descarga el archivo convertido."""
    output_path = settings.get_output_dir() / job_id / filename

    if not output_path.exists():
        raise HTTPException(status_code=404, detail="Archivo no encontrado o expirado")

    return FileResponse(
        path=str(output_path),
        filename=filename,
        media_type="application/octet-stream",
    )


@router.get("/supported", summary="Combinaciones de conversión soportadas")
async def supported_conversions():
    """Retorna la matriz de conversiones disponibles."""
    return {
        "conversions": [
            {"from": "pdf",  "to": ["docx", "xlsx", "txt", "html", "png", "jpg"]},
            {"from": "docx", "to": ["pdf"]},
            {"from": "xlsx", "to": ["pdf"]},
            {"from": "pptx", "to": ["pdf"]},
            {"from": "jpg",  "to": ["pdf"]},
            {"from": "png",  "to": ["pdf"]},
            {"from": "webp", "to": ["pdf"]},
        ],
        "max_file_size_mb": settings.MAX_FILE_SIZE_MB,
        "max_batch_files": settings.MAX_BATCH_FILES,
    }