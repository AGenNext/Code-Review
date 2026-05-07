"use client"

import { useEffect, useState } from "react"
import { Button } from "@/components/ui/button"
import { Wrench, ArrowRight } from "lucide-react"
import Link from "next/link"

type Tool = {
  id: string
  name: string
  description: string
  parameters: Record<string, string>
}

export default function ToolsPage() {
  const [tools, setTools] = useState<Tool[]>([])

  useEffect(() => {
    fetch("/api/tools").then(r => r.json()).then(setTools)
  }, [])

  return (
    <div className="min-h-screen bg-background">
      <header className="border-b bg-card sticky top-0 z-50">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center gap-2">
            <Wrench className="w-6 h-6 text-primary" />
            <h1 className="text-xl font-bold">Custom Tools</h1>
          </div>
        </div>
      </header>

      <main className="container mx-auto px-4 py-6">
        <div className="grid md:grid-cols-2 gap-4">
          {tools.map((tool) => (
            <div key={tool.id} className="border rounded-lg p-4 bg-card">
              <h2 className="text-lg font-semibold mb-2">{tool.name}</h2>
              <p className="text-muted-foreground text-sm mb-4">{tool.description}</p>
              
              <div className="space-y-1">
                <p className="text-sm font-medium">Parameters:</p>
                {Object.entries(tool.parameters).map(([key, type]) => (
                  <div key={key} className="text-xs bg-secondary px-2 py-1 rounded inline-block mr-1">
                    {key}: <span className="text-muted-foreground">{type}</span>
                  </div>
                ))}
              </div>
            </div>
          ))}
        </div>
      </main>
    </div>
  )
}
