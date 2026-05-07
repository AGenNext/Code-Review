"use client"

import { useEffect, useState } from "react"
import { Play, Square, RotateCcw, Activity, Server, AlertCircle, CheckCircle, Clock } from "lucide-react"

type AgentState = "idle" | "starting" | "running" | "paused" | "stopping" | "error"

interface AgentInstance {
  id: string
  canonicalId: string
  state: AgentState
  startedAt: string
  memory: number
  messages: number
  errors: string[]
}

const defaultAgents = [
  { id: "code-review", name: "Code Review" },
  { id: "docs", name: "Documentation" },
  { id: "refactor", name: "Refactor" },
  { id: "test", name: "Testing" },
  { id: "debug", name: "Debug" },
  { id: "security", name: "Security" },
  { id: "performance", name: "Performance" },
  { id: "architect", name: "Architect" },
]

export default function LifecyclePage() {
  const [agents, setAgents] = useState<AgentInstance[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetchAgents()
    const interval = setInterval(fetchAgents, 5000)
    return () => clearInterval(interval)
  }, [])

  const fetchAgents = async () => {
    try {
      const res = await fetch("/api/agents/lifecycle")
      const data = await res.json()
      setAgents(data.agents || [])
    } catch (e) {
      console.error(e)
    } finally {
      setLoading(false)
    }
  }

  const handleAction = async (agentId: string, action: string) => {
    await fetch("/api/agents/lifecycle", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ agentId, action }),
    })
    fetchAgents()
  }

  const getStateColor = (state: AgentState) => {
    switch (state) {
      case "running": return "text-green-400"
      case "starting": return "text-yellow-400"
      case "stopping": return "text-orange-400"
      case "error": return "text-red-400"
      case "paused": return "text-gray-400"
      default: return "text-muted-foreground"
    }
  }

  const getStateIcon = (state: AgentState) => {
    switch (state) {
      case "running": return <CheckCircle className="w-4 h-4" />
      case "error": return <AlertCircle className="w-4 h-4" />
      default: return <Clock className="w-4 h-4" />
    }
  }

  return (
    <div className="min-h-screen bg-background">
      <header className="sticky top-0 z-50 bg-background/80 backdrop-blur border-b border-border">
        <div className="container px-4 py-4">
          <div className="flex items-center gap-3">
            <div className="p-2 rounded-lg bg-primary/10">
              <Activity className="w-6 h-6 text-primary" />
            </div>
            <div>
              <h1 className="text-xl font-bold">Agent Lifecycle</h1>
              <p className="text-xs text-muted-foreground">Manage agent states</p>
            </div>
          </div>
        </div>
      </header>

      <main className="container px-4 py-8">
        {/* Status Overview */}
        <div className="grid grid-cols-4 gap-4 mb-8">
          <div className="p-4 rounded-xl bg-card border border-border">
            <Server className="w-5 h-5 text-muted-foreground mb-2" />
            <p className="text-2xl font-bold">{agents.length}</p>
            <p className="text-xs text-muted-foreground">Total Agents</p>
          </div>
          <div className="p-4 rounded-xl bg-card border border-border">
            <CheckCircle className="w-5 h-5 text-green-400 mb-2" />
            <p className="text-2xl font-bold">{agents.filter(a => a.state === "running").length}</p>
            <p className="text-xs text-muted-foreground">Running</p>
          </div>
          <div className="p-4 rounded-xl bg-card border border-border">
            <Clock className="w-5 h-5 text-yellow-400 mb-2" />
            <p className="text-2xl font-bold">{agents.filter(a => a.state === "idle").length}</p>
            <p className="text-xs text-muted-foreground">Idle</p>
          </div>
          <div className="p-4 rounded-xl bg-card border border-border">
            <AlertCircle className="w-5 h-5 text-red-400 mb-2" />
            <p className="text-2xl font-bold">{agents.filter(a => a.state === "error").length}</p>
            <p className="text-xs text-muted-foreground">Errors</p>
          </div>
        </div>

        {/* Agent Grid */}
        <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-4">
          {defaultAgents.map((agent) => {
            const instance = agents.find(a => a.canonicalId === `copilot-hub:${agent.id}`)
            const state = instance?.state || "idle"
            
            return (
              <div key={agent.id} className="p-4 rounded-xl bg-card border border-border">
                <div className="flex items-center justify-between mb-3">
                  <h3 className="font-semibold">@{agent.id}</h3>
                  <span className={`flex items-center gap-1 text-xs ${getStateColor(state)}`}>
                    {getStateIcon(state)}
                    {state}
                  </span>
                </div>
                
                <p className="text-sm text-muted-foreground mb-4">{agent.name}</p>
                
                {instance && (
                  <div className="text-xs text-muted-foreground mb-4 space-y-1">
                    <p>Started: {new Date(instance.startedAt).toLocaleTimeString()}</p>
                    <p>Messages: {instance.messages}</p>
                  </div>
                )}
                
                <div className="flex gap-2">
                  {state === "idle" ? (
                    <button
                      onClick={() => handleAction(agent.id, "start")}
                      className="flex-1 flex items-center justify-center gap-2 px-3 py-2 rounded-lg bg-green-500/20 text-green-400 hover:bg-green-500/30 text-sm"
                    >
                      <Play className="w-4 h-4" /> Start
                    </button>
                  ) : state === "running" ? (
                    <button
                      onClick={() => handleAction(agent.id, "stop")}
                      className="flex-1 flex items-center justify-center gap-2 px-3 py-2 rounded-lg bg-red-500/20 text-red-400 hover:bg-red-500/30 text-sm"
                    >
                      <Square className="w-4 h-4" /> Stop
                    </button>
                  ) : null}
                  
                  {state === "running" && (
                    <button
                      onClick={() => handleAction(agent.id, "restart")}
                      className="flex items-center justify-center gap-2 px-3 py-2 rounded-lg bg-secondary text-sm"
                    >
                      <RotateCcw className="w-4 h-4" />
                    </button>
                  )}
                </div>
              </div>
            )
          })}
        </div>
      </main>
    </div>
  )
}
