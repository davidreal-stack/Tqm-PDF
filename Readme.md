# DocuForge

Plataforma de conversión de documentos — PDF, Office, OCR.
Convierte, comprime, fusiona y edita documentos desde el navegador.

---

## Requisitos (Windows)

Instala estas herramientas antes de continuar:

| Herramienta | Versión | Enlace |
|---|---|---|
| Python | 3.12+ | https://www.python.org/downloads/ |
| Node.js | 20+ | https://nodejs.org/ |
| LibreOffice | 24+ | https://www.libreoffice.org/download/ |
| Tesseract OCR | 5+ | https://github.com/UB-Mannheim/tesseract/wiki |
| Git | cualquiera | https://git-scm.com/ |

> Para PostgreSQL y Redis en desarrollo puedes usar Docker Desktop o WSL2.

---

## Instalación — Backend

```bash
# 1. Entra a la carpeta del backend
cd docuforge\backend

# 2. Crea y activa el entorno virtual
python -m venv .venv
.venv\Scripts\activate

# 3. Instala dependencias
pip install -r requirements.txt

# 4. Configura variables de entorno
copy .env.example .env
# Edita .env con tu editor y ajusta las rutas de LibreOffice y Tesseract

# 5. Levanta el servidor
uvicorn app.main:app --reload --port 8000
```

La API estará disponible en:
- http://localhost:8000/docs → Swagger UI interactivo
- http://localhost:8000/redoc → ReDoc

---

## Instalación — Frontend

```bash
# En otra terminal, entra a la carpeta del frontend
cd docuforge\frontend

# Instala dependencias
npm install

# Inicia el servidor de desarrollo
npm run dev
```

El frontend estará en http://localhost:5173

---

## Levantar todo con Docker

```bash
# Desde la raíz del proyecto
docker compose up --build
```

Esto levanta: API (8000) + PostgreSQL (5432) + Redis (6379)

Para incluir el worker de Celery:
```bash
docker compose --profile celery up --build
```

---

## Estructura del proyecto

```
docuforge/
├── backend/
│   ├── app/
│   │   ├── main.py                  # Entrypoint FastAPI
│   │   ├── core/
│   │   │   ├── config.py            # Settings · rutas Windows/Linux
│   │   │   └── logging.py           # Logging estructurado
│   │   ├── schemas/
│   │   │   └── documents.py         # Tipos Pydantic
│   │   ├── services/
│   │   │   ├── conversion_service.py  # Orquestador principal
│   │   │   ├── converters/
│   │   │   │   ├── image_to_pdf.py
│   │   │   │   ├── office_to_pdf.py   # LibreOffice headless
│   │   │   │   ├── pdf_to_office.py   # pdf2docx + pdfplumber
│   │   │   │   └── pdf_to_image.py    # pdf2image
│   │   │   └── tools/
│   │   │       └── pdf_tools.py       # compress·merge·split·OCR…
│   │   └── api/routes/
│   │       ├── convert.py
│   │       ├── tools.py
│   │       ├── health.py
│   │       └── jobs.py
│   ├── requirements.txt
│   ├── Dockerfile
│   └── .env.example
│
├── frontend/
│   ├── src/
│   │   ├── main.tsx
│   │   ├── App.tsx
│   │   ├── index.css
│   │   ├── components/
│   │   │   ├── layout/   Sidebar · Header
│   │   │   └── ui/       DropZone · ResultCard
│   │   ├── pages/
│   │   │   ├── ConvertPage.tsx
│   │   │   ├── ToolsPage.tsx
│   │   │   └── BatchPage.tsx
│   │   └── hooks/
│   │       └── useConvert.ts
│   ├── index.html
│   ├── package.json
│   ├── vite.config.ts
│   └── Dockerfile
│
├── docker-compose.yml
└── .gitignore
```

---

## Conversiones soportadas (Fase 1)

| Origen | Destino |
|---|---|
| PDF | Word · Excel · TXT · HTML · PNG · JPG |
| Word / Excel / PPT | PDF |
| Imagen (JPG, PNG, WEBP…) | PDF |

### Herramientas PDF

- Comprimir · Fusionar · Dividir · Rotar
- Marca de agua · Proteger con contraseña
- OCR (español + inglés)

---

## Roadmap

- **Fase 2** — Celery + Redis para conversiones async, sistema de usuarios, descarga ZIP de lotes
- **Fase 3** — OCR mejorado para español, procesamiento por lotes masivo, API pública con tokens
- **Fase 4** — App de escritorio (Tauri), modelo freemium, deploy en VPS propio