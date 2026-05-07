"use client"

import { useState } from "react"
import { Button } from "@/components/ui/button"
import { Bot, Send, Code2, BookOpen, Hammer, FlaskConical, Bug, MessageCircle } from "lucide-react"

type Message = {
  role: "user" | "assistant"
  content: string
  agent?: string
}

const agents = [
  { name: "code-review", icon: Code2, description: "Review code for bugs and issues" },
  { name: "docs", icon: BookOpen, description: "Create documentation" },
  { name: "refactor", icon: Hammer, description: "Refactor and improve code" },
  { name: "test", icon: FlaskConical, description: "Write tests" },
  { name: "debug", icon: Bug, description: "Debug and fix issues" },
]

export default function AgentsPage() {
  const [selectedAgent, setSelectedAgent] = useState<string | null>(null)
  const [input, setInput] = useState("")
  const [messages, setMessages] = useState<Message[]>([
    { role: "assistant", content: "Hi! I'm your GitHub Copilot assistant. Select an agent and ask me anything! 🚀" }
  ])

  const handleSend = () => {
    if (!input.trim()) return

    const userMessage: Message = { role: "user", content: input }
    setMessages(prev => [...prev, userMessage])

    const agentPrefix = selectedAgent ? `@${selectedAgent} ` : ""
    setTimeout(() => {
      setMessages(prev => [...prev, {
        role: "assistant",
        content: `Processing: "${agentPrefix}${input}"\n\nInvoking ${selectedAgent || "default"} agent...`,
        agent: selectedAgent || undefined
      }])
    }, 500)

    setInput("")
  }

  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <header className="border-b bg-card sticky top-0 z-50">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center gap-2">
            <Bot className="w-6 h-6 text-primary" />
            <h1 className="text-xl font-bold">GitHub Copilot Extension</h1>
          </div>
        </div>
      </header>

      <main className="container mx-auto px-4 py-6">
        {/* Agent Pills */}
        <div className="mb-6">
          <p className="text-sm text-muted-foreground mb-3">Select agent:</p>
          <div className="flex flex-wrap gap-2">
            {agents.map((agent) => (
              <Button
                key={agent.name}
                variant={selectedAgent === agent.name ? "default" : "outline"}
                size="sm"
                onClick={() => setSelectedAgent(agent.name)}
                className="gap-2"
              >
                <agent.icon className="w-4 h-4" />
                @{agent.name}
              </Button>
            ))}
          </div>
        </div>

        {/* Chat */}
        <div className="border rounded-lg bg-card">
          <div className="border-b p-4">
            <div className="flex items-center gap-2">
              <MessageCircle className="w-5 h-5" />
              <h2 className="font-semibold">Chat</h2>
            </div>
            <p className="text-sm text-muted-foreground">
              {selectedAgent ? `Using @${selectedAgent}` : "Using default agent"}
            </p>
          </div>

          {/* Messages */}
          <div className="p-4 space-y-4 min-h-[400px] max-h-[500px] overflow-y-auto">
            {messages.map((msg, idx) => (
              <div key={idx} className={`flex ${msg.role === "user" ? "justify-end" : "justify-start"}`}>
                <div className={`max-w-[80%] rounded-lg px-4 py-2 ${msg.role === "user" ? "bg-primary text-primary-foreground" : "bg-muted"}`}>
                  {msg.agent && <span className="text-xs text-muted-foreground block mb-1">@{msg.agent}</span>}
                  <p className="whitespace-pre-wrap">{msg.content}</p>
                </div>
              </div>
            ))}
          </div>

          {/* Input */}
          <div className="border-t p-4">
            <div className="flex gap-2">
              <input
                className="flex-1 rounded-md border border-input bg-background px-3 py-2 text-sm"
                placeholder={`Ask ${selectedAgent ? `@${selectedAgent} ` : ""}...`}
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyDown={(e) => e.key === "Enter" && handleSend()}
              />
              <Button onClick={handleSend} size="icon">
                <Send className="w-4 h-4" />
              </Button>
            </div>
          </div>
        </div>
      </main>
    </div>
  )
}
