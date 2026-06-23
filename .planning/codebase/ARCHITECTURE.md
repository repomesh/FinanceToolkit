<!-- refreshed: 2026-06-23 -->
# Architecture

**Analysis Date:** 2026-06-23

## System Overview

```text
┌─────────────────────────────────────────────────────────────────────┐
│                     Toolkit Entry Point                             │
│                  `toolkit_controller.py`                            │
│      (Orchestrator for all financial analysis modules)              │
├──────────────┬──────────────┬───────────────┬───────────┬──────────┤
│   Ratios     │   Models     │  Performance  │  Risk     │Technical │
│  Controllers │  Controllers │  Controllers  │Controllers│Controllers│
│  `ratios/`   │ `models/`    │`performance/` │`risk/`    │`technical/`
├──────────────┼──────────────┼───────────────┼───────────┼──────────┤
│ Discovery    │  Economics   │  FixedIncome  │ Portfolio │ Options  │
│ Controllers  │  Controllers │ Controllers   │Controllers│Controllers│
│`discovery/`  │`economics/`  │`fixedincome/` │`portfolio/`│`options/` 
└──────┬───────┴──────┬───────┴───────────────┴───────────┴──────────┘
       │              │
       ▼              ▼
┌──────────────────────────────────────────────────────────────────────┐
│                     Data Layer / Models                              │
│  fmp_model, yfinance_model, historical_model, fundamentals_model,   │
│  normalization_model, currencies_model, helpers                     │
│                 `[*_model.py] files at root`                        │
└──────────────────────────┬───────────────────────────────────────────┘
       │                   │
       ▼                   ▼
┌──────────────────────────────────────────────────────────────────────┐
│                   External APIs & Data Sources                       │
│                                                                      │
│  - FinancialModelingPrep API (FMP) - Primary financial data         │
│  - Yahoo Finance / yfinance - Stock prices, fundamentals            │
│  - FRED API - Economic indicators                                   │
└──────────────────────────────────────────────────────────────────────┘
```

## Component Responsibilities

