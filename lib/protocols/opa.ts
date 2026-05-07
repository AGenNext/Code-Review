/**
 * OPA - Open Policy Agent
 * https://openpolicyagent.org
 * 
 * General-purpose policy engine with Rego language
 * Policy decisions via /v1/data API
 */

export type OPADecision = "allow" | "deny"

export interface OPAInput {
  input: {
    principal?: string
    action: string
    resource: string
    method?: string
    path?: string
  }
}

export interface OPAResult {
  result: {
    decision: OPADecision
    reason?: string
  }
}

// Rego policy example (uses Rego language in production)
// This is a simplified JS version

export const REGO_POLICIES = {
  allow_admin_all: {
    modules: {
      policy: `
package policy

default allow = false

allow {
  input.principal == "admin"
}

allow {
  input.action == "read"
}
      `
    }
  }
}

// Default allow rule
export function defaultDecision(): OPADecision {
  return "deny"
}

// Check if input matches policy
export function evalPolicy(input: OPAInput): OPADecision {
  // Default deny
  const { principal, action } = input.input
  
  // Allow if principal is admin
  if (principal === "admin") return "allow"
  
  // Allow read actions by default
  if (action === "read") return "allow"
  
  // Default deny
  return "deny"
}

// Server response format
export function evalResult(input: OPAInput): OPAResult {
  return {
    result: {
      decision: evalPolicy(input),
    }
  }
}
