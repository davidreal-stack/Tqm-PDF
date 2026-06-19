import { useState } from "react"
import DropZone from "../components/ui/DropZone"
import ResultCard from "../components/ui/ResultCard"
import { useConvert } from "../hooks/useConvert"

const FORMATS = [
  { value: "pdf",  label: "PDF",        icon: "📄", group: "Documentos" },
  { value: "docx", label: "Word",       icon: "📝", group: "Documentos" },
  { value: "xlsx", label: "Excel",      icon: "📊", group: "Documentos" },
  { value: "pptx", label: "PowerPoint", icon: "📽",  group: "Documentos" },
  { value: "txt",  label: "Texto",      icon: "🔤", group: "Texto / Web" },
  { value: "html", label: "HTML",       icon: "🌐", group: "Texto / Web" },
  { value: "png",  label: "PNG",        icon: "🖼",  group: "Imágenes" },
  { value: "jpg",  label: "JPG",        icon: "📷", group: "Imágenes" },
]

export default function ConvertPage() {
  const [file, setFile] = useState<File | null>(null)
  const [outputFormat, setOutputFormat] = useState("pdf")
  const { status, result, convert, reset } = useConvert()

  const handleFile = (files: File[]) => {
    setFile(files[0])
    reset()
  }

  const handleConvert = () => {
    if (!file) return
    convert(file, outputFormat)
  }

  return (
    <div className="max-w-2xl mx-auto">

      {/* Step 1 — Archivo */}
      <div className="bg-white rounded-2xl border border-gray-100 shadow-sm p-6 mb-4">
        <h2 className="text-sm font-semibold text-gray-700 mb-3">1 · Selecciona el archivo</h2>
        <DropZone
          onFiles={handleFile}
          accept=".pdf,.doc,.docx,.xls,.xlsx,.ppt,.pptx,.jpg,.jpeg,.png,.webp,.tiff,.gif,.bmp,.html,.txt"
          label="Arrastra cualquier documento Office, PDF o imagen"
        />
        {file && (
          <div className="mt-3 flex items-center gap-2 text-sm text-gray-600 bg-gray-50 px-3 py-2 rounded-lg">
            <span>📎</span>
            <span className="font-medium truncate">{file.name}</span>
            <span className="text-gray-400 ml-auto flex-shrink-0">
              {(file.size / 1024).toFixed(0)} KB
            </span>
            <button onClick={() => { setFile(null); reset() }} className="text-gray-400 hover:text-red-500 transition-colors ml-1">✕</button>
          </div>
        )}
      </div>

      {/* Step 2 — Formato */}
      <div className="bg-white rounded-2xl border border-gray-100 shadow-sm p-6 mb-4">
        <h2 className="text-sm font-semibold text-gray-700 mb-3">2 · Formato de salida</h2>
        <div className="grid grid-cols-4 gap-2">
          {FORMATS.map((f) => (
            <button
              key={f.value}
              onClick={() => setOutputFormat(f.value)}
              className={`flex flex-col items-center gap-1.5 py-3 px-2 rounded-xl border text-xs font-medium transition-all
                ${outputFormat === f.value
                  ? "border-indigo-500 bg-indigo-50 text-indigo-700"
                  : "border-gray-100 hover:border-gray-200 hover:bg-gray-50 text-gray-600"
                }`}
            >
              <span className="text-2xl">{f.icon}</span>
              {f.label}
            </button>
          ))}
        </div>
      </div>

      {/* Step 3 — Convertir */}
      <button
        onClick={handleConvert}
        disabled={!file || status === "processing" || status === "uploading"}
        className="w-full py-3.5 rounded-xl bg-indigo-600 hover:bg-indigo-700 disabled:opacity-40 disabled:cursor-not-allowed
          text-white font-semibold text-sm transition-colors shadow-sm"
      >
        {status === "processing" || status === "uploading" ? "Procesando…" : "Convertir →"}
      </button>

      <ResultCard
        status={status}
        filename={result.filename}
        downloadUrl={result.downloadUrl}
        errorMsg={result.error}
        processingTimeMs={result.processingTimeMs}
        sizeBytes={result.sizeBytes}
      />
    </div>
  )
}