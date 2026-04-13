# Resources & Prompts Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add 4 MCP resources (3 static + 1 template) and 5 MCP prompts to the tiingo-mcp server, making it a full-featured MCP reference implementation for financial data.

**Architecture:** New `resources.py` and `prompts.py` modules import the `mcp` instance from `server.py` and register decorators. `server.py` imports both modules at the bottom to trigger registration. All resources are static (no API calls). Prompts return `Message` sequences guiding LLMs through multi-step workflows.

**Tech Stack:** FastMCP 3.2 (`@mcp.resource`, `@mcp.prompt`), `fastmcp.prompts.Message`

**Spec:** `docs/superpowers/specs/2026-04-13-resources-and-prompts-design.md`

---

## File Structure

| File | Action | Responsibility |
|------|--------|----------------|
| `src/tiingo_mcp/resources.py` | Create | All `@mcp.resource` functions + static content dicts |
| `src/tiingo_mcp/prompts.py` | Create | All `@mcp.prompt` functions + message templates |
| `src/tiingo_mcp/server.py` | Modify (append 2 import lines) | Import resources/prompts modules to trigger registration |
| `tests/test_resources.py` | Create | Resource tests via FastMCP `Client` |
| `tests/test_prompts.py` | Create | Prompt tests via FastMCP `Client` |

---

### Task 1: Resources — `tiingo://capabilities`

**Files:**
- Create: `src/tiingo_mcp/resources.py`
- Create: `tests/test_resources.py`

- [ ] **Step 1: Write the failing test**

Create `tests/test_resources.py`:

```python
"""Tests for MCP resource registration and content."""

from __future__ import annotations

import json

from fastmcp import Client

from tiingo_mcp.server import mcp


async def test_capabilities_resource_listed():
    async with Client(mcp) as client:
        resources = await client.list_resources()
        uris = [str(r.uri) for r in resources]
        assert "tiingo://capabilities" in uris


async def test_capabilities_resource_content():
    async with Client(mcp) as client:
        result = await client.read_resource("tiingo://capabilities")
        data = json.loads(result.content[0].text)
        assert "asset_classes" in data
        assert "stocks" in data["asset_classes"]
        assert "forex" in data["asset_classes"]
        assert "crypto" in data["asset_classes"]
        assert "rate_limits" in data
        assert "plan_restrictions" in data
        assert data["server_version"] == "1.0.0"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run pytest tests/test_resources.py -v`
Expected: FAIL — `resources` module does not exist yet, no resources registered.

- [ ] **Step 3: Write minimal implementation**

Create `src/tiingo_mcp/resources.py`:

```python
"""MCP resources exposing static reference data for the Tiingo financial data API."""

from __future__ import annotations

import json

from tiingo_mcp.server import mcp

# ── Capabilities ─────────────────────────────────────────────────────

CAPABILITIES = {
    "server_name": "Tiingo MCP Server",
    "server_version": "1.0.0",
    "asset_classes": ["stocks", "forex", "crypto"],
    "data_types": {
        "stocks": ["metadata", "eod_prices", "realtime_prices", "intraday_prices"],
        "forex": ["quotes", "historical_prices"],
        "crypto": ["metadata", "quotes", "historical_prices"],
        "cross_asset": ["news", "fundamentals", "corporate_actions"],
    },
    "rate_limits": {
        "free": "50 requests/hour",
        "power": "5,000 requests/hour",
    },
    "plan_restrictions": {
        "free_tier": [
            "stocks (all endpoints)",
            "forex (all endpoints)",
            "crypto (all endpoints)",
            "news",
            "fundamentals",
            "dividend_yield",
        ],
        "paid_tier_required": [
            "dividends (distributions)",
            "splits",
        ],
    },
    "tool_count": 17,
}


@mcp.resource("tiingo://capabilities", description="Server capabilities, supported asset classes, rate limits, and plan restrictions")
def capabilities_resource() -> str:
    return json.dumps(CAPABILITIES, indent=2)
```

Add the import trigger at the bottom of `src/tiingo_mcp/server.py` (append after the last tool definition):

```python
# ── Register resources and prompts ───────────────────────────────────

import tiingo_mcp.resources  # noqa: E402, F401
```

- [ ] **Step 4: Run test to verify it passes**

Run: `uv run pytest tests/test_resources.py -v`
Expected: PASS

- [ ] **Step 5: Lint**

Run: `uv run ruff check src/tiingo_mcp/resources.py tests/test_resources.py`

- [ ] **Step 6: Commit**

```bash
git add src/tiingo_mcp/resources.py tests/test_resources.py src/tiingo_mcp/server.py
git commit -m "feat: add tiingo://capabilities resource"
```

