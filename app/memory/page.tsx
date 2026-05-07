"use client"

import { useEffect, useState } from "react"
import { Brain, Trash2, Download, Clock, MessageCircle } from "lucide-react"

type MemoryEntry = { role: string; content: string; timestamp: string }

export default function MemoryPage() {
  const [memories, setMemories] = useState<Record<string, MemoryEntry[]>>({})
  const [sessionId, setSessionId] = useState("default")
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetch("/api/memory")
      .then(r => r.json())
      .then(setMemories)
      .finally(() => setLoading(false))
  }, [])

  const clearMemory = async () => {
    await fetch("/api/memory", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ messages: [], sessionId }),
    })
    window.location.reload()
  }

  const exportMemory = () => {
    const blob = new Blob([JSON.stringify(memories, null, 2)], { type: "application/json" })
    const url = URL.createObjectURL(blob)
    const a = document.createElement("a")
    a.href = url
    a.download = `copilot-memory-${sessionId}.json`
    a.click()
  }

  const currentMemory = memories[sessionId] || []
  const totalTokens = currentMemory.reduce((acc, m) => acc + m.content.split(" ").length, 0)

  return (
    <div className="min-h-screen bg-background">
      <header className="sticky top-0 z-50 bg-background/80 backdrop-blur border-b border-border">
        <div className="container px-4 py-4">
          <div className="flex items-center gap-3">
            <div className="p-2 rounded-lg bg-primary/10">
              <Brain className="w-6 h-6 text-primary" />
            </div>
            <h1 className="text-xl font-bold">Memory</h1>
          </div>
        </div>
      </header>

      <main className="container px-4 py-8">
        {/* Session Selector */}
        <div className="flex items-center gap-4 mb-8">
          <input
            type="text"
            value={sessionId}
            onChange={(e) => setSessionId(e.target.value)}
            placeholder="Session ID"
            className="px-4 py-2 rounded-lg border border-input bg-background"
          />
          <button onClick={clearMemory} className="flex items-center gap-2 px-4 py-2 rounded-lg border border-destructive text-destructive hover:bg-destructive/10">
            <Trash2 className="w-4 h-4" /> Clear
          </button>
          <button onClick={exportMemory} className="flex items-center gap-2 px-4 py-2 rounded-lg border border-border">
            <Download className="w-4 h-4" /> Export
          </button>
        </div>

        {/* Stats */}
        <div className="grid grid-cols-3 gap-4 mb-8">
          <div className="p-4 rounded-xl bg-card border border-border">
            <div className="flex items-center gap-2 text-muted-foreground mb-1">
              <MessageCircle className="w-4 h-4" />
              <span className="text-sm">Messages</span>
            </div>
            <p className="text-2xl font-bold">{currentMemory.length}</p>
          </div>
          <div className="p-4 rounded-xl bg-card border border-border">
            <div className="flex items-center gap-2 text-muted-foreground mb-1">
              <Clock className="w-4 h-4" />
              <span className="text-sm">Tokens</span>
            </div>
            <p className="text-2xl font-bold">~{totalTokens}</p>
          </div>
          <div className="p-4 rounded-xl bg-card border border-border">
            <div className="flex items-center gap-2 text-muted-foreground mb-1">
              <Brain className="w-4 h-4" />
              <span className="text-sm">Sessions</span>
            </div>
            <p className="text-2xl font-bold">{Object.keys(memories).length}</p>
          </div>
        </div>

        {/* Memory List */}
        <div className="space-y-4">
          {currentMemory.map((entry, i) => (
            <div key={i} className="p-4 rounded-xl bg-card border border-border">
              <div className="flex items-center gap-2 mb-2">
                <span className={`text-xs px-2 py-1 rounded ${
                  entry.role === "user" ? "bg-primary/20 text-primary" : "bg-secondary text-muted-foreground"
                }`}>
                  {entry.role}
                </span>
                <span className="text-xs text-muted-foreground">
                  {new Date(entry.timestamp).toLocaleString()}
                </span>
              </div>
              <p className="text-sm">{entry.content}</p>
            </div>
          ))}
          
          {currentMemory.length === 0 && (
            <div className="text-center py-12 text-muted-foreground">
              <Brain className="w-12 h-12 mx-auto mb-4 opacity-50" />
              <p>No memories yet. Start chatting to build your context.</p>
            </div>
          )}
        </div>
      </main>
    </div>
  )
}
