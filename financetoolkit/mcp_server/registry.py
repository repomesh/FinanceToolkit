"""
Dynamic tool registration for the FinanceToolkit MCP Server.

Discovers every public method on each FinanceToolkit controller class via
static inspection and registers a thin MCP wrapper with the correct parameter
schema for its module category:

    ticker     — Ratios, Models, Technicals, Performance, Risk, Options
    toolkit    — Toolkit direct methods (historical data, financial statements, …)
    standalone — Economics, FixedIncome (no tickers required)
    discovery  — Discovery (no tickers, no date range)
"""

from __future__ import annotations

import inspect
import logging
import re
import textwrap
from typing import Any, Union, get_args, get_origin

from mcp.server.fastmcp import FastMCP

from financetoolkit.discovery.discovery_controller import Discovery
from financetoolkit.economics.economics_controller import Economics
from financetoolkit.fixedincome.fixedincome_controller import FixedIncome
from financetoolkit.mcp_server.formatting import format_result
from financetoolkit.mcp_server.provider import ToolkitProvider
from financetoolkit.models.models_controller import Models
from financetoolkit.options.options_controller import Options
from financetoolkit.performance.performance_controller import Performance

# Controller classes imported for *static inspection only* — never instantiated here.
from financetoolkit.ratios.ratios_controller import Ratios
from financetoolkit.risk.risk_controller import Risk
from financetoolkit.technicals.technicals_controller import Technicals
from financetoolkit.toolkit_controller import Toolkit

try:
    from types import UnionType  # Python 3.10+
except ImportError:
    UnionType = None  # type: ignore[misc,assignment]

logger = logging.getLogger(__name__)

# ══════════════════════════════════════════════════════════════════════
#  Module category definitions
# ══════════════════════════════════════════════════════════════════════
CATEGORY_TICKER = "ticker"
CATEGORY_TOOLKIT = "toolkit"
CATEGORY_STANDALONE = "standalone"
CATEGORY_DISCOVERY = "discovery"

# Maps module_name → (controller_class, category)
MODULE_REGISTRY: dict[str, tuple[type, str]] = {
    "ratios": (Ratios, CATEGORY_TICKER),
    "technicals": (Technicals, CATEGORY_TICKER),
    "models": (Models, CATEGORY_TICKER),
    "performance": (Performance, CATEGORY_TICKER),
    "risk": (Risk, CATEGORY_TICKER),
    "options": (Options, CATEGORY_TICKER),
    "economics": (Economics, CATEGORY_STANDALONE),
    "fixedincome": (FixedIncome, CATEGORY_STANDALONE),
    "discovery": (Discovery, CATEGORY_DISCOVERY),
}

# Explicit allowlist of Toolkit direct methods exposed as MCP tools.
_TOOLKIT_DIRECT_METHODS = frozenset(
    {
        "get_profile",
        "get_quote",
        "get_rating",
        "get_analyst_estimates",
        "get_earnings_calendar",
        "get_revenue_geographic_segmentation",
        "get_revenue_product_segmentation",
        "get_historical_data",
        "get_intraday_data",
        "get_dividend_calendar",
        "get_esg_scores",
        "get_historical_statistics",
        "get_treasury_data",
        "get_exchange_rates",
        "get_balance_sheet_statement",
        "get_income_statement",
        "get_cash_flow_statement",
        "get_statistics_statement",
    }
)

# Backward-compatible class map used by list_categories.
MODULE_CLASS_MAP: dict[str, type] = {
    name: cls for name, (cls, _) in MODULE_REGISTRY.items()
}
MODULE_CLASS_MAP["toolkit"] = Toolkit

# ══════════════════════════════════════════════════════════════════════
#  Filtering constants
# ══════════════════════════════════════════════════════════════════════

# Methods to skip during inspection.
_SKIP_METHODS = frozenset(
    {
        "to_dict",
        "to_json",
        "to_csv",
        "to_html",
        "copy",
        "keys",
        "values",
        "items",
        "get_normalization_files",
    }
)

