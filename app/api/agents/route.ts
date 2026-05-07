import { NextResponse } from "next/server"
import { AGENTS, AGENT_TIERS, canonicalId } from "@/lib/agents/types"

export async function GET() {
  // Add canonical IDs to response
  const agentsWithCanonical = AGENTS.map(agent => ({
    ...agent,
    canonicalId: canonicalId(agent.id),
  }))
  
  return NextResponse.json({
    agents: agentsWithCanonical,
    tiers: AGENT_TIERS,
    prefix: "copilot-hub",
  })
}
