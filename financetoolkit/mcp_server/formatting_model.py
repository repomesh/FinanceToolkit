"""
Formatting Model: converts Finance Toolkit results to JSON for LLM consumption.

JSON is preferred over Markdown tables because keys are self-labelling,
nesting is explicit, and there is no parsing ambiguity.
"""

from __future__ import annotations

import contextlib
import json
import math
from typing import Any

import numpy as np
import pandas as pd

from financetoolkit.utilities.logger_model import get_logger

logger = get_logger()

_MAX_TICKER_LEN = 5


def _clean(val: Any) -> int | float | str | bool | None:
    """Convert a single value to a JSON-serializable Python primitive."""
    try:
        if pd.isna(val):
            return None
    except (TypeError, ValueError):
        pass
    if isinstance(val, pd.Period):
        return str(val)
    if isinstance(val, pd.Timestamp):
        return val.strftime("%Y-%m-%d")
    if isinstance(val, np.integer):
        return int(val)
    if isinstance(val, np.floating):
        f = float(val)
        return None if math.isnan(f) else f
    if isinstance(val, np.bool_):
        return bool(val)
    return val


def _clean_key(key: Any) -> str:
    """Convert a column or index label to a JSON-safe string key."""
    if isinstance(key, pd.Period):
        return str(key)
    if isinstance(key, pd.Timestamp):
        return key.strftime("%Y-%m-%d")
    return str(key)


def _idx_key(index: pd.Index) -> str:
    """Infer a sensible key name for a flat index."""
    if index.name:
        return str(index.name)
    if isinstance(index, (pd.DatetimeIndex, pd.PeriodIndex)):
        return "date"
    with contextlib.suppress(Exception):
        sample = str(index[0])
        if len(sample) <= _MAX_TICKER_LEN and sample.isupper():
            return "ticker"
    return "index"


def _df_to_records(df: pd.DataFrame) -> list[dict]:
    """Convert a FinanceToolkit DataFrame to a flat list of JSON-serializable dicts.

    Three cases handled by DataFrame shape:

    1. MultiIndex *columns* ``(metric, ticker)`` — historical data.
       Stack the ticker level into the row index so each record is one
       ``(date, ticker)`` observation with all metrics as keys.

    2. MultiIndex *index* ``(ticker, metric)`` — multi-ticker financials.
       Each row is already a ``(ticker, metric)`` pair; period/date columns
       become keys inside each record.

    3. Flat index + flat columns — single-ticker financials, quotes, etc.
       The index value becomes one key (name inferred from dtype/content);
       columns become the remaining keys.
    """
    # ── Case 1: MultiIndex columns (metric, ticker) ───────────────────────────
    if isinstance(df.columns, pd.MultiIndex):
        orig_name = _idx_key(df.index)
        ticker_name = df.columns.names[-1] or "ticker"

        stacked = df.stack(level=-1, dropna=False)
        stacked.index.names = [orig_name, ticker_name]

        flat = stacked.reset_index()
        return [
            {_clean_key(k): _clean(v) for k, v in row.items()}
            for _, row in flat.iterrows()
        ]

    # ── Case 2: MultiIndex index (ticker, metric) — multi-ticker financials ───
    if isinstance(df.index, pd.MultiIndex):
        level_names: list[str] = []
        for i, name in enumerate(df.index.names):
            if name:
                level_names.append(str(name))
                continue
            vals = df.index.get_level_values(i)
            sample = str(vals[0]) if len(vals) else ""
            last = i == len(df.index.names) - 1
            if not last and len(sample) <= _MAX_TICKER_LEN and sample.isupper():
                level_names.append("ticker")
            elif last:
                level_names.append("metric")
            else:
                level_names.append(f"level_{i}")

        df = df.copy()
        df.index.names = level_names
        flat = df.reset_index()

        # When show_columns narrows to one metric the last-level column repeats
        # the same value in every row — drop it so records stay concise.
        last_level = level_names[-1] if level_names else None
        if last_level and len(flat[last_level].unique()) == 1:
            flat = flat.drop(columns=[last_level])

        return [
            {_clean_key(k): _clean(v) for k, v in row.items()}
            for _, row in flat.iterrows()
        ]

    # ── Case 3: Flat index, flat columns ──────────────────────────────────────
    df = df.copy()
    if df.index.name:
        idx_name = str(df.index.name)
    elif isinstance(df.columns, (pd.DatetimeIndex, pd.PeriodIndex)):
        # Columns are time periods → rows are either tickers or metric names
        try:
            sample = str(df.index[0])
            idx_name = (
                "ticker"
                if (len(sample) <= _MAX_TICKER_LEN and sample.isupper())
                else "metric"
            )
        except Exception:
            idx_name = "metric"
    else:
        idx_name = _idx_key(df.index)
    df.index.name = idx_name
    flat = df.reset_index()
    return [
        {_clean_key(k): _clean(v) for k, v in row.items()} for _, row in flat.iterrows()
    ]


def format_result(
    dataset: dict | pd.Series | pd.DataFrame | int | float | str | None,
) -> str:
    """Format a Finance Toolkit result as a compact JSON string for LLM consumption.

    Args:
        dataset: The value returned by a controller ``get_*`` method.

    Returns:
        A JSON string.  DataFrames become lists of flat records; dicts of
        DataFrames become JSON objects keyed by the original dict keys;
        scalars become ``{"value": <scalar>}``; missing data becomes
        ``{"error": "No data available."}``.
    """
    if dataset is None:
        return json.dumps({"error": "No data available."})

    if isinstance(dataset, pd.Series):
        dataset = dataset.to_frame()

    if isinstance(dataset, pd.DataFrame):
        if dataset.empty or not int(dataset.notna().to_numpy().sum()):
            return json.dumps({"error": "No data available."})
        return json.dumps(_df_to_records(dataset), default=str)

    if isinstance(dataset, dict):
        out: dict[str, Any] = {}
        for key, value in dataset.items():
            if isinstance(value, pd.DataFrame):
                if not value.empty and int(value.notna().to_numpy().sum()):
                    out[str(key)] = _df_to_records(value)
                else:
                    out[str(key)] = []
            else:
                out[str(key)] = _clean(value)
        return json.dumps(out, default=str)

    if isinstance(dataset, (int, float, str)):
        return json.dumps({"value": _clean(dataset)})

    logger.warning("Unexpected result type: %s. Returning raw string.", type(dataset))
    return json.dumps({"value": str(dataset)})
