"""
FinanceToolkit MCP Server — entry point.

Exposes 250+ financial metrics as MCP tools with:
- Category-aware routing (ticker, standalone, discovery, toolkit-direct)
- SQLite-backed caching (10-min TTL by default)
- ``list_metrics_by_category`` discovery tool for small-context models
- Clean error propagation for LLM-friendly messages
- Claude Desktop & OpenRouter compatible (stdio transport)
"""

import difflib
import os
import re
from datetime import datetime

import pandas as pd
from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP

from financetoolkit.helpers import calculate_growth as _calc_growth
from financetoolkit.mcp_server.formatting_model import format_result
from financetoolkit.mcp_server.provider_model import ToolkitProvider
from financetoolkit.mcp_server.registry_model import (
    get_tool_index,
    register_all_tools,
)
from financetoolkit.utilities.logger_model import get_logger

load_dotenv()
logger = get_logger()

_provider = ToolkitProvider(
    api_key=os.environ.get("FMP_API_KEY"),
    cache_ttl=int(os.environ.get("FINANCE_MCP_CACHE_TTL", "600")),
    db_path=os.environ.get("FINANCE_MCP_CACHE_DB", "finance_cache.db"),
)

# ── FastMCP instance ─────────────────────────────────────────────────
mcp = FastMCP(
    name="FinanceToolkit Analyst",
    instructions=(
        "You are an expert financial analyst AI powered by the FinanceToolkit MCP server. "
        "You have access to 150+ pre-computed financial metrics, models, and economic indicators. "
        "Your primary goal is to retrieve precise financial data efficiently without hallucinating calculations.\n\n"
        "### CORE DIRECTIVES\n"
        "1. **USE PRE-COMPUTED METRICS:** NEVER fetch raw financial statements (Income, Balance, Cash Flow) "
        "or historical price data to compute ratios, performance, or risk metrics manually. "
        "Always use the dedicated tool.\n"
        "2. **BATCH REQUESTS:** Tools natively support multiple tickers/countries. Pass a list "
        "(e.g., `tickers=['AAPL', 'MSFT']` or `countries=['United States', 'Japan']`) "
        "instead of making multiple tool calls.\n"
        "3. **MACRO VS MICRO:** Economics & Fixed Income tools do NOT take stock tickers. Use "
        "the `countries` parameter instead. "
        "To compare macro vs micro (e.g., Tesla P/E vs US Inflation), make separate tool calls "
        "and synthesize the results.\n"
        "4. **PERIODICITY & CONTEXT:** Use `quarterly=true` for quarterly data. Limit output size using "
        "`start_date`, `end_date`, and `small_context=true` (limits output to 3 years) to avoid "
        "context window overflow.\n\n"
        "### MODULE ROUTING GUIDE\n"
        "- **Ratios** (`ratios_*`): P/E, EPS, ROE, ROA, Margins, Debt-to-Equity, Dividend Yield, EV/EBITDA, Market Cap.\n"
        "- **Performance** (`performance_*`): Sharpe, Sortino, Alpha, Beta, CAPM, Fama-French, Treynor.\n"
        "- **Risk** (`risk_*`): VaR, CVaR, GARCH, Max Drawdown, Skewness, Kurtosis.\n"
        "- **Models** (`models_*`): DCF, WACC, DuPont, Altman Z, Piotroski, Graham.\n"
        "- **Technicals** (`technicals_*`): RSI, MACD, Bollinger Bands, Moving Averages, Support/Resistance.\n"
        "- **Options** (`options_*`): Black-Scholes, Greeks, Implied Volatility, Option Chains.\n"
        "- **Economics** (`economics_*`): GDP, CPI/Inflation, Unemployment, Interest Rates (Use `countries`).\n"
        "- **Fixed Income** (`fixedincome_*`): Bond Yields, Fed/ECB Rates, EURIBOR, Duration (No tickers needed).\n"
        "- **Discovery** (`discovery_*`): Stock Screener, Instrument Search, Top Gainers/Losers.\n"
        "- **Raw Data** (`toolkit_*`): ONLY use for raw profiles, historical prices, or raw statements "
        "when no metric tool exists.\n\n"
        "### UTILITY TOOLS\n"
        "- `search_metrics(query)`: Execute this first if you are unsure which tool computes a specific metric.\n"
        "- `calculate_growth(metric, tickers)`: Computes period-over-period growth rates for any supported metric.\n\n"
        "### COMMON ALIAS MAPPING\n"
        "- Valuation: P/E -> `ratios_get_price_to_earnings_ratio` | EV/EBITDA -> `ratios_get_ev_to_ebitda_ratio` "
        " | Market Cap -> `ratios_get_market_cap`\n"
        "- Profitability: EPS -> `ratios_get_earnings_per_share` | ROE -> `ratios_get_return_on_equity` | "
        "ROA -> `ratios_get_return_on_assets`\n"
        "- Margins: Gross/Net/Operating -> `ratios_get_gross_margin` / "
        "`ratios_get_net_profit_margin` / `ratios_get_operating_margin`\n"
        "- Liquidity/Debt: D/E -> `ratios_get_debt_to_equity_ratio` | "
        "Current Ratio -> `ratios_get_current_ratio` | FCF Yield -> `ratios_get_free_cash_flow_yield`\n"
        "- Macro: Inflation/CPI -> `economics_get_inflation_rate` | "
        "GDP -> `economics_get_gross_domestic_product` | Rates -> `economics_get_long_term_interest_rate`\n"
        "- Risk/Return: Sharpe -> `performance_get_sharpe_ratio` | "
        "Beta -> `performance_get_beta` | WACC -> `models_get_weighted_average_cost_of_capital`\n"
        "- Momentum: RSI -> `technicals_get_relative_strength_index` | MACD -> "
        "`technicals_get_moving_average_convergence_divergence`\n\n"
        "### OUTPUT PRESENTATION RULES\n"
        "1. **ALWAYS USE TABLES:** When a tool returns data with multiple values (time series, "
        "multiple countries, multiple tickers), ALWAYS present it as a Markdown table. "
        "NEVER collapse multi-value data into bullet points, inline lists, or comma-separated values.\n"
        "2. **PRESERVE TOOL OUTPUT:** Tool results are already formatted as Markdown tables — "
        "render them as-is. Do not reformat, summarise, or rewrite them as prose or lists.\n"
        "3. **TRENDS IN INTERPRETATION ONLY:** Do not annotate trends, peaks, or ranges inline "
        "with the data table. Reserve all trend commentary, observations, and analysis for a "
        "separate 'Interpretation' section that follows the table(s).\n"
        "4. **RANGE SUMMARIES ARE FORBIDDEN:** Never write 'Netherlands (2015→2026): 792,438 → 974,434' "
        "as a summary of a time series. Show the full table instead.\n\n"
        "### EXECUTION DISCIPLINE\n"
        "1. **NO DUPLICATE TOOL CALLS:** Before calling any tool, check whether you have already "
        "called that tool with the same (or equivalent) parameters in this session. "
        "If you have, use the result you already received — do NOT call it again.\n"
        "2. **PLAN BEFORE CALLING:** When a user asks a broad question, decide upfront which tools "
        "you need, call each exactly once, then synthesise all results together.\n"
        "3. **BATCH, DON'T REPEAT:** If you need the same metric for multiple countries or tickers, "
        "pass them all in one call (comma-separated). Never split a multi-entity request into "
        "separate single-entity calls.\n"
        "4. **STOP WHEN DONE:** Once you have all the data needed to answer the question, stop "
        "calling tools and present the analysis. Do not call additional tools speculatively."
    ),
)