---

### Task 2: Resources — `tiingo://fundamentals/definitions`

**Files:**
- Modify: `tests/test_resources.py`
- Modify: `src/tiingo_mcp/resources.py`

- [ ] **Step 1: Write the failing test**

Append to `tests/test_resources.py`:

```python
async def test_fundamentals_definitions_resource_listed():
    async with Client(mcp) as client:
        resources = await client.list_resources()
        uris = [str(r.uri) for r in resources]
        assert "tiingo://fundamentals/definitions" in uris


async def test_fundamentals_definitions_content():
    async with Client(mcp) as client:
        result = await client.read_resource("tiingo://fundamentals/definitions")
        data = json.loads(result.content[0].text)
        assert "metrics" in data
        metrics = data["metrics"]
        assert len(metrics) > 0
        first = metrics[0]
        assert "name" in first
        assert "description" in first
        assert "statement_type" in first
```

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run pytest tests/test_resources.py::test_fundamentals_definitions_resource_listed -v`
Expected: FAIL — resource not registered.

- [ ] **Step 3: Write minimal implementation**

Append to `src/tiingo_mcp/resources.py`:

```python
# ── Fundamentals Definitions ─────────────────────────────────────────

FUNDAMENTALS_DEFINITIONS = {
    "description": "Curated reference of commonly used Tiingo fundamental metrics. For the full raw list, use the get_fundamentals_definitions tool.",
    "metrics": [
        {"name": "marketCap", "description": "Total market capitalization (share price x shares outstanding)", "statement_type": "overview"},
        {"name": "peRatio", "description": "Price-to-earnings ratio (price / EPS TTM)", "statement_type": "overview"},
        {"name": "pbRatio", "description": "Price-to-book ratio (price / book value per share)", "statement_type": "overview"},
        {"name": "trailingPEG1Y", "description": "PEG ratio using 1-year trailing earnings growth", "statement_type": "overview"},
        {"name": "revenue", "description": "Total revenue / net sales for the period", "statement_type": "income_statement"},
        {"name": "costRev", "description": "Cost of revenue / cost of goods sold", "statement_type": "income_statement"},
        {"name": "grossProfit", "description": "Revenue minus cost of revenue", "statement_type": "income_statement"},
        {"name": "operatingIncome", "description": "Income from core business operations", "statement_type": "income_statement"},
        {"name": "netIncome", "description": "Bottom-line profit after all expenses, taxes, and interest", "statement_type": "income_statement"},
        {"name": "eps", "description": "Earnings per share (basic)", "statement_type": "income_statement"},
        {"name": "epsDil", "description": "Earnings per share (diluted)", "statement_type": "income_statement"},
        {"name": "totalAssets", "description": "Sum of all current and non-current assets", "statement_type": "balance_sheet"},
        {"name": "totalLiabilities", "description": "Sum of all current and long-term liabilities", "statement_type": "balance_sheet"},
        {"name": "totalEquity", "description": "Shareholders' equity (assets minus liabilities)", "statement_type": "balance_sheet"},
        {"name": "totalDebt", "description": "Short-term plus long-term debt", "statement_type": "balance_sheet"},
        {"name": "totalCash", "description": "Cash and cash equivalents", "statement_type": "balance_sheet"},
        {"name": "operatingCashFlow", "description": "Cash generated by core business operations", "statement_type": "cash_flow"},
        {"name": "investingCashFlow", "description": "Cash used for investments (capex, acquisitions)", "statement_type": "cash_flow"},
        {"name": "financingCashFlow", "description": "Cash from financing activities (debt, equity issuance, dividends)", "statement_type": "cash_flow"},
        {"name": "freeCashFlow", "description": "Operating cash flow minus capital expenditures", "statement_type": "cash_flow"},
    ],
}


@mcp.resource("tiingo://fundamentals/definitions", description="Curated reference of common fundamental metrics with descriptions and statement types")
def fundamentals_definitions_resource() -> str:
    return json.dumps(FUNDAMENTALS_DEFINITIONS, indent=2)
```

- [ ] **Step 4: Run test to verify it passes**

Run: `uv run pytest tests/test_resources.py -v`
Expected: All PASS

- [ ] **Step 5: Commit**

```bash
git add src/tiingo_mcp/resources.py tests/test_resources.py
git commit -m "feat: add tiingo://fundamentals/definitions resource"
```

---

### Task 3: Resources — `tiingo://guide/date-formats`

**Files:**
- Modify: `tests/test_resources.py`
- Modify: `src/tiingo_mcp/resources.py`

- [ ] **Step 1: Write the failing test**

Append to `tests/test_resources.py`:

