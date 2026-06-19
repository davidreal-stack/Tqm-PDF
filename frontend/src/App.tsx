import { useState } from "react"
import Sidebar from "./components/layout/Sidebar"
import Header from "./components/layout/Header"
import ConvertPage from "./pages/ConvertPage"
import ToolsPage from "./pages/ToolsPage"
import BatchPage from "./pages/BatchPage"

export type ActiveTool =
  | "convert"
  | "compress"
  | "merge"
  | "split"
  | "rotate"
  | "watermark"
  | "protect"
  | "ocr"
  | "batch"

export default function App() {
  const [activeTool, setActiveTool] = useState<ActiveTool>("convert")

  const renderPage = () => {
    if (activeTool === "convert") return <ConvertPage />
    if (activeTool === "batch") return <BatchPage />
    return <ToolsPage tool={activeTool} />
  }

  return (
    <div className="flex h-screen bg-gray-50 font-sans">
      <Sidebar activeTool={activeTool} onSelect={setActiveTool} />
      <div className="flex flex-col flex-1 overflow-hidden">
        <Header activeTool={activeTool} />
        <main className="flex-1 overflow-y-auto p-6 md:p-8">
          {renderPage()}
        </main>
      </div>
    </div>
  )
}