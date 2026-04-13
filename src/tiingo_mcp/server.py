"""FastMCP server exposing the full Tiingo financial data API as MCP tools."""

from __future__ import annotations

import json
from contextlib import asynccontextmanager
from typing import Any

from fastmcp import Context, FastMCP

from tiingo_mcp.client import TiingoAPIError, TiingoClient

# ── Shared client (lazy singleton) ───────────────────────────────────

_client: TiingoClient | None = None


def _get_client() -> TiingoClient:
    global _client
    if _client is None:
        _client = TiingoClient()
    return _client


@asynccontextmanager
async def _lifespan(server: FastMCP):
    yield
    if _client is not None:
        await _client.close()


mcp = FastMCP(
    name="Tiingo MCP Server",
    version="1.0.0",
    instructions=(
        "Financial data server powered by Tiingo. Provides real-time and historical "
        "stock prices, forex rates, crypto data, news, fundamentals, and corporate actions. "
        "All date parameters use YYYY-MM-DD format."
    ),
    lifespan=_lifespan,
)


def _fmt(data: Any) -> str:
    """Format API response data as indented JSON text."""
    return json.dumps(data, indent=2, default=str)


async def _safe_call(ctx: Context, coro) -> str:
    """Execute an API call with standardized error handling."""
    try:
        result = await coro
        return _fmt(result)
    except TiingoAPIError as exc:
        await ctx.error(f"Tiingo API error: {exc}")
        return _fmt({"error": exc.detail, "status_code": exc.status_code})
    except Exception as exc:
        await ctx.error(f"Unexpected error: {exc}")
        return _fmt({"error": str(exc)})


# ── EOD Stock Prices ──────────────────────────────────────────────────


@mcp.tool
async def get_stock_metadata(ticker: str, ctx: Context) -> str:
    """Get metadata for a stock ticker including name, exchange, description, and date range.

    Args:
        ticker: Stock ticker symbol (e.g. AAPL, MSFT, GOOGL).
    """
    return await _safe_call(ctx, _get_client().get_stock_metadata(ticker))


@mcp.tool
async def get_stock_prices(
    ticker: str,
    ctx: Context,
    start_date: str | None = None,
    end_date: str | None = None,
    resample_freq: str | None = None,
) -> str:
    """Get historical end-of-day stock prices with adjusted and unadjusted OHLCV data.

    Args:
        ticker: Stock ticker symbol (e.g. AAPL).
        start_date: Start date in YYYY-MM-DD format.
        end_date: End date in YYYY-MM-DD format.
        resample_freq: Resample frequency — daily, weekly, monthly, or annually.
    """
    return await _safe_call(
        ctx,
        _get_client().get_stock_prices(
            ticker,
            start_date=start_date,
            end_date=end_date,
            resample_freq=resample_freq,
        ),
    )


# ── IEX Real-Time / Intraday ─────────────────────────────────────────


@mcp.tool
async def get_realtime_price(
    ticker: str,
    ctx: Context,
    after_hours: bool | None = None,
) -> str:
    """Get the current real-time IEX top-of-book price for a stock.

    Args:
        ticker: Stock ticker symbol (e.g. AAPL).
        after_hours: Include after-hours pricing data.
    """
    return await _safe_call(ctx, _get_client().get_realtime_price(ticker, after_hours=after_hours))


@mcp.tool
async def get_intraday_prices(
    ticker: str,
    ctx: Context,
    start_date: str | None = None,
    end_date: str | None = None,
    resample_freq: str | None = None,
) -> str:
    """Get historical intraday prices from IEX at various intervals.

    Args:
        ticker: Stock ticker symbol (e.g. AAPL).
        start_date: Start date in YYYY-MM-DD format.
        end_date: End date in YYYY-MM-DD format.
        resample_freq: Resample frequency — 1min, 5min, 15min, 30min, 1hour, etc.
    """
    return await _safe_call(
        ctx,
        _get_client().get_intraday_prices(
            ticker,
            start_date=start_date,
            end_date=end_date,
            resample_freq=resample_freq,
        ),
    )