```python
async def test_date_formats_resource_listed():
    async with Client(mcp) as client:
        resources = await client.list_resources()
        uris = [str(r.uri) for r in resources]
        assert "tiingo://guide/date-formats" in uris


async def test_date_formats_content():
    async with Client(mcp) as client:
        result = await client.read_resource("tiingo://guide/date-formats")
        data = json.loads(result.content[0].text)
        assert "date_format" in data
        assert data["date_format"] == "YYYY-MM-DD"
        assert "resample_frequencies" in data
        assert "stocks_eod" in data["resample_frequencies"]
        assert "intraday" in data["resample_frequencies"]
        assert "news_sort_options" in data
        assert "corporate_actions_date_params" in data
```

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run pytest tests/test_resources.py::test_date_formats_resource_listed -v`
Expected: FAIL

- [ ] **Step 3: Write minimal implementation**

Append to `src/tiingo_mcp/resources.py`:

```python
# ── Date Formats Guide ───────────────────────────────────────────────

DATE_FORMATS_GUIDE = {
    "date_format": "YYYY-MM-DD",
    "resample_frequencies": {
        "stocks_eod": ["daily", "weekly", "monthly", "annually"],
        "intraday": ["1min", "5min", "15min", "30min", "1hour"],
        "forex": ["1min", "5min", "15min", "30min", "1hour", "1day"],
        "crypto": ["1min", "5min", "15min", "30min", "1hour", "1day"],
    },
    "news_sort_options": ["crawlDate", "publishedDate"],
    "corporate_actions_date_params": {
        "dividends_and_splits": {
            "start_param": "startExDate",
            "end_param": "endExDate",
            "note": "These use ex-date, not regular startDate/endDate",
        },
        "dividend_yield": {
            "start_param": "startDate",
            "end_param": "endDate",
        },
    },
}


@mcp.resource("tiingo://guide/date-formats", description="Date format, resample frequencies, sort options, and parameter reference for all endpoints")
def date_formats_resource() -> str:
    return json.dumps(DATE_FORMATS_GUIDE, indent=2)
```

- [ ] **Step 4: Run test to verify it passes**

Run: `uv run pytest tests/test_resources.py -v`
Expected: All PASS

- [ ] **Step 5: Commit**

```bash
git add src/tiingo_mcp/resources.py tests/test_resources.py
git commit -m "feat: add tiingo://guide/date-formats resource"
```

---

### Task 4: Resources — `tiingo://guide/{asset_class}` template

**Files:**
- Modify: `tests/test_resources.py`
- Modify: `src/tiingo_mcp/resources.py`

- [ ] **Step 1: Write the failing tests**

Append to `tests/test_resources.py`:

```python
import pytest


VALID_ASSET_CLASSES = ["stocks", "forex", "crypto", "news", "fundamentals", "corporate-actions"]


async def test_guide_template_listed():
    async with Client(mcp) as client:
        templates = await client.list_resource_templates()
        uris = [str(t.uri_template) for t in templates]
        assert any("guide" in u and "asset_class" in u for u in uris)


@pytest.mark.parametrize("asset_class", VALID_ASSET_CLASSES)
async def test_guide_template_valid_asset_classes(asset_class: str):
    async with Client(mcp) as client:
        result = await client.read_resource(f"tiingo://guide/{asset_class}")
        data = json.loads(result.content[0].text)
        assert "asset_class" in data
        assert data["asset_class"] == asset_class
        assert "tools" in data
        assert "ticker_format" in data
        assert "workflows" in data


async def test_guide_template_invalid_asset_class():
    async with Client(mcp) as client:
        result = await client.read_resource("tiingo://guide/invalid")
        data = json.loads(result.content[0].text)
        assert "error" in data
        assert "valid values" in data["error"].lower() or "invalid" in data["error"].lower()
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `uv run pytest tests/test_resources.py::test_guide_template_listed -v`
Expected: FAIL

- [ ] **Step 3: Write minimal implementation**

Append to `src/tiingo_mcp/resources.py`:

```python
# ── Asset Class Guides ───────────────────────────────────────────────

