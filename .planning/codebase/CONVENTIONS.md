# Coding Conventions

**Analysis Date:** 2026-06-23

## Naming Patterns

**Files:**
- Lowercase with underscores: `toolkit_controller.py`, `ratios_model.py`, `helpers.py`
- Test files prefixed with `test_`: `test_toolkit_controller.py`, `test_helpers.py`
- Model files use `*_model.py` pattern: `fmp_model.py`, `historical_model.py`, `normalization_model.py`
- Controller files use `*_controller.py` pattern: `toolkit_controller.py`, `ratios_controller.py`

**Functions:**
- Lowercase with underscores: `calculate_growth()`, `get_request()`, `combine_dataframes()`
- Getters use `get_` prefix: `get_request()`, `get_profile()`, `get_historical_data()`
- Utilities/calculators use verb-noun pattern: `calculate_growth()`, `collect_financial_statements()`
- Private functions prefixed with underscore: `_convert_daily_to_other_period()`, `_get_analyst_estimates()`

**Variables:**
- Lowercase with underscores: `api_key`, `ticker_list`, `balance_dataset`, `error_message`
- Constants in UPPERCASE: `TICKER_LIMIT`, `ENABLE_TQDM`, `API_KEY`, `DISPLAY_LIMIT`, `EXTENSIONS_ALLOWED`
- Class attributes prefixed with double underscore for private: `__captured`, `__record_path`, `__recorded`
- Boolean prefixes: `is_`, `has_`, `enable_`, `use_`: `is_valid`, `enable_tqdm`, `use_cached_data`, `convert_currency`

**Types:**
- Modern Python 3.10+ union syntax: `str | None`, `list[int]`, `dict[str, pd.DataFrame]`
- No `Optional[]` or `Union[]` from typing module used; pure pipe operators
- Return type annotations: `-> pd.DataFrame`, `-> pd.Series | pd.DataFrame`
- Type hints on all function parameters and returns (comprehensive coverage)

**Classes:**
- PascalCase: `Toolkit`, `Ratios`, `Performance`, `Risk`, `Models`, `Options`
- One public class per module: `class Toolkit` in `toolkit_controller.py`

## Code Style

**Formatting:**
- Tool: `black` with target Python 3.13
- Line length: 122 characters (configured in `pyproject.toml`)
- Black handles all formatting automatically

**Linting:**
- Tool: `ruff` (primary linter)
- Configuration in `pyproject.toml` under `[tool.ruff]`
- Line length: 122 characters (matches black)
- Enabled rule categories: E, W, F, Q, S, UP, I, PD, SIM, PLC, PLE, PLR, PLW
- Complexity checks enabled (PLR rules for function complexity ignored in config but enforced by default)

**Ignored Linting Rules:**
- `S105, S106, S107, S310, S301, S101`: Bandit security checks (hardcoded secrets, eval, asserts)
- `PLR0913, PLR0912, PLR0911, PLR0915`: Pylint complexity rules (too many args/branches/returns/statements)
- `PD010, PD013`: Pandas docstring checks
- Per-file ignores: `financetoolkit/mcp_server/auth_model.py` ignores E501 (line too long) for HTML templates

## Import Organization

**Order:**
1. Standard library imports: `os`, `re`, `warnings`, `datetime`, `collections`, `contextlib`, `inspect`, `functools`, `json`, `math`, `pathlib`, `typing`
2. Third-party imports: `numpy`, `pandas`, `requests`, `yfinance`, `openpyxl`, `tqdm`, `scikit-learn`
3. Local imports: `from financetoolkit import ...`, `from financetoolkit.utilities import ...`

**Path Aliases:**
- No path aliases configured; full relative imports used: `from financetoolkit.utilities import logger_model`
- Imports use full module paths from package root

**Import Style:**
- Combined as imports used: `from X import a, b, c` on single line when possible
- Wrap aliases used: `from module import function as _function` for private re-exports
- Minimize wildcard imports; specific names imported

## Error Handling

**Patterns:**
- Explicit exception handling for known errors: `except (requests.exceptions.HTTPError, ValueError) as e:`
- HTTP errors caught with `response.raise_for_status()` then handle in except block
- SSL/certificate errors handled specifically with fallback: `except requests.exceptions.SSLError:`
- Broad `Exception` catches with logging used in resilient code: `except Exception as e: logger.error(...)`
- ValueError raised for invalid input parameters with descriptive messages: `raise ValueError("Please input a valid start date (%Y-%m-%d) like '2010-01-01'")`
- No custom exception classes in codebase; standard exceptions preferred

**Format:**
- Error messages formatted as: `f"Please ensure the start date {start_date} is before the end date {end_date}"`
- Descriptive context provided in error messages

## Logging

**Framework:** Python's `logging` module (custom setup in `financetoolkit/utilities/logger_model.py`)

**Logger Access:**
- Centralized: `from financetoolkit.utilities import logger_model`
- Get logger in each module: `logger = logger_model.get_logger()`
- Logger set up at toolkit initialization: `logger_model.setup_logger()`

