import os
import socket

import uvicorn


def _is_port_available(host: str, port: int) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        try:
            sock.bind((host, port))
        except OSError:
            return False
    return True


def _resolve_port(host: str) -> int:
    raw_port = os.getenv("PORT", "auto").strip().lower()
    if raw_port and raw_port != "auto":
        return int(raw_port)

    start = int(os.getenv("PORT_START", "8000"))
    end = int(os.getenv("PORT_END", "8999"))
    if end < start:
        raise ValueError("PORT_END must be greater than or equal to PORT_START")

    for port in range(start, end + 1):
        if _is_port_available(host, port):
            return port

    raise RuntimeError(f"No available port found in range {start}-{end}")


def run() -> None:
    host = os.getenv("HOST", "0.0.0.0")
    port = _resolve_port(host)
    uvicorn.run("codereviewer.api.app:app", host=host, port=port, reload=False)


if __name__ == "__main__":
    run()
