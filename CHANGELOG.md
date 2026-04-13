# Changelog

## 1.1.0 (2026-04-13)

### Resources (4)

Static reference data exposed as MCP resources — no API calls consumed.

- `tiingo://capabilities` — server capabilities, asset classes, rate limits, plan restrictions
- `tiingo://fundamentals/definitions` — curated reference of 20 fundamental metrics
- `tiingo://guide/date-formats` — date formats, resample frequencies, sort options
- `tiingo://guide/{asset_class}` — per-asset-class usage guide (stocks, forex, crypto, news, fundamentals, corporate-actions)

### Prompts (5)

Reusable analysis workflow templates that guide LLMs through multi-step financial analysis.

- `analyze-stock` — comprehensive single-stock analysis (metadata, prices, fundamentals, news)
- `compare-stocks` — side-by-side comparison of two tickers
- `crypto-market-overview` — crypto market snapshot with 7-day trends
- `earnings-report-analysis` — earnings report analysis with price reaction and news sentiment
- `forex-pair-analysis` — currency pair trend and volatility analysis

## 1.0.0 (2026-04-13)

Initial release.

### Tools (17)

- **EOD Stocks**: `get_stock_metadata`, `get_stock_prices`
- **IEX Real-Time**: `get_realtime_price`, `get_intraday_prices`
- **Forex**: `get_forex_quote`, `get_forex_prices`
- **Crypto**: `get_crypto_quote`, `get_crypto_prices`, `get_crypto_metadata`
- **News**: `get_news`
- **Fundamentals**: `get_fundamentals_definitions`, `get_financial_statements`, `get_daily_fundamentals`, `get_company_meta`
- **Corporate Actions**: `get_dividends`, `get_dividend_yield`, `get_splits`

### Features

- Full async implementation with httpx
- Automatic retries on transient errors
- Structured error handling (401, 403, 404, 429, 5xx)
- PyPI-publishable, installable via `uvx tiingo-mcp`
- stdio and HTTP transport support
