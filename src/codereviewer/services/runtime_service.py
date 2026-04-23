from codereviewer.core.models import ModelConfiguration, Provider, RuntimeProfile
from codereviewer.infra.repositories import InMemoryRuntimeProfileRepository

SUPPORTED_MODELS: list[ModelConfiguration] = [
    ModelConfiguration(model_id="claude-sonnet-4", display_name="Claude Sonnet 4", provider=Provider.anthropic),
    ModelConfiguration(model_id="anthropic.claude-sonnet-4", display_name="Claude Sonnet 4 (Bedrock)", provider=Provider.bedrock),
    ModelConfiguration(model_id="claude-sonnet-4@vertex", display_name="Claude Sonnet 4 (Vertex)", provider=Provider.vertex),
    ModelConfiguration(model_id="claude-sonnet-4@foundry", display_name="Claude Sonnet 4 (Foundry)", provider=Provider.foundry),
]


class RuntimeProfileService:
    def __init__(self, repo: InMemoryRuntimeProfileRepository) -> None:
        self.repo = repo

    def create_profile(self, profile: RuntimeProfile) -> RuntimeProfile:
        return self.repo.save(profile)

    def list_profiles(self) -> list[RuntimeProfile]:
        return self.repo.list()

    def list_models(self, provider: Provider | None = None) -> list[ModelConfiguration]:
        if provider is None:
            return SUPPORTED_MODELS
        return [m for m in SUPPORTED_MODELS if m.provider == provider]
