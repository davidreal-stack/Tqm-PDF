"""
/api/v1/health — Health check
"""
from fastapi import APIRouter
from app.core.config import settings
from app.services.converters.office_to_pdf import OfficeToPdfConverter

router = APIRouter()


@router.get("/health", summary="Estado del servicio")
async def health_check():
    return {
        "status": "ok",
        "version": settings.APP_VERSION,
        "libreoffice_available": OfficeToPdfConverter.is_available(),
    }