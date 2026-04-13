"""Tests for the FastMCP server tool registration and integration."""

from __future__ import annotations

import json

from fastmcp import Client
from pytest_httpx import HTTPXMock

import tiingo_mcp.server as srv
from tiingo_mcp.client import TiingoClient
from tiingo_mcp.server import mcp

EXPECTED_TOOLS = [
    "get_stock_metadata",
    "get_stock_prices",
    "get_realtime_price",
    "get_intraday_prices",
    "get_forex_quote",
    "get_forex_prices",
    "get_crypto_quote",
    "get_crypto_prices",
    "get_crypto_metadata",
    "get_news",
    "get_fundamentals_definitions",
    "get_financial_statements",
    "get_daily_fundamentals",
    "get_company_meta",
    "get_dividends",
    "get_dividend_yield",
    "get_splits",
]


# ── Tool registration ─────────────────────────────────────────────────


async def test_all_tools_registered():
    async with Client(mcp) as client:
        tools = await client.list_tools()
        tool_names = sorted(t.name for t in tools)
        assert tool_names == sorted(EXPECTED_TOOLS)


async def test_tool_count():
    async with Client(mcp) as client:
        tools = await client.list_tools()
        assert len(tools) == 17


# ── Tool invocation via MCP client ───────────────────────────────────


async def test_get_stock_metadata_via_mcp(httpx_mock: HTTPXMock):
    srv._client = TiingoClient(api_key="test-key")
    expected = {"ticker": "AAPL", "name": "Apple Inc"}
    httpx_mock.add_response(json=expected)

    async with Client(mcp) as client:
        result = await client.call_tool("get_stock_metadata", {"ticker": "AAPL"})
        data = json.loads(result.content[0].text)
        assert data["ticker"] == "AAPL"


async def test_get_stock_prices_via_mcp(httpx_mock: HTTPXMock):
    srv._client = TiingoClient(api_key="test-key")
    expected = [{"date": "2024-01-15", "close": 185.0}]
    httpx_mock.add_response(json=expected)

    async with Client(mcp) as client:
        result = await client.call_tool(
            "get_stock_prices",
            {"ticker": "AAPL", "start_date": "2024-01-15"},
        )
        data = json.loads(result.content[0].text)
        assert data[0]["close"] == 185.0


async def test_get_news_via_mcp(httpx_mock: HTTPXMock):
    srv._client = TiingoClient(api_key="test-key")
    expected = [{"title": "Markets rally"}]
    httpx_mock.add_response(json=expected)

    async with Client(mcp) as client:
        result = await client.call_tool("get_news", {"tickers": "AAPL", "limit": 5})
        data = json.loads(result.content[0].text)
        assert data[0]["title"] == "Markets rally"


async def test_get_crypto_quote_via_mcp(httpx_mock: HTTPXMock):
    srv._client = TiingoClient(api_key="test-key")
    expected = [{"ticker": "btcusd", "lastPrice": 42000.0}]
    httpx_mock.add_response(json=expected)

    async with Client(mcp) as client:
        result = await client.call_tool("get_crypto_quote", {"tickers": "btcusd"})
        data = json.loads(result.content[0].text)
        assert data[0]["lastPrice"] == 42000.0


# ── Error propagation ────────────────────────────────────────────────


async def test_api_error_returns_error_json(httpx_mock: HTTPXMock):
    srv._client = TiingoClient(api_key="test-key")
    httpx_mock.add_response(status_code=401, text="Unauthorized")

    async with Client(mcp) as client:
        result = await client.call_tool("get_stock_metadata", {"ticker": "AAPL"})
        data = json.loads(result.content[0].text)
        assert "error" in data
        assert data["status_code"] == 401


async def test_rate_limit_returns_error_json(httpx_mock: HTTPXMock):
    srv._client = TiingoClient(api_key="test-key")
    httpx_mock.add_response(status_code=429, text="Rate limited")

    async with Client(mcp) as client:
        result = await client.call_tool("get_stock_metadata", {"ticker": "AAPL"})
        data = json.loads(result.content[0].text)
        assert "error" in data
        assert data["status_code"] == 429


# ── Tool descriptions ────────────────────────────────────────────────


async def test_tools_have_descriptions():
    async with Client(mcp) as client:
        tools = await client.list_tools()
        for tool in tools:
            assert tool.description, f"Tool {tool.name} has no description"
            assert len(tool.description) > 10, f"Tool {tool.name} has short description"