# ── Forex ─────────────────────────────────────────────────────────────


@mcp.tool
async def get_forex_quote(ticker: str, ctx: Context) -> str:
    """Get the current top-of-book forex quote for a currency pair.

    Args:
        ticker: Currency pair (e.g. eurusd, gbpusd, usdjpy).
    """
    return await _safe_call(ctx, _get_client().get_forex_quote(ticker))


@mcp.tool
async def get_forex_prices(
    ticker: str,
    ctx: Context,
    start_date: str | None = None,
    end_date: str | None = None,
    resample_freq: str | None = None,
) -> str:
    """Get historical forex prices for a currency pair.

    Args:
        ticker: Currency pair (e.g. eurusd, gbpusd, usdjpy).
        start_date: Start date in YYYY-MM-DD format.
        end_date: End date in YYYY-MM-DD format.
        resample_freq: Resample frequency — 1min, 5min, 15min, 30min, 1hour, 1day.
    """
    return await _safe_call(
        ctx,
        _get_client().get_forex_prices(
            ticker,
            start_date=start_date,
            end_date=end_date,
            resample_freq=resample_freq,
        ),
    )


# ── Crypto ────────────────────────────────────────────────────────────


@mcp.tool
async def get_crypto_quote(
    ctx: Context,
    tickers: str | None = None,
) -> str:
    """Get current top-of-book crypto prices.

    Returns data for all supported cryptos if no tickers specified.

    Args:
        tickers: Comma-separated crypto tickers (e.g. btcusd, ethusd). Omit for all.
    """
    return await _safe_call(ctx, _get_client().get_crypto_quote(tickers))


@mcp.tool
async def get_crypto_prices(
    tickers: str,
    ctx: Context,
    start_date: str | None = None,
    end_date: str | None = None,
    resample_freq: str | None = None,
) -> str:
    """Get historical crypto prices.

    Args:
        tickers: Comma-separated crypto tickers (e.g. btcusd, ethusd).
        start_date: Start date in YYYY-MM-DD format.
        end_date: End date in YYYY-MM-DD format.
        resample_freq: Resample frequency — 1min, 5min, 15min, 30min, 1hour, 1day.
    """
    return await _safe_call(
        ctx,
        _get_client().get_crypto_prices(
            tickers,
            start_date=start_date,
            end_date=end_date,
            resample_freq=resample_freq,
        ),
    )


@mcp.tool
async def get_crypto_metadata(
    ctx: Context,
    tickers: str | None = None,
) -> str:
    """Get metadata for crypto tickers including supported exchanges and pairs.

    Args:
        tickers: Comma-separated crypto tickers to filter by. Omit for all.
    """
    return await _safe_call(ctx, _get_client().get_crypto_metadata(tickers))


# ── News ──────────────────────────────────────────────────────────────


@mcp.tool
async def get_news(
    ctx: Context,
    tickers: str | None = None,
    tags: str | None = None,
    source: str | None = None,
    start_date: str | None = None,
    end_date: str | None = None,
    limit: int | None = None,
    offset: int | None = None,
    sort_by: str | None = None,
) -> str:
    """Search financial news articles from 50M+ sources.

    Args:
        tickers: Comma-separated ticker symbols to filter by (e.g. AAPL,MSFT).
        tags: Comma-separated tags to filter by.
        source: News source to filter by.
        start_date: Start date in YYYY-MM-DD format.
        end_date: End date in YYYY-MM-DD format.
        limit: Maximum number of articles to return (default 10).
        offset: Number of articles to skip for pagination.
        sort_by: Sort order — crawlDate or publishedDate.
    """
    return await _safe_call(
        ctx,
        _get_client().get_news(
            tickers=tickers,
            tags=tags,
            source=source,
            start_date=start_date,
            end_date=end_date,
            limit=limit,
            offset=offset,
            sort_by=sort_by,
        ),
    )