ASSET_CLASS_GUIDES = {
    "stocks": {
        "asset_class": "stocks",
        "description": "US equity end-of-day and real-time price data",
        "tools": ["get_stock_metadata", "get_stock_prices", "get_realtime_price", "get_intraday_prices"],
        "ticker_format": "Standard US ticker symbols, e.g. AAPL, MSFT, GOOGL, TSLA",
        "workflows": [
            "Get metadata first to confirm ticker exists and see available date range",
            "Use get_stock_prices for historical EOD analysis (daily/weekly/monthly)",
            "Use get_realtime_price for current IEX top-of-book price",
            "Use get_intraday_prices for minute-level data (1min, 5min, 15min, 30min, 1hour)",
        ],
        "plan_restrictions": "All stock endpoints available on free tier",
        "common_pitfalls": [
            "Intraday data uses IEX exchange — not consolidated tape",
            "after_hours parameter only applies to get_realtime_price",
        ],
    },
    "forex": {
        "asset_class": "forex",
        "description": "Foreign exchange currency pair data",
        "tools": ["get_forex_quote", "get_forex_prices"],
        "ticker_format": "Lowercase currency pair, e.g. eurusd, gbpusd, usdjpy, audusd",
        "workflows": [
            "Use get_forex_quote for current top-of-book price",
            "Use get_forex_prices for historical data with resample support",
        ],
        "plan_restrictions": "All forex endpoints available on free tier",
        "common_pitfalls": [
            "Ticker must be lowercase (eurusd not EURUSD)",
            "Pairs are directional — eurusd and usdeur are different",
        ],
    },
    "crypto": {
        "asset_class": "crypto",
        "description": "Cryptocurrency price and metadata across exchanges",
        "tools": ["get_crypto_quote", "get_crypto_prices", "get_crypto_metadata"],
        "ticker_format": "Lowercase crypto pair, e.g. btcusd, ethusd, solusd, dogeusd",
        "workflows": [
            "Use get_crypto_metadata to discover available pairs and exchanges",
            "Use get_crypto_quote for current prices (omit tickers for all)",
            "Use get_crypto_prices for historical data with resample support",
        ],
        "plan_restrictions": "All crypto endpoints available on free tier",
        "common_pitfalls": [
            "Tickers are comma-separated for multi-asset queries",
            "Quote endpoint returns all cryptos if no tickers specified — can be large",
        ],
    },
    "news": {
        "asset_class": "news",
        "description": "Financial news articles from 50M+ sources",
        "tools": ["get_news"],
        "ticker_format": "Comma-separated standard tickers for filtering, e.g. AAPL,MSFT",
        "workflows": [
            "Filter by tickers for company-specific news",
            "Filter by tags for topic-specific news",
            "Filter by source for source-specific news",
            "Use sort_by to order by crawlDate or publishedDate",
            "Use limit and offset for pagination",
        ],
        "plan_restrictions": "Available on free tier",
        "common_pitfalls": [
            "Default limit is 10 articles — increase for broader searches",
            "crawlDate is when Tiingo found the article, publishedDate is when it was published",
        ],
    },
    "fundamentals": {
        "asset_class": "fundamentals",
        "description": "Company financial statements and daily valuation metrics",
        "tools": ["get_fundamentals_definitions", "get_financial_statements", "get_daily_fundamentals", "get_company_meta"],
        "ticker_format": "Standard US ticker symbols, e.g. AAPL, MSFT",
        "workflows": [
            "Use get_fundamentals_definitions or read tiingo://fundamentals/definitions for metric reference",
            "Use get_daily_fundamentals for daily valuation metrics (P/E, market cap)",
            "Use get_financial_statements for quarterly/annual income, balance sheet, cash flow",
            "Use get_company_meta for sector, industry, and location data",
        ],
        "plan_restrictions": "Available on free tier",
        "common_pitfalls": [
            "get_company_meta takes comma-separated tickers (can query multiple at once)",
            "Financial statements are quarterly by default — use date range to narrow",
        ],
    },
    "corporate-actions": {
        "asset_class": "corporate-actions",
        "description": "Dividends, splits, and dividend yield data",
        "tools": ["get_dividends", "get_dividend_yield", "get_splits"],
        "ticker_format": "Standard US ticker or ETF symbols, e.g. AAPL, SPY, VTI",
        "workflows": [
            "Use get_dividend_yield for historical yield data (free tier)",
            "Use get_dividends for detailed distribution history (paid tier)",
            "Use get_splits for stock split history (paid tier)",
        ],
        "plan_restrictions": "dividend_yield is free tier; dividends and splits require paid plan (403 on free tier)",
        "common_pitfalls": [
            "Dividends and splits use startExDate/endExDate params (not startDate/endDate)",
            "Dividend yield uses standard startDate/endDate params",
            "Free tier users will get 403 errors on dividends and splits endpoints",
        ],
    },
}

VALID_ASSET_CLASSES = list(ASSET_CLASS_GUIDES.keys())


@mcp.resource(
    "tiingo://guide/{asset_class}",
    description="Usage guide for a specific asset class: tools, workflows, ticker formats, and pitfalls",
)
def asset_class_guide_resource(asset_class: str) -> str:
    if asset_class not in ASSET_CLASS_GUIDES:
        return json.dumps({
            "error": f"Invalid asset class '{asset_class}'. Valid values: {', '.join(VALID_ASSET_CLASSES)}",
        })
    return json.dumps(ASSET_CLASS_GUIDES[asset_class], indent=2)
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `uv run pytest tests/test_resources.py -v`
Expected: All PASS

