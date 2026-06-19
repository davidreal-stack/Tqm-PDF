import { useState } from "react"

const API = "http://localhost:8000/api/v1"

export type UploadStatus = "idle" | "uploading" | "processing" | "done" | "error"

export interface UploadResult {
  downloadUrl?: string
  filename?: string
  sizeBytes?: number
  processingTimeMs?: number
  error?: string
}

export function useConvert() {
  const [status, setStatus] = useState<UploadStatus>("idle")
  const [result, setResult] = useState<UploadResult>({})

  async function convert(file: File, outputFormat: string, extra?: Record<string, string>) {
    setStatus("uploading")
    setResult({})

    const fd = new FormData()
    fd.append("file", file)
    fd.append("output_format", outputFormat)
    if (extra) Object.entries(extra).forEach(([k, v]) => fd.append(k, v))

    setStatus("processing")

    try {
      const res = await fetch(`${API}/convert/`, { method: "POST", body: fd })
      const data = await res.json()

      if (!res.ok) {
        setStatus("error")
        setResult({ error: data.detail || `Error ${res.status}` })
        return
      }

      setStatus("done")
      setResult({
        downloadUrl: data.download_url,
        filename: data.filename,
        sizeBytes: data.size_bytes,
        processingTimeMs: data.processing_time_ms,
      })
    } catch (err: any) {
      setStatus("error")
      setResult({ error: err.message || "No se pudo conectar con el servidor" })
    }
  }

  async function callTool(
    endpoint: string,
    file: File,
    extra?: Record<string, string>
  ) {
    setStatus("uploading")
    setResult({})

    const fd = new FormData()
    fd.append("file", file)
    if (extra) Object.entries(extra).forEach(([k, v]) => fd.append(k, v))

    setStatus("processing")

    try {
      const res = await fetch(`${API}/tools/${endpoint}`, { method: "POST", body: fd })
      const data = await res.json()

      if (!res.ok) {
        setStatus("error")
        setResult({ error: data.detail || `Error ${res.status}` })
        return
      }

      setStatus("done")
      setResult({
        downloadUrl: data.download_url,
        filename: data.filename,
        sizeBytes: data.size_bytes,
      })
    } catch (err: any) {
      setStatus("error")
      setResult({ error: err.message || "No se pudo conectar con el servidor" })
    }
  }

  async function mergeFiles(files: File[]) {
    setStatus("uploading")
    setResult({})

    const fd = new FormData()
    files.forEach((f) => fd.append("files", f))

    setStatus("processing")

    try {
      const res = await fetch(`${API}/tools/merge`, { method: "POST", body: fd })
      const data = await res.json()

      if (!res.ok) {
        setStatus("error")
        setResult({ error: data.detail || `Error ${res.status}` })
        return
      }

      setStatus("done")
      setResult({ downloadUrl: data.download_url, filename: data.filename, sizeBytes: data.size_bytes })
    } catch (err: any) {
      setStatus("error")
      setResult({ error: err.message })
    }
  }

  function reset() {
    setStatus("idle")
    setResult({})
  }

  return { status, result, convert, callTool, mergeFiles, reset }
}