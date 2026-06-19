"""
Office → PDF usando LibreOffice headless
Soporta: DOCX, XLSX, PPTX, ODT, ODS, ODP y más
"""
from __future__ import annotations

import asyncio
import shutil
import subprocess
import tempfile
from pathlib import Path

from app.core.config import settings
from app.core.logging import logger
from app.schemas.documents import OutputFormat


class OfficeToPdfConverter:
    """
    Usa LibreOffice headless para conversiones de Office.
    Es el método más robusto para preservar el formato.
    """

    # Extensiones que soporta LibreOffice
    SUPPORTED_INPUT = {
        ".docx", ".doc", ".odt", ".rtf",
        ".xlsx", ".xls", ".ods", ".csv",
        ".pptx", ".ppt", ".odp",
        ".html", ".htm",
    }

    # Mapeo de OutputFormat → filtro LibreOffice
    FORMAT_FILTERS = {
        OutputFormat.PDF:  "writer_pdf_Export",
        OutputFormat.DOCX: "MS Word 2007 XML",
        OutputFormat.XLSX: "Calc MS Excel 2007 XML",
        OutputFormat.PPTX: "Impress MS PowerPoint 2007 XML",
        OutputFormat.TXT:  "Text",
        OutputFormat.HTML: "HTML",
    }

    async def convert(self, input_path: Path, output_dir: Path) -> Path:
        """Convierte Office → PDF."""
        return await asyncio.get_event_loop().run_in_executor(
            None, self._run_libreoffice, input_path, output_dir, "pdf"
        )

    async def convert_to_format(
        self,
        input_path: Path,
        output_dir: Path,
        output_format: OutputFormat,
    ) -> Path:
        """Convierte Office → Office (DOCX→XLSX, etc.)."""
        fmt = output_format.value
        return await asyncio.get_event_loop().run_in_executor(
            None, self._run_libreoffice, input_path, output_dir, fmt
        )

    # ── Sync internals ────────────────────────────────────────────────────────

    def _run_libreoffice(
        self,
        input_path: Path,
        output_dir: Path,
        output_format: str,
    ) -> Path:
        """
        Ejecuta LibreOffice headless en un directorio temporal aislado
        para evitar conflictos con el perfil de usuario cuando hay
        múltiples conversiones en paralelo.
        """
        log = logger.bind(input=input_path.name, fmt=output_format)

        # LibreOffice necesita un directorio de perfil único por proceso
        with tempfile.TemporaryDirectory(prefix="lo_profile_") as profile_dir:
            cmd = [
                settings.LIBREOFFICE_PATH,
                "--headless",
                "--norestore",
                f"-env:UserInstallation=file://{profile_dir}",
                "--convert-to", output_format,
                "--outdir", str(output_dir),
                str(input_path),
            ]

            log.info("Ejecutando LibreOffice", cmd=" ".join(cmd))

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=120,   # 2 minutos máximo
            )

        if result.returncode != 0:
            log.error("LibreOffice falló", stderr=result.stderr)
            raise RuntimeError(
                f"LibreOffice falló al convertir {input_path.name}: {result.stderr}"
            )

        # LibreOffice nombra el archivo igual que el input pero con nueva extensión
        output_path = output_dir / f"{input_path.stem}.{output_format}"
        if not output_path.exists():
            # Buscar si lo nombró diferente
            candidates = list(output_dir.glob(f"{input_path.stem}.*"))
            if candidates:
                output_path = candidates[0]
            else:
                raise FileNotFoundError(
                    f"LibreOffice no generó el archivo de salida en {output_dir}"
                )

        log.info("Conversión exitosa", output=output_path.name, size_kb=output_path.stat().st_size // 1024)
        return output_path

    @staticmethod
    def is_available() -> bool:
        """Verifica si LibreOffice está instalado."""
        return shutil.which(settings.LIBREOFFICE_PATH) is not None