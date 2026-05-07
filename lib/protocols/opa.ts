/**
 * OPA - Open Agent Protocol
 * Standard interface for agent communication
 */

export interface OPARequest {
  method: string
  params: {
    agent?: string
    message?: string
    sessionId?: string
  }
}

export interface OPAResponse {
  result?: { agent: string; response: string; sessionId: string }
  error?: { code: string; message: string }
}

export interface OPAgent {
  agent: string
  name: string
  capabilities: string[]
  protocol_version: string
}

export function createOPACall(method: string, params: OPARequest["params"]): OPARequest {
  return { method, params }
}

export function buildOPAResponse(result: OPAResponse["result"]): OPAResponse {
  return result ? { result } : { error: { code: "-32600", message: "Invalid Request" } }
}

export function getOPAAgents(): OPAgent[] {
  return [
    { agent: "copilot-hub:code-review", name: "Code Review", capabilities: ["code_analysis"], protocol_version: "1.0" },
    { agent: "copilot-hub:docs", name: "Docs", capabilities: ["generate_docs"], protocol_version: "1.0" },
    { agent: "copilot-hub:refactor", name: "Refactor", capabilities: ["code_refactor"], protocol_version: "1.0" },
    { agent: "copilot-hub:test", name: "Test", capabilities: ["write_tests"], protocol_version: "1.0" },
    { agent: "copilot-hub:debug", name: "Debug", capabilities: ["debug_code"], protocol_version: "1.0" },
  ]
}