# Parameters always removed from method inspection.
_SKIP_PARAMS = frozenset({"self", "progress_bar"})

# Parameters handled at the wrapper / Toolkit-init level.
_INIT_HANDLED_PARAMS = frozenset(
    {
        "tickers",
        "countries",
        "start_date",
        "end_date",
        "quarterly",
        "benchmark_ticker",
    }
)

# ══════════════════════════════════════════════════════════════════════
#  Tool index — populated during registration
# ══════════════════════════════════════════════════════════════════════
_TOOL_INDEX: dict[str, list[dict[str, str]]] = {}


# ══════════════════════════════════════════════════════════════════════
#  Helpers
# ══════════════════════════════════════════════════════════════════════


def _clean_docstring(
    doc: str | None,
    max_chars: int = 500,
) -> str:
    """Extract the first paragraph and any 'Also known as:' line from a docstring."""
    if not doc:
        return "No description available."

    full = textwrap.dedent(doc).strip()

    # Extract first paragraph (everything before the first blank line).
    first_para_end = full.find("\n\n")
    first_para = full[:first_para_end].strip() if first_para_end > 0 else full
    desc = re.sub(r"\s+", " ", first_para)

    # Append 'Also known as:' if present anywhere in the full docstring.
    aka_match = re.search(r"Also known as:\s*(.+?)(?:\n|$)", full)
    if aka_match:
        aka = aka_match.group(1).strip().rstrip(".")
        desc = f"{desc} Also known as: {aka}."

    return (desc[: max_chars - 3] + "...") if len(desc) > max_chars else desc


def _to_bool(v: Any) -> bool:
    """Coerce a value to bool (handles string inputs from LLMs)."""
    if isinstance(v, bool):
        return v
    return str(v).lower() in ("true", "1", "yes")


def _unwrap_type(annotation: Any) -> Any:
    """Unwrap Optional / Union annotations to the primary concrete type."""
    origin = get_origin(annotation)
    is_union = origin is Union or (
        UnionType is not None and isinstance(annotation, UnionType)
    )
    if is_union:
        args = [a for a in get_args(annotation) if a is not type(None)]
        return args[0] if args else str
    return annotation


def _coerce_value(val: Any, annotation: Any) -> Any:
    """Best-effort type coercion for LLM-provided parameter values."""
    if val is None or val == "":
        return None
    target = _unwrap_type(annotation)
    if target is bool:
        return _to_bool(val)
    if target is int:
        try:
            return int(float(val))
        except (ValueError, TypeError):
            return val
    if target is float:
        try:
            return float(val)
        except (ValueError, TypeError):
            return val
    return val


def _validate_date(date_str: str) -> str:
    """Normalise a date string to YYYY-MM-DD or return a safe default."""
    if not date_str:
        return ""
    cleaned = date_str.replace("/", "-")
    if re.match(r"^\d{4}-\d{2}-\d{2}$", cleaned):
        return cleaned
    return "2020-01-01"


def _extract_extra_params(method: Any) -> list[inspect.Parameter]:
    """Return method parameters that are NOT handled by the wrapper."""
    sig = inspect.signature(method)
    return [
        p
        for name, p in sig.parameters.items()
        if name not in _SKIP_PARAMS
        and name not in _INIT_HANDLED_PARAMS
        and p.kind
        in (
            inspect.Parameter.POSITIONAL_OR_KEYWORD,
            inspect.Parameter.KEYWORD_ONLY,
        )
    ]


# ══════════════════════════════════════════════════════════════════════
#  Wrapper construction
# ══════════════════════════════════════════════════════════════════════


