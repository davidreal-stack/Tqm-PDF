import { useState } from "react"
import DropZone from "../components/ui/DropZone"

const API = "http://localhost:8000/api/v1"

type FileStatus = "pending" | "processing" | "done" | "error"

interface FileItem {
  id: string
  file: File
  status: FileStatus
  downloadUrl?: string
  filename?: string
  sizeBytes?: number
  processingTimeMs?: number
  error?: string
}

const OUTPUT_FORMATS = [
  { value: "pdf",  label: "PDF",        icon: "📄" },
  { value: "docx", label: "Word",       icon: "📝" },
  { value: "xlsx", label: "Excel",      icon: "📊" },
  { value: "txt",  label: "Texto",      icon: "🔤" },
  { value: "png",  label: "PNG",        icon: "🖼"  },
  { value: "jpg",  label: "JPG",        icon: "📷" },
]

function fmt(bytes: number) {
  if (bytes < 1024) return `${bytes} B`
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(0)} KB`
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`
}

export default function BatchPage() {
  const [items, setItems]       = useState<FileItem[]>([])
  const [format, setFormat]     = useState("pdf")
  const [running, setRunning]   = useState(false)

  const handleFiles = (files: File[]) => {
    const newItems: FileItem[] = files
      .filter(f => !items.some(i => i.file.name === f.name && i.file.size === f.size))
      .map(f => ({
        id: `${f.name}-${f.size}-${Date.now()}`,
        file: f,
        status: "pending",
      }))
    setItems(prev => [...prev, ...newItems])
  }

  const removeItem = (id: string) =>
    setItems(prev => prev.filter(i => i.id !== id))

  const clearAll = () => setItems([])

  const updateItem = (id: string, patch: Partial<FileItem>) =>
    setItems(prev => prev.map(i => i.id === id ? { ...i, ...patch } : i))

  const runBatch = async () => {
    const pending = items.filter(i => i.status === "pending")
    if (!pending.length) return
    setRunning(true)

    // Procesamos en paralelo con concurrencia limitada a 5
    const CONCURRENCY = 5
    const queue = [...pending]

    const worker = async () => {
      while (queue.length > 0) {
        const item = queue.shift()!
        updateItem(item.id, { status: "processing" })

        const fd = new FormData()
        fd.append("file", item.file)
        fd.append("output_format", format)

        try {
          const res = await fetch(`${API}/convert/`, { method: "POST", body: fd })
          const data = await res.json()

          if (!res.ok) {
            updateItem(item.id, { status: "error", error: data.detail || `Error ${res.status}` })
          } else {
            updateItem(item.id, {
              status: "done",
              downloadUrl: data.download_url,
              filename: data.filename,
              sizeBytes: data.size_bytes,
              processingTimeMs: data.processing_time_ms,
            })
          }
        } catch (err: any) {
          updateItem(item.id, { status: "error", error: err.message || "Sin conexión" })
        }
      }
    }

    await Promise.all(Array.from({ length: CONCURRENCY }, worker))
    setRunning(false)
  }

  const done    = items.filter(i => i.status === "done").length
  const errors  = items.filter(i => i.status === "error").length
  const pending = items.filter(i => i.status === "pending").length
  const total   = items.length

  return (
    <div className="max-w-3xl mx-auto">

      {/* Selector de formato */}
      <div className="bg-white rounded-2xl border border-gray-100 shadow-sm p-6 mb-4">
        <h2 className="text-sm font-semibold text-gray-700 mb-3">Formato de salida para todos los archivos</h2>
        <div className="flex gap-2 flex-wrap">
          {OUTPUT_FORMATS.map(f => (
            <button
              key={f.value}
              onClick={() => setFormat(f.value)}
              className={`flex items-center gap-1.5 px-3 py-2 rounded-xl border text-sm font-medium transition-all
                ${format === f.value
                  ? "border-indigo-500 bg-indigo-50 text-indigo-700"
                  : "border-gray-100 hover:border-gray-200 text-gray-600"}`}
            >
              <span>{f.icon}</span> {f.label}
            </button>
          ))}
        </div>
      </div>

      {/* Drop zone */}
      <div className="bg-white rounded-2xl border border-gray-100 shadow-sm p-6 mb-4">
        <h2 className="text-sm font-semibold text-gray-700 mb-3">
          Agrega archivos{" "}
          <span className="font-normal text-gray-400">({total}/50)</span>
        </h2>
        <DropZone
          onFiles={handleFiles}
          multiple
          accept=".pdf,.doc,.docx,.xls,.xlsx,.ppt,.pptx,.jpg,.jpeg,.png,.webp"
          label="Arrastra múltiples archivos aquí"
        />
      </div>

      {/* Lista de archivos */}
      {items.length > 0 && (
        <div className="bg-white rounded-2xl border border-gray-100 shadow-sm mb-4 overflow-hidden">
          {/* Header de la lista */}
          <div className="flex items-center justify-between px-5 py-3 border-b border-gray-50">
            <div className="flex items-center gap-3 text-xs text-gray-500">
              <span className="bg-gray-100 text-gray-600 px-2 py-0.5 rounded-full font-medium">
                {total} archivos
              </span>
              {done > 0 && (
                <span className="bg-green-100 text-green-700 px-2 py-0.5 rounded-full font-medium">
                  {done} listos
                </span>
              )}
              {errors > 0 && (
                <span className="bg-red-100 text-red-700 px-2 py-0.5 rounded-full font-medium">
                  {errors} errores
                </span>
              )}
            </div>
            <button
              onClick={clearAll}
              disabled={running}
              className="text-xs text-gray-400 hover:text-red-500 transition-colors disabled:opacity-40"
            >
              Limpiar todo
            </button>
          </div>

          {/* Filas */}
          <ul className="divide-y divide-gray-50 max-h-72 overflow-y-auto">
            {items.map(item => (
              <li key={item.id} className="flex items-center gap-3 px-5 py-3">
                {/* Icono de estado */}
                <span className="flex-shrink-0 text-base">
                  {item.status === "pending"    && "⏳"}
                  {item.status === "processing" && (
                    <span className="inline-block w-4 h-4 border-2 border-indigo-200 border-t-indigo-600 rounded-full animate-spin" />
                  )}
                  {item.status === "done"       && "✅"}
                  {item.status === "error"      && "❌"}
                </span>

                {/* Nombre */}
                <span className="flex-1 text-sm text-gray-700 truncate">{item.file.name}</span>

                {/* Tamaño original */}
                <span className="text-xs text-gray-400 flex-shrink-0">
                  {fmt(item.file.size)}
                </span>

                {/* Resultado */}
                {item.status === "done" && item.downloadUrl && (
                  <a
                    href={`http://localhost:8000${item.downloadUrl}`}
                    download={item.filename}
                    className="flex-shrink-0 text-xs bg-green-50 text-green-700 hover:bg-green-100 px-2.5 py-1 rounded-lg font-medium transition-colors"
                  >
                    ⬇ Descargar
                  </a>
                )}

                {item.status === "error" && (
                  <span className="flex-shrink-0 text-xs text-red-500 max-w-32 truncate" title={item.error}>
                    {item.error}
                  </span>
                )}

                {/* Quitar */}
                {item.status === "pending" && (
                  <button
                    onClick={() => removeItem(item.id)}
                    className="flex-shrink-0 text-gray-300 hover:text-red-400 transition-colors text-sm"
                  >
                    ✕
                  </button>
                )}
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* Botones de acción */}
      <div className="flex gap-3">
        <button
          onClick={runBatch}
          disabled={pending === 0 || running}
          className="flex-1 py-3.5 rounded-xl bg-indigo-600 hover:bg-indigo-700 disabled:opacity-40
            disabled:cursor-not-allowed text-white font-semibold text-sm transition-colors shadow-sm"
        >
          {running
            ? `Procesando… (${done + errors}/${total})`
            : `Convertir ${pending} archivo${pending !== 1 ? "s" : ""} a ${format.toUpperCase()} →`}
        </button>

        {/* Descargar todos los listos como ZIP — Fase 2 */}
        {done > 1 && !running && (
          <button
            disabled
            title="Próximamente en Fase 2"
            className="px-4 py-3.5 rounded-xl border border-gray-200 text-gray-400 text-sm font-medium
              cursor-not-allowed"
          >
            ⬇ ZIP (pronto)
          </button>
        )}
      </div>

      {/* Resumen final */}
      {!running && done + errors === total && total > 0 && (
        <div className={`mt-4 p-4 rounded-xl text-sm font-medium
          ${errors === 0
            ? "bg-green-50 text-green-800 border border-green-100"
            : "bg-amber-50 text-amber-800 border border-amber-100"}`}
        >
          {errors === 0
            ? `✅ Todos los archivos convertidos correctamente.`
            : `⚠️ ${done} convertidos correctamente, ${errors} con errores.`}
        </div>
      )}
    </div>
  )
}