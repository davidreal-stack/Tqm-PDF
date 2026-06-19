"""
Servicio de conversión principal — orquesta todos los motores
"""
from __future__ import annotations

import time
import uuid
from pathlib import Path
from typing import Optional

from app.core.config import settings
from app.core.logging import logger
from app.schemas.documents import OutputFormat
from app.services.converters.image_to_pdf import ImageToPdfConverter
from app.services.converters.office_to_pdf import OfficeToPdfConverter
from app.services.converters.pdf_to_office import PdfToOfficeConverter
from app.services.converters.pdf_to_image import PdfToImageConverter


class ConversionResult:
    def __init__(
        self,
        output_path: Path,
        filename: str,
        pages: Optional[int] = None,
        processing_time_ms: int = 0,
    ):
        self.output_path = output_path
        self.filename = filename
        self.pages = pages
        self.processing_time_ms = processing_time_ms
        self.size_bytes = output_path.stat().st_size if output_path.exists() else 0


class ConversionService:
    """
    Detecta el tipo de archivo de entrada y el formato de salida deseado,
    y delega al converter correcto.
    """

    OFFICE_EXTENSIONS = {".docx", ".doc", ".xlsx", ".xls", ".pptx", ".ppt", ".odt", ".ods", ".odp"}
    IMAGE_EXTENSIONS  = {".jpg", ".jpeg", ".png", ".bmp", ".webp", ".tiff", ".tif", ".gif"}
    PDF_EXTENSION     = ".pdf"

    def __init__(self):
        self.office_to_pdf = OfficeToPdfConverter()
        self.pdf_to_office = PdfToOfficeConverter()
        self.image_to_pdf  = ImageToPdfConverter()
        self.pdf_to_image  = PdfToImageConverter()

    async def convert(
        self,
        input_path: Path,
        output_format: OutputFormat,
        job_id: Optional[str] = None,
        **kwargs,
    ) -> ConversionResult:
        job_id = job_id or str(uuid.uuid4())
        ext = input_path.suffix.lower()
        start = time.monotonic()

        log = logger.bind(job_id=job_id, input=input_path.name, output_format=output_format)
        log.info("Iniciando conversión")

        output_dir = settings.get_output_dir() / job_id
        output_dir.mkdir(parents=True, exist_ok=True)

        # ── Imagen → PDF ──────────────────────────────────────────────────────
        if ext in self.IMAGE_EXTENSIONS and output_format == OutputFormat.PDF:
            result_path = await self.image_to_pdf.convert(input_path, output_dir)

        # ── Office → PDF ──────────────────────────────────────────────────────
        elif ext in self.OFFICE_EXTENSIONS and output_format == OutputFormat.PDF:
            result_path = await self.office_to_pdf.convert(input_path, output_dir)

        # ── PDF → Word ────────────────────────────────────────────────────────
        elif ext == self.PDF_EXTENSION and output_format == OutputFormat.DOCX:
            result_path = await self.pdf_to_office.to_docx(input_path, output_dir, **kwargs)

        # ── PDF → Excel ───────────────────────────────────────────────────────
        elif ext == self.PDF_EXTENSION and output_format == OutputFormat.XLSX:
            result_path = await self.pdf_to_office.to_xlsx(input_path, output_dir)

        # ── PDF → Imágenes ────────────────────────────────────────────────────
        elif ext == self.PDF_EXTENSION and output_format in (OutputFormat.PNG, OutputFormat.JPG):
            result_path = await self.pdf_to_image.convert(
                input_path, output_dir, fmt=output_format.value, **kwargs
            )

        # ── PDF → TXT ─────────────────────────────────────────────────────────
        elif ext == self.PDF_EXTENSION and output_format == OutputFormat.TXT:
            result_path = await self.pdf_to_office.to_txt(input_path, output_dir)

        # ── PDF → HTML ────────────────────────────────────────────────────────
        elif ext == self.PDF_EXTENSION and output_format == OutputFormat.HTML:
            result_path = await self.pdf_to_office.to_html(input_path, output_dir)

        # ── Office → Office (vía LibreOffice) ─────────────────────────────────
        elif ext in self.OFFICE_EXTENSIONS:
            result_path = await self.office_to_pdf.convert_to_format(
                input_path, output_dir, output_format
            )

        else:
            raise ValueError(
                f"Conversión no soportada: {ext} → {output_format}. "
                "Consulta /api/v1/convert/supported para ver combinaciones válidas."
            )

        elapsed_ms = int((time.monotonic() - start) * 1000)
        log.info("Conversión completada", elapsed_ms=elapsed_ms, output=result_path.name)

        return ConversionResult(
            output_path=result_path,
            filename=result_path.name,
            processing_time_ms=elapsed_ms,
        )