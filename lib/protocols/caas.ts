/**
 * CaaS - Communication as a Service
 * Agent messaging and event streaming
 */

export interface CaaSMessage {
  id: string
  from: string
  to: string
  content: string
  type: "text" | "tool" | "system"
  timestamp: string
}

export interface CaaSEvent {
  id: string
  event: string
  data: Record<string, unknown>
  timestamp: string
}

export interface CaaSChannel {
  id: string
  name: string
  participants: string[]
  type: "direct" | "group"
}

// Create message
export function createCaaSMessage(
  from: string,
  to: string,
  content: string,
  type: CaaSMessage["type"] = "text"
): CaaSMessage {
  return {
    id: `${Date.now()}-${Math.random().toString(36).slice(2)}`,
    from,
    to,
    content,
    type,
    timestamp: new Date().toISOString(),
  }
}

// Create event
export function createCaaSEvent(event: string, data: Record<string, unknown> = {}): CaaSEvent {
  return {
    id: `${Date.now()}-${Math.random().toString(36).slice(2)}`,
    event,
    data,
    timestamp: new Date().toISOString(),
  }
}

// Create channel
export function createCaaSChannel(name: string, participants: string[]): CaaSChannel {
  return {
    id: `channel-${Date.now()}`,
    name,
    participants,
    type: participants.length === 2 ? "direct" : "group",
  }
}

// CaaS channels
export function getDefaultChannels(): CaaSChannel[] {
  return [
    { id: "general", name: "General", participants: ["*"], type: "group" },
    { id: "code-review-channel", name: "Code Review", participants: ["copilot-hub:code-review"], type: "direct" },
    { id: "debug-channel", name: "Debug", participants: ["copilot-hub:debug"], type: "direct" },
  ]
}
