/**
 * AuthZen - Agent Authentication Protocol
 * https://github.com/authzen/authzen
 * 
 * Authentication for AI agents with credentials and permissions
 */

export interface AuthZenCredential {
  type: "api_key" | "bearer" | "jwt" | "oauth2"
  token: string
  expires_at?: string
}

export interface AuthZenScope {
  resource: string
  actions: string[]
}

export interface AuthZenPrincipal {
  id: string
  type: "agent" | "user" | "service"
  name: string
  scopes: AuthZenScope[]
}

export interface AuthZenPolicy {
  id: string
  principals: string[]
  resources: string[]
  actions: string[]
  effect: "allow" | "deny"
}

export interface AuthZenRequest {
  principalId: string
  action: string
  resource: string
}

export interface AuthZenResponse {
  allowed: boolean
  reason?: string
  expires_at?: string
}

// AuthZen token builder
export function createAuthZenToken(
  principal: AuthZenPrincipal,
  scopes: AuthZenScope[],
  expiresIn: number = 3600
): AuthZenCredential {
  const now = Math.floor(Date.now() / 1000)
  return {
    type: "jwt",
    token: `eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.${btoa(JSON.stringify({ principal, scopes }))}`,
    expires_at: new Date((now + expiresIn) * 1000).toISOString(),
  }
}

// Check if action is allowed
export function authorize(
  request: AuthZenRequest,
  policies: AuthZenPolicy[]
): AuthZenResponse {
  const policy = policies.find(p => 
    p.principals.includes(request.principalId) &&
    p.resources.includes(request.resource)
  )
  
  if (!policy) {
    return { allowed: false, reason: "No matching policy" }
  }
  
  if (!policy.actions.includes(request.action)) {
    return { allowed: false, reason: "Action not permitted" }
  }
  
  return { allowed: policy.effect === "allow" }
}

// Default policies for copilot-hub agents
export function getDefaultPolicies(): AuthZenPolicy[] {
  return [
    {
      id: "admin-policy",
      principals: ["copilot-hub:admin"],
      resources: ["*"],
      actions: ["*"],
      effect: "allow",
    },
    {
      id: "user-policy",
      principals: ["copilot-hub:user"],
      resources: ["memory:*", "chat:*"],
      actions: ["read", "write"],
      effect: "allow",
    },
    {
      id: "readonly-policy",
      principals: ["copilot-hub:guest"],
      resources: ["agents", "skills", "tools"],
      actions: ["read"],
      effect: "allow",
    },
  ]
}

// Agent authentication
export function authenticateAgent(
  apiKey: string,
  validKeys: string[]
): AuthZenPrincipal | null {
  if (!validKeys.includes(apiKey)) {
    return null
  }
  
  return {
    id: "copilot-hub:agent",
    type: "agent",
    name: "CopilotHub Agent",
    scopes: [
      { resource: "chat", actions: ["read", "write"] },
      { resource: "memory", actions: ["read", "write"] },
    ],
  }
}
