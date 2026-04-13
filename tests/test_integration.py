"""Live integration tests against the Tiingo API.

Run with: TIINGO_API_KEY=... uv run pytest tests/test_integration.py -v -s
Skipped automatically if TIINGO_API_KEY is not set.
"""

from __future__ import annotations

import os

import pytest

from tiingo_mcp.client import TiingoAPIError, TiingoClient

pytestmark = pytest.mark.skipif(
    not os.environ.get("TIINGO_API_KEY"),
    reason="TIINGO_API_KEY not set",
)


@pytest.fixture
async def client():
    c = TiingoClient()
    yield c
    await c.close()


# ── EOD Stock Prices ──────────────────────────────────────────────────


async def test_live_stock_metadata(client: TiingoClient):
    result = await client.get_stock_metadata("AAPL")
    assert isinstance(result, dict)
    assert result["ticker"] == "AAPL"
    assert "name" in result
    assert "exchangeCode" in result
    assert "startDate" in result
    assert "endDate" in result
    assert "description" in result
    print(f"  ✓ AAPL: {result['name']} ({result['exchangeCode']})")


async def test_live_stock_prices(client: TiingoClient):
    result = await client.get_stock_prices("AAPL", start_date="2024-01-02", end_date="2024-01-05")
    assert isinstance(result, list)
    assert len(result) > 0
    row = result[0]
    for field in ["date", "close", "high", "low", "open", "volume", "adjClose"]:
        assert field in row, f"Missing field: {field}"
    print(f"  ✓ AAPL prices: {len(result)} rows, first close={row['close']}")


async def test_live_stock_prices_resample(client: TiingoClient):
    result = await client.get_stock_prices(
        "MSFT", start_date="2024-01-01", end_date="2024-03-31", resample_freq="monthly"
    )
    assert isinstance(result, list)
    assert len(result) <= 4
    print(f"  ✓ MSFT monthly: {len(result)} rows")


# ── IEX Real-Time / Intraday ─────────────────────────────────────────


async def test_live_realtime_price(client: TiingoClient):
    result = await client.get_realtime_price("AAPL")
    assert isinstance(result, list)
    assert len(result) > 0
    row = result[0]
    assert "ticker" in row
    print(f"  ✓ AAPL IEX: last={row.get('last', row.get('tngoLast', 'N/A'))}")


async def test_live_realtime_price_after_hours(client: TiingoClient):
    result = await client.get_realtime_price("AAPL", after_hours=True)
    assert isinstance(result, list)
    assert len(result) > 0
    print(f"  ✓ AAPL after-hours: returned {len(result)} quote(s)")


async def test_live_intraday_prices(client: TiingoClient):
    result = await client.get_intraday_prices(
        "AAPL", start_date="2024-06-03", resample_freq="1hour"
    )
    assert isinstance(result, list)
    assert len(result) > 0
    row = result[0]
    assert "date" in row
    assert "close" in row
    print(f"  ✓ AAPL intraday: {len(result)} rows (1hour)")


# ── Forex ─────────────────────────────────────────────────────────────


async def test_live_forex_quote(client: TiingoClient):
    result = await client.get_forex_quote("eurusd")
    assert isinstance(result, list)
    assert len(result) > 0
    row = result[0]
    assert "ticker" in row
    print(f"  ✓ EURUSD: midPrice={row.get('midPrice', 'N/A')}")


async def test_live_forex_prices(client: TiingoClient):
    result = await client.get_forex_prices(
        "eurusd", start_date="2024-06-01", end_date="2024-06-05", resample_freq="1day"
    )
    assert isinstance(result, list)
    assert len(result) > 0
    print(f"  ✓ EURUSD history: {len(result)} rows")


# ── Crypto ────────────────────────────────────────────────────────────


async def test_live_crypto_quote(client: TiingoClient):
    result = await client.get_crypto_quote("btcusd")
    assert isinstance(result, list)
    assert len(result) > 0
    row = result[0]
    assert "ticker" in row
    top = row.get("topOfBookData", [{}])
    price = top[0].get("lastPrice", "N/A") if top else "N/A"
    print(f"  ✓ BTCUSD: lastPrice={price}")


async def test_live_crypto_prices(client: TiingoClient):
    result = await client.get_crypto_prices(
        "btcusd", start_date="2024-06-01", end_date="2024-06-03", resample_freq="1day"
    )
    assert isinstance(result, list)
    assert len(result) > 0
    print(f"  ✓ BTCUSD history: {len(result)} rows")


async def test_live_crypto_metadata(client: TiingoClient):
    result = await client.get_crypto_metadata("btcusd")
    assert isinstance(result, list)
    assert len(result) > 0
    row = result[0]
    assert "ticker" in row
    print(f"  ✓ BTCUSD meta: baseCurrency={row.get('baseCurrency', 'N/A')}")


