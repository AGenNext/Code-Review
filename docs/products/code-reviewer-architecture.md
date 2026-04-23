# AgentNxt CodeReviewer Architecture

## Shared core
- `core/models.py`: canonical review entities
- `core/logic.py`: severity-to-recommendation and summary scoring

## Backend/API
- FastAPI app in `api/app.py`
- Services:
  - `ReviewService`: orchestrates job lifecycle
  - `RuntimeProfileService`: manages provider/model runtime profiles
  - `ClaudeAgentSDKReviewer`: Claude Agent SDK boundary adapter

## Surface architecture
- Production surface implemented now: AgentNxt CodeReviewer Web (`web/ui.py` + API)
- Starter adapters under `apps/`:
  - desktop
  - mobile
  - vscode
  - slack
  - github
  - chrome

Each surface consumes shared API contracts and shared core logic.