def _build_common_signature_params(category: str) -> list[inspect.Parameter]:
    """Build the common MCP-level parameters for a given category."""
    P = inspect.Parameter
    POS = P.POSITIONAL_OR_KEYWORD
    params: list[P] = []

    if category in (CATEGORY_TICKER, CATEGORY_TOOLKIT):
        params.append(P("tickers", POS, default="AAPL", annotation=str))

    if category == CATEGORY_STANDALONE:
        params.append(P("countries", POS, default="", annotation=str))

    if category != CATEGORY_DISCOVERY:
        params.extend(
            [
                P("start_date", POS, default="2015-01-01", annotation=str),
                P("end_date", POS, default="", annotation=str),
                P("quarterly", POS, default=False, annotation=bool),
            ]
        )

    if category in (CATEGORY_TICKER, CATEGORY_TOOLKIT):
        params.append(P("benchmark_ticker", POS, default="SPY", annotation=str))

    # Formatting params — always present.
    params.extend(
        [
            P("small_context", POS, default=False, annotation=bool),
            P("historical", POS, default=False, annotation=bool),
        ]
    )
    return params


def _build_wrapper(
    provider: ToolkitProvider,
    module_name: str,
    method_name: str,
    extra_params: list[inspect.Parameter],
    category: str,
) -> callable:
    """
    Create a wrapper callable with an explicit ``__signature__`` that
    FastMCP can introspect to generate the JSON-RPC tool schema.

    The wrapper:
    1. Receives all params from the LLM via FastMCP.
    2. Splits them into init-level, formatting, and method-level groups.
    3. Routes through the provider with category-aware dispatch.
    4. Formats the result into compact Markdown.
    5. Returns clean error messages on failure.
    """
    # Pre-compute param metadata for the closure.
    param_meta: list[tuple[str, Any, Any]] = [
        (p.name, p.annotation, p.default) for p in extra_params
    ]

    def wrapper(**kwargs: Any) -> str:
        # ── Formatting params ─────────────────────────────────────
        small_context = _to_bool(kwargs.pop("small_context", False))
        hist = _to_bool(kwargs.pop("historical", False))

        # ── Method-specific params ────────────────────────────────
        method_kwargs: dict[str, Any] = {}
        for pname, pann, _pdefault in param_meta:
            if pname in kwargs:
                method_kwargs[pname] = _coerce_value(kwargs.pop(pname), pann)
            # If not provided, let the underlying method use its own default.

        # ── Init-level params (remaining in kwargs) ───────────────
        raw_tickers = kwargs.pop("tickers", None)
        tickers: list[str] | None = None
        if raw_tickers:
            tickers = [
                t.strip().upper() for t in str(raw_tickers).split(",") if t.strip()
            ]

        raw_countries = kwargs.pop("countries", None)
        countries: list[str] | None = None
        if raw_countries:
            countries = [c.strip() for c in str(raw_countries).split(",") if c.strip()]

        start_date = _validate_date(
            kwargs.pop("start_date", "2015-01-01") or "2015-01-01"
        )
        end_date = kwargs.pop("end_date", "") or None
        quarterly = _to_bool(kwargs.pop("quarterly", False))
        benchmark_ticker = kwargs.pop("benchmark_ticker", "SPY")

        # ── Dispatch via provider ─────────────────────────────────
        try:
            result = provider.call_method(
                module_name=module_name,
                method_name=method_name,
                category=category,
                tickers=tickers,
                countries=countries,
                start_date=start_date,
                end_date=end_date,
                quarterly=quarterly,
                benchmark_ticker=benchmark_ticker,
                **method_kwargs,
            )
            return format_result(
                result,
                small_context=small_context,
                historical=hist,
                title=f"{module_name}.{method_name}",
            )
        except (ValueError, KeyError) as exc:
            return f"⚠ Invalid input for `{module_name}.{method_name}`: {exc}"
        except TypeError as exc:
            return f"⚠ Parameter error for `{module_name}.{method_name}`: {exc}"
        except ConnectionError as exc:
            return f"⚠ API connection failed: {exc}"
        except Exception as exc:
            logger.warning(
                "Tool %s.%s failed: %s",
                module_name,
                method_name,
                exc,
                exc_info=True,
            )
            return (
                f"⚠ `{module_name}.{method_name}` failed — "
                f"{type(exc).__name__}: {exc}"
            )

    # ── Attach explicit signature for FastMCP schema generation ───
    common = _build_common_signature_params(category)
    POS = inspect.Parameter.POSITIONAL_OR_KEYWORD
    sig_params = list(common)

    for p in extra_params:
        ann = p.annotation if p.annotation is not inspect.Parameter.empty else str
        default = p.default if p.default is not inspect.Parameter.empty else ""
        sig_params.append(
            inspect.Parameter(p.name, POS, default=default, annotation=ann)
        )

    wrapper.__signature__ = inspect.Signature(sig_params, return_annotation=str)
    wrapper.__annotations__ = {p.name: p.annotation for p in sig_params}
    wrapper.__annotations__["return"] = str

    return wrapper


