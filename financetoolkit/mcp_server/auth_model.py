"""Per-request Financial Modeling Prep API key resolution for hosted deployments.

The Finance Toolkit MCP server can run in two very different ways:

* **Local / uvx (stdio transport)** — a single user runs the server on their own
  machine.  There is no HTTP request, so the key comes from the
  ``FINANCIAL_MODELING_PREP_API_KEY`` environment variable (or a ``.env`` file).
  This is the classic setup written by the ``financetoolkit-mcp-setup`` wizard.

* **Hosted (HTTP transport, e.g. fastmcp.app / Horizon Prefect)** — a single
  shared server is used by many people, each of whom must bring their *own* FMP
  key.  The key arrives with every request, resolved here in priority order:

  1. **HTTP header** — ``X-FMP-API-Key`` (or ``X-Financial-Modeling-Prep-Api-Key``),
     or ``Authorization: Bearer <key>``.  Works with clients that allow custom
     headers (Cursor, VS Code, Claude Desktop custom connectors, Smithery remote,
     most registries).
  2. **URL query parameter** — ``?fmp_api_key=<key>`` (or ``?api_key=<key>``).
     This is the only no-chat, no-header path that works with Claude.ai, whose
     connector UI accepts a bare URL only.

When no HTTP request is active (stdio) the resolver returns an empty string and
callers fall back to the environment variable, preserving the local uvx setup.
"""

from __future__ import annotations

import fastmcp.server.dependencies as deps

from financetoolkit.utilities.logger_model import get_logger

logger = get_logger()

# Header names checked in order.  Custom ``x-*`` headers are forwarded by
# FastMCP's ``get_http_headers`` by default; ``authorization`` must be opted in.
_HEADER_NAMES: tuple[str, ...] = (
    "x-fmp-api-key",
    "x-financial-modeling-prep-api-key",
)

# Query-string parameter names checked in order.
_QUERY_NAMES: tuple[str, ...] = (
    "fmp_api_key",
    "api_key",
    "fmp_key",
)


def resolve_api_key() -> str:
    """Resolve the FMP API key from the active HTTP request, if any.

    Returns an empty string when there is no HTTP request (e.g. stdio transport)
    or when no key was supplied, so callers can fall back to the environment
    variable. Never raises.

    Resolution order: custom header → ``Authorization: Bearer`` → query param.

    Returns:
        str: The resolved API key, or ``""`` when none is present.
    """
    # 1. Custom headers (and Authorization, explicitly opted in).
    headers = deps.get_http_headers(include={"authorization"})
    for name in _HEADER_NAMES:
        value = headers.get(name)
        if value:
            return value.strip()

    authorization = headers.get("authorization", "")
    if authorization[:7].lower() == "bearer ":
        token = authorization[7:].strip()
        if token:
            return token

    # 2. URL query parameters (the Claude.ai path).
    try:
        request = deps.get_http_request()
    except RuntimeError:
        # No active HTTP request — stdio transport.
        return ""

    for name in _QUERY_NAMES:
        value = request.query_params.get(name)
        if value:
            return value.strip()

    return ""
