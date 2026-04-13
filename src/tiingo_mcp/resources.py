"""MCP resources for the Tiingo MCP server -- all static, no API calls."""

from __future__ import annotations

import json

from tiingo_mcp.server import mcp

# ── Asset class guides ────────────────────────────────────────────────

ASSET_CLASS_GUIDES: dict[str, dict] = {
    "stocks": {
        "asset_class": "stocks",
        "description": (
            "US and international equities with EOD historical prices, real-time IEX quotes,"
            " and intraday data."
        ),
        "tools": [
            "get_stock_metadata",
            "get_stock_prices",
            "get_realtime_price",
            "get_intraday_prices",
        ],
        "ticker_format": "Uppercase symbols, e.g. AAPL, MSFT, GOOGL, BRK.B",
        "workflows": [
            (
                "Fetch metadata first with get_stock_metadata to verify ticker validity"
                " and date range."
            ),
            (
                "Use get_stock_prices for EOD OHLCV history; supports"
                " daily/weekly/monthly/annually resampling."
            ),
            "Use get_realtime_price for current IEX top-of-book price during market hours.",
            (
                "Use get_intraday_prices for sub-daily data at 1min, 5min, 15min, 30min,"
                " or 1hour intervals."
            ),
        ],
        "plan_restrictions": "All stock endpoints available on free tier.",
        "common_pitfalls": [
            "Ticker symbols are case-sensitive in the URL -- always uppercase.",
            (
                "Intraday data is limited to recent history; check metadata for available"
                " date range."
            ),
            (
                "get_realtime_price may return stale data outside market hours"
                " unless after_hours=True."
            ),
        ],
    },
    "forex": {
        "asset_class": "forex",
        "description": (
            "Foreign exchange currency pairs with real-time quotes and historical prices."
        ),
        "tools": [
            "get_forex_quote",
            "get_forex_prices",
        ],
        "ticker_format": "Lowercase concatenated pair, e.g. eurusd, gbpusd, usdjpy",
        "workflows": [
            "Use get_forex_quote for the current top-of-book bid/ask for a pair.",
            (
                "Use get_forex_prices for historical OHLCV data;"
                " supports 1min to 1day resampling."
            ),
        ],
        "plan_restrictions": "Available on free tier.",
        "common_pitfalls": [
            "Tickers must be lowercase (eurusd, not EURUSD).",
            "Forex market is 24/5 -- weekends have no data.",
            "resample_freq '1day' is distinct from EOD stock resampling.",
        ],
    },
    "crypto": {
        "asset_class": "crypto",
        "description": "Cryptocurrency prices, metadata, and historical data across exchanges.",
        "tools": [
            "get_crypto_quote",
            "get_crypto_prices",
            "get_crypto_metadata",
        ],
        "ticker_format": "Lowercase base+quote, e.g. btcusd, ethusd, solusd",
        "workflows": [
            "Use get_crypto_metadata to discover available tickers and supported exchanges.",
            (
                "Use get_crypto_quote for current prices;"
                " omit tickers to get all supported cryptos."
            ),
            (
                "Use get_crypto_prices for historical OHLCV data at various intraday"
                " or daily intervals."
            ),
            (
                "Pass comma-separated tickers to get_crypto_prices for multiple assets"
                " at once."
            ),
        ],
        "plan_restrictions": "Available on free tier.",
        "common_pitfalls": [
            "Crypto tickers are lowercase (btcusd, not BTCUSD).",
            "Crypto trades 24/7 -- no market-hours limitation.",
            (
                "get_crypto_quote with no tickers returns a large payload;"
                " filter by tickers when possible."
            ),
        ],
    },
    "news": {
        "asset_class": "news",
        "description": (
            "Financial news articles from 50M+ sources, filterable by ticker, tag, and source."
        ),
        "tools": [
            "get_news",
        ],
        "ticker_format": "Comma-separated uppercase symbols, e.g. AAPL,MSFT",
        "workflows": [
            "Filter by tickers to get company-specific news; multiple tickers = OR logic.",
            "Filter by tags for topic-based news (e.g. earnings, dividends).",
            "Use start_date/end_date to restrict date range; default returns most recent.",
            "Paginate with limit and offset for large result sets.",
            (
                "Use sort_by='crawlDate' for recency or 'publishedDate'"
                " for article publish date."
            ),
        ],
        "plan_restrictions": "Available on free tier.",
        "common_pitfalls": [
            "Default limit is 10 articles -- increase for broader searches.",
            "Omitting tickers returns broad market news, not company-specific.",
            "sort_by values are crawlDate and publishedDate (exact case required).",
        ],
    },
    "fundamentals": {
        "asset_class": "fundamentals",
        "description": (
            "Company financial statements, daily fundamental metrics, definitions,"
            " and company metadata."
        ),
        "tools": [
            "get_fundamentals_definitions",
            "get_financial_statements",
            "get_daily_fundamentals",
            "get_company_meta",
        ],
        "ticker_format": "Uppercase symbols, e.g. AAPL, MSFT",
        "workflows": [
            (
                "Call get_fundamentals_definitions once to understand available metrics"
                " and their types."
            ),
            (
                "Use get_financial_statements for quarterly/annual income, balance sheet,"
                " and cash flow data."
            ),
            (
                "Use get_daily_fundamentals for time-series of daily metrics like marketCap"
                " and P/E ratio."
            ),
            (
                "Use get_company_meta for sector, industry, country, and SIC code;"
                " supports multiple tickers."
            ),
        ],
        "plan_restrictions": "All fundamentals endpoints available on free tier.",
        "common_pitfalls": [
            "Financial statements are reported quarterly; don't expect daily granularity.",
            (
                "get_daily_fundamentals returns many rows --"
                " use start_date/end_date to limit results."
            ),
            "get_company_meta accepts comma-separated tickers for batch lookups.",
        ],
    },
    "corporate-actions": {
        "asset_class": "corporate-actions",
        "description": (
            "Dividends, dividend yield history, and stock splits for equities and ETFs."
        ),
        "tools": [
            "get_dividends",
            "get_dividend_yield",
            "get_splits",
        ],
        "ticker_format": "Uppercase symbols, e.g. AAPL, SPY, TSLA",
        "workflows": [
            (
                "Use get_dividends for historical cash distributions;"
                " dates filter by ex-dividend date."
            ),
            "Use get_dividend_yield for time-series of yield percentage.",
            "Use get_splits for historical split events; dates filter by ex-split date.",
            (
                "For dividends and splits, start_date/end_date map to"
                " startExDate/endExDate internally."
            ),
            "For dividend_yield, start_date/end_date map to startDate/endDate.",
        ],
        "plan_restrictions": (
            "get_dividends and get_splits return 403 on free tier;"
            " get_dividend_yield is available on free tier."
        ),
        "common_pitfalls": [
            "get_dividends and get_splits require a paid plan -- free tier returns 403.",
            "Date params for dividends/splits filter by ex-date, not payment date.",
            "ETFs (e.g. SPY, QQQ) have dividend data via get_dividends.",
        ],
    },
}

