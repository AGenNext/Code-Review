from codereviewer.core.models import Provider, RuntimeProfile
from codereviewer.infra.repositories import InMemoryRuntimeProfileRepository
from codereviewer.services.runtime_service import RuntimeProfileService


def test_runtime_profile_default_switch() -> None:
    repo = InMemoryRuntimeProfileRepository()
    service = RuntimeProfileService(repo)

    p1 = service.create_profile(RuntimeProfile(name="one", provider=Provider.anthropic, model_id="m1", auth_reference="a1", is_default=True))
    p2 = service.create_profile(RuntimeProfile(name="two", provider=Provider.bedrock, model_id="m2", auth_reference="a2", is_default=True))

    assert repo.get(p1.id).is_default is False
    assert repo.get(p2.id).is_default is True


def test_models_filtered_by_provider() -> None:
    service = RuntimeProfileService(InMemoryRuntimeProfileRepository())
    anthropic_models = service.list_models(Provider.anthropic)
    assert anthropic_models
    assert all(m.provider == Provider.anthropic for m in anthropic_models)
