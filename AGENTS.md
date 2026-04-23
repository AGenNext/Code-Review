# AGENTS: AgentNxt CodeReviewer

## Repo identity
- Org: `agentnxt`
- Repo: `code-reviewer`
- Product display name: `CodeReviewer`
- Product repo slug: `code-reviewer`

## Working rules
- Treat this repository root as the only working root.
- Do not create nested org folders or scaffold sibling repos inside this repository.
- Keep product-first naming for surfaces: `CodeReviewer Web`, `CodeReviewer Desktop`, `CodeReviewer Mobile`, `CodeReviewer VS Code`, `CodeReviewer Slack`, `CodeReviewer GitHub`, `CodeReviewer Chrome`.
- Do not introduce shorthand variants such as `coderev`.
- Maintain shared-core-first architecture: domain logic belongs in `src/codereviewer/core`.
- Keep backend contracts typed via Pydantic models.

## Architecture rules
- Use Claude Agent SDK as the core agent architecture for this product.
- Keep provider selection separate from model selection in API and UI.
- Preserve support for providers: `anthropic`, `bedrock`, `vertex`, `foundry`.
- Do not present scaffolded surfaces as implemented products.
- Surface-specific folders are not sufficient documentation by themselves.

## Documentation rules
- The root `README.md` must include a surface status matrix.
- Every named surface must be explicitly labeled as one of: `implemented`, `scaffolded`, or `planned`.
- Every named surface must be documented in product or architecture docs, not only represented by folder stubs.
- Desktop must be described explicitly when named, including purpose, status, and intended runtime model.
- Prompts and docs must distinguish clearly between `build now` work and `architecture only` work.
- When naming matters, state org, repo, path, and product name separately.
- If a name is a deliberate choice, treat it as locked unless changed explicitly in the source of truth.

## Coding conventions
- Python code should be typed and test-covered.
- Keep changes small, explicit, and reviewable.
- Avoid vague placeholders when a concrete status or boundary can be stated.

## Testing
- Run `pytest` for all changes.
- If tests cannot run, document the exact reason and the exact missing dependency or environment constraint.
