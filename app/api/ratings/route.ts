import { NextResponse } from "next/server"

const ratings = {
  "code-review": { average: 4.8, count: 156 },
  "docs": { average: 4.5, count: 98 },
  "refactor": { average: 4.9, count: 203 },
  "test": { average: 4.6, count: 142 },
  "debug": { average: 4.7, count: 89 },
}

export async function GET() {
  return NextResponse.json(ratings)
}
