"""Tests for the Tiingo API client."""

from __future__ import annotations

import pytest
from pytest_httpx import HTTPXMock

from tiingo_mcp.client import TiingoAPIError, TiingoClient

# ── Client initialization ─────────────────────────────────────────────


def test_client_requires_api_key(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.delenv("TIINGO_API_KEY", raising=False)
    with pytest.raises(ValueError, match="TIINGO_API_KEY"):
        TiingoClient()


def test_client_reads_env_var(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("TIINGO_API_KEY", "env-key")
    client = TiingoClient()
    assert client.api_key == "env-key"


def test_client_prefers_explicit_key(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("TIINGO_API_KEY", "env-key")
    client = TiingoClient(api_key="explicit-key")
    assert client.api_key == "explicit-key"


# ── Error handling ────────────────────────────────────────────────────


async def test_401_raises_api_error(tiingo_client: TiingoClient, httpx_mock: HTTPXMock):
    httpx_mock.add_response(status_code=401, text="Unauthorized")
    with pytest.raises(TiingoAPIError, match="Invalid API key"):
        await tiingo_client.get_stock_metadata("AAPL")


async def test_404_raises_api_error(tiingo_client: TiingoClient, httpx_mock: HTTPXMock):
    httpx_mock.add_response(status_code=404, text="Not Found")
    with pytest.raises(TiingoAPIError, match="not found"):
        await tiingo_client.get_stock_metadata("INVALID")


async def test_429_raises_rate_limit_error(tiingo_client: TiingoClient, httpx_mock: HTTPXMock):
    httpx_mock.add_response(status_code=429, text="Too Many Requests")
    with pytest.raises(TiingoAPIError, match="Rate limit"):
        await tiingo_client.get_stock_metadata("AAPL")


async def test_500_raises_api_error(tiingo_client: TiingoClient, httpx_mock: HTTPXMock):
    httpx_mock.add_response(status_code=500, text="Internal Server Error")
    with pytest.raises(TiingoAPIError) as exc_info:
        await tiingo_client.get_stock_metadata("AAPL")
    assert exc_info.value.status_code == 500


# ── EOD Stock endpoints ──────────────────────────────────────────────


async def test_get_stock_metadata(tiingo_client: TiingoClient, httpx_mock: HTTPXMock):
    expected = {"ticker": "AAPL", "name": "Apple Inc", "exchangeCode": "NASDAQ"}
    httpx_mock.add_response(json=expected)
    result = await tiingo_client.get_stock_metadata("AAPL")
    assert result["ticker"] == "AAPL"


async def test_get_stock_prices(tiingo_client: TiingoClient, httpx_mock: HTTPXMock):
    expected = [{"date": "2024-01-15", "close": 185.0, "volume": 50000000}]
    httpx_mock.add_response(json=expected)
    result = await tiingo_client.get_stock_prices("AAPL", start_date="2024-01-15")
    assert len(result) == 1
    assert result[0]["close"] == 185.0


async def test_get_stock_prices_sends_params(tiingo_client: TiingoClient, httpx_mock: HTTPXMock):
    httpx_mock.add_response(json=[])
    await tiingo_client.get_stock_prices(
        "AAPL", start_date="2024-01-01", end_date="2024-01-31", resample_freq="weekly"
    )
    request = httpx_mock.get_request()
    assert request is not None
    assert "startDate=2024-01-01" in str(request.url)
    assert "endDate=2024-01-31" in str(request.url)
    assert "resampleFreq=weekly" in str(request.url)


# ── IEX endpoints ────────────────────────────────────────────────────


async def test_get_realtime_price(tiingo_client: TiingoClient, httpx_mock: HTTPXMock):
    expected = [{"ticker": "AAPL", "last": 185.5}]
    httpx_mock.add_response(json=expected)
    result = await tiingo_client.get_realtime_price("AAPL")
    assert result[0]["last"] == 185.5


async def test_get_intraday_prices(tiingo_client: TiingoClient, httpx_mock: HTTPXMock):
    expected = [{"date": "2024-01-15T10:00:00", "close": 185.0}]
    httpx_mock.add_response(json=expected)
    result = await tiingo_client.get_intraday_prices("AAPL", resample_freq="5min")
    assert len(result) == 1


# ── Forex endpoints ──────────────────────────────────────────────────


async def test_get_forex_quote(tiingo_client: TiingoClient, httpx_mock: HTTPXMock):
    expected = [{"ticker": "eurusd", "midPrice": 1.0850}]
    httpx_mock.add_response(json=expected)
    result = await tiingo_client.get_forex_quote("eurusd")
    assert result[0]["midPrice"] == 1.0850


async def test_get_forex_prices(tiingo_client: TiingoClient, httpx_mock: HTTPXMock):
    expected = [{"date": "2024-01-15", "close": 1.0850}]
    httpx_mock.add_response(json=expected)
    result = await tiingo_client.get_forex_prices("eurusd", start_date="2024-01-15")
    assert len(result) == 1


# ── Crypto endpoints ─────────────────────────────────────────────────


async def test_get_crypto_quote(tiingo_client: TiingoClient, httpx_mock: HTTPXMock):
    expected = [{"ticker": "btcusd", "lastPrice": 42000.0}]
    httpx_mock.add_response(json=expected)
    result = await tiingo_client.get_crypto_quote("btcusd")
    assert result[0]["lastPrice"] == 42000.0


async def test_get_crypto_prices(tiingo_client: TiingoClient, httpx_mock: HTTPXMock):
    expected = [{"date": "2024-01-15", "close": 42000.0}]
    httpx_mock.add_response(json=expected)
    result = await tiingo_client.get_crypto_prices("btcusd", start_date="2024-01-15")
    assert len(result) == 1


async def test_get_crypto_metadata(tiingo_client: TiingoClient, httpx_mock: HTTPXMock):
    expected = [{"ticker": "btcusd", "baseCurrency": "btc", "quoteCurrency": "usd"}]
    httpx_mock.add_response(json=expected)
    result = await tiingo_client.get_crypto_metadata("btcusd")
    assert result[0]["baseCurrency"] == "btc"


# ── News ──────────────────────────────────────────────────────────────


async def test_get_news(tiingo_client: TiingoClient, httpx_mock: HTTPXMock):
    expected = [{"id": 1, "title": "Apple earnings beat", "tickers": ["AAPL"]}]
    httpx_mock.add_response(json=expected)
    result = await tiingo_client.get_news(tickers="AAPL", limit=5)
    assert result[0]["title"] == "Apple earnings beat"


async def test_get_news_sends_params(tiingo_client: TiingoClient, httpx_mock: HTTPXMock):
    httpx_mock.add_response(json=[])
    await tiingo_client.get_news(
        tickers="AAPL", source="reuters", limit=10, sort_by="publishedDate"
    )
    request = httpx_mock.get_request()
    assert request is not None
    assert "tickers=AAPL" in str(request.url)
    assert "source=reuters" in str(request.url)
    assert "limit=10" in str(request.url)
    assert "sortBy=publishedDate" in str(request.url)


# ── Fundamentals ──────────────────────────────────────────────────────


async def test_get_fundamentals_definitions(tiingo_client: TiingoClient, httpx_mock: HTTPXMock):
    expected = [{"dataCode": "revenue", "description": "Total Revenue"}]
    httpx_mock.add_response(json=expected)
    result = await tiingo_client.get_fundamentals_definitions()
    assert result[0]["dataCode"] == "revenue"


async def test_get_financial_statements(tiingo_client: TiingoClient, httpx_mock: HTTPXMock):
    expected = [{"date": "2024-01-15", "quarter": 1, "statementData": {}}]
    httpx_mock.add_response(json=expected)
    result = await tiingo_client.get_financial_statements("AAPL")
    assert len(result) == 1


async def test_get_daily_fundamentals(tiingo_client: TiingoClient, httpx_mock: HTTPXMock):
    expected = [{"date": "2024-01-15", "marketCap": 3000000000000}]
    httpx_mock.add_response(json=expected)
    result = await tiingo_client.get_daily_fundamentals("AAPL")
    assert result[0]["marketCap"] == 3000000000000


async def test_get_company_meta(tiingo_client: TiingoClient, httpx_mock: HTTPXMock):
    expected = [{"ticker": "AAPL", "sector": "Technology", "industry": "Consumer Electronics"}]
    httpx_mock.add_response(json=expected)
    result = await tiingo_client.get_company_meta("AAPL")
    assert result[0]["sector"] == "Technology"


# ── Corporate Actions ─────────────────────────────────────────────────


async def test_get_dividends(tiingo_client: TiingoClient, httpx_mock: HTTPXMock):
    expected = [{"exDate": "2024-02-09", "amount": 0.24, "type": "Cash"}]
    httpx_mock.add_response(json=expected)
    result = await tiingo_client.get_dividends("AAPL")
    assert result[0]["amount"] == 0.24


async def test_get_dividend_yield(tiingo_client: TiingoClient, httpx_mock: HTTPXMock):
    expected = [{"date": "2024-01-15", "divYield": 0.005}]
    httpx_mock.add_response(json=expected)
    result = await tiingo_client.get_dividend_yield("AAPL")
    assert result[0]["divYield"] == 0.005


async def test_get_splits(tiingo_client: TiingoClient, httpx_mock: HTTPXMock):
    expected = [{"exDate": "2020-08-31", "ratio": 0.25}]
    httpx_mock.add_response(json=expected)
    result = await tiingo_client.get_splits("AAPL")
    assert result[0]["ratio"] == 0.25


# ── None param filtering ─────────────────────────────────────────────


async def test_none_params_are_excluded(tiingo_client: TiingoClient, httpx_mock: HTTPXMock):
    httpx_mock.add_response(json=[])
    await tiingo_client.get_stock_prices("AAPL", start_date="2024-01-01")
    request = httpx_mock.get_request()
    assert request is not None
    assert "startDate=2024-01-01" in str(request.url)
    assert "endDate" not in str(request.url)
    assert "resampleFreq" not in str(request.url)


# ── Auth header ───────────────────────────────────────────────────────


async def test_auth_header_sent(tiingo_client: TiingoClient, httpx_mock: HTTPXMock):
    httpx_mock.add_response(json={})
    await tiingo_client.get_stock_metadata("AAPL")
    request = httpx_mock.get_request()
    assert request is not None
    assert request.headers["Authorization"] == "Token test-api-key-12345"
