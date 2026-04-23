from codereviewer.core.models import FileChangeContext
from codereviewer.services.context_budget import ContextBudgetManager


def test_context_budget_prioritizes_security_and_limits_size() -> None:
    manager = ContextBudgetManager(max_chars=20)
    changes = [
        FileChangeContext(path="src/app.py", change_type="modified", patch="+print('a')" * 10),
        FileChangeContext(path="src/security/auth.py", change_type="modified", patch="+secret='x'" * 10),
    ]
    selected = manager.select_chunks(changes)
    assert selected
    assert selected[0].path == "src/security/auth.py"
    assert sum(len(chunk.content) for chunk in selected) <= 20
