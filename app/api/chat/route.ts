import { NextResponse } from "next/server"
import { CAI, createConversation, addMessage, CAIPrompt } from "@/lib/cai/conversation"

const conversations: Map<string, { agentId: string; messages: CAI[] }> = new Map()

export async function POST(request: Request) {
  const { action, agentId, message, conversationId } = await request.json()
  
  switch (action) {
    case "create": {
      const conv = createConversation(agentId)
      conversations.set(conv.id, { agentId, messages: [] })
      return NextResponse.json({ conversationId: conv.id })
    }
    
    case "send": {
      let conv = conversations.get(conversationId)
      if (!conv) {
        conv = createConversation(agentId)
        conversations.set(conversationId, conv)
      }
      
      // Add user message
      const userMsg: CAI = {
        role: "user",
        content: message,
        timestamp: new Date().toISOString(),
      }
      conv = addMessage(conv as any, userMsg)
      
      // Simulate response
      const assistantMsg: CAI = {
        role: "assistant",
        content: `Processing your request: ${message}`,
        timestamp: new Date().toISOString(),
      }
      conv = addMessage(conv as any, assistantMsg)
      conversations.set(conversationId, conv)
      
      return NextResponse.json({ message: assistantMsg })
    }
    
    case "history": {
      const conv = conversations.get(conversationId)
      return NextResponse.json({ messages: conv?.messages || [] })
    }
    
    default:
      return NextResponse.json({ error: "Unknown action" }, { status: 400 })
  }
}
