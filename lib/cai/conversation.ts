/**
 * CAI - Conversational AI
 * Context-aware conversations with memory
 */

export interface CAIConversation {
  id: string
  agentId: string
  messages: CAI[]
  context: Record<string, unknown>
  createdAt: string
  updatedAt: string
}

export interface CAI {
  role: "user" | "assistant" | "system"
  content: string
  tool_calls?: {
    id: string
    name: string
    arguments: Record<string, unknown>
  }[]
  tool_results?: {
    tool: string
    result: unknown
  }[]
  timestamp: string
  tokens?: number
}

export interface CAIPrompt {
  messages: CAI[]
  system?: string
  temperature?: number
  max_tokens?: number
  stream?: boolean
}

export interface CAIResponse {
  message: CAI
  usage?: {
    prompt_tokens: number
    completion_tokens: number
    total_tokens: number
  }
}

// Build conversation context
export function buildContext(history: CAI[], maxTokens: number = 4000): string {
  let context = ""
  for (let i = history.length - 1; i >= 0; i--) {
    const msg = history[i]
    const tokens = msg.content.split(" ").length * 1.3
    if (context.length + tokens > maxTokens) break
    context = `${msg.role}: ${msg.content}\n${context}`
  }
  return context
}

// Create a new conversation
export function createConversation(agentId: string): CAIConversation {
  return {
    id: `conv-${Date.now()}`,
    agentId,
    messages: [],
    context: {},
    createdAt: new Date().toISOString(),
    updatedAt: new Date().toISOString(),
  }
}

// Add message to conversation
export function addMessage(conversation: CAIConversation, message: CAI): CAIConversation {
  return {
    ...conversation,
    messages: [...conversation.messages, message],
    updatedAt: new Date().toISOString(),
  }
}

// Summarize conversation
export function summarizeConversation(messages: CAI[]): string {
  const userMessages = messages.filter(m => m.role === "user")
  const assistantMessages = messages.filter(m => m.role === "assistant")
  
  return `Conversation: ${userMessages.length} user messages, ${assistantMessages.length} assistant responses`
}
