"""MCP prompts for the Tiingo MCP server -- structured analysis workflows."""

from __future__ import annotations

from fastmcp.prompts import Message

from tiingo_mcp.server import mcp

# ── Prompt 1: analyze-stock ───────────────────────────────────────────


@mcp.prompt(
    name="analyze-stock",
    description="Comprehensive single-stock analysis: metadata, prices, fundamentals, and news",
)
def analyze_stock_prompt(ticker: str, include_news: bool = True) -> list[Message]:
    """Guide the LLM through a comprehensive single-stock analysis."""
    news_instruction = (
        f"4. Call get_news with tickers={ticker} to fetch recent news articles and "
        "identify key catalysts, analyst commentary, and market-moving events.\n"
        if include_news
        else "4. Skip news fetching (include_news=False).\n"
    )
    text = (
        f"Please perform a comprehensive analysis of {ticker} using the following steps:\n\n"
        f"1. Call get_stock_metadata for {ticker} to retrieve company name, exchange, "
        "description, and available date range.\n"
        f"2. Call get_stock_prices for {ticker} with a start_date 30 days ago to get recent "
        "end-of-day OHLCV price history.\n"
        f"3. Call get_daily_fundamentals for {ticker} with a start_date 30 days ago to retrieve "
        "P/E ratio, market cap, and other valuation metrics.\n"
        f"{news_instruction}"
        "\nSynthesize the results into a structured report with these sections:\n"
        "- **Company Overview**: Name, exchange, sector, and business description.\n"
        "- **Price Trend**: Recent price action, highs/lows, and percentage change over 30 days.\n"
        "- **Valuation Snapshot**: Current P/E ratio, market cap, and notable "
        "fundamental metrics.\n"
        "- **Recent Catalysts**: Key news stories or events driving price movement "
        "(if news was fetched).\n"
        "- **Summary**: One-paragraph investment narrative combining all findings."
    )
    return [Message(role="user", content=text)]


# ── Prompt 2: compare-stocks ──────────────────────────────────────────


@mcp.prompt(
    name="compare-stocks",
    description="Side-by-side comparison of two stocks: prices, fundamentals, and performance",
)
def compare_stocks_prompt(ticker1: str, ticker2: str, period: str = "3 months") -> list[Message]:
    """Guide the LLM through a side-by-side stock comparison."""
    text = (
        f"Please perform a side-by-side comparison of {ticker1} and {ticker2} "
        f"over the past {period}.\n\n"
        "Fetch the following data for each ticker:\n"
        f"1. Call get_stock_prices for {ticker1} and get_stock_prices for {ticker2} "
        f"covering the past {period} to compare price performance.\n"
        f"2. Call get_daily_fundamentals for {ticker1} and get_daily_fundamentals for {ticker2} "
        "to retrieve P/E ratios and market caps.\n"
        f"3. Call get_dividend_yield for {ticker1} and get_dividend_yield for {ticker2} "
        "to compare dividend income.\n\n"
        "Produce a comparative analysis including:\n"
        "- A table comparing: price performance (%), P/E ratio, market cap, and dividend yield.\n"
        f"- Which of {ticker1} or {ticker2} has stronger momentum over the period.\n"
        "- Relative valuation: which appears cheaper on a P/E basis.\n"
        "- Income comparison: dividend yield difference.\n"
        "- A brief recommendation on which stock looks more attractive and why."
    )
    return [Message(role="user", content=text)]


# ── Prompt 3: crypto-market-overview ─────────────────────────────────


