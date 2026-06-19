import type { ActiveTool } from "../../App"

const TITLES: Record<ActiveTool, { label: string; desc: string }> = {
  convert:   { label: "Convertir documento",  desc: "PDF ↔ Word, Excel, PPT, imágenes y más" },
  batch:     { label: "Conversión por lotes", desc: "Hasta 50 archivos en una sola operación" },
  compress:  { label: "Comprimir PDF",        desc: "Reduce el tamaño sin perder calidad visible" },
  merge:     { label: "Fusionar PDFs",        desc: "Une varios PDFs en un solo archivo" },
  split:     { label: "Dividir PDF",          desc: "Separa páginas o rangos en archivos distintos" },
  rotate:    { label: "Rotar páginas",        desc: "Rota una o todas las páginas del PDF" },
  watermark: { label: "Marca de agua",        desc: "Agrega texto de marca de agua al PDF" },
  protect:   { label: "Proteger PDF",         desc: "Encripta el PDF con contraseña AES-256" },
  ocr:       { label: "OCR",                  desc: "Extrae texto de PDFs escaneados o imágenes" },
}

export default function Header({ activeTool }: { activeTool: ActiveTool }) {
  const { label, desc } = TITLES[activeTool]
  return (
    <header className="bg-white border-b border-gray-100 px-6 md:px-8 py-4 flex items-center justify-between">
      <div>
        <h1 className="text-lg font-semibold text-gray-900">{label}</h1>
        <p className="text-sm text-gray-500 mt-0.5">{desc}</p>
      </div>
      <div className="flex items-center gap-3">
        <span className="text-xs bg-indigo-50 text-indigo-600 font-medium px-2.5 py-1 rounded-full">
          Fase 1 · MVP
        </span>
      </div>
    </header>
  )
}