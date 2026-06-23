# Testing Patterns

**Analysis Date:** 2026-06-23

## Test Framework

**Runner:**
- Framework: pytest >= 8.3
- Config: Custom conftest in `tests/conftest.py`
- No `pytest.ini` file; configuration in `pyproject.toml` under `[tool.pytest.ini_options]`

**Assertion Library:**
- pytest built-in assertions
- numpy testing utilities: `np.testing.assert_array_almost_equal()`

**Run Commands:**
```bash
pytest                              # Run all tests
pytest --live                       # Run tests using live API data instead of pickle files
pytest --forecast                   # Run tests marked with @pytest.mark.forecast
pytest --optimization              # Run tests marked with @pytest.mark.optimization
pytest --session                    # Run tests marked with @pytest.mark.session
pytest --autodoc                    # Run auto documentation tests
pytest --rewrite-expected           # Force rewrite of recorded expected data
pytest --cov=financetoolkit         # Run with coverage (pytest-cov)
pytest -v                           # Verbose output
```

## Test File Organization

**Location:**
- Co-located alongside source: `tests/` directory mirrors `financetoolkit/` structure
- Example: Source `financetoolkit/ratios/ratios_controller.py` has test `tests/ratios/test_ratios_controller.py`

**Naming:**
- Test modules: `test_*.py` pattern
- Test functions: `test_*()` pattern
- Test classes: Not used; functions preferred

**Structure:**
```
tests/
├── conftest.py              # Shared fixtures and test configuration
├── datasets/                # Pickle fixtures (balance_dataset.pickle, etc.)
├── test_helpers.py          # Unit tests for helpers module
├── test_toolkit_controller.py
├── test_historical_model.py
├── test_currencies_model.py
├── test_normalization_model.py
├── test_fundamentals_model.py
├── ratios/
│   ├── __init__.py
│   ├── test_ratios_controller.py
│   └── [individual ratio test files]
├── models/
│   ├── __init__.py
│   ├── test_models_controller.py
│   ├── test_wacc_model.py
│   ├── test_growth_model.py
│   └── [other model tests]
├── options/
│   └── test_options_controller.py
├── performance/
│   └── test_performance_controller.py
├── risk/
│   └── test_risk_controller.py
├── technicals/
│   └── test_technicals_controller.py
├── portfolio/
│   └── test_overview_model.py
├── fixedincome/
│   └── test_fixedincome_controller.py
├── economics/
│   └── test_economics_controller.py
├── discovery/
│   └── test_discovery_controller.py
├── utilities/
│   └── test_logger_model.py
└── mcp_server/
    └── test_mcp_controller.py
```

## Test Structure

**Suite Organization:**

Standard test function structure without classes:

```python
def test_toolkit_balance(recorder):
    toolkit = Toolkit(
        tickers=["AAPL", "MSFT"],
        balance=balance_dataset,
        convert_currency=False,
        start_date="2019-12-31",
        end_date="2023-01-01",
        sleep_timer=False,
    )

    toolkit._daily_risk_free_rate = risk_free_rate
    toolkit._daily_treasury_data = treasury_data

    recorder.capture(toolkit.get_balance_sheet_statement())
    recorder.capture(toolkit.get_balance_sheet_statement(growth=True))
    recorder.capture(toolkit.get_balance_sheet_statement(growth=True, lag=[1, 2, 3]))
```

**Key Characteristics:**
- Parametrized: Each test creates specific fixture instances (Toolkit with specific datasets)
- Recorded outputs: Uses `recorder.capture()` to compare output against expected recordings
- Modular: Each test targets one public method or workflow
- Data-driven: Shared pickle datasets used (`balance_dataset.pickle`, `income_dataset.pickle`, etc.)

**Patterns:**
- **Setup Pattern**: Load pickle data, create Toolkit with specific settings, set internal state
  ```python
  balance_dataset = pd.read_pickle("tests/datasets/balance_dataset.pickle")
  toolkit = Toolkit(tickers=["AAPL", "MSFT"], balance=balance_dataset, ...)
  ```

- **Teardown Pattern**: Not used; tests are stateless and independent

