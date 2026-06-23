# Technology Stack

**Analysis Date:** 2026-06-23

## Languages

**Primary:**
- Python 3.10+ - Core financial analysis library and CLI tools
- Python 3.13 - Target version for code formatting and type checking

**Secondary:**
- HTML/CSS/JavaScript - OAuth 2.1 authentication UI template (embedded in `financetoolkit/mcp_server/auth_model.py`)

## Runtime

**Environment:**
- Python 3.10 to 3.15 (inclusive) - Supported versions per `pyproject.toml`
- Docker support via Python 3.12-slim container

**Package Manager:**
- `uv` - Universal Python package manager for dependency management
- Lockfile: `uv.lock` present

## Frameworks

**Core:**
- pandas >= 2.2 - DataFrames and time series data handling
- scikit-learn >= 1.6 - Machine learning algorithms (risk metrics, performance calculations)
- requests >= 2.32 - HTTP client for API calls

**Financial Data:**
- yfinance - Stock/ETF price data and financial statements (fallback source)

**MCP Server:**
- fastmcp >= 3.4.2 - Model Context Protocol server framework (optional, MCP extra)
- mcp[cli] >= 1.27.0 - MCP protocol implementation
- starlette - ASGI web framework for OAuth 2.1 auth endpoints
- uvicorn - ASGI server for hosting MCP endpoints
- anyio - Async I/O utilities

**Utilities:**
- openpyxl >= 3.1 - Excel file I/O for data export
- tqdm >= 4.67 - Progress bars for long-running operations
- pyyaml >= 6.0 - Configuration file parsing (`config.yaml`)
- python-dotenv >= 1.0 - Environment variable loading
- tabulate >= 0.9.0 - Text table formatting
- rich >= 13.0 - Terminal formatting and logging

**Testing:**
- pytest >= 8.3 - Test runner
- pytest-mock >= 3.14 - Mocking fixtures
- pytest-recording >= 0.13 - VCR-style HTTP recording
- pytest-cov >= 6.1 - Code coverage reporting
- pytest-timeout >= 2.3 - Timeout enforcement for tests
- ipykernel >= 6.29 - Jupyter notebook support

**Code Quality:**
- black >= 26.3.1 - Code formatter (targets Python 3.13)
- ruff >= 0.13.2 - Linter and import sorter
- codespell >= 2.4 - Spell checker for source code
- types-pyyaml >= 6.0 - Type stubs for PyYAML
- types-requests >= 2.32 - Type stubs for requests

**Build:**
- hatchling - Build system
- pre-commit - Git hooks for linting/formatting

## Key Dependencies

**Critical:**
- pandas - Handles all financial data structures (statements, time series)
- scikit-learn - Risk calculations (VaR, GARCH, drawdown, skewness, kurtosis), performance metrics (Sharpe, Sortino, alpha, beta)
- requests - HTTP calls to FMP and OECD APIs; handles SSL fallback for corporate proxies
- yfinance - Fallback for stock price and financial statement data when FMP unavailable

**Infrastructure:**
- SQLite - Result caching via `SQLiteCache` class in `financetoolkit/mcp_server/cache_model.py` (thread-safe, location configurable)
- pickle - Local file-based caching for DataFrames in `financetoolkit/utilities/cache_model.py`

## Configuration

**Environment:**
- `.env` file - Stores FMP API key and other secrets (location: project root or `$XDG_CONFIG_HOME/financetoolkit/`)
- `config.yaml` - MCP server configuration: tool groups, module mappings, cache TTL, skip methods
- `pyproject.toml` - Project metadata, dependencies, build config, tool settings

**Build:**
- `pyproject.toml` - Hatchling-based build, Python version constraints, entry points
- `Dockerfile` - Multi-stage Python 3.12-slim image for containerized MCP server
- `docker-compose.yml` - Orchestrates Finance Toolkit MCP server with volume persistence

**Code Style:**
- Black - Line length 122, targets Python 3.13
- Ruff - E, W, F, Q, S, UP, I, PD, SIM, PLC, PLE, PLR, PLW checks enabled
- `.pre-commit-config.yaml` - Hooks: pre-commit-hooks, black, ruff, codespell

## Platform Requirements

**Development:**
- Python 3.10+ with pip/uv
- `uv` for dependency management (optional but recommended)
- Git for version control and pre-commit hooks

**Production:**
- Docker 20.10+ (via `docker-compose.yml`)
- Python 3.10+ runtime
- Network access to:
  - FinancialModelingPrep API (https://site.financialmodellingprep.com/)
  - OECD SDMX API (https://sdmx.oecd.org/public/rest/data/)
  - Yahoo Finance (via yfinance)
- Writeable filesystem for SQLite cache (configurable via `FINANCE_TOOLKIT_CACHE_DB`)

## Entry Points

**CLI:**
- `financetoolkit-mcp` - Starts the MCP server
- `financetoolkit-mcp-inspector` - Debugging tool for MCP endpoints
- `financetoolkit-mcp-setup` - Initial setup and configuration

---

*Stack analysis: 2026-06-23*
