# AGENTS: AgentNxt CodeReviewer

## Working rules
- Treat this repository root as the only working root.
- Keep product-first naming for surfaces (AgentNxt CodeReviewer Web/Desktop/Mobile/VS Code/Slack/GitHub/Chrome).
- Keep backend contracts typed via Pydantic models.
- Maintain shared-core-first architecture: domain logic belongs in `src/codereviewer/core`.

## Coding conventions
- Python code should be typed and test-covered.
- Keep provider selection separate from model selection in API and UI.
- Preserve support for providers: `anthropic`, `bedrock`, `vertex`, `foundry`.

## Testing
- Run `pytest` for all changes.
