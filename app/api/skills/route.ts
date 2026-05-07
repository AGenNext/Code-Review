import { NextResponse } from "next/server"

const skills = [
  { id: "code-review", name: "Code Review", description: "Review code for bugs, security issues, and best practices", tools: ["read_file", "search_code"] },
  { id: "docs", name: "Documentation", description: "Generate and improve documentation", tools: ["read_file", "write_file"] },
  { id: "refactor", name: "Refactoring", description: "Refactor code for better design", tools: ["read_file", "write_file", "search_code"] },
  { id: "test", name: "Testing", description: "Write comprehensive tests", tools: ["read_file", "write_file", "execute_tests"] },
  { id: "debug", name: "Debugging", description: "Debug and fix issues", tools: ["read_file", "search_code", "execute_code"] },
]

export async function GET() {
  return NextResponse.json(skills)
}
