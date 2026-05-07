/**
 * GitHub Copilot SDK Extension - Main Application Entry Point
 * 
 * This demonstrates how to use the Copilot SDK with custom agents
 * to handle different types of tasks.
 */

import { CopilotClient, defineTool, approveAll } from "@github/copilot-sdk";
import { customAgents } from "./agents/index.js";

/**
 * Custom tool example using defineTool helper
 */
const analyzeCodeTool = defineTool("analyze_code", {
  description: "Analyze code for bugs, security issues, and best practices",
  parameters: {
    type: "object",
    properties: {
      code: { type: "string", description: "The code to analyze" },
      focus: { 
        type: "string", 
        enum: ["bugs", "security", "performance", "style"],
        description: "What aspect to focus on"
      },
    },
    required: ["code"],
  },
  handler: async (args: { code: string; focus?: string }) => {
    return `Analyzed code with focus on ${args.focus || 'general issues'}: ${args.code}`;
  },
});

/**
 * Main application demonstrating custom agent usage
 */
async function main() {
  console.log("🤖 GitHub Copilot SDK Extension");
  console.log("=".repeat(40));

  // Create the Copilot client
  const client = new CopilotClient();
  
  try {
    // Start the client (this verifies Copilot CLI is installed)
    console.log("Starting Copilot client...");
    await client.start();
    console.log("✅ Client started successfully\n");

    // Create session with custom agents
    console.log("Creating session with custom agents...");
    const session = await client.createSession({
      model: "gpt-4.1",
      customAgents: customAgents,
      tools: [analyzeCodeTool],
      onPermissionRequest: approveAll,
      streaming: true,
    });

    // Listen for events
    session.on("assistant.message", (event) => {
      console.log("\n📝 Assistant message:");
      console.log(event.data.content);
    });

    session.on("assistant.message_delta", (event) => {
      process.stdout.write(event.data.deltaContent);
    });

    session.on("session.idle", () => {
      console.log("\n💤 Session idle");
    });

    // Example 1: Ask for code review directly
    console.log("\n--- Example 1: Direct Code Review ---");
    await session.sendAndWait({
      prompt: `@code-review Review this JavaScript function for bugs:

function factorial(n) {
  if (n <= 1) return 1;
  return n * factorial(n - 1);
}`,
    });

    // Example 2: Ask for documentation
    console.log("\n\n--- Example 2: Documentation Request ---");
    await session.sendAndWait({
      prompt: `@docs Write a JSDoc comment for this function:

function factorial(n) {
  if (n <= 1) return 1;
  return n * factorial(n - 1);
}`,
    });

    // Example 3: Ask for test generation
    console.log("\n\n--- Example 3: Test Generation ---");
    await session.sendAndWait({
      prompt: `@test Generate Jest tests for factorial function`,
    });

    // Example 4: Use default agent for general help
    console.log("\n\n--- Example 4: Default Agent ---");
    await session.sendAndWait({
      prompt: "Explain what the factorial function does",
    });

    console.log("\n" + "=".repeat(40));
    console.log("✅ All examples completed successfully!");

  } catch (error) {
    console.error("❌ Error:", error);
    throw error;
  } finally {
    // Clean up
    await client.stop();
    console.log("Client stopped");
  }
}

// Export for use as a module
export { main, customAgents };

// Run main if executed directly
if (import.meta.url === `file://${process.argv[1]}`) {
  main()
    .then(() => {
      console.log("\n✨ Extension demo completed");
      process.exit(0);
    })
    .catch((error) => {
      console.error("Fatal error:", error);
      process.exit(1);
    });
}