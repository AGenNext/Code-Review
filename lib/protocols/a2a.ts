/**
 * A2A - Agent to Agent Protocol
 */

export interface A2AMessage {
  id: string
  type: "request" | "response" | "error"
  sender: string
  receiver: string
  content: string
  created_at: string
}

export interface A2AAgentCard {
  agent: string
  name: string
  description: string
  url: string
  version: string
  capabilities: string[]
  skills: string[]
}

export function createA2AMessage(sender: string, receiver: string, content: string): A2AMessage {
  return {
    id: `${Date.now()}-${Math.random().toString(36).slice(2)}`,
    type: "request",
    sender,
    receiver,
    content,
    created_at: new Date().toISOString(),
  }
}

export function getA2AAgents(): A2AAgentCard[] {
  return [
    { agent: "copilot-hub:code-review", name: "Code Review Agent", description: "Finds bugs", url: "/agents", version: "1.0", capabilities: ["code_analysis"], skills: ["code-review"] },
    { agent: "copilot-hub:docs", name: "Docs Agent", description: "Writes docs", url: "/agents", version: "1.0", capabilities: ["generate_docs"], skills: ["docs"] },
    { agent: "copilot-hub:refactor", name: "Refactor Agent", description: "Improves code", url: "/agents", version: "1.0", capabilities: ["code_refactor"], skills: ["refactor"] },
    { agent: "copilot-hub:test", name: "Test Agent", description: "Writes tests", url: "/agents", version: "1.0", capabilities: ["write_tests"], skills: ["test"] },
    { agent: "copilot-hub:debug", name: "Debug Agent", description: "Fixes bugs", url: "/agents", version: "1.0", capabilities: ["debug_code"], skills: ["debug"] },
  ]
}
