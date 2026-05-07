/**
 * OPA - Open Policy Agent
 * Agent access control and authorization
 */

export interface OPAPolicy {
  id: string
  name: string
  effect: "allow" | "deny"
  principals: string[]    // Who (agents, users)
  resources: string[]   // What (endpoints, data)
  actions: string[]    // How (GET, POST, etc)
  conditions?: Record<string, unknown>
}

export interface OPARequest {
  principal: string
  action: string
  resource: string
}

export interface OPAResponse {
  decision: "allow" | "deny"
  policies: string[]
  reason?: string
}

// Default policies
export const getDefaultPolicies(): OPAPolicy[] => [
  {
    id: "admin-full",
    name: "Full admin access",
    effect: "allow",
    principals: ["copilot-hub:admin"],
    resources: ["*"],
    actions: ["*"],
  },
  {
    id: "user-chat",
    name: "Chat access",
    effect: "allow",
    principals: ["copilot-hub:user"],
    resources: ["/api/chat", "/api/agents"],
    actions: ["GET", "POST"],
  },
  {
    id: "readonly",
    name: "Read-only access",
    effect: "allow",
    principals: ["*"],
    resources: ["/api/skills", "/api/tools", "/api/agents"],
    actions: ["GET"],
  },
  {
    id: "deny-destructive",
    name: "Deny delete",
    effect: "deny",
    principals: ["*"],
    resources: ["*"],
    actions: ["DELETE"],
  },
]

// Evaluate request
export function evaluate(policies: OPAPolicy[], request: OPARequest): OPAResponse {
  const matched: string[] = []
  
  for (const policy of policies) {
    const principalMatch = policy.principals.includes(request.principal) || policy.principals.includes("*")
    const resourceMatch = policy.resources.includes(request.resource) || policy.resources.includes("*")
    const actionMatch = policy.actions.includes(request.action) || policy.actions.includes("*")
    
    if (principalMatch && resourceMatch && actionMatch) {
      matched.push(policy.id)
      
      if (policy.effect === "allow") {
        return { decision: "allow", policies: matched }
      }
    }
  }
  
  return { 
    decision: matched.length > 0 ? "deny" : "allow", 
    policies: matched,
    reason: matched.length > 0 ? "Matched deny policy" : "No matching allow policy"
  }
}

// Create policy
export function createPolicy(
  name: string,
  effect: OPAPolicy["effect"],
  principals: string[],
  resources: string[],
  actions: string[]
): OPAPolicy {
  return {
    id: `policy-${Date.now()}`,
    name,
    effect,
    principals,
    resources,
    actions,
  }
}
