"""
Configuración centralizada — usa variables de entorno o archivo .env
Compatible con Windows, macOS y Linux.
"""
import os
import sys
from functools import lru_cache
from pathlib import Path
from typing import List

from pydantic_settings import BaseSettings, SettingsConfigDict


def _default_data_dir() -> Path:
    """
    Devuelve un directorio de datos portable:
      Windows → %LOCALAPPDATA%\\DocuForge   (ej. C:\\Users\\TU_USER\\AppData\\Local\\DocuForge)
      macOS   → ~/Library/Application Support/DocuForge
      Linux   → ~/.local/share/DocuForge
    """
    if sys.platform == "win32":
        base = Path(os.environ.get("LOCALAPPDATA", Path.home() / "AppData" / "Local"))
    elif sys.platform == "darwin":
        base = Path.home() / "Library" / "Application Support"
    else:
        base = Path(os.environ.get("XDG_DATA_HOME", Path.home() / ".local" / "share"))
    return base / "DocuForge"


_DATA_DIR = _default_data_dir()


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # ── App ───────────────────────────────────────────────────────────────────
    APP_NAME: str = "DocuForge"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    SECRET_KEY: str = "CHANGE_ME_IN_PRODUCTION"

    # ── Servidor ──────────────────────────────────────────────────────────────
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    CORS_ORIGINS: List[str] = ["http://localhost:5173", "http://localhost:3000"]

    # ── Base de datos ─────────────────────────────────────────────────────────
    DATABASE_URL: str = "postgresql+asyncpg://docuforge:secret@localhost:5432/docuforge"

    # ── Redis / Celery ────────────────────────────────────────────────────────
    REDIS_URL: str = "redis://localhost:6379/0"
    CELERY_BROKER_URL: str = "redis://localhost:6379/0"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/1"

    # ── Storage ───────────────────────────────────────────────────────────────
    STORAGE_BACKEND: str = "local"          # "local" | "s3" | "minio"
    # Usa rutas relativas al directorio de datos del SO — sobrescribible en .env
    LOCAL_UPLOAD_DIR: Path = _DATA_DIR / "uploads"
    LOCAL_OUTPUT_DIR: Path = _DATA_DIR / "outputs"
    FILE_TTL_SECONDS: int = 3600            # 1 hora — se borra automáticamente

    # ── S3 / MinIO (opcional) ─────────────────────────────────────────────────
    S3_ENDPOINT_URL: str = ""
    S3_ACCESS_KEY: str = ""
    S3_SECRET_KEY: str = ""
    S3_BUCKET: str = "docuforge"

    # ── Auth / JWT ────────────────────────────────────────────────────────────
    JWT_SECRET: str = "CHANGE_ME_IN_PRODUCTION"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRE_MINUTES: int = 60 * 24

    # ── Límites de subida ─────────────────────────────────────────────────────
    MAX_FILE_SIZE_MB: int = 100
    MAX_BATCH_FILES: int = 50

    # ── LibreOffice ───────────────────────────────────────────────────────────
    # Windows: instalar desde https://www.libreoffice.org y ajustar esta ruta
    LIBREOFFICE_PATH: str = (
        r"C:\Program Files\LibreOffice\program\soffice.exe"
        if sys.platform == "win32"
        else "libreoffice"
    )

    # ── Tesseract ─────────────────────────────────────────────────────────────
    # Windows: instalar desde https://github.com/UB-Mannheim/tesseract/wiki
    TESSERACT_CMD: str = (
        r"C:\Program Files\Tesseract-OCR\tesseract.exe"
        if sys.platform == "win32"
        else "tesseract"
    )
    OCR_DEFAULT_LANG: str = "spa+eng"

    def get_upload_dir(self) -> Path:
        self.LOCAL_UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
        return self.LOCAL_UPLOAD_DIR

    def get_output_dir(self) -> Path:
        self.LOCAL_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        return self.LOCAL_OUTPUT_DIR


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()