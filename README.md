# GitHub Copilot SDK Extension

A custom extension for GitHub Copilot that provides specialized agents for different development tasks.

## Features

- **Code Review Agent** - Expert at reviewing code for bugs, security issues, and best practices
- **Documentation Agent** - Specialized in creating and improving code documentation
- **Refactoring Agent** - Expert at code refactoring and improvements
- **Testing Agent** - Specialized in writing comprehensive tests
- **Debugging Agent** - Expert at debugging and solving issues

## Prerequisites

- Node.js 18 or later
- GitHub Copilot CLI installed and authenticated

## Installation

```bash
npm install
```

## Usage

### Run the Demo

```bash
npm run dev
```

This will start the Copilot client and demonstrate all custom agents with example prompts.

### Programmatic Usage

```typescript
import { CopilotClient } from "@github/copilot-sdk";
import { customAgents } from "./agents/index.js";

const client = new CopilotClient();
await client.start();

const session = await client.createSession({
  model: "gpt-4.1",
  customAgents: customAgents,
});

const response = await session.sendAndWait({
  prompt: "@code-review Review this code for bugs: ...",
});

console.log(response?.data.content);

await client.stop();
```

## Custom Agents

### Invoking Agents

Use the `@agent-name` prefix to invoke a specific agent:

```bash
@code-review Review my code for security issues
@docs Write documentation for this function
@refactor Improve the design of this class
@test Generate tests for this module
@debug Fix this error
```

### Agent Configuration

Each agent can be configured with:
- `name` - Unique agent identifier
- `displayName` - Display name for UI
- `description` - What the agent does
- `tools` - List of allowed tools
- `prompt` - System prompt
- `mcpServers` - MCP servers to attach
- `infer` - Whether to auto-select this agent

## MCP Servers

The extension supports Model Context Protocol (MCP) servers:

```typescript
const session = await client.createSession({
  model: "gpt-4.1",
  mcpServers: {
    filesystem: {
      command: "npx",
      args: ["-y", "@modelcontextprotocol/server-filesystem", "/tmp"],
    },
  },
});
```

## Custom Tools

Define custom tools that agents can use:

```typescript
const tools = [
  {
    name: "my_tool",
    description: "What the tool does",
    inputSchema: {
      type: "object",
      properties: {
        param: { type: "string" },
      },
      required: ["param"],
    },
  },
];
```

## Events

Listen to session events:

```typescript
session.on("assistant.message", (event) => {
  console.log(event.data.content);
});

session.on("tool.use", (event) => {
  console.log(`Using tool: ${event.data.tool}`);
});

session.on("session.idle", () => {
  console.log("Session completed");
});
```

## Architecture

```
src/
├── index.ts       # Main application entry point
├── agents/      # Custom agent definitions
├── tools/       # Custom tool definitions
└── mcp/        # MCP server configurations
```

## License

MIT