VALID_ASSET_CLASSES = sorted(ASSET_CLASS_GUIDES.keys())


# ── Resource 1: capabilities ──────────────────────────────────────────


@mcp.resource(
    "tiingo://capabilities",
    description=(
        "Server capabilities, supported asset classes, rate limits, and plan restrictions"
    ),
)
def capabilities_resource() -> str:
    """Return static server capability metadata."""
    data = {
        "server_name": "Tiingo MCP Server",
        "server_version": "1.0.0",
        "asset_classes": {
            "stocks": {
                "description": "US and international equities",
                "data_types": [
                    "eod_prices",
                    "intraday_prices",
                    "realtime_quote",
                    "metadata",
                ],
            },
            "forex": {
                "description": "Foreign exchange currency pairs",
                "data_types": ["realtime_quote", "historical_prices"],
            },
            "crypto": {
                "description": "Cryptocurrencies across exchanges",
                "data_types": ["realtime_quote", "historical_prices", "metadata"],
            },
        },
        "rate_limits": {
            "free": "50 req/hr",
            "power": "5000 req/hr",
        },
        "plan_restrictions": {
            "free_tier": [
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
                "get_dividend_yield",
            ],
            "paid_tier_required": [
                "get_dividends",
                "get_splits",
            ],
        },
        "tool_count": 17,
    }
    return json.dumps(data)


# ── Resource 2: fundamentals definitions ─────────────────────────────


