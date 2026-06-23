# External Integrations

**Analysis Date:** 2026-06-23

## APIs & External Services

**Financial Data Providers:**
- FinancialModelingPrep (FMP)
  - What it's used for: Comprehensive financial statements, ratios, historical data, company profiles, earnings/dividend calendars, analyst estimates, ESG scores, treasury data
  - SDK/Client: `requests` library via `get_request()` helper
  - Auth: API key via `FT_MCP_SECRET_KEY` env var, per-user resolution in hosted mode
  - Endpoints: `fmp_model.py` functions like `get_financial_data()` handle rate limits and retry logic
  - Rate limiting: Free tier (1 req/sec), Premium tiers with higher limits; configured subscription handling in `financetoolkit/fmp_model.py` lines 35-150+
  - Error handling: Returns error indicator columns (e.g., `LIMIT REACH`, `INVALID API KEY`, `PREMIUM QUERY PARAMETER`) instead of raising exceptions

- Yahoo Finance (yfinance)
  - What it's used for: Stock price data, financial statements (fallback when FMP unavailable), intraday data
  - SDK/Client: `yfinance` package
  - Auth: None (public API)
  - Fallback: Primary fallback when FMP rate limit reached or API key invalid
  - Error handling: `RemoteDisconnected`, `HTTPError`, `URLError`, `YFRateLimitError` caught in `financetoolkit/yfinance_model.py`

**Macroeconomic Data:**
- OECD Statistics (SDMX API)
  - What it's used for: GDP, inflation, unemployment, trade balances, government debt, interest rates, labour metrics, carbon/renewable energy
  - SDK/Client: `requests` library via `get_request()` helper
  - Auth: None (public API)
  - Base URL: `https://sdmx.oecd.org/public/rest/data/` with CSV format response
  - Country codes: Extensive mapping in `financetoolkit/economics/oecd_model.py` (lines 21-200+)
  - Caching: Used by `Economics` controller (`financetoolkit/economics/economics_controller.py`) to avoid redundant calls

## Data Storage

**Databases:**
- SQLite (result cache)
  - Connection: Configurable path via `FINANCE_TOOLKIT_CACHE_DB` env var; defaults to `$XDG_CONFIG_HOME/financetoolkit/financetoolkit_cache.db`
  - Client: `sqlite3` (stdlib) with thread-safe wrapper in `financetoolkit/mcp_server/cache_model.py`
  - Purpose: MCP server caches DataFrame results with JSON serialization, 10-minute TTL (configurable via `FINANCE_TOOLKIT_CACHE_TTL`)
  - Schema: Single table with `key`, `value`, `timestamp` columns; hash-based key generation in `SQLiteCache` class

- Pickle Files (local filesystem cache)
  - Location: Project-specific cache directory
  - Client: Python `pickle` module
  - Purpose: Local development/CLI caching of DataFrames via `load_cached_data()` / `save_cached_data()` in `financetoolkit/utilities/cache_model.py`

**File Storage:**
- Local filesystem only
  - `.env` file for API keys (project root or `~/.config/financetoolkit/`)
  - `config.yaml` for MCP server configuration
  - Cache files (pickle, SQLite database)
  - Excel export via openpyxl (user-driven, not automatic)

**Caching:**
- SQLite with TTL enforcement (MCP server) - `financetoolkit/mcp_server/cache_model.py`
- Pickle file cache (CLI/library mode) - `financetoolkit/utilities/cache_model.py`
- No distributed caching (Redis, Memcached)

## Authentication & Identity

**Auth Provider:**
- Custom OAuth 2.1 implementation
  - Implementation: `financetoolkit/mcp_server/auth_model.py`
  - Flow: Authorization Code flow with PKCE support
  - Token endpoint: `/oauth/token`
  - Authorization endpoint: `/oauth/authorize`
  - Callback endpoint: `/oauth/callback`
  - HTML UI: Embedded template in auth_model.py (self-contained, no external CDN)