@mcp.prompt(
    name="crypto-market-overview",
    description="Crypto market snapshot: current prices, 24h changes, and 7-day trends",
)
def crypto_market_overview_prompt(tickers: str = "btcusd,ethusd,solusd") -> list[Message]:
    """Guide the LLM through a crypto market snapshot."""
    text = (
        f"Please provide a crypto market overview for the following tickers: {tickers}.\n\n"
        "Fetch the following data:\n"
        f"1. Call get_crypto_quote with tickers={tickers} to get current prices, "
        "24-hour volume, and latest bid/ask.\n"
        f"2. Call get_crypto_prices for {tickers} with a start_date 7 days ago to retrieve "
        "7-day price history for trend analysis.\n\n"
        "Summarize the results as a market snapshot:\n"
        "- **Current Prices**: Latest price for each ticker.\n"
        "- **24h Change**: Estimated price change over the past 24 hours "
        "based on available data.\n"
        "- **7-Day Trend**: Direction (up/down/flat) and percentage change for each ticker "
        "over the past 7 days.\n"
        "- **Market Narrative**: A brief paragraph on overall crypto market sentiment "
        "based on the data."
    )
    return [Message(role="user", content=text)]


# ── Prompt 4: earnings-report-analysis ───────────────────────────────


@mcp.prompt(
    name="earnings-report-analysis",
    description=(
        "Analyze a stock's earnings report: financials, price reaction, and news sentiment"
    ),
)
def earnings_report_analysis_prompt(ticker: str, earnings_date: str) -> list[Message]:
    """Guide the LLM through an earnings report analysis."""
    text = (
        f"Please analyze the earnings report for {ticker} around the date {earnings_date}.\n\n"
        "Fetch the following data:\n"
        f"1. Call get_financial_statements for {ticker} with a date range spanning "
        f"approximately 3 months before and after {earnings_date} to retrieve the relevant "
        "quarterly income statement, balance sheet, and cash flow data.\n"
        f"2. Call get_stock_prices for {ticker} with a start_date 2 weeks before "
        f"{earnings_date} and end_date 2 weeks after {earnings_date} to capture the "
        "price reaction around the earnings event.\n"
        f"3. Call get_news with tickers={ticker} and a date range 1 week before and "
        f"after {earnings_date} to gather analyst reactions, guidance commentary, "
        "and post-earnings sentiment.\n\n"
        "Synthesize the findings into:\n"
        "- **Financial Results**: Key metrics from the earnings report "
        "(revenue, net income, EPS, margins).\n"
        "- **Beat or Miss**: Did the company beat or miss expectations based on trends?\n"
        "- **Price Reaction**: How the stock moved in the 2 weeks before and after earnings.\n"
        "- **News Sentiment**: Summary of analyst and media reaction from the news data.\n"
        "- **Outlook**: Any forward guidance or notable commentary from the news articles."
    )
    return [Message(role="user", content=text)]


# ── Prompt 5: forex-pair-analysis ────────────────────────────────────


@mcp.prompt(
    name="forex-pair-analysis",
    description="Currency pair analysis: current rate, historical trend, and volatility",
)
def forex_pair_analysis_prompt(pair: str, period: str = "1 month") -> list[Message]:
    """Guide the LLM through a forex pair analysis."""
    text = (
        f"Please perform a currency pair analysis for {pair} over the past {period}.\n\n"
        "Fetch the following data:\n"
        f"1. Call get_forex_quote for {pair} to get the current top-of-book bid, ask, "
        "and mid price.\n"
        f"2. Call get_forex_prices for {pair} with a start_date {period} ago and "
        "resample_freq='1day' to retrieve daily OHLCV history for the period.\n\n"
        "Analyze and present:\n"
        "- **Current Rate**: Latest bid/ask spread and mid price for the pair.\n"
        f"- **Trend over {period}**: Direction and magnitude of the rate change, "
        "identifying key support/resistance levels.\n"
        "- **Volatility**: Daily price range analysis — average true range or high-low spread "
        "over the period.\n"
        "- **Notable Moves**: Any significant spikes or drops and their likely causes.\n"
        "- **Summary**: One-paragraph assessment of the pair's current momentum and "
        "near-term outlook."
    )
    return [Message(role="user", content=text)]