# ══════════════════════════════════════════════════════════════════════
#  Built-in discovery & utility tools
# ══════════════════════════════════════════════════════════════════════


@mcp.tool()
def list_categories() -> str:
    """List all available metric categories and how many tools each has.

    Use this first to understand what's available, then call
    ``list_metrics_by_category`` with a specific category name.
    """
    index = get_tool_index()

    # Human-friendly category descriptions that guide tool selection.
    _CATEGORY_DESCRIPTIONS: dict[str, str] = {
        "ratios": "Pre-computed financial ratios (PE, EPS, ROE, margins, liquidity, valuation)."
        "Use these INSTEAD of raw financial statements.",
        "performance": "Risk-adjusted returns (Sharpe, Sortino, alpha, beta, CAPM, Fama-French)."
        "No need to fetch price data first.",
        "risk": "Risk metrics (VaR, CVaR, GARCH, drawdown, skewness, kurtosis). No need to fetch price data first.",
        "models": "Financial models (DCF/intrinsic value, WACC, Dupont, Altman Z, Piotroski). Pre-computed.",
        "technicals": "Technical indicators (RSI, MACD, Bollinger, moving averages, support/resistance)."
        "Applied to price data automatically.",
        "options": "Option pricing and Greeks (Black-Scholes, binomial, delta, gamma, theta, vega, implied vol).",
        "economics": "Macroeconomic data by country (GDP, inflation, unemployment, interest rates)."
        "NO tickers needed — use `countries` param.",
        "fixedincome": "Bond yields, central bank rates, EURIBOR, duration, present value. NO tickers needed.",
        "discovery": "Market discovery (stock/ETF/crypto lists, screener, gainers/losers, sector performance)."
        "NO tickers needed.",
        "toolkit": "Raw data (historical prices, financial statements, company profile, quotes)."
        "Use ratios/performance/risk tools for computed metrics.",
    }

    lines = ["| Category | Tools | Description |", "| --- | --- | --- |"]
    for cat in sorted(index.keys()):
        n = len(index.get(cat, []))
        desc = _CATEGORY_DESCRIPTIONS.get(cat, "N/A")
        lines.append(f"| `{cat}` | {n} | {desc} |")
    lines.append(f"\n**Total tools: {sum(len(v) for v in index.values())}**")
    lines.append("\n**Tip:** Use `search_metrics('keyword')` to find tools by keyword.")
    return "\n".join(lines)


