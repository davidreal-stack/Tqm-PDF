interface Props {
  status: "idle" | "uploading" | "processing" | "done" | "error"
  filename?: string
  downloadUrl?: string
  errorMsg?: string
  processingTimeMs?: number
  sizeBytes?: number
}

function fmt(bytes: number) {
  if (bytes < 1024) return `${bytes} B`
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`
  return `${(bytes / (1024 * 1024)).toFixed(2)} MB`
}

export default function ResultCard({
  status, filename, downloadUrl, errorMsg, processingTimeMs, sizeBytes,
}: Props) {
  if (status === "idle") return null

  if (status === "uploading" || status === "processing") {
    return (
      <div className="mt-6 p-5 rounded-2xl border border-indigo-100 bg-indigo-50 flex items-center gap-4">
        <div className="w-8 h-8 border-4 border-indigo-200 border-t-indigo-600 rounded-full animate-spin flex-shrink-0" />
        <div>
          <p className="font-medium text-indigo-800">
            {status === "uploading" ? "Subiendo archivo…" : "Procesando…"}
          </p>
          <p className="text-sm text-indigo-600 mt-0.5">Esto puede tomar unos segundos</p>
        </div>
      </div>
    )
  }

  if (status === "error") {
    return (
      <div className="mt-6 p-5 rounded-2xl border border-red-100 bg-red-50">
        <p className="font-medium text-red-700">❌ Error al procesar</p>
        <p className="text-sm text-red-600 mt-1">{errorMsg || "Error desconocido"}</p>
      </div>
    )
  }

  // done
  return (
    <div className="mt-6 p-5 rounded-2xl border border-green-100 bg-green-50">
      <div className="flex items-start justify-between gap-4">
        <div>
          <p className="font-semibold text-green-800">✅ ¡Listo!</p>
          {filename && <p className="text-sm text-green-700 mt-1 font-mono">{filename}</p>}
          <div className="flex gap-4 mt-2">
            {sizeBytes !== undefined && (
              <span className="text-xs text-green-600">{fmt(sizeBytes)}</span>
            )}
            {processingTimeMs !== undefined && (
              <span className="text-xs text-green-600">{processingTimeMs} ms</span>
            )}
          </div>
        </div>
        {downloadUrl && (
          <a
            href={`http://localhost:8000${downloadUrl}`}
            download={filename}
            className="flex-shrink-0 inline-flex items-center gap-2 bg-green-600 hover:bg-green-700 text-white text-sm font-medium px-4 py-2 rounded-lg transition-colors"
          >
            ⬇ Descargar
          </a>
        )}
      </div>
    </div>
  )
}