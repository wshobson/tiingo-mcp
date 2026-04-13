"""Tests for MCP prompts registered in prompts.py."""

from __future__ import annotations

from fastmcp import Client

import tiingo_mcp.prompts  # noqa: F401
from tiingo_mcp.server import mcp

# ── analyze-stock ─────────────────────────────────────────────────────


async def test_analyze_stock_prompt_listed():
    async with Client(mcp) as client:
        prompts = await client.list_prompts()
        names = [p.name for p in prompts]
        assert "analyze-stock" in names


async def test_analyze_stock_prompt_content():
    async with Client(mcp) as client:
        result = await client.get_prompt("analyze-stock", arguments={"ticker": "AAPL"})
        assert len(result.messages) == 1
        msg = result.messages[0]
        assert msg.role == "user"
        text = msg.content.text
        assert "AAPL" in text
        assert "get_stock_metadata" in text
        assert "get_stock_prices" in text
        assert "get_daily_fundamentals" in text
        assert "get_news" in text


async def test_analyze_stock_with_news_disabled():
    async with Client(mcp) as client:
        result = await client.get_prompt(
            "analyze-stock", arguments={"ticker": "MSFT", "include_news": "false"}
        )
        text = result.messages[0].content.text
        # When news is disabled, get_news should not appear or should say skip/do not
        if "get_news" in text:
            assert any(word in text.lower() for word in ("skip", "do not", "false"))
        else:
            assert "MSFT" in text


# ── compare-stocks ────────────────────────────────────────────────────


async def test_compare_stocks_prompt_listed():
    async with Client(mcp) as client:
        prompts = await client.list_prompts()
        names = [p.name for p in prompts]
        assert "compare-stocks" in names


async def test_compare_stocks_prompt_content():
    async with Client(mcp) as client:
        result = await client.get_prompt(
            "compare-stocks", arguments={"ticker1": "AAPL", "ticker2": "MSFT"}
        )
        assert len(result.messages) == 1
        msg = result.messages[0]
        assert msg.role == "user"
        text = msg.content.text
        assert "AAPL" in text
        assert "MSFT" in text
        assert "get_stock_prices" in text
        assert "get_daily_fundamentals" in text
        assert "get_dividend_yield" in text


# ── crypto-market-overview ────────────────────────────────────────────


async def test_crypto_market_overview_prompt_listed():
    async with Client(mcp) as client:
        prompts = await client.list_prompts()
        names = [p.name for p in prompts]
        assert "crypto-market-overview" in names


async def test_crypto_market_overview_prompt_content():
    async with Client(mcp) as client:
        result = await client.get_prompt("crypto-market-overview", arguments={})
        assert len(result.messages) == 1
        msg = result.messages[0]
        assert msg.role == "user"
        text = msg.content.text
        # Default tickers
        assert "btcusd" in text
        assert "ethusd" in text
        assert "solusd" in text
        assert "get_crypto_quote" in text
        assert "get_crypto_prices" in text


async def test_crypto_market_overview_custom_tickers():
    async with Client(mcp) as client:
        result = await client.get_prompt(
            "crypto-market-overview", arguments={"tickers": "btcusd,dogeusd"}
        )
        text = result.messages[0].content.text
        assert "btcusd" in text
        assert "dogeusd" in text


# ── earnings-report-analysis ──────────────────────────────────────────


async def test_earnings_report_prompt_listed():
    async with Client(mcp) as client:
        prompts = await client.list_prompts()
        names = [p.name for p in prompts]
        assert "earnings-report-analysis" in names


async def test_earnings_report_prompt_content():
    async with Client(mcp) as client:
        result = await client.get_prompt(
            "earnings-report-analysis",
            arguments={"ticker": "NVDA", "earnings_date": "2024-02-21"},
        )
        assert len(result.messages) == 1
        msg = result.messages[0]
        assert msg.role == "user"
        text = msg.content.text
        assert "NVDA" in text
        assert "2024-02-21" in text
        assert "get_financial_statements" in text
        assert "get_stock_prices" in text
        assert "get_news" in text


# ── forex-pair-analysis ───────────────────────────────────────────────


async def test_forex_pair_prompt_listed():
    async with Client(mcp) as client:
        prompts = await client.list_prompts()
        names = [p.name for p in prompts]
        assert "forex-pair-analysis" in names


async def test_forex_pair_prompt_content():
    async with Client(mcp) as client:
        result = await client.get_prompt(
            "forex-pair-analysis", arguments={"pair": "eurusd"}
        )
        assert len(result.messages) == 1
        msg = result.messages[0]
        assert msg.role == "user"
        text = msg.content.text
        assert "eurusd" in text
        assert "get_forex_quote" in text
        assert "get_forex_prices" in text


# ── counts and metadata ───────────────────────────────────────────────


async def test_prompt_count():
    async with Client(mcp) as client:
        prompts = await client.list_prompts()
        assert len(prompts) == 5


async def test_all_prompts_have_descriptions():
    async with Client(mcp) as client:
        prompts = await client.list_prompts()
        for prompt in prompts:
            assert prompt.description, f"Prompt '{prompt.name}' has no description"
            assert len(prompt.description.strip()) > 0
