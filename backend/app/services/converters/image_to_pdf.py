"""
Imagen → PDF
Soporta: JPG, PNG, BMP, WEBP, TIFF, GIF
"""
from __future__ import annotations

import asyncio
from pathlib import Path

import img2pdf
from PIL import Image

from app.core.logging import logger


class ImageToPdfConverter:
    """
    Convierte una imagen (o lista de imágenes) a PDF preservando
    las dimensiones originales y la calidad.
    """

    SUPPORTED = {".jpg", ".jpeg", ".png", ".bmp", ".webp", ".tiff", ".tif", ".gif"}

    async def convert(self, input_path: Path, output_dir: Path) -> Path:
        """Convierte una sola imagen a PDF."""
        return await asyncio.get_event_loop().run_in_executor(
            None, self._convert_sync, input_path, output_dir
        )

    async def convert_batch(self, input_paths: list[Path], output_dir: Path) -> Path:
        """Combina múltiples imágenes en un solo PDF (una página por imagen)."""
        return await asyncio.get_event_loop().run_in_executor(
            None, self._convert_batch_sync, input_paths, output_dir
        )

    # ── Sync internals ────────────────────────────────────────────────────────

    def _convert_sync(self, input_path: Path, output_dir: Path) -> Path:
        output_path = output_dir / f"{input_path.stem}.pdf"
        log = logger.bind(input=input_path.name, output=output_path.name)

        # Normalizar imagen (WEBP y otros formatos se convierten a RGB/RGBA primero)
        normalized = self._normalize_image(input_path)

        try:
            with open(output_path, "wb") as f:
                f.write(img2pdf.convert(str(normalized)))
            log.info("Imagen convertida a PDF")
        finally:
            if normalized != input_path:
                normalized.unlink(missing_ok=True)

        return output_path

    def _convert_batch_sync(self, input_paths: list[Path], output_dir: Path) -> Path:
        output_path = output_dir / "combined.pdf"
        normalized_paths = []

        try:
            for p in input_paths:
                normalized_paths.append(self._normalize_image(p))

            with open(output_path, "wb") as f:
                f.write(img2pdf.convert([str(p) for p in normalized_paths]))

            logger.info("Imágenes combinadas en PDF", total=len(input_paths))
        finally:
            for p in normalized_paths:
                if p not in input_paths:
                    p.unlink(missing_ok=True)

        return output_path

    def _normalize_image(self, path: Path) -> Path:
        """
        img2pdf no acepta directamente WEBP/TIFF multi-frame/GIF.
        Convierte a PNG temporal si es necesario.
        """
        ext = path.suffix.lower()
        if ext in (".webp", ".tiff", ".tif", ".gif", ".bmp"):
            tmp_path = path.with_suffix(".tmp.png")
            img = Image.open(path)
            if img.mode in ("RGBA", "LA", "P"):
                img = img.convert("RGBA")
            else:
                img = img.convert("RGB")
            img.save(tmp_path, "PNG")
            return tmp_path
        return path