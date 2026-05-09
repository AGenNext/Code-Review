"""
Management Agent using LangGraph

A stateful agent for managing GitHub repositories, Docker deployments, and CI/CD workflows.
"""

import os
import json
import subprocess
from typing import TypedDict, Optional, List, Any
from datetime import datetime

# LangGraph imports
from langgraph.graph import StateGraph, END
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic

# Agent State
class AgentState(TypedDict):
    """The state of the agent."""
    messages: List[Any]
    current_task: Optional[str]
    task_history: List[dict]
    repo_info: Optional[dict]
    deployment_status: Optional[str]
    error: Optional[str]
    result: Optional[Any]


# Configuration
class Config:
    """Agent configuration."""
    # LLM Settings
    model = os.getenv("LLM_MODEL", "anthropic/claude-3-sonnet-20240229")
    api_key = os.getenv("LLM_API_KEY")
    base_url = os.getenv("LLM_BASE_URL")
    temperature = 0.7
    
    # GitHub Settings
    github_token = os.getenv("GITHUB_TOKEN")
    github_owner = os.getenv("GITHUB_OWNER")
    github_repo = os.getenv("GITHUB_REPO")
    
    # Docker Settings
    dockerregistry = os.getenv("DOCKER_REGISTRY", "ghcr.io")
    docker_username = os.getenv("DOCKER_USERNAME")
    
    # Workspace
    workspace = os.getenv("WORKSPACE", "/workspace/project")


# Initialize LLM
def get_llm() -> Any:
    """Initialize the language model."""
    if "anthropic" in Config.model.lower():
        return ChatAnthropic(
            model=Config.model,
            api_key=Config.api_key,
            temperature=Config.temperature,
        )
    return ChatOpenAI(
        model=Config.model,
        api_key=Config.api_key,
        base_url=Config.base_url,
        temperature=Config.temperature,
    )


# GitHub Operations
class GitHubClient:
    """GitHub API operations."""
    
    def __init__(self, token: str):
        self.token = token
        self.headers = {
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github.v3+json",
            "X-GitHub-Api-Version": "2022-11-28",
        }
    
    def get_repo(self, owner: str, repo: str) -> dict:
        """Get repository information."""
        import urllib.request
        url = f"https://api.github.com/repos/{owner}/{repo}"
        req = urllib.request.Request(url, headers=self.headers)
        with urllib.request.urlopen(req) as resp:
            return json.loads(resp.read().decode())
    
    def create_pr(self, owner: str, repo: str, title: str, body: str, base: str, head: str) -> dict:
        """Create a pull request."""
        import urllib.request
        url = f"https://api.github.com/repos/{owner}/{repo}/pulls"
        data = json.dumps({"title": title, "body": body, "base": base, "head": head}).encode()
        req = urllib.request.Request(url, data=data, headers=self.headers, method="POST")
        with urllib.request.urlopen(req) as resp:
            return json.loads(resp.read().decode())
    
    def get_workflow_runs(self, owner: str, repo: str) -> dict:
        """Get workflow runs."""
        import urllib.request
        url = f"https://api.github.com/repos/{owner}/{repo}/actions/runs"
        req = urllib.request.Request(url, headers=self.headers)
        with urllib.request.urlopen(req) as resp:
            return json.loads(resp.read().decode())


# Docker Operations
class DockerClient:
    """Docker operations."""
    
    def build(self, path: str, tag: str, dockerfile: str = "Dockerfile") -> dict:
        """Build Docker image."""
        cmd = ["docker", "build", "-t", tag, "-f", dockerfile, path]
        result = subprocess.run(cmd, capture_output=True, text=True)
        return {"success": result.returncode == 0, "output": result.stdout, "error": result.stderr}
    
    def push(self, tag: str) -> dict:
        """Push Docker image."""
        cmd = ["docker", "push", tag]
        result = subprocess.run(cmd, capture_output=True, text=True)
        return {"success": result.returncode == 0, "output": result.stdout, "error": result.stderr}
    
    def run(self, image: str, ports: dict = None, env: dict = None) -> dict:
        """Run Docker container."""
        cmd = ["docker", "run", "-d"]
        if ports:
            for host, container in ports.items():
                cmd.extend(["-p", f"{host}:{container}"])
        if env:
            for key, value in env.items():
                cmd.extend(["-e", f"{key}={value}"])
        cmd.append(image)
        result = subprocess.run(cmd, capture_output=True, text=True)
        return {"success": result.returncode == 0, "container_id": result.stdout.strip()}


