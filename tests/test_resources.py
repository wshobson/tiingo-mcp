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


# ── capabilities content validation ─────────────────────────────────


async def test_capabilities_lists_all_asset_classes():
    async with Client(mcp) as client:
        result = await client.read_resource("tiingo://capabilities")
        data = json.loads(result[0].text)
        assert set(data["asset_classes"].keys()) == {"stocks", "forex", "crypto"}


async def test_capabilities_rate_limits_both_tiers():
    async with Client(mcp) as client:
        result = await client.read_resource("tiingo://capabilities")
        data = json.loads(result[0].text)
        assert "free" in data["rate_limits"]
        assert "power" in data["rate_limits"]


async def test_capabilities_plan_restrictions_paid_tools():
    async with Client(mcp) as client:
        result = await client.read_resource("tiingo://capabilities")
        data = json.loads(result[0].text)
        paid = data["plan_restrictions"]["paid_tier_required"]
        assert "get_dividends" in paid
        assert "get_splits" in paid


async def test_capabilities_free_tier_tool_count():
    async with Client(mcp) as client:
        result = await client.read_resource("tiingo://capabilities")
        data = json.loads(result[0].text)
        free = data["plan_restrictions"]["free_tier"]
        paid = data["plan_restrictions"]["paid_tier_required"]
        assert len(free) + len(paid) == data["tool_count"]


# ── fundamentals definitions content validation ─────────────────────


async def test_fundamentals_definitions_covers_all_statement_types():
    async with Client(mcp) as client:
        result = await client.read_resource("tiingo://fundamentals/definitions")
        data = json.loads(result[0].text)
        types = {m["statement_type"] for m in data["metrics"]}
        assert types == {"overview", "income_statement", "balance_sheet", "cash_flow"}


async def test_fundamentals_definitions_includes_key_metrics():
    async with Client(mcp) as client:
        result = await client.read_resource("tiingo://fundamentals/definitions")
        data = json.loads(result[0].text)
        names = {m["name"] for m in data["metrics"]}
        expected = {"marketCap", "peRatio", "revenue", "netIncome", "eps", "freeCashFlow"}
        assert expected.issubset(names)


# ── date formats content validation ─────────────────────────────────


async def test_date_formats_stocks_eod_frequencies():
    async with Client(mcp) as client:
        result = await client.read_resource("tiingo://guide/date-formats")
        data = json.loads(result[0].text)
        assert "daily" in data["resample_frequencies"]["stocks_eod"]
        assert "annually" in data["resample_frequencies"]["stocks_eod"]


async def test_date_formats_intraday_frequencies():
    async with Client(mcp) as client:
        result = await client.read_resource("tiingo://guide/date-formats")
        data = json.loads(result[0].text)
        assert "1min" in data["resample_frequencies"]["intraday"]
        assert "1hour" in data["resample_frequencies"]["intraday"]


async def test_date_formats_corporate_actions_ex_date_params():
    async with Client(mcp) as client:
        result = await client.read_resource("tiingo://guide/date-formats")
        data = json.loads(result[0].text)
        divs = data["corporate_actions_date_params"]["dividends_and_splits"]
        assert "startExDate" in divs["start_date_maps_to"]
        assert "endExDate" in divs["end_date_maps_to"]


# ── guide template content validation ───────────────────────────────


@pytest.mark.parametrize("asset_class", VALID_ASSET_CLASSES)
async def test_guide_tools_are_nonempty_strings(asset_class: str):
    async with Client(mcp) as client:
        result = await client.read_resource(f"tiingo://guide/{asset_class}")
        data = json.loads(result[0].text)
        for tool in data["tools"]:
            assert isinstance(tool, str)
            assert len(tool) > 0


@pytest.mark.parametrize("asset_class", VALID_ASSET_CLASSES)
async def test_guide_has_common_pitfalls(asset_class: str):
    async with Client(mcp) as client:
        result = await client.read_resource(f"tiingo://guide/{asset_class}")
        data = json.loads(result[0].text)
        assert "common_pitfalls" in data
        assert isinstance(data["common_pitfalls"], list)
        assert len(data["common_pitfalls"]) >= 1


@pytest.mark.parametrize("asset_class", VALID_ASSET_CLASSES)
async def test_guide_has_plan_restrictions(asset_class: str):
    async with Client(mcp) as client:
        result = await client.read_resource(f"tiingo://guide/{asset_class}")
        data = json.loads(result[0].text)
        assert "plan_restrictions" in data
        assert len(data["plan_restrictions"]) > 0


async def test_guide_stocks_references_correct_tools():
    async with Client(mcp) as client:
        result = await client.read_resource("tiingo://guide/stocks")
        data = json.loads(result[0].text)
        assert "get_stock_metadata" in data["tools"]
        assert "get_stock_prices" in data["tools"]
        assert "get_realtime_price" in data["tools"]
        assert "get_intraday_prices" in data["tools"]


async def test_guide_corporate_actions_mentions_paid_tier():
    async with Client(mcp) as client:
        result = await client.read_resource("tiingo://guide/corporate-actions")
        data = json.loads(result[0].text)
        assert "403" in data["plan_restrictions"] or "paid" in data["plan_restrictions"].lower()


async def test_guide_invalid_returns_valid_json():
    async with Client(mcp) as client:
        result = await client.read_resource("tiingo://guide/bonds")
        data = json.loads(result[0].text)
        assert "error" in data
        assert "bonds" in data["error"]


async def test_guide_invalid_lists_valid_options():
    async with Client(mcp) as client:
        result = await client.read_resource("tiingo://guide/options")
        data = json.loads(result[0].text)
        for ac in VALID_ASSET_CLASSES:
            assert ac in data["error"]


# ── resource descriptions ───────────────────────────────────────────


async def test_all_resources_have_descriptions():
    async with Client(mcp) as client:
        resources = await client.list_resources()
        for r in resources:
            assert r.description, f"Resource {r.uri} has no description"

        templates = await client.list_resource_templates()
        for t in templates:
            assert t.description, f"Template {t.uriTemplate} has no description"
