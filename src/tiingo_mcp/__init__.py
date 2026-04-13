"""Tiingo MCP Server — A production-grade MCP server for the Tiingo financial data API."""

from tiingo_mcp.server import mcp

__version__ = "1.0.0"


def main() -> None:
    """Entry point for the tiingo-mcp CLI."""
    mcp.run()
