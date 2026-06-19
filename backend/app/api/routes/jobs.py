"""
/api/v1/jobs — Estado de trabajos async (Fase 2: Celery)
Por ahora stub para conversiones síncronas.
"""
from fastapi import APIRouter, HTTPException
from app.schemas.documents import JobResponse, JobStatus
import uuid

router = APIRouter()


@router.get("/{job_id}", response_model=JobResponse, summary="Estado de un trabajo")
async def get_job_status(job_id: str):
    """
    En Fase 1 las conversiones son síncronas — el job siempre retorna DONE
    inmediatamente desde /convert. Este endpoint se expande en Fase 2 con Celery.
    """
    try:
        uid = uuid.UUID(job_id)
    except ValueError:
        raise HTTPException(400, "job_id inválido")

    return JobResponse(
        job_id=uid,
        status=JobStatus.DONE,
        progress=100,
    )