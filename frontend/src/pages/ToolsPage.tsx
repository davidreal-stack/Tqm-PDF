import { useState } from "react"
import type { ActiveTool } from "../App"
import DropZone from "../components/ui/DropZone"
import ResultCard from "../components/ui/ResultCard"
import { useConvert } from "../hooks/useConvert"

interface Props { tool: Exclude<ActiveTool, "convert" | "batch"> }

export default function ToolsPage({ tool }: Props) {
  const [file, setFile] = useState<File | null>(null)
  const [files, setFiles] = useState<File[]>([])
  const { status, result, callTool, mergeFiles, reset } = useConvert()

  // Tool-specific options state
  const [quality, setQuality]         = useState("ebook")
  const [pages, setPages]             = useState("")
  const [degrees, setDegrees]         = useState("90")
  const [waterText, setWaterText]     = useState("CONFIDENCIAL")
  const [opacity, setOpacity]         = useState("0.3")
  const [password, setPassword]       = useState("")
  const [ocrLang, setOcrLang]         = useState("spa+eng")

  const handleFile   = (fs: File[]) => { setFile(fs[0]); reset() }
  const handleFiles  = (fs: File[]) => { setFiles(fs); reset() }

  const handleRun = () => {
    if (tool === "merge") {
      if (files.length < 2) return
      mergeFiles(files)
      return
    }
    if (!file) return

    const extras: Record<string, string> = {
      compress:  { quality },
      split:     { pages },
      rotate:    { degrees },
      watermark: { text: waterText, opacity, angle: "45" },
      protect:   { user_password: password },
      ocr:       { lang: ocrLang, dpi: "300" },
    }[tool] ?? {}

    callTool(tool, file, extras)
  }

  const isMerge = tool === "merge"

  return (
    <div className="max-w-2xl mx-auto">
      <div className="bg-white rounded-2xl border border-gray-100 shadow-sm p-6 mb-4">
        <h2 className="text-sm font-semibold text-gray-700 mb-3">
          {isMerge ? "Selecciona los PDFs a fusionar (mín. 2)" : "Selecciona el PDF"}
        </h2>

        {isMerge ? (
          <>
            <DropZone onFiles={handleFiles} accept=".pdf" multiple label="Arrastra varios PDFs aquí" />
            {files.length > 0 && (
              <ul className="mt-3 space-y-1">
                {files.map((f, i) => (
                  <li key={i} className="flex items-center gap-2 text-sm text-gray-600 bg-gray-50 px-3 py-1.5 rounded-lg">
                    <span>📄</span>
                    <span className="truncate">{f.name}</span>
                    <span className="ml-auto text-gray-400">{(f.size / 1024).toFixed(0)} KB</span>
                    <button
                      onClick={() => setFiles(files.filter((_, j) => j !== i))}
                      className="text-gray-400 hover:text-red-500"
                    >✕</button>
                  </li>
                ))}
              </ul>
            )}
          </>
        ) : (
          <>
            <DropZone onFiles={handleFile} accept=".pdf" label="Arrastra tu PDF aquí" />
            {file && (
              <div className="mt-3 flex items-center gap-2 text-sm text-gray-600 bg-gray-50 px-3 py-2 rounded-lg">
                <span>📄</span>
                <span className="font-medium truncate">{file.name}</span>
                <span className="text-gray-400 ml-auto">{(file.size / 1024).toFixed(0)} KB</span>
                <button onClick={() => { setFile(null); reset() }} className="text-gray-400 hover:text-red-500">✕</button>
              </div>
            )}
          </>
        )}
      </div>

      {/* Opciones según herramienta */}
      {tool === "compress" && (
        <div className="bg-white rounded-2xl border border-gray-100 shadow-sm p-6 mb-4">
          <h2 className="text-sm font-semibold text-gray-700 mb-3">Calidad de compresión</h2>
          <div className="grid grid-cols-2 gap-2">
            {[
              { v: "screen",   label: "Pantalla",  desc: "Máxima compresión (72 dpi)" },
              { v: "ebook",    label: "eBook",     desc: "Equilibrado (150 dpi) ★" },
              { v: "printer",  label: "Impresora", desc: "Alta calidad (300 dpi)" },
              { v: "prepress", label: "Preprensa", desc: "Máxima calidad (300 dpi+)" },
            ].map((opt) => (
              <button
                key={opt.v}
                onClick={() => setQuality(opt.v)}
                className={`text-left p-3 rounded-xl border text-sm transition-all
                  ${quality === opt.v ? "border-indigo-500 bg-indigo-50" : "border-gray-100 hover:border-gray-200"}`}
              >
                <p className="font-medium text-gray-800">{opt.label}</p>
                <p className="text-xs text-gray-500 mt-0.5">{opt.desc}</p>
              </button>
            ))}
          </div>
        </div>
      )}

      {tool === "split" && (
        <div className="bg-white rounded-2xl border border-gray-100 shadow-sm p-6 mb-4">
          <h2 className="text-sm font-semibold text-gray-700 mb-2">Rango de páginas</h2>
          <input
            type="text"
            value={pages}
            onChange={(e) => setPages(e.target.value)}
            placeholder="Ej: 1-3,5,7-9 — vacío = una pág. por archivo"
            className="w-full px-3 py-2.5 border border-gray-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-indigo-300"
          />
        </div>
      )}

      {tool === "rotate" && (
        <div className="bg-white rounded-2xl border border-gray-100 shadow-sm p-6 mb-4">
          <h2 className="text-sm font-semibold text-gray-700 mb-3">Grados de rotación</h2>
          <div className="flex gap-2">
            {["90", "180", "270"].map((d) => (
              <button
                key={d}
                onClick={() => setDegrees(d)}
                className={`flex-1 py-2.5 rounded-xl border text-sm font-medium transition-all
                  ${degrees === d ? "border-indigo-500 bg-indigo-50 text-indigo-700" : "border-gray-100 hover:border-gray-200 text-gray-600"}`}
              >
                {d}°
              </button>
            ))}
          </div>
        </div>
      )}

      {tool === "watermark" && (
        <div className="bg-white rounded-2xl border border-gray-100 shadow-sm p-6 mb-4 space-y-4">
          <div>
            <label className="text-sm font-semibold text-gray-700 block mb-1.5">Texto de marca</label>
            <input
              type="text"
              value={waterText}
              onChange={(e) => setWaterText(e.target.value)}
              className="w-full px-3 py-2.5 border border-gray-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-indigo-300"
            />
          </div>
          <div>
            <label className="text-sm font-semibold text-gray-700 block mb-1.5">
              Opacidad: {Math.round(parseFloat(opacity) * 100)}%
            </label>
            <input
              type="range" min="0.05" max="0.9" step="0.05"
              value={opacity}
              onChange={(e) => setOpacity(e.target.value)}
              className="w-full accent-indigo-600"
            />
          </div>
        </div>
      )}

      {tool === "protect" && (
        <div className="bg-white rounded-2xl border border-gray-100 shadow-sm p-6 mb-4">
          <label className="text-sm font-semibold text-gray-700 block mb-1.5">Contraseña</label>
          <input
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            placeholder="Mínimo 6 caracteres"
            className="w-full px-3 py-2.5 border border-gray-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-indigo-300"
          />
        </div>
      )}

      {tool === "ocr" && (
        <div className="bg-white rounded-2xl border border-gray-100 shadow-sm p-6 mb-4">
          <h2 className="text-sm font-semibold text-gray-700 mb-3">Idioma del documento</h2>
          <div className="flex gap-2 flex-wrap">
            {[
              { v: "spa",     label: "Solo español" },
              { v: "eng",     label: "Solo inglés" },
              { v: "spa+eng", label: "Español + Inglés ★" },
            ].map((opt) => (
              <button
                key={opt.v}
                onClick={() => setOcrLang(opt.v)}
                className={`px-4 py-2 rounded-xl border text-sm font-medium transition-all
                  ${ocrLang === opt.v ? "border-indigo-500 bg-indigo-50 text-indigo-700" : "border-gray-100 hover:border-gray-200 text-gray-600"}`}
              >
                {opt.label}
              </button>
            ))}
          </div>
        </div>
      )}

      <button
        onClick={handleRun}
        disabled={
          (isMerge ? files.length < 2 : !file) ||
          status === "processing" ||
          status === "uploading"
        }
        className="w-full py-3.5 rounded-xl bg-indigo-600 hover:bg-indigo-700 disabled:opacity-40 disabled:cursor-not-allowed
          text-white font-semibold text-sm transition-colors shadow-sm"
      >
        {status === "processing" || status === "uploading" ? "Procesando…" : "Ejecutar →"}
      </button>

      <ResultCard
        status={status}
        filename={result.filename}
        downloadUrl={result.downloadUrl}
        errorMsg={result.error}
        sizeBytes={result.sizeBytes}
      />
    </div>
  )
}