@mcp.resource(
    "tiingo://fundamentals/definitions",
    description=(
        "Curated reference of common fundamental metrics with descriptions and statement types"
    ),
)
def fundamentals_definitions_resource() -> str:
    """Return a curated reference of common fundamental metrics."""
    data = {
        "description": (
            "Curated reference of common Tiingo fundamental metrics. "
            "Use get_fundamentals_definitions tool to fetch the full live list from the API."
        ),
        "metrics": [
            # Overview / daily
            {
                "name": "marketCap",
                "description": "Market capitalisation (shares outstanding x price)",
                "statement_type": "overview",
            },
            {
                "name": "peRatio",
                "description": "Price-to-earnings ratio (price / trailing EPS)",
                "statement_type": "overview",
            },
            {
                "name": "pbRatio",
                "description": "Price-to-book ratio (price / book value per share)",
                "statement_type": "overview",
            },
            {
                "name": "trailingPEG1Y",
                "description": "Trailing PEG ratio over 1 year (P/E / earnings growth rate)",
                "statement_type": "overview",
            },
            # Income statement
            {
                "name": "revenue",
                "description": "Total revenue (net sales)",
                "statement_type": "income_statement",
            },
            {
                "name": "costRev",
                "description": "Cost of revenue (cost of goods sold)",
                "statement_type": "income_statement",
            },
            {
                "name": "grossProfit",
                "description": "Gross profit (revenue - cost of revenue)",
                "statement_type": "income_statement",
            },
            {
                "name": "operatingIncome",
                "description": "Operating income (EBIT before interest and taxes)",
                "statement_type": "income_statement",
            },
            {
                "name": "netIncome",
                "description": "Net income attributable to common shareholders",
                "statement_type": "income_statement",
            },
            {
                "name": "eps",
                "description": "Basic earnings per share",
                "statement_type": "income_statement",
            },
            {
                "name": "epsDil",
                "description": "Diluted earnings per share",
                "statement_type": "income_statement",
            },
            # Balance sheet
            {
                "name": "totalAssets",
                "description": "Total assets",
                "statement_type": "balance_sheet",
            },
            {
                "name": "totalLiabilities",
                "description": "Total liabilities",
                "statement_type": "balance_sheet",
            },
            {
                "name": "totalEquity",
                "description": "Total shareholders equity",
                "statement_type": "balance_sheet",
            },
            {
                "name": "totalDebt",
                "description": "Total debt (short-term + long-term borrowings)",
                "statement_type": "balance_sheet",
            },
            {
                "name": "totalCash",
                "description": "Cash and cash equivalents",
                "statement_type": "balance_sheet",
            },
            # Cash flow
            {
                "name": "operatingCashFlow",
                "description": "Net cash from operating activities",
                "statement_type": "cash_flow",
            },
            {
                "name": "investingCashFlow",
                "description": "Net cash from investing activities",
                "statement_type": "cash_flow",
            },
            {
                "name": "financingCashFlow",
                "description": "Net cash from financing activities",
                "statement_type": "cash_flow",
            },
            {
                "name": "freeCashFlow",
                "description": (
                    "Free cash flow (operating cash flow - capital expenditures)"
                ),
                "statement_type": "cash_flow",
            },
        ],
    }
    return json.dumps(data)


# ── Resource 3: date formats guide ───────────────────────────────────


@mcp.resource(
    "tiingo://guide/date-formats",
    description=(
        "Date format, resample frequencies, sort options, and parameter reference"
        " for all endpoints"
    ),
)
def date_formats_resource() -> str:
    """Return date format and parameter reference for all endpoints."""
    data = {
        "date_format": "YYYY-MM-DD",
        "resample_frequencies": {
            "stocks_eod": ["daily", "weekly", "monthly", "annually"],
            "intraday": ["1min", "5min", "15min", "30min", "1hour"],
            "forex": ["1min", "5min", "15min", "30min", "1hour", "1day"],
            "crypto": ["1min", "5min", "15min", "30min", "1hour", "1day"],
        },
        "news_sort_options": ["crawlDate", "publishedDate"],
        "corporate_actions_date_params": {
            "note": (
                "Dividends and splits filter by ex-date;"
                " dividend_yield filters by calendar date."
            ),
            "dividends_and_splits": {
                "start_date_maps_to": "startExDate",
                "end_date_maps_to": "endExDate",
            },
            "dividend_yield": {
                "start_date_maps_to": "startDate",
                "end_date_maps_to": "endDate",
            },
        },
    }
    return json.dumps(data)


# ── Resource 4: asset class guide (template) ─────────────────────────


@mcp.resource(
    "tiingo://guide/{asset_class}",
    description=(
        "Usage guide for a specific asset class: tools, workflows, ticker formats, and pitfalls"
    ),
)
def asset_class_guide_resource(asset_class: str) -> str:
    """Return a usage guide for the given asset class."""
    guide = ASSET_CLASS_GUIDES.get(asset_class)
    if guide is None:
        error = {
            "error": (
                f"Invalid asset class '{asset_class}'."
                f" Valid values: {', '.join(VALID_ASSET_CLASSES)}"
            )
        }
        return json.dumps(error)
    return json.dumps(guide)