@mcp.tool()
def list_metrics_by_category(category: str) -> str:
    """List every available metric/tool within a category.

    Args:
        category: One of ratios, technicals, models, performance, risk,
                  economics, fixedincome, options, discovery, toolkit.

    Returns a table with tool names and descriptions so you can pick the
    right one to call.
    """
    index = get_tool_index()
    cat = category.lower().strip()
    if cat not in index:
        available = ", ".join(sorted(index.keys()))
        return f"Unknown category `{cat}`. Available: {available}"

    tools = index[cat]
    if not tools:
        return f"No tools registered for `{cat}`."

    lines = [
        f"### {cat} — {len(tools)} metrics\n",
        "| Tool | Description |",
        "| --- | --- |",
    ]
    for t in tools:
        lines.append(f"| `{t['tool']}` | {t['description']} |")
    return "\n".join(lines)


_SEARCH_STOP_WORDS = frozenset(
    {
        "a",
        "an",
        "the",
        "and",
        "or",
        "of",
        "is",
        "are",
        "was",
        "were",
        "for",
        "to",
        "in",
        "on",
        "at",
        "by",
        "it",
        "its",
        "with",
        "this",
        "that",
        "what",
        "how",
        "get",
        "show",
        "me",
        "my",
        "our",
        "their",
        "which",
        "from",
        "as",
        "per",
        "be",
        "been",
        "has",
        "have",
        "had",
        "do",
        "does",
        "did",
        "will",
        "would",
        "can",
        "could",
        "should",
    }
)


@mcp.tool()
def search_metrics(query: str) -> str:
    """Search across all metrics by keyword with typo tolerance.

    This tool supports minor typos and common financial abbreviations.

    Args:
        query: Free-text search (e.g. 'debt', 'moving average', 'sharpe',
               'retun on equty').

    Returns matching tools across all categories, sorted by relevance.
    """
    index = get_tool_index()
    query_tokens = [
        w.lower()
        for w in re.findall(r"\b[a-zA-Z]{2,}\b", query)
        if w.lower() not in _SEARCH_STOP_WORDS
    ]
    if not query_tokens:
        return (
            f"No meaningful search terms in '{query}'. " "Try a more specific keyword."
        )

    results: list[tuple[float, dict]] = []
    for cat, tools in index.items():
        for t in tools:
            search_text = f"{t['tool']} {t['description']}".lower()
            text_words = set(re.findall(r"\b[a-z]{3,}\b", search_text))
            score = 0.0
            for token in query_tokens:
                if token in search_text:
                    score += 1.0
                elif len(token) >= 4:  # noqa
                    close = difflib.get_close_matches(
                        token, text_words, n=1, cutoff=0.82
                    )
                    if close:
                        score += 0.7
            if score > 0:
                results.append((score / len(query_tokens), {**t, "category": cat}))

    results.sort(key=lambda x: x[0], reverse=True)
    hits = [(s, t) for s, t in results if s >= 0.3][:30]  # noqa

    if not hits:
        return (
            f"No strong matches for '{query}'. "
            "Try `list_categories()` to browse all modules."
        )

    lines = [
        f"### Search results for '{query}' — {len(hits)} matches\n",
        "| Category | Tool | Description |",
        "| --- | --- | --- |",
    ]
    for _, h in hits:
        lines.append(f"| `{h['category']}` | `{h['tool']}` | {h['description']} |")
    return "\n".join(lines)


