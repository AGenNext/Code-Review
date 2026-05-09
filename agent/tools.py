"""
Agent Tools

Tools available to the LangGraph management agent.
"""

import os
import json
import subprocess
import urllib.request
from typing import Any, Optional
from dataclasses import dataclass


@dataclass
class ToolResult:
    """Result from a tool execution."""
    success: bool
    data: Any = None
    error: Optional[str] = None


class GitHubTool:
    """GitHub operations tool."""
    
    name = "github"
    description = "GitHub repository and PR operations"
    
    def __init__(self, token: str):
        self.token = token
        self.headers = {
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github.v3+json",
        }
    
    def get_repo(self, owner: str, repo: str) -> ToolResult:
        """Get repository information."""
        try:
            url = f"https://api.github.com/repos/{owner}/{repo}"
            req = urllib.request.Request(url, headers=self.headers)
            with urllib.request.urlopen(req) as resp:
                return ToolResult(success=True, data=json.loads(resp.read().decode()))
        except Exception as e:
            return ToolResult(success=False, error=str(e))
    
    def create_pr(self, owner: str, repo: str, title: str, body: str, base: str, head: str) -> ToolResult:
        """Create a pull request."""
        try:
            url = f"https://api.github.com/repos/{owner}/{repo}/pulls"
            data = json.dumps({"title": title, "body": body, "base": base, "head": head}).encode()
            headers = {**self.headers, "Content-Type": "application/json"}
            req = urllib.request.Request(url, data=data, headers=headers, method="POST")
            with urllib.request.urlopen(req) as resp:
                return ToolResult(success=True, data=json.loads(resp.read().decode()))
        except Exception as e:
            return ToolResult(success=False, error=str(e))
    
    def list_workflows(self, owner: str, repo: str) -> ToolResult:
        """List workflow runs."""
        try:
            url = f"https://api.github.com/repos/{owner}/{repo}/actions/runs"
            req = urllib.request.Request(url, headers=self.headers)
            with urllib.request.urlopen(req) as resp:
                return ToolResult(success=True, data=json.loads(resp.read().decode()))
        except Exception as e:
            return ToolResult(success=False, error=str(e))
    
    def get_workflow_status(self, owner: str, repo: str, run_id: int) -> ToolResult:
        """Get workflow run status."""
        try:
            url = f"https://api.github.com/repos/{owner}/{repo}/actions/runs/{run_id}"
            req = urllib.request.Request(url, headers=self.headers)
            with urllib.request.urlopen(req) as resp:
                return ToolResult(success=True, data=json.loads(resp.read().decode()))
        except Exception as e:
            return ToolResult(success=False, error=str(e))
    
    def get_pulls(self, owner: str, repo: str) -> ToolResult:
        """List pull requests."""
        try:
            url = f"https://api.github.com/repos/{owner}/{repo}/pulls"
            req = urllib.request.Request(url, headers=self.headers)
            with urllib.request.urlopen(req) as resp:
                return ToolResult(success=True, data=json.loads(resp.read().decode()))
        except Exception as e:
            return ToolResult(success=False, error=str(e))
    
    def create_issue(self, owner: str, repo: str, title: str, body: str) -> ToolResult:
        """Create an issue."""
        try:
            url = f"https://api.github.com/repos/{owner}/{repo}/issues"
            data = json.dumps({"title": title, "body": body}).encode()
            headers = {**self.headers, "Content-Type": "application/json"}
            req = urllib.request.Request(url, data=data, headers=headers, method="POST")
            with urllib.request.urlopen(req) as resp:
                return ToolResult(success=True, data=json.loads(resp.read().decode()))
        except Exception as e:
            return ToolResult(success=False, error=str(e))


