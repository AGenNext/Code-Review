"use client"

import { useState, useRef, useEffect, Suspense } from "react"
import { Button } from "@/components/ui/button"
import { Bot, Send, Code2, BookOpen, Hammer, FlaskConical, Bug, Shield, Zap, Building, ChevronDown, Lock, Plus } from "lucide-react"
import { useSearchParams } from "next/navigation"

type Message = { role: "user" | "assistant"; content: string; agent?: string }

const agentDetails = {
  "code-review": { icon: Code2, color: "text-yellow-400", bg: "bg-yellow-400/10", label: "Code Review", badge: "Free", lock: false },
  "docs": { icon: BookOpen, color: "text-blue-400", bg: "bg-blue-400/10", label: "Documentation", badge: "Free", lock: false },
  "refactor": { icon: Hammer, color: "text-purple-400", bg: "bg-purple-400/10", label: "Refactor", badge: "Free", lock: false },
  "test": { icon: FlaskConical, color: "text-green-400", bg: "bg-green-400/10", label: "Testing", badge: "Free", lock: false },
  "debug": { icon: Bug, color: "text-red-400", bg: "bg-red-400/10", label: "Debug", badge: "Free", lock: false },
  "security": { icon: Shield, color: "text-orange-400", bg: "bg-orange-400/10", label: "Security", badge: "Pro", lock: true },
  "performance": { icon: Zap, color: "text-cyan-400", bg: "bg-cyan-400/10", label: "Performance", badge: "Pro", lock: true },
  "architect": { icon: Building, color: "text-pink-400", bg: "bg-pink-400/10", label: "Architect", badge: "Enterprise", lock: true },
}

function AgentsContent() {
  const searchParams = useSearchParams()
  const initialAgent = searchParams.get("skill")
  const [selected, setSelected] = useState<string | null>(initialAgent)
  const [input, setInput] = useState("")
  const [messages, setMessages] = useState<Message[]>([])
  const [showAll, setShowAll] = useState(false)
  const scrollRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    scrollRef.current?.scrollIntoView({ behavior: "smooth" })
  }, [messages])

  const handleSend = () => {
    if (!input.trim()) return
    const userMsg: Message = { role: "user", content: input }
    setMessages(p => [...p, userMsg])
    
    setTimeout(() => {
      setMessages(p => [...p, { 
        role: "assistant", 
        content: `Analyzing your request with @${selected || "default"} agent...\n\nI'll help you with: ${input}`,
        agent: selected || undefined 
      }])
    }, 600)
    setInput("")
  }

  const displayAgents = showAll ? Object.entries(agentDetails) : Object.entries(agentDetails).slice(0, 5)
  const currentAgent = selected ? agentDetails[selected as keyof typeof agentDetails] : null

  return (
    <div className="min-h-screen bg-background">
      <header className="sticky top-0 z-50 bg-background/80 backdrop-blur border-b border-border">
        <div className="container px-4 py-4">
          <div className="flex items-center gap-3">
            <div className="p-2 rounded-lg bg-primary/10">
              <Bot className="w-6 h-6 text-primary" />
            </div>
            <div>
              <h1 className="text-xl font-bold">CopilotHub</h1>
              <p className="text-xs text-muted-foreground">Select an agent to start</p>
            </div>
          </div>
        </div>
      </header>

      <main className="container px-4 py-6">
        {/* Agent Grid */}
        <div className="mb-8">
          <div className="flex items-center justify-between mb-4">
            <p className="text-sm text-muted-foreground">Choose your AI agent</p>
            <button onClick={() => setShowAll(!showAll)} className="text-sm text-primary hover:underline">
              {showAll ? "Show less" : "Show all"}
            </button>
          </div>
          
          <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
            {displayAgents.map(([id, agent]) => {
              const Icon = agent.icon
              return (
                <button
                  key={id}
                  onClick={() => setSelected(id)}
                  disabled={agent.lock}
                  className={`relative p-4 rounded-xl border transition-all ${
                    selected === id 
                      ? `border-primary ${agent.bg} ring-1 ring-primary` 
                      : "border-border hover:border-primary/50"
                  } ${agent.lock ? "opacity-50 cursor-not-allowed" : ""}`}
                >
                  {agent.lock && (
                    <Lock className="absolute top-2 right-2 w-4 h-4 text-muted-foreground" />
                  )}
                  <Icon className={`w-6 h-6 ${agent.color} mb-2`} />
                  <div className="text-left">
                    <p className="font-medium text-sm">@{id}</p>
                    <p className="text-xs text-muted-foreground">{agent.label}</p>
                  </div>
                  <span className={`absolute bottom-2 right-2 text-xs px-1.5 py-0.5 rounded ${
                    agent.badge === "Free" ? "bg-green-500/20 text-green-400" : "bg-primary/20 text-primary"
                  }`}>
                    {agent.badge}
                  </span>
                </button>
              )
            })}
          </div>
        </div>

        {/* Chat Interface */}
        <div className="rounded-2xl border border-border bg-card overflow-hidden">
          <div className="px-6 py-4 border-b border-border">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                {currentAgent && (
                  <>
                    <currentAgent.icon className={`w-5 h-5 ${currentAgent.color}`} />
                    <div>
                      <h2 className="font-semibold">{currentAgent.label}</h2>
                      <p className="text-xs text-muted-foreground">@{selected}</p>
                    </div>
                  </>
                )}
              </div>
              <ChevronDown className="w-5 h-5 text-muted-foreground" />
            </div>
          </div>

          <div className="h-[450px] overflow-y-auto p-6 space-y-4">
            {messages.map((msg, i) => (
              <div key={i} className={`flex ${msg.role === "user" ? "justify-end" : "justify-start"}`}>
                <div className={`max-w-[80%] rounded-2xl px-5 py-3 ${
                  msg.role === "user" ? "bg-primary text-primary-foreground" : "bg-muted"
                }`}>
                  {msg.agent && (
                    <div className={`text-xs mb-1 opacity-70`}>@{msg.agent}</div>
                  )}
                  <p className="whitespace-pre-wrap">{msg.content}</p>
                </div>
              </div>
            ))}
            {messages.length === 0 && (
              <div className="text-center py-12 text-muted-foreground">
                <Bot className="w-12 h-12 mx-auto mb-4 opacity-50" />
                <p>Select an agent and start chatting</p>
              </div>
            )}
            <div ref={scrollRef} />
          </div>

          <div className="p-4 border-t border-border">
            <div className="flex gap-3">
              <input
                className="flex-1 rounded-xl border border-input bg-background px-4 py-3 text-sm focus:outline-none focus:ring-2 focus:ring-primary"
                placeholder={`Ask ${selected ? "@" + selected : ""}...`}
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyDown={(e) => e.key === "Enter" && handleSend()}
                disabled={!selected}
              />
              <Button size="icon" onClick={handleSend} disabled={!selected || !input.trim()} className="rounded-xl">
                <Send className="w-5 h-5" />
              </Button>
            </div>
          </div>
        </div>
      </main>
    </div>
  )
}

export default function AgentsPage() {
  return (
    <Suspense fallback={<div className="min-h-screen bg-background flex items-center justify-center">Loading...</div>}>
      <AgentsContent />
    </Suspense>
  )
}