@mcp.tool()
def search_instruments(query: str, search_method: str = "name") -> str:
    """Search for ticker symbols by company name, symbol, CIK, CUSIP, or ISIN.

    Args:
        query: The search term (e.g. 'Apple', 'META', '0000320193').
        search_method: One of 'name', 'symbol', 'cik', 'cusip', 'isin'.
    """
    try:
        result = _provider.call_method(
            module_name="discovery",
            method_name="search_instruments",
            category="discovery",
            query=query,
            search_method=search_method,
        )
        return format_result(result, title=f"Search: {query}")
    except Exception as exc:
        return f"⚠ Search failed: {exc}"


@mcp.tool()
def clear_cache() -> str:
    """Clear the local result cache. Use when you need fresh data."""
    n = _provider.clear_cache()
    return f"Cache cleared. {n} entries removed."


@mcp.tool()
def calculate_growth(
    metric: str,
    tickers: str = "AAPL",
    start_date: str = "2015-01-01",
    end_date: str = "",
    quarterly: bool = False,
    lag: int = 1,
    countries: str = "",
) -> str:
    """Calculate period-over-period growth rates for any metric.

    This tool computes growth rates (percentage change) for any metric
    available in the toolkit. Works with both ticker-based metrics
    (ratios, performance) and standalone metrics (economics).

    Args:
        metric: The metric tool name to calculate growth for, e.g.
                'ratios_get_revenue_per_share', 'economics_get_gross_domestic_product'.
        tickers: Comma-separated ticker symbols (for ticker-based metrics).
        start_date: Start date in YYYY-MM-DD format.
        end_date: End date in YYYY-MM-DD format (defaults to today).
        quarterly: Whether to use quarterly data.
        lag: Number of periods for growth calculation (1 = QoQ or YoY).
        countries: Comma-separated country names (for economics metrics).
    """
    # Parse the metric name to find module and method
    parts = metric.replace("-", "_").split("_", 1)
    if len(parts) < 2:  # noqa
        return f"⚠ Invalid metric name '{metric}'. "
    "Use format: category_method_name"

    module_name = parts[0]
    method_name = parts[1]

    # Determine category from module name
    category_map = {
        "ratios": "ticker",
        "technicals": "ticker",
        "models": "ticker",
        "performance": "ticker",
        "risk": "ticker",
        "options": "ticker",
        "economics": "standalone",
        "fixedincome": "standalone",
        "discovery": "discovery",
        "toolkit": "toolkit",
    }

    category = category_map.get(module_name)
    if not category:
        return f"⚠ Unknown module '{module_name}'. Available: {', '.join(category_map.keys())}"

    try:
        ticker_list = (
            [t.strip().upper() for t in tickers.split(",") if t.strip()]
            if tickers
            else None
        )
        country_list = (
            [c.strip() for c in countries.split(",") if c.strip()]
            if countries
            else None
        )
        if not end_date:

            end_date = datetime.now().strftime("%Y-%m-%d")

        result = _provider.call_method(
            module_name=module_name,
            method_name=method_name,
            category=category,
            tickers=ticker_list,
            countries=country_list,
            start_date=start_date,
            end_date=end_date,
            quarterly=quarterly,
        )

        if isinstance(result, pd.DataFrame | pd.Series):
            growth = _calc_growth(result, lag=lag)
            return format_result(
                growth,
                title=f"Growth of {module_name}.{method_name} (lag={lag})",
            )
        return "⚠ Cannot compute growth — result is not tabular data."

    except Exception as exc:
        return f"⚠ Growth calculation failed for `{metric}`: {exc}"


# ══════════════════════════════════════════════════════════════════════
#  Startup — register all dynamic tools (NO Toolkit instantiated)
# ══════════════════════════════════════════════════════════════════════

_UTILITY_TOOL_COUNT = 6


def _startup() -> None:
    """Register all dynamic tools and log summary."""
    count = register_all_tools(mcp, _provider)
    logger.info(
        "FinanceToolkit MCP Server ready — %d metric tools + %d utility tools",
        count,
        _UTILITY_TOOL_COUNT,
    )


_startup()


def main() -> None:
    """Run the MCP server (stdio transport for Claude Desktop compatibility)."""
    transport = os.environ.get("MCP_TRANSPORT", "stdio")
    logger.info("Starting MCP server on transport=%s", transport)
    mcp.run(transport=transport)


if __name__ == "__main__":
    main()
