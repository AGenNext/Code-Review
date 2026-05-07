import { Bot } from "lucide-react"
import Link from "next/link"

export default function Home() {
  return (
    <div className="min-h-screen bg-background flex items-center justify-center">
      <div className="text-center">
        <Bot className="w-16 h-16 mx-auto mb-4 text-primary" />
        <h1 className="text-4xl font-bold mb-2">GitHub Copilot Extension</h1>
        <p className="text-muted-foreground mb-6">Custom agents for code review, documentation, testing, and more</p>
        <Link 
          href="/agents"
          className="inline-flex items-center justify-center rounded-md text-sm font-medium bg-primary text-primary-foreground hover:bg-primary/90 h-10 px-4 py-2"
        >
          Open Chat
        </Link>
      </div>
    </div>
  )
}
