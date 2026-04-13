"""Shared fixtures for tiingo-mcp tests."""

from __future__ import annotations

import pytest

from tiingo_mcp.client import TiingoClient


@pytest.fixture
def api_key() -> str:
    return "test-api-key-12345"


@pytest.fixture
def tiingo_client(api_key: str) -> TiingoClient:
    return TiingoClient(api_key=api_key)


@pytest.fixture(autouse=True)
def _reset_server_client():
    """Reset the module-level singleton between tests."""
    import tiingo_mcp.server as srv

    srv._client = None
    yield
    srv._client = None