- [ ] **Step 5: Lint**

Run: `uv run ruff check src/tiingo_mcp/resources.py tests/test_resources.py`

- [ ] **Step 6: Commit**

```bash
git add src/tiingo_mcp/resources.py tests/test_resources.py
git commit -m "feat: add tiingo://guide/{asset_class} resource template"
```

---

### Task 5: Resource registration count test

**Files:**
- Modify: `tests/test_resources.py`

- [ ] **Step 1: Add a summary test to lock down the resource count**

Append to `tests/test_resources.py`:

```python
async def test_resource_count():
    async with Client(mcp) as client:
        resources = await client.list_resources()
        # 3 static resources: capabilities, fundamentals/definitions, guide/date-formats
        assert len(resources) == 3


async def test_resource_template_count():
    async with Client(mcp) as client:
        templates = await client.list_resource_templates()
        # 1 template: guide/{asset_class}
        assert len(templates) == 1
```

- [ ] **Step 2: Run to verify passing**

Run: `uv run pytest tests/test_resources.py -v`
Expected: All PASS

- [ ] **Step 3: Commit**

```bash
git add tests/test_resources.py
git commit -m "test: add resource count assertions"
```

---

### Task 6: Prompts — `analyze-stock`

**Files:**
- Create: `src/tiingo_mcp/prompts.py`
- Create: `tests/test_prompts.py`
- Modify: `src/tiingo_mcp/server.py` (add prompts import)

- [ ] **Step 1: Write the failing test**

Create `tests/test_prompts.py`:

```python
"""Tests for MCP prompt registration and content."""

from __future__ import annotations

from fastmcp import Client

from tiingo_mcp.server import mcp


async def test_analyze_stock_prompt_listed():
    async with Client(mcp) as client:
        prompts = await client.list_prompts()
        names = [p.name for p in prompts]
        assert "analyze-stock" in names


async def test_analyze_stock_prompt_content():
    async with Client(mcp) as client:
        result = await client.get_prompt("analyze-stock", arguments={"ticker": "AAPL"})
        assert len(result.messages) >= 1
        assert result.messages[0].role == "user"
        text = result.messages[0].content.text
        assert "AAPL" in text
        assert "get_stock_metadata" in text
        assert "get_stock_prices" in text
        assert "get_daily_fundamentals" in text


async def test_analyze_stock_with_news_disabled():
    async with Client(mcp) as client:
        result = await client.get_prompt(
            "analyze-stock",
            arguments={"ticker": "MSFT", "include_news": "false"},
        )
        text = result.messages[0].content.text
        assert "MSFT" in text
        assert "get_news" not in text or "skip" in text.lower() or "do not" in text.lower()
```

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run pytest tests/test_prompts.py -v`
Expected: FAIL — `prompts` module does not exist yet.

- [ ] **Step 3: Write minimal implementation**

Create `src/tiingo_mcp/prompts.py`:

```python
"""MCP prompts providing reusable financial analysis workflow templates."""

from __future__ import annotations

from fastmcp.prompts import Message

from tiingo_mcp.server import mcp


@mcp.prompt(
    name="analyze-stock",
    description="Comprehensive single-stock analysis: metadata, prices, fundamentals, and news",
)
def analyze_stock_prompt(ticker: str, include_news: bool = True) -> list[Message]:
    news_section = f"""
4. Fetch recent news using `get_news` with tickers="{ticker}" and limit=5.
   - Identify key catalysts, sentiment, and upcoming events."""

    skip_news = """
4. Skip the news step (news was excluded from this analysis)."""

    return [
        Message(
            role="user",
            content=f"""Perform a comprehensive analysis of {ticker} using the Tiingo MCP Server tools. Follow these steps in order:

1. Fetch company metadata using `get_stock_metadata` with ticker="{ticker}".
   - Note the company name, exchange, description, and available date range.

2. Fetch recent price history using `get_stock_prices` with ticker="{ticker}" for the last 30 days.
   - Identify the price trend (up, down, sideways), recent highs/lows, and volatility.

3. Fetch daily fundamentals using `get_daily_fundamentals` with ticker="{ticker}" for the most recent data.
   - Note key metrics: market cap, P/E ratio, P/B ratio, and EPS.
{news_section if include_news else skip_news}

5. Synthesize your findings into a structured report:
   - **Company Overview**: Name, exchange, sector (if available)
   - **Price Trend**: 30-day direction, key levels, volatility assessment
   - **Valuation Snapshot**: P/E, P/B, market cap, and how they compare to typical ranges
   - **Recent Catalysts**: Key news and events (if included)
   - **Summary**: Bull case, bear case, and overall assessment""",
        )
    ]
