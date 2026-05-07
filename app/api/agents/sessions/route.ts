import { NextResponse } from "next/server"

const sessions: Record<string, { agentId: string; messages: { role: string; content: string; timestamp: string }[] }> = {}

export async function GET() {
  return NextResponse.json(sessions)
}

export async function POST(request: Request) {
  const body = await request.json()
  const { sessionId, agentId, messages } = body
  
  if (!sessions[sessionId]) {
    sessions[sessionId] = { agentId, messages: [] }
  }
  
  if (messages) {
    sessions[sessionId].messages.push(...messages.map((m: { role: string; content: string }) => ({
      ...m,
      timestamp: new Date().toISOString(),
    })))
  }
  
  return NextResponse.json({ success: true, session: sessions[sessionId] })
}
