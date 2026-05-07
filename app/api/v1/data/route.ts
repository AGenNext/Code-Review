import { NextResponse } from "next/server"
import { OPAInput, evalResult } from "@/lib/protocols/opa"

// OPA Data API - v1/data endpoint
export async function POST(request: Request) {
  const body = await request.json()
  const input: OPAInput = body
  
  if (!input?.input) {
    return NextResponse.json({ 
      decision: "deny",
      error: "invalid input" 
    }, { status: 400 })
  }
  
  const result = evalResult(input)
  return NextResponse.json(result)
}

export async function GET() {
  // Return policy info
  return NextResponse.json({
    open_policy_agent: {
      version: "0.61.0",
      bundled_packages: ["policy"],
      decision_logs: true,
    }
  })
}
