"""Tests for MCP resources registered in resources.py."""

from __future__ import annotations

import json

import pytest
from fastmcp import Client

import tiingo_mcp.resources  # noqa: F401
from tiingo_mcp.server import mcp

VALID_ASSET_CLASSES = ["corporate-actions", "crypto", "forex", "fundamentals", "news", "stocks"]


# ── capabilities ─────────────────────────────────────────────────────


async def test_capabilities_resource_listed():
    async with Client(mcp) as client:
        resources = await client.list_resources()
        uris = [str(r.uri) for r in resources]
        assert "tiingo://capabilities" in uris


async def test_capabilities_resource_content():
    async with Client(mcp) as client:
        result = await client.read_resource("tiingo://capabilities")
        data = json.loads(result[0].text)
        assert "asset_classes" in data
        assert "rate_limits" in data
        assert "plan_restrictions" in data
        assert data["server_version"] == "1.0.0"
        assert data["tool_count"] == 17
        assert "stocks" in data["asset_classes"]
        assert "free" in data["rate_limits"]
        assert "paid_tier_required" in data["plan_restrictions"]


# ── fundamentals/definitions ─────────────────────────────────────────


async def test_fundamentals_definitions_resource_listed():
    async with Client(mcp) as client:
        resources = await client.list_resources()
        uris = [str(r.uri) for r in resources]
        assert "tiingo://fundamentals/definitions" in uris


async def test_fundamentals_definitions_content():
    async with Client(mcp) as client:
        result = await client.read_resource("tiingo://fundamentals/definitions")
        data = json.loads(result[0].text)
        assert "metrics" in data
        assert isinstance(data["metrics"], list)
        assert len(data["metrics"]) >= 20
        for metric in data["metrics"]:
            assert "name" in metric, f"Missing 'name' in metric: {metric}"
            assert "description" in metric, f"Missing 'description' in metric: {metric}"
            assert "statement_type" in metric, f"Missing 'statement_type' in metric: {metric}"


# ── guide/date-formats ───────────────────────────────────────────────


async def test_date_formats_resource_listed():
    async with Client(mcp) as client:
        resources = await client.list_resources()
        uris = [str(r.uri) for r in resources]
        assert "tiingo://guide/date-formats" in uris


async def test_date_formats_content():
    async with Client(mcp) as client:
        result = await client.read_resource("tiingo://guide/date-formats")
        data = json.loads(result[0].text)
        assert data["date_format"] == "YYYY-MM-DD"
        assert "resample_frequencies" in data
        freqs = data["resample_frequencies"]
        assert "stocks_eod" in freqs
        assert "intraday" in freqs
        assert "forex" in freqs
        assert "crypto" in freqs
        assert "news_sort_options" in data
        assert "corporate_actions_date_params" in data
        ca = data["corporate_actions_date_params"]
        assert "dividends_and_splits" in ca
        assert "dividend_yield" in ca


# ── guide/{asset_class} template ─────────────────────────────────────


async def test_guide_template_listed():
    async with Client(mcp) as client:
        templates = await client.list_resource_templates()
        uri_templates = [str(t.uriTemplate) for t in templates]
        assert "tiingo://guide/{asset_class}" in uri_templates


@pytest.mark.parametrize("asset_class", VALID_ASSET_CLASSES)
async def test_guide_template_valid_asset_classes(asset_class: str):
    async with Client(mcp) as client:
        result = await client.read_resource(f"tiingo://guide/{asset_class}")
        data = json.loads(result[0].text)
        assert "asset_class" in data, f"Missing 'asset_class' for {asset_class}"
        assert "tools" in data, f"Missing 'tools' for {asset_class}"
        assert "ticker_format" in data, f"Missing 'ticker_format' for {asset_class}"
        assert "workflows" in data, f"Missing 'workflows' for {asset_class}"
        assert isinstance(data["tools"], list)
        assert len(data["tools"]) >= 1
        assert isinstance(data["workflows"], list)
        assert len(data["workflows"]) >= 1


async def test_guide_template_invalid_asset_class():
    async with Client(mcp) as client:
        result = await client.read_resource("tiingo://guide/invalid")
        data = json.loads(result[0].text)
        assert "error" in data
        assert "invalid" in data["error"]


# ── counts ───────────────────────────────────────────────────────────


async def test_resource_count():
    async with Client(mcp) as client:
        resources = await client.list_resources()
        assert len(resources) == 3


async def test_resource_template_count():
    async with Client(mcp) as client:
        templates = await client.list_resource_templates()
        assert len(templates) == 1