class DockerTool:
    """Docker operations tool."""
    
    name = "docker"
    description = "Docker build, push, and run operations"
    
    def __init__(self, registry: str = "ghcr.io", username: str = None):
        self.registry = registry
        self.username = username
    
    def build(self, path: str, tag: str, dockerfile: str = "Dockerfile") -> ToolResult:
        """Build Docker image."""
        try:
            cmd = ["docker", "build", "-t", tag, "-f", dockerfile, path]
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode != 0:
                return ToolResult(success=False, error=result.stderr)
            return ToolResult(success=True, data={"image": tag, "output": result.stdout})
        except Exception as e:
            return ToolResult(success=False, error=str(e))
    
    def push(self, tag: str) -> ToolResult:
        """Push Docker image."""
        try:
            cmd = ["docker", "push", tag]
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode != 0:
                return ToolResult(success=False, error=result.stderr)
            return ToolResult(success=True, data={"pushed": tag})
        except Exception as e:
            return ToolResult(success=False, error=str(e))
    
    def run(self, image: str, ports: dict = None, env: dict = None, name: str = None) -> ToolResult:
        """Run Docker container."""
        try:
            cmd = ["docker", "run", "-d"]
            if name:
                cmd.extend(["--name", name])
            if ports:
                for host, container in ports.items():
                    cmd.extend(["-p", f"{host}:{container}"])
            if env:
                for key, value in env.items():
                    cmd.extend(["-e", f"{key}={value}"])
            cmd.append(image)
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode != 0:
                return ToolResult(success=False, error=result.stderr)
            return ToolResult(success=True, data={"container_id": result.stdout.strip()})
        except Exception as e:
            return ToolResult(success=False, error=str(e))
    
    def stop(self, container_id: str) -> ToolResult:
        """Stop Docker container."""
        try:
            cmd = ["docker", "stop", container_id]
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode != 0:
                return ToolResult(success=False, error=result.stderr)
            return ToolResult(success=True, data={"stopped": container_id})
        except Exception as e:
            return ToolResult(success=False, error=str(e))
    
    def logs(self, container_id: str, tail: int = 100) -> ToolResult:
        """Get container logs."""
        try:
            cmd = ["docker", "logs", "--tail", str(tail), container_id]
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode != 0:
                return ToolResult(success=False, error=result.stderr)
            return ToolResult(success=True, data={"logs": result.stdout})
        except Exception as e:
            return ToolResult(success=False, error=str(e))
    
    def ps(self, all: bool = False) -> ToolResult:
        """List containers."""
        try:
            cmd = ["docker", "ps"]
            if all:
                cmd.append("-a")
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode != 0:
                return ToolResult(success=False, error=result.stderr)
            return ToolResult(success=True, data={"containers": result.stdout})
        except Exception as e:
            return ToolResult(success=False, error=str(e))


class TerminalTool:
    """Shell command execution tool."""
    
    name = "terminal"
    description = "Execute shell commands"
    
    def execute(self, command: str, cwd: str = None, timeout: int = 30) -> ToolResult:
        """Execute a shell command."""
        try:
            result = subprocess.run(
                command,
                shell=True,
                cwd=cwd,
                capture_output=True,
                text=True,
                timeout=timeout,
            )
            if result.returncode != 0:
                return ToolResult(success=False, error=result.stderr)
            return ToolResult(success=True, data={"output": result.stdout, "exit_code": result.returncode})
        except Exception as e:
            return ToolResult(success=False, error=str(e))
    
    def check_status(self) -> ToolResult:
        """Check system status."""
        try:
            # Check git status
            git_result = subprocess.run(
                ["git", "status", "--porcelain"],
                capture_output=True,
                text=True,
            )
            
            # Check docker status
            docker_result = subprocess.run(
                ["docker", "ps", "-a"],
                capture_output=True,
                text=True,
            )
            
            return ToolResult(success=True, data={
                "git_status": git_result.stdout,
                "docker_containers": docker_result.stdout,
            })
        except Exception as e:
            return ToolResult(success=False, error=str(e))


class FileTool:
    """File operations tool."""
    
    name = "file_editor"
    description = "Read, write, and edit files"
    
    def read(self, path: str) -> ToolResult:
        """Read a file."""
        try:
            with open(path, "r") as f:
                return ToolResult(success=True, data=f.read())
        except FileNotFoundError:
            return ToolResult(success=False, error=f"File not found: {path}")
        except Exception as e:
            return ToolResult(success=False, error=str(e))
    
    def write(self, path: str, content: str) -> ToolResult:
        """Write to a file."""
        try:
            os.makedirs(os.path.dirname(path), exist_ok=True)
            with open(path, "w") as f:
                f.write(content)
            return ToolResult(success=True, data={"written": path})
        except Exception as e:
            return ToolResult(success=False, error=str(e))
    
    def exists(self, path: str) -> bool:
        """Check if file exists."""
        return os.path.exists(path)


def get_tools(config: dict = None) -> dict:
    """Get all available tools."""
    config = config or {}
    
    tools = {
        "terminal": TerminalTool(),
    }
    
    # Add GitHub tool if token available
    token = config.get("github_token") or os.getenv("GITHUB_TOKEN")
    if token:
        tools["github"] = GitHubTool(token)
    
    # Add Docker tool
    tools["docker"] = DockerTool(
        registry=config.get("docker_registry", "ghcr.io"),
        username=config.get("docker_username"),
    )
    
    # Add file tool
    tools["file_editor"] = FileTool()
    
    return tools


# Export all tools
__all__ = [
    "GitHubTool",
    "DockerTool",
    "TerminalTool",
    "FileTool",
    "ToolResult",
    "get_tools",
]