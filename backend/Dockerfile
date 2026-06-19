FROM python:3.12-slim

# ── Sistema ────────────────────────────────────────────────────────────────────
RUN apt-get update && apt-get install -y --no-install-recommends \
    # LibreOffice headless (conversiones Office)
    libreoffice \
    # Poppler (PDF → imágenes)
    poppler-utils \
    # Tesseract OCR + paquete de idiomas español
    tesseract-ocr \
    tesseract-ocr-spa \
    tesseract-ocr-eng \
    # Ghostscript (compresión PDF)
    ghostscript \
    # Fonts
    fonts-liberation \
    fonts-dejavu-core \
    # Build tools para algunas libs Python
    gcc \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# ── Python ────────────────────────────────────────────────────────────────────
WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# ── App ───────────────────────────────────────────────────────────────────────
COPY . .

# ── Directorios de trabajo ────────────────────────────────────────────────────
RUN mkdir -p /tmp/docuforge/uploads /tmp/docuforge/outputs

# ── Usuario sin privilegios ───────────────────────────────────────────────────
RUN useradd -m -r docuforge \
    && chown -R docuforge:docuforge /app /tmp/docuforge
USER docuforge

# ── Entrypoint ────────────────────────────────────────────────────────────────
EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]