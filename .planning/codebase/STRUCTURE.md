<!-- refreshed: 2026-06-23 -->
# Codebase Structure

**Analysis Date:** 2026-06-23

## Directory Layout

```
FinanceToolkit/
├── financetoolkit/              # Main package root
│   ├── __init__.py              # Exports: Toolkit, Economics, FixedIncome, Discovery, Portfolio
│   ├── toolkit_controller.py     # Main Toolkit class (entry point)
│   ├── helpers.py               # Shared utility functions
│   ├── fmp_model.py             # FMP API client functions
│   ├── yfinance_model.py        # Yahoo Finance client functions
│   ├── historical_model.py      # Historical price data processing
│   ├── fundamentals_model.py    # Financial statement collection
│   ├── normalization_model.py   # Statement standardization/normalization
│   ├── currencies_model.py      # Currency conversion utilities
│   │
│   ├── ratios/                  # Ratio calculations (50+ financial ratios)
│   │   ├── ratios_controller.py # Main Ratios class
│   │   ├── efficiency_model.py  # Asset turnover, receivables turnover, etc.
│   │   ├── liquidity_model.py   # Current, quick, cash ratios
│   │   ├── profitability_model.py # Profit margins, ROA, ROE
│   │   ├── solvency_model.py    # Debt ratios, interest coverage
│   │   ├── valuation_model.py   # P/E, P/B, EV/EBITDA ratios
│   │   ├── helpers.py           # Ratio-specific utilities
│   │   └── __init__.py
│   │
│   ├── models/                  # Financial models
│   │   ├── models_controller.py # Main Models class (DUPONT, DCF, WACC, etc.)
│   │   ├── dupont_model.py      # DuPont analysis
│   │   ├── enterprise_model.py  # Enterprise value calculations
│   │   ├── intrinsic_model.py   # DCF intrinsic value
│   │   ├── growth_model.py      # Growth calculations
│   │   ├── wacc_model.py        # Weighted average cost of capital
│   │   ├── altman_model.py      # Altman Z-Score
│   │   ├── piotroski_model.py   # Piotroski F-Score
│   │   ├── helpers.py           # Model-specific utilities
│   │   └── __init__.py
│   │
│   ├── performance/             # Performance metrics
│   │   ├── performance_controller.py # Main Performance class
│   │   ├── performance_model.py # Sharpe, Sortino, Beta, CAPM, etc.
│   │   ├── helpers.py           # Performance-specific utilities
│   │   └── __init__.py
│   │
│   ├── risk/                    # Risk metrics
│   │   ├── risk_controller.py   # Main Risk class
│   │   ├── risk_model.py        # VaR, CVaR, drawdown, etc.
│   │   ├── helpers.py           # Risk-specific utilities
│   │   └── __init__.py
│   │
│   ├── technicals/              # Technical analysis indicators
│   │   ├── technicals_controller.py # Main Technicals class
│   │   ├── momentum_model.py    # RSI, MACD, Stochastic, etc.
│   │   ├── volatility_model.py  # Bollinger Bands, ATR, etc.
│   │   ├── overlap_model.py     # Moving averages, SAR, etc.
│   │   ├── breadth_model.py     # Breadth indicators
│   │   ├── statistic_model.py   # Statistical indicators
│   │   └── __init__.py
│   │
│   ├── options/                 # Option pricing and Greeks
│   │   ├── options_controller.py # Main Options class
│   │   ├── black_scholes_model.py # Black-Scholes pricing
│   │   ├── binomial_trees_model.py # Binomial tree pricing
│   │   ├── greeks_model.py      # Option Greeks (delta, gamma, vega, etc.)
│   │   ├── options_model.py     # Option-related utilities
│   │   └── __init__.py
│   │
│   ├── discovery/               # Ticker/instrument discovery
│   │   ├── discovery_controller.py # Main Discovery class
│   │   ├── discovery_model.py   # Discovery API methods
│   │   └── __init__.py
│   │
│   ├── economics/               # Economic indicators
│   │   ├── economics_controller.py # Main Economics class
│   │   ├── economics_model.py   # Economics API methods
│   │   └── __init__.py
│   │
│   ├── fixedincome/             # Fixed income instruments
│   │   ├── fixedincome_controller.py # Main FixedIncome class
│   │   ├── fixedincome_model.py # Fixed income API methods
│   │   ├── helpers.py           # Fixed income utilities
│   │   └── __init__.py
│   │
│   ├── portfolio/               # Portfolio analysis
│   │   ├── portfolio_controller.py # Main Portfolio class
│   │   ├── portfolio_model.py   # Portfolio analysis methods
│   │   ├── example_datasets/    # Sample portfolio data
│   │   └── __init__.py
│   │
│   ├── utilities/               # Cross-cutting utilities
│   │   ├── logger_model.py      # Logging setup and singleton
│   │   ├── cache_model.py       # Pickle/pandas caching utilities
│   │   ├── error_model.py       # @handle_errors decorator
│   │   └── __init__.py
│   │
│   └── mcp_server/              # Model Context Protocol integration
│       ├── mcp_controller.py    # FastMCP server bootstrap
│       ├── inspection_controller.py # Introspect Toolkit public methods
│       ├── registry_controller.py   # Tool registry and mapping
│       ├── auth_model.py        # Auth middleware and key resolution
│       ├── provider_model.py    # ToolkitProvider (Toolkit wrapper)
│       ├── cache_model.py       # MCP-specific caching
│       ├── tools_model.py       # Utility tools (helpers not in Toolkit)
│       ├── coercion_model.py    # Type coercion for MCP
│       ├── formatting_model.py  # Result formatting for MCP
│       ├── setup_model.py       # Setup wizard for MCP
│       ├── config.yaml          # Tool registry configuration
│       ├── mcpb/                # MCP binary/assets directory
│       ├── __init__.py
│       ├── __main__.py          # Entry point for `python -m financetoolkit.mcp_server`
│       └── SKILL.md             # MCP server skill documentation
│
├── tests/                       # Test suite (mirrors source structure)
│   ├── conftest.py             # Pytest fixtures and configuration
│   ├── test_toolkit_controller.py
│   ├── test_helpers.py
│   ├── test_fundamentals_model.py
│   ├── test_normalization_model.py
│   ├── test_historical_model.py
│   ├── test_currencies_model.py
│   ├── ratios/                 # Ratio tests
│   ├── models/                 # Models tests
│   ├── performance/            # Performance tests
│   ├── risk/                   # Risk tests
│   ├── technicals/             # Technicals tests
│   ├── options/                # Options tests
│   ├── discovery/              # Discovery tests
│   ├── economics/              # Economics tests
│   ├── fixedincome/            # FixedIncome tests
│   ├── portfolio/              # Portfolio tests
│   ├── mcp_server/             # MCP tests
│   ├── utilities/              # Utilities tests
│   ├── csv/                    # Test data (CSV format)
│   ├── json/                   # Test data (JSON format)
│   ├── datasets/               # Test datasets directory
│   └── technical/              # Technical analysis test data
│
├── examples/                   # Example scripts and notebooks
│
├── .planning/                  # Project planning directory (GSD)
│   └── codebase/               # Codebase mapping documents
│       ├── ARCHITECTURE.md     # This architecture analysis
│       └── STRUCTURE.md        # This structure analysis
│
├── .agents/                    # Agent configurations (if any)
├── .claude/                    # Claude Code settings
├── .vscode/                    # VSCode settings
├── .github/                    # GitHub workflows
│
├── pyproject.toml              # Python project metadata, dependencies, tool config
├── uv.lock                     # UV dependency lock file
├── .pre-commit-config.yaml     # Pre-commit hooks (black, ruff, codespell)
├── .gitignore                  # Git ignore rules
├── README.md                   # Project documentation
├── CONTRIBUTING.md            # Contribution guidelines
├── LICENSE.txt                # MIT License
├── MCP.md                      # MCP server documentation
├── Dockerfile                  # Docker image definition
├── docker-compose.yml          # Docker compose for local dev
│
└── .env                        # Environment variables (DO NOT COMMIT)
```

