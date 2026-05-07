"use client"

import { useEffect, useState } from "react"
import { Wrench, Sparkles } from "lucide-react"

type Tool = { id: string; name: string; description: string; parameters: Record<string, string> }

export default function ToolsPage() {
  const [tools, setTools] = useState<Tool[]>([])

  useEffect(() => {
    fetch("/api/tools").then(r => r.json()).then(setTools)
  }, [])

  const colors = ["text-yellow-400", "text-blue-400", "text-purple-400", "text-green-400", "text-red-400", "text-orange-400", "text-pink-400", "text-cyan-400"]

  return (
    <div className="min-h-screen bg-background">
      <header className="sticky top-0 z-50 bg-background/80 backdrop-blur border-b border-border">
        <div className="container px-4 py-4">
          <div className="flex items-center gap-3">
            <div className="p-2 rounded-lg bg-primary/10">
              <Wrench className="w-6 h-6 text-primary" />
            </div>
            <h1 className="text-xl font-bold">Tools</h1>
          </div>
        </div>
      </header>

      <main className="container px-4 py-8">
        <div className="grid md:grid-cols-2 gap-4">
          {tools.map((tool, i) => (
            <div key={tool.id} className="p-6 rounded-2xl bg-card border border-border hover:border-primary/50 transition-all animate-slide-up" style={{ animationDelay: `${i * 50}ms` }}>
              <div className="flex items-start gap-4">
                <div className={`p-3 rounded-xl bg-secondary ${colors[i % colors.length]}`}>
                  <Sparkles className="w-5 h-5" />
                </div>
                <div className="flex-1">
                  <h3 className="text-lg font-semibold mb-1">{tool.name}</h3>
                  <p className="text-sm text-muted-foreground mb-3">{tool.description}</p>
                  <div className="flex flex-wrap gap-2">
                    {Object.entries(tool.parameters).map(([key, type]) => (
                      <code key={key} className="text-xs bg-secondary px-3 py-1 rounded-full">
                        {key}: <span className="text-muted-foreground">{type}</span>
                      </code>
                    ))}
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>
      </main>
    </div>
  )
}