# ══════════════════════════════════════════════════════════════════════
#  Registration
# ══════════════════════════════════════════════════════════════════════


def _register_module_tools(
    mcp: FastMCP,
    provider: ToolkitProvider,
    module_name: str,
    cls: type,
    category: str,
) -> int:
    """Register all public methods of *cls* as MCP tools."""
    count = 0
    _TOOL_INDEX[module_name] = []

    try:
        members = inspect.getmembers(cls, predicate=inspect.isfunction)
    except Exception as exc:
        logger.warning("Cannot inspect %s: %s", module_name, exc)
        return 0

    for meth_name, meth_func in sorted(members):
        if meth_name.startswith("_") or meth_name in _SKIP_METHODS:
            continue

        doc = _clean_docstring(meth_func.__doc__)
        full_desc = f"[{module_name}] {doc}"
        extra = _extract_extra_params(meth_func)

        try:
            fn = _build_wrapper(provider, module_name, meth_name, extra, category)
            tool_name = f"{module_name}_{meth_name}"
            fn.__name__ = tool_name
            fn.__doc__ = full_desc
            mcp.add_tool(fn, name=tool_name, description=full_desc)
            _TOOL_INDEX[module_name].append({"tool": tool_name, "description": doc})
            count += 1
        except Exception as exc:
            logger.debug("Skipping %s.%s: %s", module_name, meth_name, exc)

    return count


def _register_toolkit_direct_tools(
    mcp: FastMCP,
    provider: ToolkitProvider,
) -> int:
    """Register Toolkit direct methods (historical data, financials, …)."""
    count = 0
    module_name = "toolkit"
    _TOOL_INDEX[module_name] = []

    for meth_name in sorted(_TOOLKIT_DIRECT_METHODS):
        meth_func = getattr(Toolkit, meth_name, None)
        if meth_func is None:
            logger.debug("Toolkit.%s not found — skipping", meth_name)
            continue

        doc = _clean_docstring(meth_func.__doc__)
        full_desc = f"[toolkit] {doc}"
        extra = _extract_extra_params(meth_func)

        try:
            fn = _build_wrapper(
                provider,
                module_name,
                meth_name,
                extra,
                CATEGORY_TOOLKIT,
            )
            tool_name = f"{module_name}_{meth_name}"
            fn.__name__ = tool_name
            fn.__doc__ = full_desc
            mcp.add_tool(fn, name=tool_name, description=full_desc)
            _TOOL_INDEX[module_name].append({"tool": tool_name, "description": doc})
            count += 1
        except Exception as exc:
            logger.debug("Skipping toolkit.%s: %s", meth_name, exc)

    return count


def register_all_tools(mcp: FastMCP, provider: ToolkitProvider) -> int:
    """
    Discover and register all FinanceToolkit methods as MCP tools.

    Uses static class inspection — no Toolkit instance is created.
    """
    total = 0

    # Sub-module controllers
    for module_name, (cls, category) in MODULE_REGISTRY.items():
        n = _register_module_tools(mcp, provider, module_name, cls, category)
        logger.info("Registered %d tools for %s (%s)", n, module_name, category)
        total += n

    # Toolkit direct methods (historical data, financials, etc.)
    n = _register_toolkit_direct_tools(mcp, provider)
    logger.info("Registered %d toolkit direct tools", n)
    total += n

    logger.info("Total tools registered: %d", total)
    return total


def get_tool_index() -> dict[str, list[dict[str, str]]]:
    """Return the category → tools index built during registration."""
    return _TOOL_INDEX