| Component | Responsibility | File |
|-----------|----------------|------|
| Toolkit | Main orchestrator; initializes all sub-modules; manages API keys, cache, data sources | `toolkit_controller.py` |
| Ratios | 50+ financial ratios (liquidity, profitability, efficiency, solvency, valuation) | `ratios/ratios_controller.py` |
| Models | Financial models (DUPONT, DCF, Altman, Piotroski, WACC, Enterprise Value, Growth) | `models/models_controller.py` |
| Performance | Performance metrics (Sharpe, Sortino, Beta, CAPM, Jensen's Alpha, Information Ratio) | `performance/performance_controller.py` |
| Risk | Risk metrics (Value at Risk, Conditional VaR, Downside Deviation) | `risk/risk_controller.py` |
| Technicals | Technical analysis indicators (momentum, volatility, overlap, breadth, statistics) | `technicals/technicals_controller.py` |
| Options | Option pricing (Black-Scholes, Binomial trees, Greeks) | `options/options_controller.py` |
| Discovery | Ticker/instrument discovery API wrapper | `discovery/discovery_controller.py` |
| Economics | Economic indicators and data | `economics/economics_controller.py` |
| FixedIncome | Fixed income instruments and metrics | `fixedincome/fixedincome_controller.py` |
| Portfolio | Portfolio analysis and optimization | `portfolio/portfolio_controller.py` |
| MCP Server | Model Context Protocol server for Claude/AI integration | `mcp_server/` |

## Pattern Overview

**Overall:** Multi-layer facade pattern with composition over inheritance.

**Key Characteristics:**
- Modular domain-specific controllers (Ratios, Models, Performance, etc.)
- Each controller wraps calculation models and handles business logic
- Toolkit acts as main facade, composing all sub-controllers
- Data flows from external APIs → normalization/caching layer → calculation models → controllers → results
- Controllers expose high-level methods that orchestrate multiple model calculations
- Consistent error handling via `@handle_errors` decorator
- Consistent logging via centralized logger setup

## Layers

**API & Data Source Layer:**
- Purpose: Fetch financial data from external APIs (FMP, Yahoo Finance, FRED)
- Location: `fmp_model.py`, `yfinance_model.py`
- Contains: HTTP requests, API client code, rate limit handling, retry logic
- Depends on: `requests`, `yfinance`, FRED API
- Used by: `fundamentals_model.py`, `historical_model.py`, `discovery_controller.py`, `economics_controller.py`, `fixedincome_controller.py`

**Normalization & Data Processing Layer:**
- Purpose: Standardize financial statements across data sources (FMP vs Yahoo Finance formats)
- Location: `normalization_model.py`, `fundamentals_model.py`, `historical_model.py`, `currencies_model.py`
- Contains: Statement conversion, date alignment, currency conversion, caching
- Depends on: Pandas, data retrieval layer
- Used by: Toolkit initialization, all controllers that need statements

**Calculation Models Layer:**
- Purpose: Implement financial formulas and calculations
- Location: `ratios/*_model.py`, `models/*_model.py`, `performance/performance_model.py`, `risk/risk_model.py`, `technicals/*_model.py`, `options/*_model.py`
- Contains: Stateless calculation functions (pure functions when possible)
- Depends on: Pandas, numpy, minimal external dependencies
- Used by: Controllers (ratios_controller, models_controller, etc.)

**Controller / Orchestration Layer:**
- Purpose: Compose models, handle state, provide public API
- Location: `*_controller.py` files (ratios, models, performance, risk, technicals, options, discovery, economics, fixedincome, portfolio)
- Contains: Public methods, parameter validation, caching orchestration, result formatting
- Depends on: Calculation models, helpers, utilities (cache, logger, error handling)
- Used by: Toolkit or external callers

**Toolkit Facade Layer:**
- Purpose: Single entry point; initialize all sub-controllers with data; manage configuration
- Location: `toolkit_controller.py`
- Contains: Data fetching orchestration, controller initialization, public API methods
- Depends on: All controllers, all data retrieval layers
- Used by: External users of the Finance Toolkit

**Utilities Layer:**
- Purpose: Cross-cutting concerns (logging, caching, error handling)
- Location: `utilities/` directory
- Contains: `logger_model.py` (setup_logger, get_logger), `cache_model.py` (load/save pickle/pandas), `error_model.py` (@handle_errors decorator)
- Used by: All layers

**MCP Server Layer:**
- Purpose: Expose Toolkit functionality as Model Context Protocol for Claude/AI integration
- Location: `mcp_server/`
- Contains: FastMCP server, tool registry, auth middleware, formatting
- Depends on: Toolkit, fastmcp, MCP SDK
- Used by: Claude/AI clients via MCP

## Data Flow

### Primary Request Path: Historical Analysis

1. User creates Toolkit with tickers and date range (`toolkit_controller.py:__init__`)
2. Toolkit fetches historical price data via `get_historical_data()` → FMP or yfinance
3. Toolkit fetches fundamental statements via `get_financial_data()` → FMP API
4. Statements passed through `initialize_statements_and_normalization()` → converts to standard format
5. Results cached via `cache_model.save_cached_data()`
6. Controllers (Ratios, Models, Performance) initialized with normalized data
7. User calls e.g., `toolkit.ratios.collect_profitability_ratios()`
8. Ratios controller calls calculation models (profitability_model, liquidity_model, etc.)
9. Results returned as pandas DataFrames with ticker × period index

### Calculation Flow: Ratio Calculation

1. User calls `toolkit.ratios.get_net_profit_margin()`
2. Ratios controller calls `profitability_model.get_net_profit_margin(income, balance, cash)`
3. Model accesses normalized statement columns (index names are standardized)
4. Model applies formula: Net Income ÷ Revenue
5. Result wrapped in error handler (`@handle_errors` decorator)
6. Result returned to controller
7. Controller rounds result (if rounding configured)
8. Result returned to user as pandas Series/DataFrame

**State Management:**
- Toolkit stores tickers, API keys, dates, cached data location as instance attributes
- Controllers store references to normalized statements passed during initialization
- Calculation models are stateless (pure functions)
- Global logger instance accessed via `get_logger()` singleton pattern
- Cache stored in filesystem (pickle format for dict/config, pandas format for DataFrames)

## Key Abstractions

**Controllers Pattern:**
- Purpose: Each domain (Ratios, Models, Performance) wrapped in a controller class with consistent interface
- Examples: `Ratios`, `Models`, `Performance`, `Risk`, `Technicals`, `Options`, `Discovery`, `Economics`, `FixedIncome`, `Portfolio`
- Pattern: Constructor takes ticker(s), historical data, statements; exposes public methods that call calculation models; handles rounding/formatting

**Calculation Models:**
- Purpose: Functions that implement financial formulas
- Examples: `profitability_model.get_net_profit_margin()`, `dupont_model.get_dupont_analysis()`, `performance_model.get_sharpe_ratio()`
- Pattern: Pure calculation functions that take DataFrames/Series as input; return Series/DataFrame; no state management

**Helpers:**
- Purpose: Reusable utility functions (calculate_growth, filter_columns, handle_portfolio)
- Location: `helpers.py`, module-specific helpers (ratios/helpers.py, models/helpers.py, performance/helpers.py)
- Pattern: Standalone functions used across multiple modules

## Entry Points

**Python Library Entry:**
- Location: `toolkit_controller.py:Toolkit.__init__`
- Triggers: User creates `Toolkit(tickers="AAPL", api_key="...")` instance
- Responsibilities: Fetch data, validate inputs, initialize all sub-controllers, set up logger

**MCP Server Entry:**
- Location: `mcp_server/mcp_controller.py:main()`
- Triggers: CLI invocation `financetoolkit-mcp` or programmatic FastMCP start
- Responsibilities: Build FastMCP app, register tools from registry, start uvicorn server

**Discovery Entry:**
- Location: `discovery/discovery_controller.py:Discovery.__init__`
- Triggers: User creates `Discovery(api_key="...")` for ticker/instrument discovery
- Responsibilities: Initialize with API key; no data fetching at init

## Architectural Constraints

- **Threading:** Single-threaded event loop; HTTP requests made synchronously with retries via `get_request()`; rate limiting handled via sleep timers for FMP Premium
- **Global state:** Module-level logger instance (`logger_model.get_logger()` singleton); environment variables for API keys (`FINANCIAL_MODELING_PREP_API_KEY`, `FRED_API_KEY`); module-level flag `ENABLE_TQDM` determines progress bar availability
- **Circular imports:** Avoided by using layer boundaries; controllers import from models, models import from helpers, utilities are imported by all layers
- **Data source precedence:** If FMP API key provided → use FMP; if FMP fails → fallback to Yahoo Finance; can be enforced via `enforce_source` parameter
- **Date handling:** Historical data stored in reverse chronological order by default (newest first); can be reversed via `reverse_dates` parameter; financial statements normalized to aligned date labels
- **Statement alignment:** Balance sheets and cash flows aligned to statement end dates; income statements normalized to fiscal period; all statements must have overlapping date ranges for calculations to work

## Anti-Patterns

### Division by Zero in Calculations

**What happens:** Ratio calculations (e.g., net profit margin, return on assets) may divide by zero if denominator is negative or zero
**Why it's wrong:** RuntimeWarning raised but not caught; users may not notice and trust incorrect results
**Do this instead:** Suppress RuntimeWarning globally (already done at `toolkit_controller.py:55`); ensure calculation models handle edge cases (NaN/inf values); users should validate data completeness before analysis

### Inconsistent Date Handling

**What happens:** Historical data stored with different date ordering than financial statements; some methods expect dates reversed, others don't
**Why it's wrong:** Leads to misalignment when calculating metrics; off-by-one errors in period matching
**Do this instead:** Standardize on single date order (already reversed by default); use `convert_date_label()` in normalization layer; always validate date index before calculations

### Large Monolithic Controllers

**What happens:** Controllers like `ratios_controller.py` (264KB), `models_controller.py` (56KB) contain 50+ public methods in single file
**Why it's wrong:** Hard to maintain, test, navigate; violates single responsibility principle
**Do this instead:** Consider breaking into logical sub-modules (e.g., profitability_ratios, valuation_ratios) with shared base controller; maintain registry pattern for tool discovery

### Missing Validation in Calculation Models

**What happens:** Calculation models assume valid input data; if required columns missing, KeyError raised with confusing message
**Why it's wrong:** Users unfamiliar with statement structure get cryptic errors; hard to debug
**Do this instead:** Add column validation at controller level before calling models; provide helpful error messages mentioning required columns; use `@handle_errors` decorator to catch KeyError (already implemented)

## Error Handling

**Strategy:** Layered error handling with decorator-based exception wrapping and centralized logging.

**Patterns:**
- `@handle_errors` decorator (in `utilities/error_model.py`) wraps calculation model functions; catches KeyError, ValueError, AttributeError, ZeroDivisionError, IndexError; logs error with function name; returns empty Series
- API calls wrapped in retry logic (`get_request()` in `helpers.py`); handles SSL errors, HTTP errors, rate limits via sleep timer
- Input validation at controller level (e.g., validate date format, ticker format, API key presence)
- Warnings suppressed for RuntimeWarning (division by zero) via `warnings.filterwarnings()`
- Logger provides context via `logger.error()`, `logger.warning()`, `logger.info()` calls throughout codebase

## Cross-Cutting Concerns

**Logging:** Centralized logger initialized at module load time (`logger_model.setup_logger()`) called in toolkit_controller and discovery_controller; all modules get logger via `get_logger()` singleton; logs to stderr; configurable level (default INFO)

**Validation:** API keys validated at Toolkit/Discovery init (raise ValueError if missing); dates validated via regex (`^\d{4}-\d{2}-\d{2}$`); tickers validated optionally via `remove_invalid_tickers` parameter; statements validated via @handle_errors catching missing columns (KeyError)

**Authentication:** API keys passed as string parameters or via environment variables (`FINANCIAL_MODELING_PREP_API_KEY`, `FRED_API_KEY`); MCP server has auth middleware (`MCPAuthMiddleware`) that extracts API key from headers or query params; per-user key resolution for hosted vs local instances

---

*Architecture analysis: 2026-06-23*
