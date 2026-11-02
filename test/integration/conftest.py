"""Fixtures for tests against an isolated Docker Paperless-ngx stack."""

import os
import socket
import subprocess
import time
import uuid
from collections.abc import AsyncIterator, Iterator
from pathlib import Path

import httpx
import pytest

from paperless_mcp.config import Settings
from paperless_mcp.paperless import PaperlessClient

COMPOSE_FILE = Path(__file__).with_name("docker-compose.yml")
ADMIN_USER = "paperless-test-admin"
ADMIN_PASSWORD = "paperless-test-password"


def _available_port() -> int:
    """Reserve an ephemeral localhost port for the Paperless test stack."""
    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        return int(sock.getsockname()[1])


def _compose(
    project: str,
    env: dict[str, str],
    *args: str,
    timeout: int = 300,
) -> None:
    """Run a Docker Compose command and raise with output on failure."""
    command = [
        "docker",
        "compose",
        "--project-name",
        project,
        "--file",
        str(COMPOSE_FILE),
        *args,
    ]
    result = subprocess.run(
        command,
        check=False,
        capture_output=True,
        text=True,
        timeout=timeout,
        env=env,
    )
    if result.returncode:
        raise RuntimeError(
            f"Docker Compose command failed: {' '.join(command)}\n"
            f"{result.stdout}\n{result.stderr}"
        )


def _wait_for_api(base_url: str, timeout: int = 300) -> str:
    """Wait for Paperless readiness and return its test admin API token."""
    deadline = time.monotonic() + timeout
    token_url = f"{base_url}/api/token/"
    last_error = "Paperless API did not become ready"
    with httpx.Client(timeout=5.0) as client:
        while time.monotonic() < deadline:
            try:
                response = client.post(
                    token_url,
                    json={"username": ADMIN_USER, "password": ADMIN_PASSWORD},
                )
                if response.is_success:
                    token = response.json().get("token")
                    if token:
                        return token
                    raise RuntimeError(
                        "Paperless token response did not contain a token"
                    )
                if response.status_code < 500:
                    raise RuntimeError(
                        f"Paperless token request failed: "
                        f"{response.status_code} {response.text[:500]}"
                    )
                last_error = f"Paperless returned HTTP {response.status_code}"
            except httpx.RequestError as exc:
                last_error = str(exc)
            time.sleep(2)
    raise RuntimeError(f"Paperless API was not ready: {last_error}")


@pytest.fixture(scope="session")
def paperless_settings() -> Iterator[Settings]:
    """Start a disposable Paperless stack and yield its authenticated settings."""
    project = f"paperless-mcp-it-{uuid.uuid4().hex[:8]}"
    port = int(os.environ.get("PAPERLESS_TEST_PORT", _available_port()))
    base_url = f"http://127.0.0.1:{port}"
    compose_env = os.environ.copy()
    compose_env["PAPERLESS_TEST_PORT"] = str(port)
    started = False

    try:
        started = True
        _compose(project, compose_env, "up", "--detach")
        token = _wait_for_api(base_url)
        yield Settings(base_url=base_url, api_key=token)
    finally:
        if started:
            _compose(
                project,
                compose_env,
                "down",
                "--volumes",
                "--remove-orphans",
                timeout=120,
            )


@pytest.fixture
async def paperless_service(
    paperless_settings: Settings,
) -> AsyncIterator[PaperlessClient]:
    """Create and close an API client for the current async test loop."""
    client = PaperlessClient(paperless_settings)
    try:
        yield client
    finally:
        await client.close()
