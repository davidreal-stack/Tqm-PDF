import type { ActiveTool } from "../../App"

interface NavItem {
  id: ActiveTool
  label: string
  icon: string
  group?: string
}

const NAV_ITEMS: NavItem[] = [
  { id: "convert",   label: "Convertir",       icon: "🔄", group: "Principal" },
  { id: "batch",     label: "Lotes",           icon: "📦", group: "Principal" },
  { id: "compress",  label: "Comprimir",       icon: "📉", group: "Herramientas PDF" },
  { id: "merge",     label: "Fusionar",        icon: "🔗", group: "Herramientas PDF" },
  { id: "split",     label: "Dividir",         icon: "✂️",  group: "Herramientas PDF" },
  { id: "rotate",    label: "Rotar",           icon: "🔃", group: "Herramientas PDF" },
  { id: "watermark", label: "Marca de agua",   icon: "💧", group: "Herramientas PDF" },
  { id: "protect",   label: "Proteger",        icon: "🔒", group: "Herramientas PDF" },
  { id: "ocr",       label: "OCR",             icon: "🔍", group: "Avanzado" },
]

const GROUPS = ["Principal", "Herramientas PDF", "Avanzado"]

interface Props {
  activeTool: ActiveTool
  onSelect: (tool: ActiveTool) => void
}

export default function Sidebar({ activeTool, onSelect }: Props) {
  return (
    <aside className="w-56 flex-shrink-0 bg-white border-r border-gray-100 flex flex-col shadow-sm">
      {/* Logo */}
      <div className="px-5 py-5 border-b border-gray-100">
        <div className="flex items-center gap-2.5">
          <div className="w-8 h-8 rounded-lg bg-indigo-600 flex items-center justify-center text-white font-bold text-sm">
            DF
          </div>
          <span className="font-semibold text-gray-900 text-base tracking-tight">DocuForge</span>
        </div>
      </div>

      {/* Nav */}
      <nav className="flex-1 px-3 py-4 overflow-y-auto">
        {GROUPS.map((group) => {
          const items = NAV_ITEMS.filter((i) => i.group === group)
          return (
            <div key={group} className="mb-5">
              <p className="px-2 mb-1.5 text-[10px] font-semibold uppercase tracking-widest text-gray-400">
                {group}
              </p>
              {items.map((item) => (
                <button
                  key={item.id}
                  onClick={() => onSelect(item.id)}
                  className={`w-full flex items-center gap-2.5 px-3 py-2 rounded-lg text-sm font-medium transition-all mb-0.5
                    ${activeTool === item.id
                      ? "bg-indigo-50 text-indigo-700"
                      : "text-gray-600 hover:bg-gray-50 hover:text-gray-900"
                    }`}
                >
                  <span className="text-base leading-none">{item.icon}</span>
                  {item.label}
                </button>
              ))}
            </div>
          )
        })}
      </nav>

      {/* Footer */}
      <div className="px-4 py-4 border-t border-gray-100">
        <p className="text-xs text-gray-400 text-center">v1.0.0 · Fase 1</p>
      </div>
    </aside>
  )
}