# ── Fundamentals ──────────────────────────────────────────────────────


@mcp.tool
async def get_fundamentals_definitions(ctx: Context) -> str:
    """Get definitions for all available fundamental metrics.

    Returns the list of metrics available in daily and statement endpoints,
    including their names, descriptions, and data types.
    """
    return await _safe_call(ctx, _get_client().get_fundamentals_definitions())


@mcp.tool
async def get_financial_statements(
    ticker: str,
    ctx: Context,
    start_date: str | None = None,
    end_date: str | None = None,
) -> str:
    """Get quarterly and annual financial statements (income, balance sheet, cash flow).

    Args:
        ticker: Stock ticker symbol (e.g. AAPL).
        start_date: Start date in YYYY-MM-DD format.
        end_date: End date in YYYY-MM-DD format.
    """
    return await _safe_call(
        ctx,
        _get_client().get_financial_statements(ticker, start_date=start_date, end_date=end_date),
    )


@mcp.tool
async def get_daily_fundamentals(
    ticker: str,
    ctx: Context,
    start_date: str | None = None,
    end_date: str | None = None,
) -> str:
    """Get daily fundamental metrics for a stock (market cap, P/E ratio, etc).

    Args:
        ticker: Stock ticker symbol (e.g. AAPL).
        start_date: Start date in YYYY-MM-DD format.
        end_date: End date in YYYY-MM-DD format.
    """
    return await _safe_call(
        ctx,
        _get_client().get_daily_fundamentals(ticker, start_date=start_date, end_date=end_date),
    )


@mcp.tool
async def get_company_meta(tickers: str, ctx: Context) -> str:
    """Get company metadata including sector, industry, and location.

    Args:
        tickers: Comma-separated ticker symbols (e.g. AAPL,MSFT,GOOGL).
    """
    return await _safe_call(ctx, _get_client().get_company_meta(tickers))


# ── Corporate Actions ─────────────────────────────────────────────────


@mcp.tool
async def get_dividends(
    ticker: str,
    ctx: Context,
    start_date: str | None = None,
    end_date: str | None = None,
) -> str:
    """Get historical dividend and distribution data for a stock or ETF.

    Args:
        ticker: Stock/ETF ticker symbol (e.g. AAPL, SPY).
        start_date: Filter dividends with ex-date on or after this date (YYYY-MM-DD).
        end_date: Filter dividends with ex-date on or before this date (YYYY-MM-DD).
    """
    return await _safe_call(
        ctx,
        _get_client().get_dividends(ticker, start_date=start_date, end_date=end_date),
    )


@mcp.tool
async def get_dividend_yield(
    ticker: str,
    ctx: Context,
    start_date: str | None = None,
    end_date: str | None = None,
) -> str:
    """Get historical dividend yield data for a stock or ETF.

    Args:
        ticker: Stock/ETF ticker symbol (e.g. AAPL, SPY).
        start_date: Start date in YYYY-MM-DD format.
        end_date: End date in YYYY-MM-DD format.
    """
    return await _safe_call(
        ctx,
        _get_client().get_dividend_yield(ticker, start_date=start_date, end_date=end_date),
    )


@mcp.tool
async def get_splits(
    ticker: str,
    ctx: Context,
    start_date: str | None = None,
    end_date: str | None = None,
) -> str:
    """Get historical stock split data.

    Args:
        ticker: Stock ticker symbol (e.g. AAPL, TSLA).
        start_date: Filter splits with ex-date on or after this date (YYYY-MM-DD).
        end_date: Filter splits with ex-date on or before this date (YYYY-MM-DD).
    """
    return await _safe_call(
        ctx,
        _get_client().get_splits(ticker, start_date=start_date, end_date=end_date),
    )


# ── Register resources and prompts ───────────────────────────────────

import tiingo_mcp.prompts  # noqa: E402
import tiingo_mcp.resources  # noqa: E402, F401
