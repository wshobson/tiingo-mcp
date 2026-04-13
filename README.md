# tiingo-mcp

[![PyPI](https://img.shields.io/badge/PyPI-tiingo--mcp%20v1.0.0-blue)](https://pypi.org/project/tiingo-mcp/)
[![Python 3.12+](https://img.shields.io/badge/python-3.12%2B-blue)](https://pypi.org/project/tiingo-mcp/)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![CI](https://github.com/wshobson/tiingo-mcp/actions/workflows/ci.yml/badge.svg)](https://github.com/wshobson/tiingo-mcp/actions/workflows/ci.yml)

An [MCP](https://modelcontextprotocol.io) server that wraps the [Tiingo](https://www.tiingo.com) financial data API. Covers stocks, forex, crypto, news, fundamentals, and corporate actions across 17 tools.

## Installation

```bash
uvx tiingo-mcp
# or
pip install tiingo-mcp
```

Requires Python 3.12+.

## Configuration

```bash
export TIINGO_API_KEY="your-api-key-here"
```

Free API keys at [api.tiingo.com](https://api.tiingo.com). The free plan covers stocks, forex, crypto, news, and fundamentals. Dividends and splits endpoints need a [Power or Business plan](https://www.tiingo.com/account/billing/pricing).

### Claude Desktop

Add to `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "tiingo": {
      "command": "uvx",
      "args": ["tiingo-mcp"],
      "env": {
        "TIINGO_API_KEY": "your-api-key-here"
      }
    }
  }
}
```

### Claude Code

```bash
claude mcp add tiingo -- uvx tiingo-mcp
```

### Other Clients

Anything that speaks stdio:

```bash
TIINGO_API_KEY=your-key tiingo-mcp
```

## Tools

### Stocks (EOD)
| Tool | Description |
|------|-------------|
| `get_stock_metadata` | Ticker info — name, exchange, description, date range |
| `get_stock_prices` | Historical EOD OHLCV with adjusted prices |

### Real-Time & Intraday (IEX)
| Tool | Description |
|------|-------------|
| `get_realtime_price` | Current IEX top-of-book quote |
| `get_intraday_prices` | Intraday prices at 1min–1hour intervals |

### Forex
| Tool | Description |
|------|-------------|
| `get_forex_quote` | Current top-of-book rate |
| `get_forex_prices` | Historical forex prices |

### Crypto
| Tool | Description |
|------|-------------|
| `get_crypto_quote` | Current prices (2,100+ tickers) |
| `get_crypto_prices` | Historical crypto prices |
| `get_crypto_metadata` | Ticker metadata and supported exchanges |

### News
| Tool | Description |
|------|-------------|
| `get_news` | Search financial articles by ticker, tag, source, date |

### Fundamentals
| Tool | Description |
|------|-------------|
| `get_fundamentals_definitions` | Metric definitions |
| `get_financial_statements` | Income statements, balance sheets, cash flow |
| `get_daily_fundamentals` | Daily metrics — market cap, P/E, EV/EBITDA |
| `get_company_meta` | Sector, industry, location |

### Corporate Actions
| Tool | Description |
|------|-------------|
| `get_dividends` | Dividend and distribution history * |
| `get_dividend_yield` | Dividend yield history |
| `get_splits` | Stock split history * |

\* *Requires Power or Business plan*

## Parameters

Dates are **YYYY-MM-DD** format.

| Parameter | Used By | Description |
|-----------|---------|-------------|
| `start_date` | Most tools | Start of date range |
| `end_date` | Most tools | End of date range |
| `resample_freq` | Price tools | `daily`, `weekly`, `monthly`, `annually`, `1min`, `5min`, `1hour`, etc. |
| `tickers` | Crypto, news, meta | Comma-separated list |

## Rate Limits

| Plan | Requests/Hour | Requests/Day |
|------|---------------|--------------|
| Free | 50 | 1,000 |
| Power | 5,000 | 50,000 |
| Business | Higher | Higher |

The server retries transient errors (2x) and returns JSON error objects for rate limits (429), auth failures (401), plan restrictions (403), and bad tickers (404).

## Development

```bash
git clone https://github.com/wshobson/tiingo-mcp.git
cd tiingo-mcp
uv sync

# Unit tests (no API key needed)
uv run pytest tests/test_client.py tests/test_server.py -v

# Integration tests (needs TIINGO_API_KEY)
uv run pytest tests/test_integration.py -v -s

# All tests
uv run pytest -v

# Lint & format
uv run ruff check src/ tests/
uv run ruff format src/ tests/
```

## License

[MIT](LICENSE)

## Links

- [Tiingo API docs](https://www.tiingo.com/documentation/general/overview)
- [Model Context Protocol](https://modelcontextprotocol.io)
- [FastMCP](https://gofastmcp.com)