- **Assertion Pattern**: Recorder-based output comparison
  ```python
  recorder.capture(toolkit.get_balance_sheet_statement())
  recorder.assert_equal()  # Compares captured output to recorded file
  ```

## Mocking

**Framework:** `unittest.mock` module (standard library)

**Patterns:**
```python
from unittest.mock import MagicMock, patch

def test_get_request_with_mock():
    mock_response = MagicMock()
    mock_response.json.return_value = {"data": "value"}
    
    with patch('requests.get', return_value=mock_response):
        result = helpers.get_request("http://example.com")
```

**Example from `test_logger_model.py`:**
```python
mock_logger = MagicMock()
mock_logger.handlers = []

with patch('logging.getLogger', return_value=mock_logger):
    mock_handler = MagicMock()
    logger_setup_function(mock_logger, mock_handler)
```

**What to Mock:**
- External HTTP requests: `requests.get()` calls
- File I/O when testing logic: Open, read, write operations
- Logger calls in unit tests to verify behavior
- Random/time-dependent operations
- Database connections (not applicable here; uses dataframes)

**What NOT to Mock:**
- pandas DataFrame operations
- Financial calculations (test actual computation)
- Utility functions like `calculate_growth()` (test real behavior)
- Internal module imports
- API response parsing when testing against recorded data

## Fixtures and Factories

**Test Data:**
Session-scoped shared fixtures in `conftest.py`:

```python
@pytest.fixture(scope="session")
def test_toolkit(live_mode: bool):
    """Provides a Toolkit instance with either live API data or pickle data."""
    if live_mode:
        return Toolkit(
            tickers=["AAPL", "MSFT"],
            api_key=os.environ.get("FINANCIAL_MODELING_PREP_API_KEY", ""),
            start_date="2024-01-01",
            end_date="2024-12-31",
        )
    
    balance_dataset = pd.read_pickle("tests/datasets/balance_dataset.pickle")
    income_dataset = pd.read_pickle("tests/datasets/income_dataset.pickle")
    # ... load other datasets
    
    toolkit = Toolkit(
        tickers=["AAPL", "MSFT"],
        historical=historical,
        balance=balance_dataset,
        income=income_dataset,
        # ...
    )
    return toolkit
```

**Module-Level Fixtures:**
```python
@pytest.fixture(scope="session")
def performance_module(test_toolkit):
    return test_toolkit.performance

@pytest.fixture(scope="session")
def risk_module(test_toolkit):
    return test_toolkit.risk

@pytest.fixture(scope="session")
def ratios_module(test_toolkit):
    return test_toolkit.ratios
```

**Location:**
- All shared fixtures: `tests/conftest.py` (634 lines)
- Pickle test data: `tests/datasets/` directory
- Module-specific fixtures: In `conftest.py` with scope="session"

**Custom Recording System:**

Recorded output comparison classes in `conftest.py`:
- `Record`: Manages single captured output (csv, json, txt)
- `PathTemplate`: Builds file paths for recordings
- `Recorder`: Manages multiple records for a test
- `LiveRecorder`: No-op recorder when using `--live` flag

```python
def test_example(recorder):
    result = toolkit.get_balance_sheet_statement()
    recorder.capture(result)
    recorder.assert_equal()  # Compares to expected recording
```

## Coverage

**Requirements:**
- No specific target enforced; coverage tracking available via `pytest-cov`
- Coverage tool installed: `pytest-cov >= 6.1`

**View Coverage:**
```bash
pytest --cov=financetoolkit --cov-report=term-missing
pytest --cov=financetoolkit --cov-report=html  # Generates HTML report
```

**Coverage by Module:**
Typical coverage varies by module type:
- Core models (`helpers.py`, calculation functions): High coverage (80%+)
- Controllers with many methods: Medium coverage (60-70%)
- Integrations (API calls): Lower coverage (30-40%, often mocked)
- Test utilities: Very high (95%+)

## Test Types

**Unit Tests:**
- Scope: Individual functions and methods
- Approach: Test single financial calculation with various inputs
- Example: `test_calculate_growth_basic()` tests growth calculation with standard inputs
  ```python
  def test_calculate_growth_basic():
      data = pd.DataFrame(...)
      result = helpers.calculate_growth(data)
      assert result.shape == data.shape
  ```
