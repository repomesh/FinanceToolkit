"""Tests for per-request API key resolution (hosted vs local transports)."""

import fastmcp.server.dependencies as deps
from starlette.requests import Request

from financetoolkit.mcp_server import auth_model


def _make_request(query: str = "") -> Request:
    """Build a minimal Starlette request carrying the given query string."""
    scope = {
        "type": "http",
        "http_version": "1.1",
        "method": "POST",
        "path": "/mcp",
        "raw_path": b"/mcp",
        "query_string": query.encode(),
        "headers": [],
    }
    return Request(scope)


def test_stdio_returns_empty(monkeypatch):
    """No active HTTP request (stdio / uvx) yields an empty string for env fallback."""

    def _raise():
        raise RuntimeError("no http request")

    monkeypatch.setattr(deps, "get_http_headers", lambda include=None: {})
    monkeypatch.setattr(deps, "get_http_request", _raise)
    assert auth_model.resolve_api_key() == ""


def test_custom_header(monkeypatch):
    """The X-FMP-API-Key header is resolved."""
    monkeypatch.setattr(
        deps, "get_http_headers", lambda include=None: {"x-fmp-api-key": "HKEY"}
    )
    monkeypatch.setattr(deps, "get_http_request", lambda: _make_request())
    assert auth_model.resolve_api_key() == "HKEY"


def test_authorization_bearer(monkeypatch):
    """An Authorization: Bearer token is resolved."""
    monkeypatch.setattr(
        deps,
        "get_http_headers",
        lambda include=None: {"authorization": "Bearer BKEY"},
    )
    monkeypatch.setattr(deps, "get_http_request", lambda: _make_request())
    assert auth_model.resolve_api_key() == "BKEY"


def test_query_param(monkeypatch):
    """The ?fmp_api_key query parameter (Claude.ai path) is resolved."""
    monkeypatch.setattr(deps, "get_http_headers", lambda include=None: {})
    monkeypatch.setattr(
        deps, "get_http_request", lambda: _make_request("fmp_api_key=QKEY")
    )
    assert auth_model.resolve_api_key() == "QKEY"


def test_query_param_alias(monkeypatch):
    """The ?api_key alias is resolved."""
    monkeypatch.setattr(deps, "get_http_headers", lambda include=None: {})
    monkeypatch.setattr(deps, "get_http_request", lambda: _make_request("api_key=AKEY"))
    assert auth_model.resolve_api_key() == "AKEY"


def test_header_beats_query(monkeypatch):
    """A header takes priority over a query parameter when both are present."""
    monkeypatch.setattr(
        deps, "get_http_headers", lambda include=None: {"x-fmp-api-key": "HKEY"}
    )
    monkeypatch.setattr(
        deps, "get_http_request", lambda: _make_request("fmp_api_key=QKEY")
    )
    assert auth_model.resolve_api_key() == "HKEY"
