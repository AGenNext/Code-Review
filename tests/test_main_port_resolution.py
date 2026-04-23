from __future__ import annotations

from codereviewer import main


def test_resolve_port_uses_explicit_port(monkeypatch) -> None:
    monkeypatch.setenv("PORT", "8123")
    assert main._resolve_port("0.0.0.0") == 8123


def test_resolve_port_finds_first_available(monkeypatch) -> None:
    monkeypatch.setenv("PORT", "auto")
    monkeypatch.setenv("PORT_START", "8100")
    monkeypatch.setenv("PORT_END", "8103")

    unavailable = {8100, 8101}
    monkeypatch.setattr(main, "_is_port_available", lambda _host, port: port not in unavailable)

    assert main._resolve_port("0.0.0.0") == 8102


def test_resolve_port_raises_when_range_exhausted(monkeypatch) -> None:
    monkeypatch.setenv("PORT", "auto")
    monkeypatch.setenv("PORT_START", "8100")
    monkeypatch.setenv("PORT_END", "8101")
    monkeypatch.setattr(main, "_is_port_available", lambda _host, _port: False)

    try:
        main._resolve_port("0.0.0.0")
    except RuntimeError as exc:
        assert "No available port found" in str(exc)
    else:
        raise AssertionError("Expected RuntimeError when no ports are available")
