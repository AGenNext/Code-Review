"use client"

import { useEffect, useState } from "react"
import { Button } from "@/components/ui/button"
import { Bot, Star, ArrowRight } from "lucide-react"
import Link from "next/link"

type Skill = {
  id: string
  name: string
  description: string
  tools: string[]
}

export default function SkillsPage() {
  const [skills, setSkills] = useState<Skill[]>([])
  const [ratings, setRatings] = useState<Record<string, { average: number; count: number }>>({})

  useEffect(() => {
    fetch("/api/skills").then(r => r.json()).then(setSkills)
    fetch("/api/ratings").then(r => r.json()).then(setRatings)
  }, [])

  return (
    <div className="min-h-screen bg-background">
      <header className="border-b bg-card sticky top-0 z-50">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center gap-2">
            <Bot className="w-6 h-6 text-primary" />
            <h1 className="text-xl font-bold">Custom Skills</h1>
          </div>
        </div>
      </header>

      <main className="container mx-auto px-4 py-6">
        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-4">
          {skills.map((skill) => (
            <div key={skill.id} className="border rounded-lg p-4 bg-card hover:shadow-md transition-shadow">
              <div className="flex items-start justify-between mb-2">
                <h2 className="text-lg font-semibold">@{skill.id}</h2>
                {ratings[skill.id] && (
                  <div className="flex items-center gap-1 text-sm">
                    <Star className="w-4 h-4 fill-yellow-400 text-yellow-400" />
                    {ratings[skill.id].average.toFixed(1)}
                  </div>
                )}
              </div>
              <p className="text-muted-foreground text-sm mb-4">{skill.description}</p>
              
              <div className="flex flex-wrap gap-1 mb-4">
                {skill.tools.map((tool) => (
                  <span key={tool} className="text-xs bg-secondary px-2 py-1 rounded">
                    {tool}
                  </span>
                ))}
              </div>
              
              <Link href={`/agents?skill=${skill.id}`}>
                <Button size="sm" className="w-full gap-2">
                  Use Skill <ArrowRight className="w-4 h-4" />
                </Button>
              </Link>
            </div>
          ))}
        </div>
      </main>
    </div>
  )
}
