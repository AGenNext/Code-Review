from codereviewer.services.sso_service import load_sso_config


def test_load_sso_config_defaults(monkeypatch) -> None:
    monkeypatch.delenv("SSO_ENABLED", raising=False)
    monkeypatch.delenv("SSO_PROVIDER", raising=False)
    monkeypatch.delenv("SSO_SCOPES", raising=False)
    config = load_sso_config()
    assert config.enabled is False
    assert config.provider == "oidc"
    assert config.scopes == ["openid", "profile", "email"]


def test_load_sso_config_explicit(monkeypatch) -> None:
    monkeypatch.setenv("SSO_ENABLED", "true")
    monkeypatch.setenv("SSO_PROVIDER", "entra")
    monkeypatch.setenv("SSO_CLIENT_ID", "client-1")
    monkeypatch.setenv("SSO_CLIENT_SECRET", "secret-1")
    monkeypatch.setenv("SSO_SCOPES", "openid,email")
    config = load_sso_config()
    assert config.enabled is True
    assert config.provider == "entra"
    assert config.client_id == "client-1"
    assert config.client_secret_configured is True
    assert config.scopes == ["openid", "email"]
