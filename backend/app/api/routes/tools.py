"""
/api/v1/tools — Herramientas avanzadas de PDF
"""
from __future__ import annotations

import uuid
from typing import List

from fastapi import APIRouter, File, Form, HTTPException, UploadFile
from fastapi.responses import FileResponse

from app.core.config import settings
from app.schemas.documents import (
    CompressOptions, MergeOptions, OcrOptions,
    ProtectOptions, RotateOptions, SplitOptions, WatermarkOptions,
)
from app.services.tools.pdf_tools import PdfToolsService

router = APIRouter()
service = PdfToolsService()


def _save_upload(file_content: bytes, filename: str, job_id: str):
    upload_dir = settings.get_upload_dir() / job_id
    upload_dir.mkdir(parents=True, exist_ok=True)
    path = upload_dir / filename
    path.write_bytes(file_content)
    return path


def _output_dir(job_id: str):
    d = settings.get_output_dir() / job_id
    d.mkdir(parents=True, exist_ok=True)
    return d


def _dl_url(job_id: str, filename: str) -> str:
    return f"/api/v1/tools/download/{job_id}/{filename}"


@router.post("/compress", summary="Comprimir PDF")
async def compress_pdf(
    file: UploadFile = File(...),
    quality: str = Form("ebook"),
):
    job_id = str(uuid.uuid4())
    content = await file.read()
    input_path = _save_upload(content, file.filename, job_id)
    output_dir = _output_dir(job_id)

    try:
        result = await service.compress(input_path, output_dir, CompressOptions(quality=quality))
    except Exception as e:
        raise HTTPException(500, detail=str(e))
    finally:
        input_path.unlink(missing_ok=True)

    return {
        "job_id": job_id,
        "filename": result.name,
        "size_bytes": result.stat().st_size,
        "original_size_bytes": len(content),
        "download_url": _dl_url(job_id, result.name),
    }


@router.post("/merge", summary="Fusionar PDFs")
async def merge_pdfs(files: List[UploadFile] = File(...)):
    if len(files) < 2:
        raise HTTPException(422, "Se necesitan al menos 2 archivos para fusionar")
    if len(files) > 30:
        raise HTTPException(422, "Máximo 30 archivos por fusión")

    job_id = str(uuid.uuid4())
    input_paths = []

    for f in files:
        content = await f.read()
        input_paths.append(_save_upload(content, f.filename, job_id))

    output_dir = _output_dir(job_id)
    try:
        result = await service.merge(input_paths, output_dir, MergeOptions())
    except Exception as e:
        raise HTTPException(500, detail=str(e))
    finally:
        for p in input_paths:
            p.unlink(missing_ok=True)

    return {
        "job_id": job_id,
        "filename": result.name,
        "size_bytes": result.stat().st_size,
        "download_url": _dl_url(job_id, result.name),
    }


@router.post("/split", summary="Dividir PDF")
async def split_pdf(
    file: UploadFile = File(...),
    pages: str = Form(None, description="Ej: '1-3,5' o vacío para una pág. por archivo"),
):
    job_id = str(uuid.uuid4())
    content = await file.read()
    input_path = _save_upload(content, file.filename, job_id)
    output_dir = _output_dir(job_id)

    try:
        result = await service.split(input_path, output_dir, SplitOptions(pages=pages))
    except Exception as e:
        raise HTTPException(500, detail=str(e))
    finally:
        input_path.unlink(missing_ok=True)

    return {
        "job_id": job_id,
        "filename": result.name,
        "size_bytes": result.stat().st_size,
        "download_url": _dl_url(job_id, result.name),
    }


@router.post("/rotate", summary="Rotar páginas de un PDF")
async def rotate_pdf(
    file: UploadFile = File(...),
    degrees: int = Form(90),
    pages: str = Form(None),
):
    job_id = str(uuid.uuid4())
    content = await file.read()
    input_path = _save_upload(content, file.filename, job_id)
    output_dir = _output_dir(job_id)

    try:
        result = await service.rotate(input_path, output_dir, RotateOptions(degrees=degrees, pages=pages))
    except Exception as e:
        raise HTTPException(500, detail=str(e))
    finally:
        input_path.unlink(missing_ok=True)

    return {"job_id": job_id, "filename": result.name, "download_url": _dl_url(job_id, result.name)}


@router.post("/watermark", summary="Añadir marca de agua")
async def watermark_pdf(
    file: UploadFile = File(...),
    text: str = Form(...),
    opacity: float = Form(0.3),
    angle: int = Form(45),
    font_size: int = Form(48),
):
    job_id = str(uuid.uuid4())
    content = await file.read()
    input_path = _save_upload(content, file.filename, job_id)
    output_dir = _output_dir(job_id)

    try:
        result = await service.watermark(
            input_path, output_dir,
            WatermarkOptions(text=text, opacity=opacity, angle=angle, font_size=font_size)
        )
    except Exception as e:
        raise HTTPException(500, detail=str(e))
    finally:
        input_path.unlink(missing_ok=True)

    return {"job_id": job_id, "filename": result.name, "download_url": _dl_url(job_id, result.name)}


@router.post("/protect", summary="Proteger PDF con contraseña")
async def protect_pdf(
    file: UploadFile = File(...),
    user_password: str = Form(...),
    owner_password: str = Form(None),
):
    job_id = str(uuid.uuid4())
    content = await file.read()
    input_path = _save_upload(content, file.filename, job_id)
    output_dir = _output_dir(job_id)

    try:
        result = await service.protect(
            input_path, output_dir,
            ProtectOptions(user_password=user_password, owner_password=owner_password)
        )
    except Exception as e:
        raise HTTPException(500, detail=str(e))
    finally:
        input_path.unlink(missing_ok=True)

    return {"job_id": job_id, "filename": result.name, "download_url": _dl_url(job_id, result.name)}


@router.post("/ocr", summary="OCR — extraer texto de PDF escaneado")
async def ocr_pdf(
    file: UploadFile = File(...),
    lang: str = Form("spa+eng"),
    dpi: int = Form(300),
):
    job_id = str(uuid.uuid4())
    content = await file.read()
    input_path = _save_upload(content, file.filename, job_id)
    output_dir = _output_dir(job_id)

    try:
        result = await service.ocr(input_path, output_dir, OcrOptions(lang=lang, dpi=dpi))
    except Exception as e:
        raise HTTPException(500, detail=str(e))
    finally:
        input_path.unlink(missing_ok=True)

    return {
        "job_id": job_id,
        "filename": result.name,
        "size_bytes": result.stat().st_size,
        "download_url": _dl_url(job_id, result.name),
        "lang": lang,
    }


@router.get("/download/{job_id}/{filename}")
async def download_tool_result(job_id: str, filename: str):
    path = settings.get_output_dir() / job_id / filename
    if not path.exists():
        raise HTTPException(404, detail="Archivo no encontrado o expirado")
    return FileResponse(path=str(path), filename=filename, media_type="application/octet-stream")