# ── News ──────────────────────────────────────────────────────────────


async def test_live_news(client: TiingoClient):
    result = await client.get_news(tickers="AAPL", limit=3)
    assert isinstance(result, list)
    assert len(result) > 0
    article = result[0]
    assert "title" in article
    assert "publishedDate" in article
    print(f"  ✓ AAPL news: {len(result)} articles, first='{article['title'][:60]}...'")


async def test_live_news_with_filters(client: TiingoClient):
    result = await client.get_news(
        tickers="MSFT,GOOGL",
        start_date="2024-06-01",
        end_date="2024-06-30",
        limit=5,
        sort_by="publishedDate",
    )
    assert isinstance(result, list)
    print(f"  ✓ MSFT/GOOGL news (June 2024): {len(result)} articles")


# ── Fundamentals ──────────────────────────────────────────────────────


async def test_live_fundamentals_definitions(client: TiingoClient):
    result = await client.get_fundamentals_definitions()
    assert isinstance(result, list)
    assert len(result) > 0
    defn = result[0]
    assert "dataCode" in defn
    print(f"  ✓ Fundamentals defs: {len(result)} metrics available")


async def test_live_financial_statements(client: TiingoClient):
    result = await client.get_financial_statements("AAPL")
    assert isinstance(result, list)
    assert len(result) > 0
    stmt = result[0]
    assert "date" in stmt
    assert "statementData" in stmt
    print(f"  ✓ AAPL statements: {len(result)} periods")


async def test_live_daily_fundamentals(client: TiingoClient):
    result = await client.get_daily_fundamentals(
        "AAPL", start_date="2024-06-01", end_date="2024-06-05"
    )
    assert isinstance(result, list)
    assert len(result) > 0
    row = result[0]
    assert "date" in row
    assert "marketCap" in row
    print(f"  ✓ AAPL daily fundamentals: {len(result)} rows, marketCap={row['marketCap']}")


async def test_live_company_meta(client: TiingoClient):
    result = await client.get_company_meta("AAPL,MSFT")
    assert isinstance(result, list)
    assert len(result) == 2
    for company in result:
        assert "ticker" in company
    tickers = [c["ticker"] for c in result]
    print(f"  ✓ Company meta: {tickers}")


# ── Corporate Actions ─────────────────────────────────────────────────


async def test_live_dividends(client: TiingoClient):
    try:
        result = await client.get_dividends("AAPL")
        assert isinstance(result, list)
        assert len(result) > 0
        print(f"  ✓ AAPL dividends: {len(result)} records")
    except TiingoAPIError as exc:
        if exc.status_code == 403:
            pytest.skip("Dividends endpoint requires Power/Business plan")
        raise


async def test_live_dividends_date_filter(client: TiingoClient):
    try:
        result = await client.get_dividends("AAPL", start_date="2024-01-01", end_date="2024-12-31")
        assert isinstance(result, list)
        print(f"  ✓ AAPL dividends (2024): {len(result)} records")
    except TiingoAPIError as exc:
        if exc.status_code == 403:
            pytest.skip("Dividends endpoint requires Power/Business plan")
        raise


async def test_live_dividend_yield(client: TiingoClient):
    result = await client.get_dividend_yield(
        "AAPL", start_date="2024-06-01", end_date="2024-06-30"
    )
    assert isinstance(result, list)
    assert len(result) > 0
    row = result[0]
    assert "date" in row
    print(f"  ✓ AAPL dividend yield: {len(result)} rows, first={row}")


async def test_live_splits(client: TiingoClient):
    try:
        result = await client.get_splits("AAPL")
        assert isinstance(result, list)
        assert len(result) > 0
        print(f"  ✓ AAPL splits: {len(result)} records")
    except TiingoAPIError as exc:
        if exc.status_code == 403:
            pytest.skip("Splits endpoint requires Power/Business plan")
        raise


async def test_live_splits_date_filter(client: TiingoClient):
    try:
        result = await client.get_splits("AAPL", start_date="2020-01-01", end_date="2020-12-31")
        assert isinstance(result, list)
        assert len(result) >= 1  # AAPL 4:1 split was Aug 2020
        print(f"  ✓ AAPL splits (2020): {len(result)} records")
    except TiingoAPIError as exc:
        if exc.status_code == 403:
            pytest.skip("Splits endpoint requires Power/Business plan")
        raise


# ── Error handling with live API ──────────────────────────────────────


async def test_live_invalid_ticker_metadata(client: TiingoClient):
    with pytest.raises(TiingoAPIError) as exc_info:
        await client.get_stock_metadata("ZZZZZNOTREAL")
    assert exc_info.value.status_code in (400, 404)
    print(f"  ✓ Invalid ticker: got {exc_info.value.status_code} as expected")