## Directory Purposes

**financetoolkit/:**
- Purpose: Main package containing all source code
- Contains: Controllers, models, utilities, MCP server
- Key files: `toolkit_controller.py` (entry point), `helpers.py` (shared utilities)

**ratios/, models/, performance/, risk/, technicals/, options/:**
- Purpose: Domain-specific calculation modules
- Contains: Controller class, calculation models, domain-specific helpers
- Pattern: Each has a `*_controller.py` with public API; `*_model.py` files with calculation functions

**discovery/, economics/, fixedincome/, portfolio/:**
- Purpose: Specialized financial analysis domains
- Contains: Controllers and models similar to core domains
- Used by: Toolkit initialization and as standalone modules

**utilities/:**
- Purpose: Cross-cutting concerns shared across all modules
- Contains: Logger singleton, cache utilities, error handling decorator
- Key files: `logger_model.py`, `cache_model.py`, `error_model.py`

**mcp_server/:**
- Purpose: Model Context Protocol server for AI/Claude integration
- Contains: FastMCP bootstrap, tool registry, auth middleware
- Key files: `mcp_controller.py` (server entry), `registry_controller.py` (tool mapping), `config.yaml` (tool definitions)

**tests/:**
- Purpose: Test suite mirroring source structure
- Contains: Unit tests, integration tests, test data (CSV, JSON)
- Key files: `conftest.py` (fixtures), test files for each module