**Logging Levels Used:**
- `logger.info()`: Informational messages about options, parameters, calculations
  - Example: `logger.info("Risk Free Rate: %s%%", round(risk_free_rate * 100, 2))`
  - Example: `logger.info("Dividend Yield: %s", ", ".join(dividend_yield_list))`
- `logger.warning()`: Non-fatal issues, API failures, data quality issues
  - Example: `logger.warning("SSL certificate verification failed for %s. Retrying without verification...")`
  - Example: `logger.warning("The data column for {column} could not be found...")`
- `logger.error()`: Failures in processing, missing data, API errors
  - Example: `logger.error("Error processing %s statement: %s. Returning empty DataFrame.")`
  - Example: `logger.error("Failed to load %s from cache for %s: %s. Returning empty DataFrame.")`

**Style:**
- Messages use `%s` string formatting (not f-strings): `logger.error("Error: %s", value)`
- Context included: module name, operation, values
- No logging at DEBUG level used in production code

## Comments

**When to Comment:**
- Complex algorithms explained: growth calculation with lag, financial ratio formulas
- Non-obvious logic, especially mathematical: `# With Pandas 2.1, pct_change will no longer automatically forward fill...`
- Workarounds noted: `# Runtime errors are ignored on purpose given the nature of the calculations`
- API/external service quirks: `# In case the user has set an API key as an environment variable...`
- Pylint/ruff directives: `# pylint: disable=too-many-instance-attributes`, `# ruff: noqa: E501`

**Module Docstrings:**
- Present in every module starting with `"""Module Name"""` followed by `__docformat__ = "google"`
- Example: 
  ```python
  """Toolkit Module"""
  
  __docformat__ = "google"
  ```

**Docstrings Style:**
- Google-style docstrings used throughout
- Present on all public functions and classes
- Structure: description, Args, Returns, Raises sections
- Example from `calculate_growth()`:
  ```python
  """
  Calculates growth for a given dataset. Defaults to a lag of 1 (i.e. 1 year or 1 quarter).

  Args:
      dataset (pd.Series | pd.DataFrame): the dataset to calculate the growth values for.
      lag (int | str): the lag to use for the calculation. Defaults to 1.

  Returns:
      pd.Series | pd.DataFrame: _description_
  """
  ```

**JSDoc/TSDoc:**
- Not applicable (Python project)

## Function Design

**Size:**
- No hard limit enforced; complexity rules disabled but encouraged to keep functions focused
- Large controller classes accepted: `ratios_controller.py` is 6901 lines with many methods
- Methods within controllers can be 50-200 lines for complex financial calculations
- Utility functions smaller: `combine_dataframes()` is 10 lines, `equal_length()` is ~15 lines

**Parameters:**
- Comprehensive type hints provided: `def calculate_growth(dataset: pd.Series | pd.DataFrame, lag: int | list[int] = 1, rounding: int | None = 4, axis: str = "columns")`
- Default values used for optional parameters
- Complex parameters documented in docstring Args section
- kwargs used sparingly; explicit parameters preferred

**Return Values:**
- Always type-hinted: `-> pd.DataFrame`, `-> pd.Series | pd.DataFrame`, `-> str | None`
- None returned explicitly when function has no result to return
- DataFrames/Series returned unmodified when possible (functional approach)

## Module Design

**Exports:**
- All public classes exported via `from module import Class`
- Private functions prefixed with underscore not re-exported
- Main entry point: `financetoolkit/__init__.py` exports `Toolkit` class

**Barrel Files:**
- `financetoolkit/__init__.py` provides public API
- Submodules organize functionality: `ratios/`, `risk/`, `models/`, `options/`, `performance/`, `technicals/`
- Each submodule has `*_controller.py` as public interface

**Module Docstring:**
Every module starts with:
```python
"""Module Name"""

__docformat__ = "google"
```

Then imports organized by category.

## Decorators

**Usage:**
- `@pytest.mark.*` for test filtering: `@pytest.mark.forecast`, `@pytest.mark.optimization`, `@pytest.mark.session`
- `@pytest.fixture` for test fixtures with scope specification: `@pytest.fixture(scope="session")`
- `@property` for class property access patterns
- Custom decorators: `@handle_portfolio` for decorator pattern supporting portfolio analysis

**Pattern Example:**
```python
@handle_portfolio
def some_method(self, *args, **kwargs):
    # wrapper handles portfolio-specific logic
    pass
```

## Type Safety

**Python Version:**
- Supported: 3.10, 3.11, 3.12, 3.13, 3.14, 3.15 (per `pyproject.toml`)
- Modern type hints used (3.10+ required for `|` union syntax)
- No `from __future__ import annotations` needed

**Type Checking:**
- Type hints present throughout; tools available but not in CI
- Ruff enforces import organization (I rules)

---

*Convention analysis: 2026-06-23*