```

Add the prompts import to the bottom of `src/tiingo_mcp/server.py` (next to the resources import):

```python
import tiingo_mcp.prompts  # noqa: E402, F401
```

- [ ] **Step 4: Run test to verify it passes**

Run: `uv run pytest tests/test_prompts.py -v`
Expected: All PASS

- [ ] **Step 5: Lint**

Run: `uv run ruff check src/tiingo_mcp/prompts.py tests/test_prompts.py`

- [ ] **Step 6: Commit**

```bash
git add src/tiingo_mcp/prompts.py tests/test_prompts.py src/tiingo_mcp/server.py
git commit -m "feat: add analyze-stock prompt"
```

---

### Task 7: Prompts — `compare-stocks`

**Files:**
- Modify: `tests/test_prompts.py`
- Modify: `src/tiingo_mcp/prompts.py`

- [ ] **Step 1: Write the failing test**

Append to `tests/test_prompts.py`:

```python
async def test_compare_stocks_prompt_listed():
    async with Client(mcp) as client:
        prompts = await client.list_prompts()
        names = [p.name for p in prompts]
        assert "compare-stocks" in names


async def test_compare_stocks_prompt_content():
    async with Client(mcp) as client:
        result = await client.get_prompt(
            "compare-stocks",
            arguments={"ticker1": "AAPL", "ticker2": "MSFT"},
        )
        assert len(result.messages) >= 1
        text = result.messages[0].content.text
        assert "AAPL" in text
        assert "MSFT" in text
        assert "get_stock_prices" in text
        assert "get_daily_fundamentals" in text
```

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run pytest tests/test_prompts.py::test_compare_stocks_prompt_listed -v`
Expected: FAIL

- [ ] **Step 3: Write minimal implementation**

Append to `src/tiingo_mcp/prompts.py`:

```python
@mcp.prompt(
    name="compare-stocks",
    description="Side-by-side comparison of two stocks: prices, fundamentals, and performance",
)
def compare_stocks_prompt(ticker1: str, ticker2: str, period: str = "3 months") -> list[Message]:
    return [
        Message(
            role="user",
            content=f"""Compare {ticker1} and {ticker2} side-by-side over the last {period} using the Tiingo MCP Server tools. Follow these steps:

1. Fetch price history for both stocks using `get_stock_prices`:
   - Call with ticker="{ticker1}" for the last {period}
   - Call with ticker="{ticker2}" for the last {period}
   - Compare: starting price, ending price, percent change, high, low

2. Fetch daily fundamentals for both using `get_daily_fundamentals`:
   - Call with ticker="{ticker1}" for the most recent data
   - Call with ticker="{ticker2}" for the most recent data
   - Compare: P/E ratio, market cap, P/B ratio, EPS

3. Fetch dividend yield for both using `get_dividend_yield`:
   - Call with ticker="{ticker1}"
   - Call with ticker="{ticker2}"

4. Present a structured comparison:
   - **Price Performance** ({period}): table with start price, end price, % change, high, low
   - **Valuation**: table with P/E, P/B, market cap, EPS
   - **Dividends**: current yield for each
   - **Verdict**: which stock performed better and why, with caveats""",
        )
    ]
```

- [ ] **Step 4: Run test to verify it passes**

Run: `uv run pytest tests/test_prompts.py -v`
Expected: All PASS

- [ ] **Step 5: Commit**

```bash
git add src/tiingo_mcp/prompts.py tests/test_prompts.py
git commit -m "feat: add compare-stocks prompt"
```

---

### Task 8: Prompts — `crypto-market-overview`

**Files:**
- Modify: `tests/test_prompts.py`
- Modify: `src/tiingo_mcp/prompts.py`

- [ ] **Step 1: Write the failing test**

Append to `tests/test_prompts.py`:

