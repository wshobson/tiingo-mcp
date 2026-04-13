# tiingo-mcp

[![PyPI version](https://img.shields.io/pypi/v/tiingo-mcp)](https://pypi.org/project/tiingo-mcp/)
[![Python](https://img.shields.io/pypi/pyversions/tiingo-mcp)](https://pypi.org/project/tiingo-mcp/)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![CI](https://github.com/wshobson/tiingo-mcp/actions/workflows/ci.yml/badge.svg)](https://github.com/wshobson/tiingo-mcp/actions/workflows/ci.yml)

A production-grade [Model Context Protocol](https://modelcontextprotocol.io) (MCP) server for the [Tiingo](https://www.tiingo.com) financial data API.

Provides **17 tools** covering the full Tiingo API surface — stocks, forex, crypto, news, fundamentals, and corporate actions — with async HTTP, automatic retries, and structured error handling.

<details>
<summary><strong>Why this server?</strong></summary>

- **Full API coverage**: 17 tools spanning every Tiingo endpoint (EOD, IEX real-time, forex, crypto, news, fundamentals, corporate actions)
- **Modern Python**: Built with FastMCP 3.2, httpx async, Python 3.12+
- **Production-ready**: Automatic retries, rate limit handling, clear error messages for plan restrictions
- **Easy install**: `uvx tiingo-mcp` or `pip install tiingo-mcp` — no build step required
- **Tested**: 60 tests including live integration tests against the Tiingo API

</details>

## Installation

```bash
# Via uvx (recommended)
uvx tiingo-mcp

# Via pip
pip install tiingo-mcp
```

Requires Python 3.12+.

## Configuration

Set your Tiingo API key as an environment variable:

```bash
export TIINGO_API_KEY="your-api-key-here"
```

Get a free API key at [api.tiingo.com](https://api.tiingo.com). The free plan includes stocks, forex, crypto, news, and fundamentals. Some corporate actions endpoints (dividends, splits) require a [Power or Business plan](https://www.tiingo.com/account/billing/pricing).

### Claude Desktop

Add to your `claude_desktop_config.json`:

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

Then set the env var in your shell or `.env` file.

### Other MCP Clients

Any MCP client that supports stdio transport can use this server:

```bash
TIINGO_API_KEY=your-key tiingo-mcp
```

Or run as a Python module:

```bash
TIINGO_API_KEY=your-key python -m tiingo_mcp
```

## Tools

### Stock Prices (EOD)
| Tool | Description |
|------|-------------|
| `get_stock_metadata` | Ticker metadata — name, exchange, description, date range |
| `get_stock_prices` | Historical end-of-day OHLCV with adjusted prices |

### Real-Time & Intraday (IEX)
| Tool | Description |
|------|-------------|
| `get_realtime_price` | Current IEX top-of-book quote |
| `get_intraday_prices` | Historical intraday prices at 1min–1hour intervals |

### Forex
| Tool | Description |
|------|-------------|
| `get_forex_quote` | Current top-of-book forex rate |
| `get_forex_prices` | Historical forex prices |

### Crypto
| Tool | Description |
|------|-------------|
| `get_crypto_quote` | Current crypto prices (2,100+ tickers) |
| `get_crypto_prices` | Historical crypto prices |
| `get_crypto_metadata` | Crypto ticker metadata and supported exchanges |

### News
| Tool | Description |
|------|-------------|
| `get_news` | Search 50M+ financial news articles by ticker, tag, source, date |

### Fundamentals
| Tool | Description |
|------|-------------|
| `get_fundamentals_definitions` | Available fundamental metric definitions |
| `get_financial_statements` | Income statements, balance sheets, cash flow |
| `get_daily_fundamentals` | Daily metrics — market cap, P/E, EV/EBITDA, etc. |
| `get_company_meta` | Company metadata — sector, industry, location |

### Corporate Actions
| Tool | Description |
|------|-------------|
| `get_dividends` | Historical dividend and distribution data * |
| `get_dividend_yield` | Historical dividend yield |
| `get_splits` | Stock split history * |

\* *Requires Tiingo Power or Business plan*

## Parameters

All date parameters use **YYYY-MM-DD** format (e.g. `2024-01-15`).

Common optional parameters across tools:

| Parameter | Used By | Description |
|-----------|---------|-------------|
| `start_date` | Most tools | Filter results from this date |
| `end_date` | Most tools | Filter results up to this date |
| `resample_freq` | Price tools | Resample interval: `daily`, `weekly`, `monthly`, `annually`, `1min`, `5min`, `1hour`, etc. |
| `tickers` | Crypto, news, meta | Comma-separated ticker list |

## Rate Limits

| Plan | Requests/Hour | Requests/Day |
|------|---------------|--------------|
| Free | 50 | 1,000 |
| Power | 5,000 | 50,000 |
| Business | Higher | Higher |

The server automatically retries on transient errors (up to 2 retries) and returns clear JSON error messages on rate limit hits (429), auth failures (401), plan restrictions (403), and invalid tickers (404).

## Development

```bash
# Clone and install
git clone https://github.com/wshobson/tiingo-mcp.git
cd tiingo-mcp
uv sync

# Run unit tests (no API key needed)
uv run pytest tests/test_client.py tests/test_server.py -v

# Run integration tests (requires TIINGO_API_KEY)
uv run pytest tests/test_integration.py -v -s

# Run all tests
uv run pytest -v

# Lint & format
uv run ruff check src/ tests/
uv run ruff format src/ tests/

# Run the server locally
TIINGO_API_KEY=your-key uv run tiingo-mcp
```

## License

[MIT](LICENSE)

## Links

- [Tiingo API Documentation](https://www.tiingo.com/documentation/general/overview)
- [Model Context Protocol](https://modelcontextprotocol.io)
- [FastMCP](https://gofastmcp.com)