# Agent Nodes
def analyze_task(state: AgentState) -> AgentState:
    """Analyze the user's task."""
    messages = state["messages"]
    last_message = messages[-1]
    
    task_prompt = f"""Analyze this request and determine the required action:
    
    {last_message.content}
    
    Determine if this is about:
    - GitHub repository management (create PR, check status, etc.)
    - Docker operations (build, push, run)
    - Code review or QA
    - General question
    
    Respond with a brief analysis and your planned action."""
    
    llm = get_llm()
    response = llm.invoke(task_prompt)
    
    return {
        **state,
        "current_task": response.content,
        "task_history": state.get("task_history", []) + [{
            "task": last_message.content,
            "analysis": response.content,
            "timestamp": datetime.now().isoformat(),
        }]
    }


def execute_github_action(state: AgentState) -> AgentState:
    """Execute GitHub-related actions."""
    try:
        client = GitHubClient(Config.github_token)
        
        # Example: Get repo info
        if Config.github_owner and Config.github_repo:
            repo_info = client.get_repo(Config.github_owner, Config.github_repo)
            return {**state, "repo_info": repo_info}
        
        return {**state, "error": "No GitHub repository configured"}
    except Exception as e:
        return {**state, "error": str(e)}


def execute_docker_action(state: AgentState) -> AgentState:
    """Execute Docker-related actions."""
    docker_client = DockerClient()
    
    task = state.get("current_task", "").lower()
    
    # Determine action based on task
    if "build" in task:
        result = docker_client.build(Config.workspace, "project:latest")
    elif "push" in task:
        result = docker_client.push("project:latest")
    elif "run" in task:
        result = docker_client.run("project:latest", {"8080": "80"})
    else:
        result = {"success": False, "error": "Unknown Docker action"}
    
    return {**state, "result": result, "deployment_status": "completed" if result.get("success") else "failed"}


def respond(state: AgentState) -> AgentState:
    """Generate a response."""
    llm = get_llm()
    
    context = f"""
    Current task: {state.get('current_task', 'None')}
    Repository: {state.get('repo_info', {}).get('full_name', 'Not configured')}
    Deployment: {state.get('deployment_status', 'Not attempted')}
    Error: {state.get('error', 'None')}
    Result: {state.get('result', 'None')}
    """
    
    response = llm.invoke(f"""
    Generate a helpful response based on:
    
    {context}
    
    Keep your response concise and actionable.
    """)
    
    return {
        **state,
        "messages": state["messages"] + [AIMessage(content=response.content)],
    }


# Build the graph
workflow = StateGraph(AgentState)

# Add nodes
workflow.add_node("analyze", analyze_task)
workflow.add_node("github", execute_github_action)
workflow.add_node("docker", execute_docker_action)
workflow.add_node("respond", respond)

# Define edges
workflow.set_entry_point("analyze")

# Conditional routing based on task type
def route_task(state: AgentState) -> str:
    task = state.get("current_task", "").lower()
    if "github" in task or "pr" in task or "repo" in task:
        return "github"
    elif "docker" in task or "deploy" in task or "container" in task:
        return "docker"
    return "respond"

workflow.add_conditional_edges(
    "analyze",
    route_task,
    {
        "github": "github",
        "docker": "docker",
        "respond": "respond",
    }
)

workflow.add_edge("github", "respond")
workflow.add_edge("docker", "respond")
workflow.add_edge("respond", END)

# Compile the agent
agent = workflow.compile()


# Run the agent
def run_agent(input_message: str) -> dict:
    """Run the management agent."""
    initial_state = {
        "messages": [HumanMessage(content=input_message)],
        "current_task": None,
        "task_history": [],
        "repo_info": None,
        "deployment_status": None,
        "error": None,
        "result": None,
    }
    
    result = agent.invoke(initial_state)
    
    return {
        "response": result["messages"][-1].content,
        "repo_info": result.get("repo_info"),
        "deployment_status": result.get("deployment_status"),
        "error": result.get("error"),
    }


# Example usage
if __name__ == "__main__":
    # Example queries
    examples = [
        "Build the Docker image and push to registry",
        "Check the latest GitHub Actions workflow run",
        "Create a PR with my latest changes",
    ]
    
    for example in examples:
        print(f"\n{'='*50}")
        print(f"Query: {example}")
        print(f"{'='*50}")
        result = run_agent(example)
        print(f"Response: {result['response']}")
        if result.get("error"):
            print(f"Error: {result['error']}")