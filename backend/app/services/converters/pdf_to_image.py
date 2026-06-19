"""
PDF → Imágenes (PNG / JPG) — una imagen por página
"""
from __future__ import annotations

import asyncio
import zipfile
from pathlib import Path

from pdf2image import convert_from_path

from app.core.config import settings
from app.core.logging import logger


class PdfToImageConverter:

    async def convert(
        self,
        input_path: Path,
        output_dir: Path,
        fmt: str = "png",
        dpi: int = 150,
    ) -> Path:
        """
        Convierte cada página del PDF en una imagen.
        Si el PDF tiene >1 página devuelve un ZIP con todas las imágenes.
        """
        return await asyncio.get_event_loop().run_in_executor(
            None, self._convert_sync, input_path, output_dir, fmt, dpi
        )

    def _convert_sync(
        self,
        input_path: Path,
        output_dir: Path,
        fmt: str,
        dpi: int,
    ) -> Path:
        log = logger.bind(input=input_path.name, fmt=fmt, dpi=dpi)
        log.info("Convirtiendo PDF a imágenes")

        images = convert_from_path(
            str(input_path),
            dpi=dpi,
            fmt=fmt,
            output_folder=str(output_dir),
            output_file=input_path.stem,
            paths_only=False,
        )

        if len(images) == 1:
            # Una sola imagen — devolver directamente
            out_path = output_dir / f"{input_path.stem}.{fmt}"
            images[0].save(str(out_path), fmt.upper())
            log.info("PDF → imagen única", output=out_path.name)
            return out_path

        # Múltiples páginas → ZIP
        image_paths = []
        for i, img in enumerate(images, start=1):
            img_path = output_dir / f"{input_path.stem}_page{i:03d}.{fmt}"
            img.save(str(img_path), fmt.upper())
            image_paths.append(img_path)

        zip_path = output_dir / f"{input_path.stem}_pages.zip"
        with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
            for p in image_paths:
                zf.write(p, p.name)

        # Limpiar imágenes sueltas
        for p in image_paths:
            p.unlink(missing_ok=True)

        log.info("PDF → imágenes ZIP", pages=len(images), output=zip_path.name)
        return zip_path