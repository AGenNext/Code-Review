from codereviewer.core.models import Provider, RuntimeProfile
from codereviewer.infra.repositories import RuntimeProfileRepository, SQLiteRepository
from codereviewer.services.runtime_service import RuntimeProfileService


def test_runtime_profile_default_switch(tmp_path) -> None:
    repo = RuntimeProfileRepository(SQLiteRepository(str(tmp_path / "db.sqlite")))
    service = RuntimeProfileService(repo)

    p1 = service.create_profile(
        RuntimeProfile(name="one", provider=Provider.anthropic, model_id="claude-sonnet-4", auth_reference="a1", is_default=True)
    )
    p2 = service.create_profile(
        RuntimeProfile(
            name="two",
            provider=Provider.bedrock,
            model_id="anthropic.claude-sonnet-4",
            auth_reference="a2",
            is_default=True,
        )
    )

    assert repo.get(p1.id).is_default is False
    assert repo.get(p2.id).is_default is True


def test_models_filtered_by_provider(tmp_path) -> None:
    service = RuntimeProfileService(RuntimeProfileRepository(SQLiteRepository(str(tmp_path / "db.sqlite"))))
    anthropic_models = service.list_models(Provider.anthropic)
    assert anthropic_models
    assert all(m.provider == Provider.anthropic for m in anthropic_models)


def test_invalid_provider_model_pair_rejected(tmp_path) -> None:
    service = RuntimeProfileService(RuntimeProfileRepository(SQLiteRepository(str(tmp_path / "db.sqlite"))))
    try:
        service.create_profile(RuntimeProfile(name="bad", provider=Provider.anthropic, model_id="not-valid", auth_reference="x"))
    except ValueError as exc:
        assert "not valid" in str(exc)
    else:
        raise AssertionError("Expected ValueError for invalid provider/model pair")
