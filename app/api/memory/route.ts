import { NextResponse } from "next/server"

const memoryStore: Record<string, { role: string; content: string; timestamp: string }[]> = {
  default: [],
}

export async function GET() {
  return NextResponse.json(memoryStore)
}

export async function POST(request: Request) {
  const body = await request.json()
  const { messages, sessionId = "default" } = body
  
  if (!memoryStore[sessionId]) {
    memoryStore[sessionId] = []
  }
  
  messages.forEach((msg: { role: string; content: string }) => {
    memoryStore[sessionId].push({
      role: msg.role,
      content: msg.content,
      timestamp: new Date().toISOString(),
    })
  })
  
  // Keep last 50 messages
  if (memoryStore[sessionId].length > 50) {
    memoryStore[sessionId] = memoryStore[sessionId].slice(-50)
  }
  
  return NextResponse.json({ success: true, count: memoryStore[sessionId].length })
}
