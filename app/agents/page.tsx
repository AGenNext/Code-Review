"use client"

import { useState, useRef, useEffect } from "react"
import { Button } from "@/components/ui/button"
import { Bot, Send, Code2, BookOpen, Hammer, FlaskConical, Bug, ChevronDown } from "lucide-react"

type Message = { role: "user" | "assistant"; content: string; agent?: string }

const agents = [
  { id: "code-review", icon: Code2, color: "text-yellow-400", bg: "bg-yellow-400/10", label: "Code Review" },
  { id: "docs", icon: BookOpen, color: "text-blue-400", bg: "bg-blue-400/10", label: "Documentation" },
  { id: "refactor", icon: Hammer, color: "text-purple-400", bg: "bg-purple-400/10", label: "Refactor" },
  { id: "test", icon: FlaskConical, color: "text-green-400", bg: "bg-green-400/10", label: "Testing" },
  { id: "debug", icon: Bug, color: "text-red-400", bg: "bg-red-400/10", label: "Debug" },
]

export default function AgentsPage() {
  const [selected, setSelected] = useState<string | null>(null)
  const [input, setInput] = useState("")
  const [messages, setMessages] = useState<Message[]>([
    { role: "assistant", content: "Welcome to CopilotHub. Select an agent and ask me anything." }
  ])
  const scrollRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    scrollRef.current?.scrollIntoView({ behavior: "smooth" })
  }, [messages])

  const handleSend = () => {
    if (!input.trim()) return
    setMessages(p => [...p, { role: "user", content: input }])
    setTimeout(() => {
      setMessages(p => [...p, { 
        role: "assistant", 
        content: `Processing your request with @${selected || "default"}...`,
        agent: selected || undefined 
      }])
    }, 500)
    setInput("")
  }

  const currentAgent = agents.find(a => a.id === selected)

  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <header className="sticky top-0 z-50 bg-background/80 backdrop-blur border-b border-border">
        <div className="container px-4 py-4">
          <div className="flex items-center gap-3">
            <div className="p-2 rounded-lg bg-primary/10">
              <Bot className="w-6 h-6 text-primary" />
            </div>
            <div>
              <h1 className="text-xl font-bold">CopilotHub</h1>
              <p className="text-xs text-muted-foreground">AI-Powered Development</p>
            </div>
          </div>
        </div>
      </header>

      <main className="container px-4 py-6">
        {/* Agent Selector */}
        <div className="mb-8">
          <p className="text-sm text-muted-foreground mb-4">Select your agent</p>
          <div className="flex flex-wrap gap-3">
            {agents.map((agent) => (
              <button
                key={agent.id}
                onClick={() => setSelected(agent.id)}
                className={`flex items-center gap-3 px-5 py-3 rounded-xl border transition-all ${
                  selected === agent.id 
                    ? `border-primary ${agent.bg} ring-1 ring-primary` 
                    : "border-border hover:border-primary/50"
                }`}
              >
                <agent.icon className={`w-5 h-5 ${agent.color}`} />
                <span className="font-medium">@{agent.id}</span>
              </button>
            ))}
          </div>
        </div>

        {/* Chat */}
        <div className="rounded-2xl border border-border bg-card overflow-hidden">
          {/* Header */}
          <div className="px-6 py-4 border-b border-border flex items-center justify-between">
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

          {/* Messages */}
          <div className="h-[500px] overflow-y-auto p-6 space-y-4">
            {messages.map((msg, i) => (
              <div key={i} className={`flex ${msg.role === "user" ? "justify-end" : "justify-start"}`}>
                <div className={`max-w-[80%] rounded-2xl px-5 py-3 ${
                  msg.role === "user"
                    ? "bg-primary text-primary-foreground"
                    : "bg-muted"
                }`}>
                  {msg.agent && (
                    <div className={`text-xs mb-1 opacity-70`}>@{msg.agent}</div>
                  )}
                  <p className="whitespace-pre-wrap">{msg.content}</p>
                </div>
              </div>
            ))}
            <div ref={scrollRef} />
          </div>

          {/* Input */}
          <div className="p-4 border-t border-border">
            <div className="flex gap-3">
              <input
                className="flex-1 rounded-xl border border-input bg-background px-4 py-3 text-sm focus:outline-none focus:ring-2 focus:ring-primary"
                placeholder={`Ask ${selected ? "@" + selected : ""}...`}
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyDown={(e) => e.key === "Enter" && handleSend()}
              />
              <Button size="icon" onClick={handleSend} className="rounded-xl">
                <Send className="w-5 h-5" />
              </Button>
            </div>
          </div>
        </div>
      </main>
    </div>
  )
}
