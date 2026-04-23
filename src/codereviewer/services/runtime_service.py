from codereviewer.core.models import ModelConfiguration, Provider, RuntimeProfile
from codereviewer.infra.repositories import RuntimeProfileRepository

SUPPORTED_MODELS: list[ModelConfiguration] = [
    ModelConfiguration(model_id="claude-sonnet-4", display_name="Claude Sonnet 4", provider=Provider.anthropic, context_window=200_000),
    ModelConfiguration(model_id="anthropic.claude-sonnet-4", display_name="Claude Sonnet 4 (Bedrock)", provider=Provider.bedrock, context_window=200_000),
    ModelConfiguration(model_id="claude-sonnet-4@vertex", display_name="Claude Sonnet 4 (Vertex)", provider=Provider.vertex, context_window=200_000),
    ModelConfiguration(model_id="claude-sonnet-4@foundry", display_name="Claude Sonnet 4 (Foundry)", provider=Provider.foundry, context_window=200_000),
]


class RuntimeProfileService:
    def __init__(self, repo: RuntimeProfileRepository) -> None:
        self.repo = repo

    def create_profile(self, profile: RuntimeProfile) -> RuntimeProfile:
        self._validate(profile)
        if profile.is_default:
            for existing in self.repo.list():
                existing.is_default = False
                self.repo.save(existing)
        return self.repo.save(profile)

    def list_profiles(self) -> list[RuntimeProfile]:
        return self.repo.list()

    def list_models(self, provider: Provider | None = None) -> list[ModelConfiguration]:
        if provider is None:
            return SUPPORTED_MODELS
        return [m for m in SUPPORTED_MODELS if m.provider == provider]

    def _validate(self, profile: RuntimeProfile) -> None:
        allowed_models = {model.model_id for model in self.list_models(profile.provider)}
        if profile.model_id not in allowed_models:
            raise ValueError(f"Model '{profile.model_id}' is not valid for provider '{profile.provider.value}'")
