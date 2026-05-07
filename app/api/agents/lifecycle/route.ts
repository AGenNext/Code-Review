import { NextResponse } from "next/server"

// Agent lifecycle states
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

// In-memory agent registry
const agentRegistry: Map<string, AgentInstance> = new Map()

// Initialize default agents
const defaultAgents = ["code-review", "docs", "refactor", "test", "debug", "security", "performance", "architect"]

export async function GET() {
  // Get all agent statuses
  const agents = Array.from(agentRegistry.values())
  return NextResponse.json({
    agents,
    summary: {
      total: agents.length,
      running: agents.filter(a => a.state === "running").length,
      idle: agents.filter(a => a.state === "idle").length,
      errors: agents.filter(a => a.state === "error").length,
    },
  })
}

export async function POST(request: Request) {
  const { action, agentId } = await request.json()
  
  switch (action) {
    case "start": {
      if (!agentId) return NextResponse.json({ error: "agentId required" }, { status: 400 })
      
      const instance: AgentInstance = {
        id: `${agentId}-${Date.now()}`,
        canonicalId: `copilot-hub:${agentId}`,
        state: "starting",
        startedAt: new Date().toISOString(),
        memory: 0,
        messages: 0,
        errors: [],
      }
      
      // Simulate start delay
      setTimeout(() => {
        instance.state = "running"
      }, 100)
      
      agentRegistry.set(instance.id, instance)
      return NextResponse.json({ 
        success: true, 
        instance: { ...instance, state: "running" }
      })
    }
    
    case "stop": {
      const instance = Array.from(agentRegistry.values()).find(a => a.canonicalId === `copilot-hub:${agentId}`)
      if (instance) {
        instance.state = "stopping"
        setTimeout(() => {
          agentRegistry.delete(instance.id)
        }, 100)
        return NextResponse.json({ success: true })
      }
      return NextResponse.json({ error: "Agent not found" }, { status: 404 })
    }
    
    case "restart": {
      const instance = Array.from(agentRegistry.values()).find(a => a.canonicalId === `copilot-hub:${agentId}`)
      if (instance) {
        instance.state = "starting"
        setTimeout(() => {
          instance.state = "running"
          instance.errors = []
        }, 100)
        return NextResponse.json({ success: true })
      }
      return NextResponse.json({ error: "Agent not found" }, { status: 404 })
    }
    
    case "status": {
      if (!agentId) return NextResponse.json({ error: "agentId required" }, { status: 400 })
      const instance = Array.from(agentRegistry.values()).find(a => a.canonicalId === `copilot-hub:${agentId}`)
      return NextResponse.json(instance || null)
    }
    
    default:
      return NextResponse.json({ error: "Unknown action" }, { status: 400 })
  }
}
