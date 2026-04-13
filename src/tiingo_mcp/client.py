"""Async HTTP client for the Tiingo financial data API."""

from __future__ import annotations

import os
from typing import Any

import httpx


class TiingoAPIError(Exception):
    """Raised when the Tiingo API returns an error response."""

    def __init__(self, status_code: int, detail: str) -> None:
        self.status_code = status_code
        self.detail = detail
        super().__init__(f"Tiingo API error {status_code}: {detail}")


class TiingoClient:
    """Async client for the Tiingo REST API.

    Uses httpx.AsyncClient with connection pooling, automatic retries,
    and token-based authentication.
    """

    BASE_URL = "https://api.tiingo.com"

    def __init__(self, api_key: str | None = None) -> None:
        self.api_key = api_key or os.environ.get("TIINGO_API_KEY", "")
        if not self.api_key:
            raise ValueError(
                "Tiingo API key is required. Set the TIINGO_API_KEY environment variable "
                "or pass api_key to TiingoClient()."
            )
        self._client = httpx.AsyncClient(
            base_url=self.BASE_URL,
            headers={
                "Authorization": f"Token {self.api_key}",
                "Content-Type": "application/json",
            },
            timeout=httpx.Timeout(30.0, connect=10.0),
            transport=httpx.AsyncHTTPTransport(retries=2),
        )

    async def _request(self, path: str, params: dict[str, Any] | None = None) -> Any:
        """Make an authenticated GET request to the Tiingo API."""
        clean_params = {k: v for k, v in (params or {}).items() if v is not None}
        response = await self._client.get(path, params=clean_params)
        if response.status_code == 429:
            raise TiingoAPIError(429, "Rate limit exceeded. Please wait before retrying.")
        if response.status_code == 401:
            raise TiingoAPIError(401, "Invalid API key or insufficient permissions.")
        if response.status_code == 403:
            raise TiingoAPIError(
                403,
                f"Access denied for {path}. "
                "This endpoint may require a higher Tiingo plan (Power or Business).",
            )
        if response.status_code == 404:
            raise TiingoAPIError(404, f"Resource not found: {path}")
        if response.status_code >= 400:
            detail = response.text[:500] if response.text else "Unknown error"
            raise TiingoAPIError(response.status_code, detail)
        return response.json()

    async def close(self) -> None:
        """Close the underlying HTTP client."""
        await self._client.aclose()

    # ── EOD Stock Prices ──────────────────────────────────────────────

    async def get_stock_metadata(self, ticker: str) -> dict[str, Any]:
        return await self._request(f"/tiingo/daily/{ticker}")

    async def get_stock_prices(
        self,
        ticker: str,
        *,
        start_date: str | None = None,
        end_date: str | None = None,
        resample_freq: str | None = None,
    ) -> list[dict[str, Any]]:
        return await self._request(
            f"/tiingo/daily/{ticker}/prices",
            params={
                "startDate": start_date,
                "endDate": end_date,
                "resampleFreq": resample_freq,
            },
        )

    # ── IEX Real-Time / Intraday ─────────────────────────────────────

    async def get_realtime_price(
        self,
        ticker: str,
        *,
        after_hours: bool | None = None,
    ) -> list[dict[str, Any]]:
        return await self._request(
            f"/iex/{ticker}",
            params={"afterHours": str(after_hours).lower() if after_hours is not None else None},
        )

    async def get_intraday_prices(
        self,
        ticker: str,
        *,
        start_date: str | None = None,
        end_date: str | None = None,
        resample_freq: str | None = None,
    ) -> list[dict[str, Any]]:
        return await self._request(
            f"/iex/{ticker}/prices",
            params={
                "startDate": start_date,
                "endDate": end_date,
                "resampleFreq": resample_freq,
            },
        )

    # ── Forex ─────────────────────────────────────────────────────────

    async def get_forex_quote(self, ticker: str) -> list[dict[str, Any]]:
        return await self._request(f"/tiingo/fx/{ticker}/top")

    async def get_forex_prices(
        self,
        ticker: str,
        *,
        start_date: str | None = None,
        end_date: str | None = None,
        resample_freq: str | None = None,
    ) -> list[dict[str, Any]]:
        return await self._request(
            f"/tiingo/fx/{ticker}/prices",
            params={
                "startDate": start_date,
                "endDate": end_date,
                "resampleFreq": resample_freq,
            },
        )

    # ── Crypto ────────────────────────────────────────────────────────

    async def get_crypto_quote(
        self,
        tickers: str | None = None,
    ) -> list[dict[str, Any]]:
        return await self._request("/tiingo/crypto/top", params={"tickers": tickers})

    async def get_crypto_prices(
        self,
        tickers: str,
        *,
        start_date: str | None = None,
        end_date: str | None = None,
        resample_freq: str | None = None,
    ) -> list[dict[str, Any]]:
        return await self._request(
            "/tiingo/crypto/prices",
            params={
                "tickers": tickers,
                "startDate": start_date,
                "endDate": end_date,
                "resampleFreq": resample_freq,
            },
        )

    async def get_crypto_metadata(self, tickers: str | None = None) -> list[dict[str, Any]]:
        return await self._request("/tiingo/crypto", params={"tickers": tickers})

    # ── News ──────────────────────────────────────────────────────────

    async def get_news(
        self,
        *,
        tickers: str | None = None,
        tags: str | None = None,
        source: str | None = None,
        start_date: str | None = None,
        end_date: str | None = None,
        limit: int | None = None,
        offset: int | None = None,
        sort_by: str | None = None,
    ) -> list[dict[str, Any]]:
        return await self._request(
            "/tiingo/news",
            params={
                "tickers": tickers,
                "tags": tags,
                "source": source,
                "startDate": start_date,
                "endDate": end_date,
                "limit": limit,
                "offset": offset,
                "sortBy": sort_by,
            },
        )

    # ── Fundamentals ──────────────────────────────────────────────────

    async def get_fundamentals_definitions(self) -> list[dict[str, Any]]:
        return await self._request("/tiingo/fundamentals/definitions")

    async def get_financial_statements(
        self,
        ticker: str,
        *,
        start_date: str | None = None,
        end_date: str | None = None,
    ) -> list[dict[str, Any]]:
        return await self._request(
            f"/tiingo/fundamentals/{ticker}/statements",
            params={"startDate": start_date, "endDate": end_date},
        )

    async def get_daily_fundamentals(
        self,
        ticker: str,
        *,
        start_date: str | None = None,
        end_date: str | None = None,
    ) -> list[dict[str, Any]]:
        return await self._request(
            f"/tiingo/fundamentals/{ticker}/daily",
            params={"startDate": start_date, "endDate": end_date},
        )

    async def get_company_meta(self, tickers: str) -> list[dict[str, Any]]:
        return await self._request(
            "/tiingo/fundamentals/meta",
            params={"tickers": tickers},
        )

    # ── Corporate Actions ─────────────────────────────────────────────

    async def get_dividends(
        self,
        ticker: str,
        *,
        start_date: str | None = None,
        end_date: str | None = None,
    ) -> list[dict[str, Any]]:
        return await self._request(
            f"/tiingo/corporate-actions/{ticker}/distributions",
            params={"startExDate": start_date, "endExDate": end_date},
        )

    async def get_dividend_yield(
        self,
        ticker: str,
        *,
        start_date: str | None = None,
        end_date: str | None = None,
    ) -> list[dict[str, Any]]:
        return await self._request(
            f"/tiingo/corporate-actions/{ticker}/distribution-yield",
            params={"startDate": start_date, "endDate": end_date},
        )

    async def get_splits(
        self,
        ticker: str,
        *,
        start_date: str | None = None,
        end_date: str | None = None,
    ) -> list[dict[str, Any]]:
        return await self._request(
            f"/tiingo/corporate-actions/{ticker}/splits",
            params={"startExDate": start_date, "endExDate": end_date},
        )