```python
async def test_crypto_market_overview_prompt_listed():
    async with Client(mcp) as client:
        prompts = await client.list_prompts()
        names = [p.name for p in prompts]
        assert "crypto-market-overview" in names


async def test_crypto_market_overview_prompt_content():
    async with Client(mcp) as client:
        result = await client.get_prompt("crypto-market-overview", arguments={})
        text = result.messages[0].content.text
        assert "btcusd" in text
        assert "ethusd" in text
        assert "get_crypto_quote" in text
        assert "get_crypto_prices" in text


async def test_crypto_market_overview_custom_tickers():
    async with Client(mcp) as client:
        result = await client.get_prompt(
            "crypto-market-overview",
            arguments={"tickers": "btcusd,dogeusd"},
        )
        text = result.messages[0].content.text
        assert "btcusd" in text
        assert "dogeusd" in text
```

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run pytest tests/test_prompts.py::test_crypto_market_overview_prompt_listed -v`
Expected: FAIL

- [ ] **Step 3: Write minimal implementation**

Append to `src/tiingo_mcp/prompts.py`:

```python
@mcp.prompt(
    name="crypto-market-overview",
    description="Crypto market snapshot: current prices, 24h changes, and 7-day trends",
)
def crypto_market_overview_prompt(tickers: str = "btcusd,ethusd,solusd") -> list[Message]:
    return [
        Message(
            role="user",
            content=f"""Provide a crypto market overview for the following tickers: {tickers}. Use the Tiingo MCP Server tools:

1. Fetch current quotes using `get_crypto_quote` with tickers="{tickers}".
   - Note: last price, 24h high/low, and volume for each.

2. Fetch 7-day price history using `get_crypto_prices` with tickers="{tickers}" and resample_freq="1hour" for the last 7 days.
   - Calculate: 7-day percent change, highest price, lowest price for each ticker.

3. Present a market overview:
   - **Current Prices**: table with ticker, last price, 24h high, 24h low, volume
   - **7-Day Performance**: table with ticker, 7d % change, 7d high, 7d low
   - **Relative Performance**: which crypto performed best/worst over 7 days
   - **Market Summary**: overall sentiment (bullish/bearish/mixed) based on the data""",
        )
    ]
```

- [ ] **Step 4: Run test to verify it passes**

Run: `uv run pytest tests/test_prompts.py -v`
Expected: All PASS

- [ ] **Step 5: Commit**

```bash
git add src/tiingo_mcp/prompts.py tests/test_prompts.py
git commit -m "feat: add crypto-market-overview prompt"
```

---

### Task 9: Prompts — `earnings-report-analysis`

**Files:**
- Modify: `tests/test_prompts.py`
- Modify: `src/tiingo_mcp/prompts.py`

- [ ] **Step 1: Write the failing test**

Append to `tests/test_prompts.py`:

```python
async def test_earnings_report_prompt_listed():
    async with Client(mcp) as client:
        prompts = await client.list_prompts()
        names = [p.name for p in prompts]
        assert "earnings-report-analysis" in names


async def test_earnings_report_prompt_content():
    async with Client(mcp) as client:
        result = await client.get_prompt(
            "earnings-report-analysis",
            arguments={"ticker": "AAPL", "earnings_date": "2025-01-30"},
        )
        text = result.messages[0].content.text
        assert "AAPL" in text
        assert "2025-01-30" in text
        assert "get_financial_statements" in text
        assert "get_stock_prices" in text
        assert "get_news" in text
```

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run pytest tests/test_prompts.py::test_earnings_report_prompt_listed -v`
Expected: FAIL

- [ ] **Step 3: Write minimal implementation**

Append to `src/tiingo_mcp/prompts.py`:

```python
@mcp.prompt(
    name="earnings-report-analysis",
    description="Analyze a stock's earnings report: financials, price reaction, and news sentiment",
)
def earnings_report_analysis_prompt(ticker: str, earnings_date: str) -> list[Message]:
    return [
        Message(
            role="user",
            content=f"""Analyze {ticker}'s earnings report around {earnings_date} using the Tiingo MCP Server tools. Follow these steps:

1. Fetch financial statements using `get_financial_statements` with ticker="{ticker}".
   - Use a date range that includes {earnings_date} (e.g., a few months before and after).
   - Identify the quarterly report closest to {earnings_date}.
   - Note: revenue, net income, EPS, and any significant changes from prior quarters.

2. Fetch price data around the earnings date using `get_stock_prices` with ticker="{ticker}".
   - Get prices for 2 weeks before and 2 weeks after {earnings_date}.
   - Identify: pre-earnings price, post-earnings price, gap up/down, and subsequent trend.

3. Fetch news around the earnings date using `get_news` with tickers="{ticker}".
   - Use a date range of 1 week before to 1 week after {earnings_date}.
   - Identify: analyst reactions, guidance commentary, and sentiment.

4. Synthesize an earnings analysis:
   - **Earnings Summary**: revenue, EPS, net income vs. prior quarter and year-ago quarter
   - **Price Reaction**: pre-earnings close, post-earnings open, gap %, and 2-week follow-through
   - **News Sentiment**: key analyst reactions, guidance tone (raised/maintained/lowered)
   - **Assessment**: was the market reaction justified by the numbers?""",
        )
    ]
```