**examples/:**
- Purpose: Example scripts and notebooks demonstrating Toolkit usage
- Contains: Jupyter notebooks, Python scripts
- Committed: Yes

**_templates/, .agents/, .claude/, .planning/:**
- Purpose: Project infrastructure and metadata
- Contains: GSD planning documents, Claude Code config, agent definitions
- Committed: Yes (except `.env`, `.planning/phases/`)

## Key File Locations

**Entry Points:**
- `financetoolkit/toolkit_controller.py`: Main Toolkit class initialization
- `financetoolkit/discovery/discovery_controller.py`: Discovery module for ticker lookup
- `financetoolkit/mcp_server/mcp_controller.py`: MCP server CLI entry point
- `financetoolkit/__init__.py`: Package exports (Toolkit, Economics, FixedIncome, Discovery, Portfolio)

**Configuration:**
- `pyproject.toml`: Python project metadata, dependencies (pandas, scikit-learn, requests, yfinance)
- `financetoolkit/mcp_server/config.yaml`: MCP tool registry and tool definitions
- `.pre-commit-config.yaml`: Linting/formatting hooks
- `.env`: API keys (FINANCIAL_MODELING_PREP_API_KEY, FRED_API_KEY)

**Core Logic:**
- `financetoolkit/fmp_model.py`: Financial Modeling Prep API client (get_financial_data, get_analyst_estimates, etc.)
- `financetoolkit/yfinance_model.py`: Yahoo Finance client
- `financetoolkit/fundamentals_model.py`: Statement collection orchestration
- `financetoolkit/normalization_model.py`: Financial statement standardization
- `financetoolkit/helpers.py`: calculate_growth, filter_columns, get_request, handle_portfolio

**Testing:**
- `tests/conftest.py`: Pytest fixtures, Record/LiveRecorder classes for VCR-style recording
- `tests/test_toolkit_controller.py`: Integration tests for Toolkit
- `tests/test_helpers.py`: Unit tests for helpers
- `tests/csv/`: Test data in CSV format
- `tests/json/`: Test data in JSON format

## Naming Conventions

**Files:**
- Controllers: `{domain}_controller.py` (e.g., `ratios_controller.py`, `models_controller.py`)
- Calculation models: `{type}_model.py` (e.g., `profitability_model.py`, `dupont_model.py`)
- Utilities: `{function}_model.py` (e.g., `logger_model.py`, `cache_model.py`, `error_model.py`)
- Tests: `test_{module}.py` (e.g., `test_toolkit_controller.py`, `test_ratios_model.py`)
- Test data: Named by ticker or scenario (e.g., `AAPL_2023.csv`, `sample_portfolio.json`)

**Directories:**
- Domain modules: Lowercase plural (ratios, models, performance, options, technicals)
- Special directories: Lowercase (utilities, mcp_server, tests, examples)
- Data directories: Lowercase plural (csv, json, datasets)

