import { useState } from "react"
import { Button } from "./components/ui/button"
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "./components/ui/card"
import { customAgents } from "./agents/index"

function App() {
  const [selectedAgent, setSelectedAgent] = useState<string | null>(null)
  const [prompt, setPrompt] = useState("")
  const [response, setResponse] = useState("")

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!selectedAgent) return
    setResponse(`Invoking @${selectedAgent} agent...\n\nPrompt: ${prompt}`)
  }

  return (
    <div className="min-h-screen bg-background p-8">
      <div className="container max-w-4xl mx-auto">
        <div className="mb-8">
          <h1 className="text-3xl font-bold">GitHub Copilot Extension</h1>
          <p className="text-muted-foreground mt-2">
            Custom agents for code review, documentation, testing, and more.
          </p>
        </div>

        <div className="grid gap-6">
          {/* Agent Selection */}
          <Card>
            <CardHeader>
              <CardTitle>Select Agent</CardTitle>
              <CardDescription>
                Choose a specialized agent for your task
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="flex flex-wrap gap-2">
                {customAgents.map((agent) => (
                  <Button
                    key={agent.name}
                    variant={selectedAgent === agent.name ? "default" : "outline"}
                    size="sm"
                    onClick={() => setSelectedAgent(agent.name)}
                  >
                    @{agent.name}
                  </Button>
                ))}
              </div>
            </CardContent>
          </Card>

          {/* Prompt Input */}
          <Card>
            <CardHeader>
              <CardTitle>Enter Prompt</CardTitle>
              <CardDescription>
                Describe what you want the agent to do
              </CardDescription>
            </CardHeader>
            <CardContent>
              <textarea
                className="w-full min-h-[120px] rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50"
                placeholder="Enter your prompt here..."
                value={prompt}
                onChange={(e) => setPrompt(e.target.value)}
              />
            </CardContent>
            <CardFooter>
              <Button onClick={handleSubmit} disabled={!selectedAgent || !prompt}>
                Run Agent
              </Button>
            </CardFooter>
          </Card>

          {/* Response */}
          {response && (
            <Card>
              <CardHeader>
                <CardTitle>Response</CardTitle>
              </CardHeader>
              <CardContent>
                <pre className="whitespace-pre-wrap text-sm">{response}</pre>
              </CardContent>
            </Card>
          )}
        </div>
      </div>
    </div>
  )
}

export default App
