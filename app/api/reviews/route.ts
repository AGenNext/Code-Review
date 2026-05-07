import { NextResponse } from "next/server"

const reviews = [
  { id: 1, skill: "code-review", rating: 5, comment: "Excellent for finding bugs!", author: "Dev1", date: "2024-01-15" },
  { id: 2, skill: "docs", rating: 4, comment: "Great documentation generator", author: "Dev2", date: "2024-01-14" },
  { id: 3, skill: "refactor", rating: 5, comment: "Really helped clean up my code", author: "Dev3", date: "2024-01-13" },
  { id: 4, skill: "test", rating: 4, comment: "Wrote good tests quickly", author: "Dev4", date: "2024-01-12" },
  { id: 5, skill: "debug", rating: 5, comment: "Found the bug in minutes!", author: "Dev5", date: "2024-01-11" },
]

export async function GET() {
  return NextResponse.json(reviews)
}