- Data: Use minimal test data (small DataFrames created inline)
- Mocking: Mock external calls; test calculations directly

**Integration Tests:**
- Scope: Multi-step workflows within Toolkit
- Approach: Load real financial statement data, run through toolkit methods
- Example: `test_toolkit_ratios()` tests toolkit with balance + income + historical data
  ```python
  def test_toolkit_ratios(recorder):
      toolkit = Toolkit(
          balance=balance_dataset,
          income=income_dataset,
          historical=historical_dataset,
          # ...
      )
      recorder.capture(toolkit.ratios.collect_all_ratios())
  ```
- Data: Use pickle datasets (balance_dataset.pickle, income_dataset.pickle, etc.)
- Assertion: Output compared against recorded expected results

**API/Live Tests:**
- Scope: External API integration (Financial Modeling Prep, FRED)
- Approach: Conditional execution with `--live` flag or skip by default
- Example: `test_get_option_chains(recorder, options_module, live_mode)`
  ```python
  def test_get_option_chains(recorder, options_module, live_mode):
      if live_mode:
          # Make real API call
      else:
          # Use pickled response or skip
  ```
- Data: Live API responses or recorded pickles
- Mocking: Bypassed with `--live`; uses recorded data otherwise

**E2E Tests:**
- Framework: pytest-recording for VCR-style cassettes
- Approach: Record HTTP interactions, replay in tests
- Tool: `pytest-recording >= 0.13` configured in `pyproject.toml`
- Not extensively used; most integration tests use pickle files instead

## Common Patterns

**Async Testing:**
- Not applicable; codebase is synchronous
- No `pytest-asyncio` used

**Error Testing:**
```python
def test_calculate_growth_with_invalid_data():
    data = pd.DataFrame()  # Empty
    result = helpers.calculate_growth(data)
    # Result should be handled gracefully (may be empty or NaN)
```

**Parametrized Tests:**
Not heavily used; test functions created individually:
```python
def test_calculate_growth_basic():
    # Test case 1
    pass

def test_calculate_growth_with_lag():
    # Test case 2
    pass

def test_calculate_growth_with_list_lag():
    # Test case 3
    pass
```

Alternative with `@pytest.mark.parametrize()` not observed in codebase.

**Recording Test Marker:**
```python
@pytest.mark.record_stdout(
    record_mode="once",
    save_record=True,
    assert_in_list=["Expected Output String"]
)
def test_with_output_recording():
    # Test that captures and records stdout
    pass
```

**Custom Markers:**
```python
@pytest.mark.forecast
def test_forecast_model():
    # Run only with --forecast flag
    pass

@pytest.mark.optimization
def test_optimization_test():
    # Run only with --optimization flag
    pass

@pytest.mark.session
def test_session_level():
    # Run only with --session flag
    pass
```

**Live Mode Testing:**
```python
def test_with_live_data(live_mode):
    if live_mode:
        # Execute with real API calls
        toolkit = Toolkit(api_key=os.getenv("FINANCIAL_MODELING_PREP_API_KEY"))
    else:
        # Use pickle data
        pass
```

**Filtering Warnings:**
```python
# Module-level
pytestmark = pytest.mark.filterwarnings("ignore::FutureWarning")

# Individual test
@pytest.mark.filterwarnings("ignore::DeprecationWarning")
def test_with_warning_suppression():
    pass
```

## Test Configuration

**pytest.ini_options:**
From `pyproject.toml`:
```toml
[tool.pytest.ini_options]
filterwarnings = [
    "ignore::pytest.PytestAssertRewriteWarning:",
]
```

**conftest.py Configuration:**
- Custom command-line options: `--forecast`, `--optimization`, `--session`, `--rewrite-expected`, `--autodoc`, `--live`
- Session fixtures: `test_toolkit`, `performance_module`, `risk_module`, `ratios_module`, `options_module`, `fixedincome_module`, `economics_module`
- Test fixtures: `recorder`, `record_stdout`, `default_csv_path`, `default_txt_path`, `default_json_path`, `live_mode`, `rewrite_expected`

---

*Testing analysis: 2026-06-23*
