import Link from "next/link"
import { Bot, Sparkles, Zap, Shield, ArrowRight, Star } from "lucide-react"

export default function Home() {
  return (
    <div className="min-h-screen bg-background">
      {/* Hero */}
      <section className="relative min-h-[90vh] flex items-center justify-center overflow-hidden">
        <div className="absolute inset-0 opacity-20">
          <div className="absolute top-1/4 left-1/4 w-96 h-96 bg-primary/30 rounded-full blur-[128px] animate-float" />
          <div className="absolute bottom-1/4 right-1/4 w-96 h-96 bg-accent/20 rounded-full blur-[128px] animate-float delay-200" />
        </div>
        
        <div className="container relative z-10 px-4">
          <div className="text-center space-y-6 animate-slide-up">
            <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-secondary border border-primary/30">
              <Sparkles className="w-4 h-4 text-primary" />
              <span className="text-sm">AI-Powered Development</span>
            </div>
            
            <h1 className="text-6xl md:text-8xl font-bold tracking-tight">
              <span className="text-primary">Copilot</span>
              <span className="text-foreground">Hub</span>
            </h1>
            
            <p className="text-xl text-muted-foreground max-w-2xl mx-auto">
              Five specialized agents. Infinite possibilities. 
              Code review, documentation, refactoring, testing, and debugging — elevated.
            </p>
            
            <div className="flex justify-center gap-4 pt-4">
              <Link href="/agents">
                <button className="group relative px-8 py-4 bg-primary text-primary-foreground rounded-lg font-semibold overflow-hidden">
                  <span className="relative z-10 flex items-center gap-2">
                    Launch <ArrowRight className="w-5 h-5 group-hover:translate-x-1 transition-transform" />
                  </span>
                  <div className="absolute inset-0 bg-primary/80 animate-glow" />
                </button>
              </Link>
              <Link href="/skills">
                <button className="px-8 py-4 border border-border rounded-lg font-semibold hover:bg-secondary transition-colors">
                  Explore Skills
                </button>
              </Link>
            </div>
          </div>
        </div>
      </section>

      {/* Features */}
      <section className="py-24 border-t border-border">
        <div className="container px-4">
          <h2 className="text-3xl font-bold text-center mb-16">Five Agents, One Hub</h2>
          
          <div className="grid md:grid-cols-3 gap-6">
            {[
              { icon: Zap, name: "Code Review", desc: "Find bugs before they find you", color: "text-yellow-400" },
              { icon: Shield, name: "Security", desc: "Enterprise-grade protection", color: "text-green-400" },
              { icon: Star, name: "Quality", desc: "Best practices enforced", color: "text-purple-400" },
            ].map((item, i) => (
              <div key={i} className="p-6 rounded-xl bg-card border border-border hover:border-primary/50 transition-colors">
                <item.icon className={`w-10 h-10 ${item.color} mb-4`} />
                <h3 className="text-xl font-semibold mb-2">{item.name}</h3>
                <p className="text-muted-foreground">{item.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="py-8 border-t border-border">
        <div className="container px-4 text-center text-muted-foreground text-sm">
          <p>© 2024 CopilotHub. Built with GitHub Copilot SDK.</p>
        </div>
      </footer>
    </div>
  )
}
