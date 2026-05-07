"use client"

import { useEffect, useState } from "react"
import { Button } from "@/components/ui/button"
import { Bot, Star, ArrowRight, Sparkles } from "lucide-react"
import Link from "next/link"

type Skill = { id: string; name: string; description: string; tools: string[] }

export default function SkillsPage() {
  const [skills, setSkills] = useState<Skill[]>([])
  const [ratings, setRatings] = useState<Record<string, { average: number; count: number }>>({})

  useEffect(() => {
    fetch("/api/skills").then(r => r.json()).then(setSkills)
    fetch("/api/ratings").then(r => r.json()).then(setRatings)
  }, [])

  return (
    <div className="min-h-screen bg-background">
      <header className="sticky top-0 z-50 bg-background/80 backdrop-blur border-b border-border">
        <div className="container px-4 py-4">
          <div className="flex items-center gap-3">
            <div className="p-2 rounded-lg bg-primary/10">
              <Sparkles className="w-6 h-6 text-primary" />
            </div>
            <h1 className="text-xl font-bold">Skills</h1>
          </div>
        </div>
      </header>

      <main className="container px-4 py-8">
        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-4">
          {skills.map((skill, i) => (
            <div key={skill.id} className={`group relative p-6 rounded-2xl bg-card border border-border hover:border-primary/50 transition-all animate-slide-up delay-${i * 100}`}>
              <div className="flex items-start justify-between mb-3">
                <div className="p-2 rounded-lg bg-primary/10">
                  <Bot className={`w-5 h-5 ${
                    skill.id === "code-review" ? "text-yellow-400" :
                    skill.id === "docs" ? "text-blue-400" :
                    skill.id === "refactor" ? "text-purple-400" :
                    skill.id === "test" ? "text-green-400" : "text-red-400"
                  }`} />
                </div>
                {ratings[skill.id] && (
                  <div className="flex items-center gap-1 text-sm">
                    <Star className="w-4 h-4 fill-yellow-400 text-yellow-400" />
                    {ratings[skill.id].average.toFixed(1)}
                  </div>
                )}
              </div>
              
              <h3 className="text-lg font-semibold mb-2">@{skill.id}</h3>
              <p className="text-sm text-muted-foreground mb-4">{skill.description}</p>
              
              <div className="flex flex-wrap gap-2 mb-4">
                {skill.tools.map((tool) => (
                  <span key={tool} className="text-xs bg-secondary px-3 py-1 rounded-full">
                    {tool}
                  </span>
                ))}
              </div>
              
              <Link href={`/agents?skill=${skill.id}`}>
                <Button size="sm" className="w-full gap-2 group-hover:bg-primary group-hover:text-primary-foreground transition-colors">
                  Use <ArrowRight className="w-4 h-4" />
                </Button>
              </Link>
            </div>
          ))}
        </div>
      </main>
    </div>
  )
}