**Python Classes:**
- Controllers: PascalCase (Toolkit, Ratios, Models, Performance, Risk, Technicals, Options, Discovery, Economics, FixedIncome, Portfolio)
- Functions: snake_case (get_net_profit_margin, calculate_growth, handle_errors)
- Internal functions: Leading underscore (e.g., `_process_or_load_statement`)
- Constants: UPPER_SNAKE_CASE (API_KEY, FRED_API_KEY, TICKER_LIMIT, ENABLE_TQDM)

**Column/Index Names:**
- Financial statement columns: Original from data source (normalized by normalization_model)
- Result indices: Ticker symbols, periods
- Case: Follows financial standard (e.g., "Net Income", "Operating Cash Flow")

## Where to Add New Code

**New Financial Ratio:**
- Implementation: Create function in `financetoolkit/ratios/{category}_model.py` (e.g., liquidity_model.py for a new liquidity ratio)
- Public API: Add public method to `financetoolkit/ratios/ratios_controller.py`
- Tests: Add test in `tests/ratios/test_{category}_model.py`
- Example: New profitability ratio → add function to `profitability_model.py` → expose via `Ratios.get_new_ratio()` → test in `tests/ratios/test_profitability_model.py`

**New Financial Model:**
- Implementation: Create new file `financetoolkit/models/{model_name}_model.py` with calculation functions
- Public API: Add public method to `financetoolkit/models/models_controller.py`
- Tests: Add test in `tests/models/test_{model_name}_model.py`
- Example: New valuation model → create `valuation_model.py` → add `Models.get_new_valuation_model()` → test in `tests/models/`

**New Domain Module (e.g., Derivatives):**
- Structure: Create directory `financetoolkit/derivatives/` with:
  - `derivatives_controller.py` (main class)
  - Calculation models: `{type}_model.py` files
  - `helpers.py` (if needed)
  - `__init__.py` (empty or re-exports)
- Integration: Add controller to `Toolkit.__init__()` in `toolkit_controller.py`
- Tests: Create `tests/derivatives/` directory with test modules
- MCP: Add tool registry entries in `financetoolkit/mcp_server/config.yaml`

**New Utility Function:**
- Shared helpers: Add to `financetoolkit/helpers.py`
- Domain-specific: Add to `{domain}/helpers.py`
- Logging: Add calls via `logger_model.get_logger()` then `logger.info()` or `logger.error()`
- Caching: Use `cache_model.load_cached_data()` or `cache_model.save_cached_data()`

**New Test:**
- Unit test: `tests/{domain}/test_{module}.py` mirroring source structure
- Fixtures: Add to `tests/conftest.py` if reusable; otherwise define in test file
- Test data: Store in `tests/csv/` (DataFrames) or `tests/json/` (dicts/lists)
- Recording: Use `Record` class in conftest for VCR-style capture/replay

**MCP Tool:**
- Tool definition: Add entry to `financetoolkit/mcp_server/config.yaml` under appropriate category
- Tool implementation: Usually via `ToolRegistry` auto-discovery or `UtilityToolRegistry` for custom tools
- Auth: Handled by `MCPAuthMiddleware` (API key resolution)
- Example: New Toolkit method automatically discovered; exposed as MCP tool via registry

## Special Directories

**tests/csv/, tests/json/:**
- Purpose: Test data fixtures (DataFrames and JSON objects)
- Generated: No (manually created or captured via Record class)
- Committed: Yes (version control for test reproducibility)
- Structure: Organized by module (e.g., tests/csv/ratios/AAPL_ratios.csv, tests/json/models/DCF_output.json)

**financetoolkit/mcp_server/mcpb/:**
- Purpose: MCP binary assets and resources (if any)
- Generated: No (manual assets)
- Committed: Yes

**tests/datasets/, tests/technical/:**
- Purpose: Larger test datasets and technical analysis test data
- Generated: No (manually curated)
- Committed: Yes

**cached/ (at runtime):**
- Purpose: Cached financial data (pickle and pandas format)
- Generated: Yes (automatically created when use_cached_data=True)
- Committed: No (added to .gitignore)
- Structure: {ticker}_{statement_type}.pickle, {ticker}_historical.pickle

**examples/**
- Purpose: Jupyter notebooks and Python scripts demonstrating usage
- Generated: No (manually written)
- Committed: Yes

---

*Structure analysis: 2026-06-23*
