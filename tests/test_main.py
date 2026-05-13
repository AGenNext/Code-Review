import socket

import pytest

from codereviewer import main


def test_resolve_port_uses_explicit_port(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("PORT", "8080")

    assert main._resolve_port("127.0.0.1") == 8080


def test_resolve_port_auto_selects_available_port(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("PORT", "auto")
    monkeypatch.setenv("PORT_START", "38111")
    monkeypatch.setenv("PORT_END", "38111")

    assert main._resolve_port("127.0.0.1") == 38111


def test_resolve_port_rejects_invalid_range(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("PORT", "auto")
    monkeypatch.setenv("PORT_START", "9000")
    monkeypatch.setenv("PORT_END", "8000")

    with pytest.raises(ValueError, match="PORT_END"):
        main._resolve_port("127.0.0.1")


def test_resolve_port_raises_when_range_is_unavailable(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("PORT", "auto")
    monkeypatch.setenv("PORT_START", "38112")
    monkeypatch.setenv("PORT_END", "38112")

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind(("127.0.0.1", 38112))
        sock.listen(1)
        with pytest.raises(RuntimeError, match="No available port"):
            main._resolve_port("127.0.0.1")
