export type AgentCapability = "code_review" | "docs" | "refactor" | "test" | "debug" | "security" | "performance" | "design"

export type AgentTier = "free" | "pro" | "enterprise"

export interface Agent {
  id: string
  name: string
  description: string
  icon: string
  color: string
  capabilities: AgentCapability[]
  tier: AgentTier
  systemPrompt: string
  tools: string[]
}

export interface AgentSession {
  agentId: string
  sessionId: string
  messages: { role: string; content: string; timestamp: string }[]
  context: string[]
  createdAt: string
}

export const AGENT_TIERS: Record<AgentTier, { name: string; price: string; features: string[] }> = {
  free: { name: "Free", price: "$0", features: ["Basic chat", "5 messages/day"] },
  pro: { name: "Pro", price: "$9/mo", features: ["Unlimited chat", "Memory", "All agents"] },
  enterprise: { name: "Enterprise", price: "$49/mo", features: ["API access", "Custom agents", "Priority"] },
}

export const AGENTS: Agent[] = [
  {
    id: "code-review",
    name: "Code Review",
    description: "Find bugs, security issues, and best practices",
    icon: "🔍",
    color: "text-yellow-400",
    capabilities: ["code_review", "security"],
    tier: "free",
    systemPrompt: "You are an expert code reviewer. Analyze code for bugs, security vulnerabilities, and best practices.",
    tools: ["read_file", "search_code", "list_files"],
  },
  {
    id: "docs",
    name: "Documentation",
    description: "Generate API docs, READMEs, and comments",
    icon: "📖",
    color: "text-blue-400",
    capabilities: ["docs"],
    tier: "free",
    systemPrompt: "You are a technical writer. Create clear, comprehensive documentation.",
    tools: ["read_file", "write_file"],
  },
  {
    id: "refactor",
    name: "Refactor",
    description: "Improve code design and structure",
    icon: "🔨",
    color: "text-purple-400",
    capabilities: ["refactor", "design"],
    tier: "free",
    systemPrompt: "You are an expert at refactoring. Improve code structure without changing behavior.",
    tools: ["read_file", "write_file", "search_code"],
  },
  {
    id: "test",
    name: "Test",
    description: "Write unit tests, integration tests, and mocks",
    icon: "🧪",
    color: "text-green-400",
    capabilities: ["test"],
    tier: "free",
    systemPrompt: "You are a testing expert. Write comprehensive tests with good coverage.",
    tools: ["read_file", "write_file", "execute_tests"],
  },
  {
    id: "debug",
    name: "Debug",
    description: "Debug errors and fix issues",
    icon: "🐛",
    color: "text-red-400",
    capabilities: ["debug", "performance"],
    tier: "free",
    systemPrompt: "You are a debugging expert. Find root causes and fix bugs.",
    tools: ["read_file", "search_code", "execute_code"],
  },
  {
    id: "security",
    name: "Security",
    description: "Security audit and vulnerability scanning",
    icon: "🛡️",
    color: "text-orange-400",
    capabilities: ["security"],
    tier: "pro",
    systemPrompt: "You are a security expert. Find vulnerabilities and suggest fixes.",
    tools: ["read_file", "search_code", "execute_code"],
  },
  {
    id: "performance",
    name: "Performance",
    description: "Optimize code performance and bottlenecks",
    icon: "⚡",
    color: "text-cyan-400",
    capabilities: ["performance"],
    tier: "pro",
    systemPrompt: "You are a performance expert. Optimize code for speed and efficiency.",
    tools: ["read_file", "search_code", "execute_code", "profile"],
  },
  {
    id: "architect",
    name: "Architect",
    description: "System design and architecture decisions",
    icon: "🏗️",
    color: "text-pink-400",
    capabilities: ["design"],
    tier: "enterprise",
    systemPrompt: "You are a software architect. Design scalable systems.",
    tools: ["read_file", "write_file", "search_code"],
  },
]
