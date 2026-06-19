"""
Herramientas PDF avanzadas:
compress · merge · split · rotate · watermark · protect · unlock · ocr
"""
from __future__ import annotations

import asyncio
import subprocess
from pathlib import Path
from typing import List, Optional

from pypdf import PdfReader, PdfWriter
from reportlab.lib.colors import Color
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas as rl_canvas

from app.core.config import settings
from app.core.logging import logger
from app.schemas.documents import (
    CompressOptions, MergeOptions, OcrOptions,
    ProtectOptions, RotateOptions, SplitOptions, WatermarkOptions,
)


class PdfToolsService:

    # ── Comprimir ─────────────────────────────────────────────────────────────

    async def compress(self, input_path: Path, output_dir: Path, opts: CompressOptions) -> Path:
        return await asyncio.get_event_loop().run_in_executor(
            None, self._compress_sync, input_path, output_dir, opts
        )

    def _compress_sync(self, input_path: Path, output_dir: Path, opts: CompressOptions) -> Path:
        output_path = output_dir / f"{input_path.stem}_compressed.pdf"

        # Ghostscript ofrece la mejor compresión
        cmd = [
            "gs",
            "-sDEVICE=pdfwrite",
            "-dCompatibilityLevel=1.5",
            f"-dPDFSETTINGS=/{opts.quality}",
            "-dNOPAUSE", "-dBATCH", "-dQUIET",
            f"-sOutputFile={output_path}",
            str(input_path),
        ]

        result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
        if result.returncode != 0:
            # Fallback a pypdf si Ghostscript no está disponible
            logger.warning("Ghostscript no disponible, usando pypdf", error=result.stderr[:200])
            output_path = self._compress_pypdf(input_path, output_path)

        original_size = input_path.stat().st_size
        compressed_size = output_path.stat().st_size
        ratio = (1 - compressed_size / original_size) * 100
        logger.info("PDF comprimido", ratio_pct=f"{ratio:.1f}%", quality=opts.quality)
        return output_path

    def _compress_pypdf(self, input_path: Path, output_path: Path) -> Path:
        reader = PdfReader(str(input_path))
        writer = PdfWriter()
        for page in reader.pages:
            page.compress_content_streams()
            writer.add_page(page)
        with open(output_path, "wb") as f:
            writer.write(f)
        return output_path

    # ── Fusionar ─────────────────────────────────────────────────────────────

    async def merge(
        self,
        input_paths: List[Path],
        output_dir: Path,
        opts: MergeOptions,
    ) -> Path:
        return await asyncio.get_event_loop().run_in_executor(
            None, self._merge_sync, input_paths, output_dir, opts
        )

    def _merge_sync(self, input_paths: List[Path], output_dir: Path, opts: MergeOptions) -> Path:
        output_path = output_dir / "merged.pdf"
        ordered = (
            [input_paths[i] for i in opts.order]
            if opts.order
            else input_paths
        )

        writer = PdfWriter()
        for path in ordered:
            reader = PdfReader(str(path))
            for page in reader.pages:
                writer.add_page(page)

        with open(output_path, "wb") as f:
            writer.write(f)

        logger.info("PDFs fusionados", total=len(ordered), output=output_path.name)
        return output_path

    # ── Dividir ───────────────────────────────────────────────────────────────

    async def split(self, input_path: Path, output_dir: Path, opts: SplitOptions) -> Path:
        return await asyncio.get_event_loop().run_in_executor(
            None, self._split_sync, input_path, output_dir, opts
        )

    def _split_sync(self, input_path: Path, output_dir: Path, opts: SplitOptions) -> Path:
        import zipfile

        reader = PdfReader(str(input_path))
        total = len(reader.pages)
        pages_to_extract = self._parse_page_range(opts.pages, total) if opts.pages else None

        output_files = []

        if pages_to_extract:
            # Extraer páginas específicas como un solo PDF
            writer = PdfWriter()
            for p in pages_to_extract:
                writer.add_page(reader.pages[p - 1])
            out = output_dir / f"{input_path.stem}_pages_{opts.pages.replace(',','_')}.pdf"
            with open(out, "wb") as f:
                writer.write(f)
            output_files.append(out)
        else:
            # Una página por archivo
            for i, page in enumerate(reader.pages, start=1):
                writer = PdfWriter()
                writer.add_page(page)
                out = output_dir / f"{input_path.stem}_page{i:03d}.pdf"
                with open(out, "wb") as f:
                    writer.write(f)
                output_files.append(out)

        if len(output_files) == 1:
            return output_files[0]

        zip_path = output_dir / f"{input_path.stem}_split.zip"
        with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
            for p in output_files:
                zf.write(p, p.name)
                p.unlink(missing_ok=True)

        logger.info("PDF dividido", pages=len(output_files))
        return zip_path

    # ── Rotar ─────────────────────────────────────────────────────────────────

    async def rotate(self, input_path: Path, output_dir: Path, opts: RotateOptions) -> Path:
        return await asyncio.get_event_loop().run_in_executor(
            None, self._rotate_sync, input_path, output_dir, opts
        )

    def _rotate_sync(self, input_path: Path, output_dir: Path, opts: RotateOptions) -> Path:
        output_path = output_dir / f"{input_path.stem}_rotated.pdf"
        reader = PdfReader(str(input_path))
        writer = PdfWriter()
        total = len(reader.pages)

        target_pages = (
            {p for p in self._parse_page_range(opts.pages, total)}
            if opts.pages else None
        )

        for i, page in enumerate(reader.pages, start=1):
            if target_pages is None or i in target_pages:
                page.rotate(opts.degrees)
            writer.add_page(page)

        with open(output_path, "wb") as f:
            writer.write(f)

        logger.info("PDF rotado", degrees=opts.degrees)
        return output_path

    # ── Marca de agua ─────────────────────────────────────────────────────────

    async def watermark(self, input_path: Path, output_dir: Path, opts: WatermarkOptions) -> Path:
        return await asyncio.get_event_loop().run_in_executor(
            None, self._watermark_sync, input_path, output_dir, opts
        )

    def _watermark_sync(self, input_path: Path, output_dir: Path, opts: WatermarkOptions) -> Path:
        import tempfile, os

        output_path = output_dir / f"{input_path.stem}_watermarked.pdf"

        # Crear PDF de marca de agua con reportlab
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
            tmp_path = tmp.name

        reader_orig = PdfReader(str(input_path))
        first_page = reader_orig.pages[0]
        w = float(first_page.mediabox.width)
        h = float(first_page.mediabox.height)

        c = rl_canvas.Canvas(tmp_path, pagesize=(w, h))
        c.saveState()
        c.setFillColor(Color(0, 0, 0, alpha=opts.opacity))
        c.setFont("Helvetica-Bold", opts.font_size)
        c.translate(w / 2, h / 2)
        c.rotate(opts.angle)
        c.drawCentredString(0, 0, opts.text)
        c.restoreState()
        c.save()

        watermark_page = PdfReader(tmp_path).pages[0]
        writer = PdfWriter()

        for page in reader_orig.pages:
            page.merge_page(watermark_page)
            writer.add_page(page)

        with open(output_path, "wb") as f:
            writer.write(f)

        os.unlink(tmp_path)
        logger.info("Marca de agua aplicada", text=opts.text)
        return output_path

    # ── Proteger ──────────────────────────────────────────────────────────────

    async def protect(self, input_path: Path, output_dir: Path, opts: ProtectOptions) -> Path:
        return await asyncio.get_event_loop().run_in_executor(
            None, self._protect_sync, input_path, output_dir, opts
        )

    def _protect_sync(self, input_path: Path, output_dir: Path, opts: ProtectOptions) -> Path:
        output_path = output_dir / f"{input_path.stem}_protected.pdf"
        reader = PdfReader(str(input_path))
        writer = PdfWriter()

        for page in reader.pages:
            writer.add_page(page)

        permissions = PdfWriter.generate_file_encryption_key(
            user_password=opts.user_password,
            owner_password=opts.owner_password or opts.user_password,
        )
        writer.encrypt(
            user_password=opts.user_password,
            owner_password=opts.owner_password,
            use_128bit=True,
        )

        with open(output_path, "wb") as f:
            writer.write(f)

        logger.info("PDF protegido con contraseña")
        return output_path

    # ── Desbloquear ───────────────────────────────────────────────────────────

    async def unlock(
        self,
        input_path: Path,
        output_dir: Path,
        password: str,
    ) -> Path:
        return await asyncio.get_event_loop().run_in_executor(
            None, self._unlock_sync, input_path, output_dir, password
        )

    def _unlock_sync(self, input_path: Path, output_dir: Path, password: str) -> Path:
        output_path = output_dir / f"{input_path.stem}_unlocked.pdf"
        reader = PdfReader(str(input_path))

        if reader.is_encrypted:
            if not reader.decrypt(password):
                raise ValueError("Contraseña incorrecta")

        writer = PdfWriter()
        for page in reader.pages:
            writer.add_page(page)

        with open(output_path, "wb") as f:
            writer.write(f)

        logger.info("PDF desbloqueado")
        return output_path

    # ── OCR ───────────────────────────────────────────────────────────────────

    async def ocr(self, input_path: Path, output_dir: Path, opts: OcrOptions) -> Path:
        return await asyncio.get_event_loop().run_in_executor(
            None, self._ocr_sync, input_path, output_dir, opts
        )

    def _ocr_sync(self, input_path: Path, output_dir: Path, opts: OcrOptions) -> Path:
        import pytesseract
        from pdf2image import convert_from_path
        from reportlab.pdfgen import canvas as rl_canvas
        from reportlab.lib.pagesizes import letter
        import io
        from PIL import Image

        output_path = output_dir / f"{input_path.stem}_ocr.pdf"
        pytesseract.pytesseract.tesseract_cmd = settings.TESSERACT_CMD

        images = convert_from_path(str(input_path), dpi=opts.dpi)
        logger.info("OCR iniciado", pages=len(images), lang=opts.lang)

        # Generar PDF con texto invisible superpuesto (searchable PDF)
        pdf_pages = []
        for i, img in enumerate(images, start=1):
            data = pytesseract.image_to_pdf_or_hocr(
                img, extension="pdf", lang=opts.lang, config="--psm 3"
            )
            pdf_pages.append(data)

        if len(pdf_pages) == 1:
            output_path.write_bytes(pdf_pages[0])
        else:
            writer = PdfWriter()
            for page_data in pdf_pages:
                reader = PdfReader(io.BytesIO(page_data))
                writer.add_page(reader.pages[0])
            with open(output_path, "wb") as f:
                writer.write(f)

        logger.info("OCR completado", output=output_path.name)
        return output_path

    # ── Utils ─────────────────────────────────────────────────────────────────

    @staticmethod
    def _parse_page_range(pages_str: str, total: int) -> List[int]:
        """
        Parsea '1-3,5,7-9' → [1, 2, 3, 5, 7, 8, 9]
        Valida que estén dentro del rango del documento.
        """
        result = []
        for part in pages_str.split(","):
            part = part.strip()
            if "-" in part:
                start, end = part.split("-", 1)
                result.extend(range(int(start), int(end) + 1))
            else:
                result.append(int(part))
        valid = [p for p in result if 1 <= p <= total]
        if not valid:
            raise ValueError(f"Rango de páginas '{pages_str}' no válido para un PDF de {total} páginas")
        return valid