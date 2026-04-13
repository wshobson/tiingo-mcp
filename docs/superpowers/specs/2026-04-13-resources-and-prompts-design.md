# Tiingo MCP Server: Resources & Prompts Design

## Overview

Expand the tiingo-mcp server beyond tools to include MCP resources and prompts, making it a full-featured reference implementation of the MCP spec for financial data.

**Decisions made:**
- Target audience: Both LLM agents and developers (full reference implementation)
- Resources and prompts ship together in one pass
- Resources are static/derived only — no live API calls (preserves rate limits, clean mental model)
- Approach B: Comprehensive — categorized resources + workflow prompts

## Resources

All resources return static/derived content. No Tiingo API calls are made when resources are read.

### 1. `tiingo://capabilities` (static)

Server capability overview. Returns JSON describing:
- Supported asset classes: stocks, forex, crypto
- Available data types: prices (EOD, intraday, real-time), fundamentals, news, corporate actions
- Rate limit tiers: free (50 req/hr), power (5,000 req/hr)
- Plan-restricted endpoints: dividends and splits require paid tier; dividend yield is free
- Server version and tool count

### 2. `tiingo://fundamentals/definitions` (static)

Curated fundamentals metric reference. Returns a JSON summary of the most commonly used fundamental metrics (market cap, P/E, EPS, revenue, etc.) with plain-language descriptions and which statement type they come from (income, balance sheet, cash flow). This is a curated subset — the full raw definitions list is still available via the `get_fundamentals_definitions` tool. The resource costs zero API calls and prevents the common pattern where an LLM calls the definitions tool before every fundamentals query.

### 3. `tiingo://guide/date-formats` (static)

Date format and parameter reference. Covers:
- Date format: YYYY-MM-DD
- Resample frequencies per asset class:
  - Stocks EOD: daily, weekly, monthly, annually
  - Intraday/Forex/Crypto: 1min, 5min, 15min, 30min, 1hour, 1day
- News sort options: crawlDate, publishedDate
- Corporate actions date params: startExDate/endExDate (not startDate/endDate)

### 4. `tiingo://guide/{asset_class}` (resource template)

Usage guide parameterized by asset class. Valid values: `stocks`, `forex`, `crypto`, `news`, `fundamentals`, `corporate-actions`.

Each guide includes:
- Available tools for that asset class
- Typical analysis workflows
- Parameter guidance and examples
- Ticker format (e.g., `AAPL` for stocks, `eurusd` for forex, `btcusd` for crypto)
- Plan-tier restrictions (if any)
- Common pitfalls

**Total: 4 resource registrations** (3 static + 1 template serving 6 asset classes).

## Prompts

Each prompt returns a `user` Message containing structured analysis instructions. The LLM executes the workflow by calling the server's tools. Prompts do not call tools themselves.

### 1. `analyze-stock`

Comprehensive single-stock analysis.

**Args:**
- `ticker` (str, required): Stock ticker symbol
- `include_news` (bool, optional, default true): Whether to include recent news

**Workflow guidance:**
1. Fetch metadata via `get_stock_metadata`
2. Pull recent prices via `get_stock_prices` (last 30 days)
3. Get daily fundamentals via `get_daily_fundamentals` (P/E, market cap)
4. Optionally fetch recent news via `get_news`
5. Synthesize: price trend, valuation snapshot, recent catalysts

### 2. `compare-stocks`

Side-by-side comparison of two tickers.

**Args:**
- `ticker1` (str, required): First stock ticker
- `ticker2` (str, required): Second stock ticker
- `period` (str, optional, default "3 months"): Comparison period

**Workflow guidance:**
1. Fetch prices and fundamentals for both tickers
2. Produce comparative table: price performance, P/E ratio, market cap, dividend yield

### 3. `crypto-market-overview`

Snapshot of the crypto market.

**Args:**
- `tickers` (str, optional, default "btcusd,ethusd,solusd"): Comma-separated crypto tickers

**Workflow guidance:**
1. Fetch current quotes via `get_crypto_quote`
2. Fetch recent price history via `get_crypto_prices` (7 days)
3. Summarize: current prices, 24h change, 7-day trend, relative performance

### 4. `earnings-report-analysis`

Analyze a stock around an earnings date.

**Args:**
- `ticker` (str, required): Stock ticker symbol
- `earnings_date` (str, required): Earnings date in YYYY-MM-DD format

**Workflow guidance:**
1. Pull financial statements spanning the earnings date via `get_financial_statements`
2. Fetch price data for 2-week window around the date via `get_stock_prices`
3. Fetch news around that period via `get_news`
4. Analyze: earnings surprise, price reaction, sentiment shift

### 5. `forex-pair-analysis`

Currency pair analysis.

**Args:**
- `pair` (str, required): Currency pair (e.g., "eurusd")
- `period` (str, optional, default "1 month"): Analysis period

**Workflow guidance:**
1. Fetch current quote via `get_forex_quote`
2. Fetch historical prices via `get_forex_prices`
3. Analyze: trend, volatility, key levels

**Total: 5 prompt registrations.**

## Code Organization

```
src/tiingo_mcp/
├── __init__.py          # (unchanged)
├── client.py            # (unchanged)
├── server.py            # FastMCP instance + tools; imports resources/prompts to trigger registration
├── resources.py         # @mcp.resource functions + static content
└── prompts.py           # @mcp.prompt functions + message templates
```

- `resources.py` and `prompts.py` import `mcp` from `server.py` to register their decorators
- `server.py` imports both modules at the bottom to trigger registration
- Static content (capabilities dict, guide text, definitions) lives in the module that uses it

## Testing

```
tests/
├── test_client.py       # (unchanged)
├── test_server.py        # (unchanged, existing tool tests)
├── test_integration.py   # (unchanged)
├── test_resources.py     # Resource function tests — pure functions, no mocking needed
└── test_prompts.py       # Prompt function tests — assert on Message structure and content
```

- Resource tests: call each resource function, verify return type and content structure
- Prompt tests: call each prompt with sample args, verify Message list structure, role values, and that tool names are referenced in the content
- Resource template test: verify all 6 asset_class values return valid content, and invalid values produce a clear error

## Dependencies

No new dependencies. FastMCP 2.x+ (already installed) has full `@mcp.resource()` and `@mcp.prompt()` support. Return types use `fastmcp.prompts.Message` and built-in strings/dicts.

## Migration / Breaking Changes

None. Resources and prompts are additive. All existing tools continue to work identically. No changes to `client.py` or existing tests.