**API Key Resolution (Hosted MCP Mode):**
- Per-request header-based resolution in priority order:
  1. `x-fmp-api-key` header
  2. `x-financial-modeling-prep-api-key` header
  3. Query parameter: `fmp_api_key` or `api_key` or `fmp_key`
  4. Fallback to env var: `FT_MCP_SECRET_KEY` (server-side default)
- Implementation: `financetoolkit/mcp_server/auth_model.py` lines 31-41 and `resolve_api_key()` function in `provider_model.py`
- JWT handling: Signed tokens with HMAC-SHA256 (secret key in `FT_MCP_SECRET_KEY`)

## Monitoring & Observability

**Error Tracking:**
- None (no Sentry, Rollbar, etc.)
- Custom error categorization in `financetoolkit/utilities/error_model.py` for financial data fetch failures
- Error columns returned in DataFrames when API calls fail (graceful degradation)

**Logs:**
- Python logging module via `financetoolkit/utilities/logger_model.py`
- Console output with ISO timestamp format
- Level: INFO (default), configurable via `DEBUG` env var
- No log aggregation (local console only in production Docker mode)

## CI/CD & Deployment

**Hosting:**
- Docker container (Python 3.12-slim) for MCP server
- Deployed to: `financetoolkit.jeroenbouma.com/mcp` (currently live)
- Transport: Streamable HTTP via FastMCP

**CI Pipeline:**
- None detected (no GitHub Actions, GitLab CI, Jenkins)
- Pre-commit hooks enforced locally via `.pre-commit-config.yaml`:
  - YAML validation
  - End-of-file fixes
  - Trailing whitespace removal
  - Private key detection
  - Black formatting
  - Ruff linting
  - Codespell checks

**Build Pipeline:**
- Hatchling (pyproject.toml-based)
- Entry points: `financetoolkit-mcp`, `financetoolkit-mcp-inspector`, `financetoolkit-mcp-setup`
- Docker build: `FROM python:3.12-slim` → install `uv` → sync dependencies → copy source → expose port 8000 → healthcheck

## Environment Configuration

**Required env vars:**
- `FT_MCP_SECRET_KEY` - OAuth/JWT secret key for MCP server (must be set in hosted mode)
- `FMP_API_KEY` or headers - Financial Modeling Prep API key (fallback if per-request header not provided)

**Optional env vars:**
- `FINANCE_TOOLKIT_CACHE_DB` - Path to SQLite cache database (defaults to `~/.config/financetoolkit/financetoolkit_cache.db`)
- `FINANCE_TOOLKIT_CACHE_TTL` - Cache time-to-live in seconds (default: 600)
- `DEBUG` - Enable debug logging
- `MCP_TRANSPORT` - Protocol transport (default: `streamable-http`)
- `MCP_HOST` - Server bind address (default: `0.0.0.0`)
- `MCP_PORT` - Server port (default: `8000`)
- `XDG_CONFIG_HOME` - Config directory location (Unix standard, defaults to `~/.config`)

**Secrets location:**
- `.env` file (not committed, listed in `.gitignore`)
- Environment variables at runtime
- Per-user query parameters in hosted mode (Claude.ai integration via MCP)

## Webhooks & Callbacks

**Incoming:**
- OAuth 2.1 callback endpoint: `/oauth/callback` - Accepts authorization code, exchanges for access token
- MCP tool invocation endpoints - FastMCP handles streaming HTTP protocol

**Outgoing:**
- None (Finance Toolkit is read-only; no webhook push to external services)

## Testing Integration Configuration

**pytest Fixtures:**
- Custom `Record` class for VCR-style HTTP recording (`tests/conftest.py`)
- Support for `--live` flag to skip recorded responses and fetch fresh data
- Per-test recording of FMP/OECD/yfinance API responses
- Approximate float comparison (1e-9 tolerance) for numerical stability

**Test Data Sources:**
- Live mode: Actual API calls to FMP, OECD, yfinance (requires valid API keys)
- Recording mode: Pre-captured JSON/CSV files in `tests/cassettes/` (location inferred from conftest)
- Markers: Skip tests without `--live` when using recorded mode

---

*Integration audit: 2026-06-23*