- [ ] **Step 4: Run test to verify it passes**

Run: `uv run pytest tests/test_prompts.py -v`
Expected: All PASS

- [ ] **Step 5: Commit**

```bash
git add src/tiingo_mcp/prompts.py tests/test_prompts.py
git commit -m "feat: add earnings-report-analysis prompt"
```

---

### Task 10: Prompts — `forex-pair-analysis`

**Files:**
- Modify: `tests/test_prompts.py`
- Modify: `src/tiingo_mcp/prompts.py`

- [ ] **Step 1: Write the failing test**

Append to `tests/test_prompts.py`:

```python
async def test_forex_pair_prompt_listed():
    async with Client(mcp) as client:
        prompts = await client.list_prompts()
        names = [p.name for p in prompts]
        assert "forex-pair-analysis" in names


async def test_forex_pair_prompt_content():
    async with Client(mcp) as client:
        result = await client.get_prompt(
            "forex-pair-analysis",
            arguments={"pair": "eurusd"},
        )
        text = result.messages[0].content.text
        assert "eurusd" in text
        assert "get_forex_quote" in text
        assert "get_forex_prices" in text
```

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run pytest tests/test_prompts.py::test_forex_pair_prompt_listed -v`
Expected: FAIL

- [ ] **Step 3: Write minimal implementation**

Append to `src/tiingo_mcp/prompts.py`:

```python
@mcp.prompt(
    name="forex-pair-analysis",
    description="Currency pair analysis: current rate, historical trend, and volatility",
)
def forex_pair_analysis_prompt(pair: str, period: str = "1 month") -> list[Message]:
    return [
        Message(
            role="user",
            content=f"""Analyze the {pair} currency pair over the last {period} using the Tiingo MCP Server tools:

1. Fetch the current quote using `get_forex_quote` with ticker="{pair}".
   - Note: current mid price, bid, ask, and spread.

2. Fetch historical prices using `get_forex_prices` with ticker="{pair}" for the last {period}.
   - Use resample_freq="1day" for daily data points.
   - Calculate: period high, period low, opening price, percent change.

3. Present a currency pair analysis:
   - **Current Rate**: mid price, bid/ask spread
   - **Trend Analysis**: direction over {period}, key support/resistance levels
   - **Volatility**: daily range analysis, high-low spread as percentage
   - **Summary**: overall trend assessment and notable observations""",
        )
    ]
```

- [ ] **Step 4: Run test to verify it passes**

Run: `uv run pytest tests/test_prompts.py -v`
Expected: All PASS

- [ ] **Step 5: Commit**

```bash
git add src/tiingo_mcp/prompts.py tests/test_prompts.py
git commit -m "feat: add forex-pair-analysis prompt"
```

---

### Task 11: Prompt count test + verify existing tests still pass

**Files:**
- Modify: `tests/test_prompts.py`

- [ ] **Step 1: Add prompt count test**

Append to `tests/test_prompts.py`:

```python
async def test_prompt_count():
    async with Client(mcp) as client:
        prompts = await client.list_prompts()
        assert len(prompts) == 5


async def test_all_prompts_have_descriptions():
    async with Client(mcp) as client:
        prompts = await client.list_prompts()
        for prompt in prompts:
            assert prompt.description, f"Prompt {prompt.name} has no description"
            assert len(prompt.description) > 10, f"Prompt {prompt.name} has short description"
```

- [ ] **Step 2: Run full test suite to verify nothing is broken**

Run: `uv run pytest -v`
Expected: All tests pass — existing tool tests, new resource tests, new prompt tests.

- [ ] **Step 3: Lint entire project**

Run: `uv run ruff check src/ tests/`

- [ ] **Step 4: Commit**

```bash
git add tests/test_prompts.py
git commit -m "test: add prompt count and description assertions"
```

---

### Task 12: Update server.py tool count test

**Files:**
- Modify: `tests/test_server.py`

The existing `test_tool_count` asserts exactly 17 tools. Resources and prompts don't change this, but verify it still passes and that the tool list in `test_server.py` doesn't need updating.

- [ ] **Step 1: Run the existing server tests**

Run: `uv run pytest tests/test_server.py -v`
Expected: All PASS — tools are unchanged, resources/prompts don't affect tool list.

- [ ] **Step 2: Final full test run**

Run: `uv run pytest -v`
Expected: All PASS.

- [ ] **Step 3: Final lint**

Run: `uv run ruff check src/ tests/`
Run: `uv run ruff format --check src/ tests/`

- [ ] **Step 4: Commit any fixes if needed**

Only if lint or format found issues:

```bash
git add -u
git commit -m "style: fix lint/format issues"
```
