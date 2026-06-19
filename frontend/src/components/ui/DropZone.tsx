import { useCallback, useState } from "react"

interface Props {
  onFiles: (files: File[]) => void
  accept?: string
  multiple?: boolean
  label?: string
}

export default function DropZone({
  onFiles,
  accept = "*/*",
  multiple = false,
  label = "Arrastra tu archivo aquí o haz clic para seleccionar",
}: Props) {
  const [dragging, setDragging] = useState(false)

  const handleDrop = useCallback(
    (e: React.DragEvent) => {
      e.preventDefault()
      setDragging(false)
      const files = Array.from(e.dataTransfer.files)
      if (files.length) onFiles(multiple ? files : [files[0]])
    },
    [onFiles, multiple]
  )

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = Array.from(e.target.files || [])
    if (files.length) onFiles(multiple ? files : [files[0]])
    e.target.value = ""
  }

  return (
    <label
      onDragOver={(e) => { e.preventDefault(); setDragging(true) }}
      onDragLeave={() => setDragging(false)}
      onDrop={handleDrop}
      className={`flex flex-col items-center justify-center w-full min-h-48 rounded-2xl border-2 border-dashed cursor-pointer transition-all
        ${dragging
          ? "border-indigo-500 bg-indigo-50 scale-[1.01]"
          : "border-gray-200 bg-gray-50 hover:border-indigo-300 hover:bg-indigo-50/40"
        }`}
    >
      <input type="file" accept={accept} multiple={multiple} className="hidden" onChange={handleChange} />
      <div className="text-4xl mb-3 select-none">{dragging ? "📂" : "📁"}</div>
      <p className="text-sm font-medium text-gray-700 text-center px-4">{label}</p>
      <p className="text-xs text-gray-400 mt-1">o haz clic para explorar archivos</p>
    </label>
  )
}