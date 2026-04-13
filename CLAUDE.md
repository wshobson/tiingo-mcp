# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

```bash
uv sync                                          # Install/update dependencies
uv run pytest -v                                  # Run all tests (unit + integration)
uv run pytest tests/test_client.py -v             # Unit tests only (no API key needed)
uv run pytest tests/test_server.py -v             # MCP server tests (no API key needed)
uv run pytest tests/test_integration.py -v -s     # Live API tests (needs TIINGO_API_KEY)
uv run pytest tests/test_client.py::test_get_news -v  # Run a single test
uv run ruff check src/ tests/                     # Lint
uv run ruff format src/ tests/                    # Format
uv run ruff check --fix src/ tests/               # Auto-fix lint issues
uv build                                          # Build sdist + wheel
TIINGO_API_KEY=key uv run tiingo-mcp              # Run server locally (stdio)
```

## Architecture

This is a FastMCP 3.2 server that wraps the Tiingo financial data REST API. Two core modules:

- **`client.py`** — `TiingoClient` wraps `httpx.AsyncClient` with token auth, automatic retries (2x via `AsyncHTTPTransport`), and status-code-specific error handling (`TiingoAPIError`). Each Tiingo endpoint has a dedicated async method that maps `snake_case` Python params to `camelCase` Tiingo query params. `None` params are stripped before sending.

- **`server.py`** — Defines the `FastMCP` instance (`mcp`) and 17 `@mcp.tool` async functions. Tools call `_get_client()` (a lazy module-level singleton) and wrap all API calls in `_safe_call()` which catches `TiingoAPIError` and returns structured JSON error responses instead of raising. The server has a `_lifespan` context manager that closes the httpx client on shutdown.

The entry point chain: `tiingo-mcp` CLI → `tiingo_mcp:main()` → `mcp.run()` (stdio transport).

## Key Patterns

- **Client singleton**: `server._client` is a module-level `TiingoClient | None`, lazily initialized by `_get_client()`. Tests reset it via the `_reset_server_client` autouse fixture in `conftest.py`.
- **Error handling flow**: Tiingo HTTP errors → `TiingoAPIError` in client → caught by `_safe_call()` in server → returned as JSON `{"error": ..., "status_code": ...}` to the LLM (never raises through MCP).
- **Parameter mapping**: Client methods use `snake_case`; the `params` dict passed to `_request()` uses Tiingo's `camelCase` keys. Corporate actions endpoints use `startExDate`/`endExDate` (not `startDate`/`endDate`).
- **Test layers**: `test_client.py` uses `pytest-httpx` (`HTTPXMock`) to mock HTTP responses. `test_server.py` uses FastMCP's `Client(mcp)` for in-memory MCP invocation. `test_integration.py` hits the live API and skips 403s (plan-restricted endpoints).

## Tiingo API Notes

- Auth: `Authorization: Token {key}` header on all requests
- Free plan gets stocks, forex, crypto, news, fundamentals, dividend yield. Dividends (distributions) and splits endpoints return 403 on free tier.
- Base URL: `https://api.tiingo.com`
- Rate limits: Free = 50 req/hr, Power = 5,000 req/hr

## Version

Version is declared in two places that must stay in sync: `pyproject.toml` (`version`) and `src/tiingo_mcp/__init__.py` (`__version__`).
