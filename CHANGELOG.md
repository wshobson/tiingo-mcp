# Changelog

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
