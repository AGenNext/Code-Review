import { NextResponse } from "next/server"
import { AGENTS, AGENT_TIERS } from "@/lib/agents/types"

export async function GET() {
  return NextResponse.json({
    agents: AGENTS,
    tiers: AGENT_TIERS,
  })
}
