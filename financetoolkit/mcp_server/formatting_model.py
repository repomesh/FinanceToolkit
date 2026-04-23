"""
Token-dense output formatting for LLM consumption.

Converts DataFrames into compact Markdown tables and handles
small-context model output trimming.
"""

from typing import Any

import pandas as pd

from financetoolkit.utilities.logger_model import get_logger

logger = get_logger()


def _non_null_count(df: pd.DataFrame) -> int:
    """Return the total count of non-null cells in a DataFrame."""
    return int(df.notna().to_numpy().sum())


def _format_single_value(
    df: pd.DataFrame,
    title: str | None = None,
    precision: int = 4,
) -> str:
    """
    Format a DataFrame that contains exactly one non-null value as a readable
    scalar string instead of a one-cell table.

    Label is built from the optional *title*, the row index label, and the
    column name so the caller always knows what the number refers to.
    """
    flat = df.stack().dropna()
    if flat.empty:
        return "No data available."

    val = flat.iloc[0]
    raw_idx = flat.index[0]

    parts: list[str] = []
    if title:
        parts.append(title)
    if isinstance(raw_idx, tuple):
        parts.extend(str(x) for x in raw_idx)
    else:
        parts.append(str(raw_idx))

    label = " \u00b7 ".join(p for p in parts if p)

    formatted = f"{val:.{precision}g}" if isinstance(val, float) else str(val)
    return f"**{label}:** {formatted}" if label else formatted


def dataframe_to_markdown(
    df: pd.DataFrame,
    *,
    max_rows: int | None = None,
    max_cols: int | None = None,
    precision: int = 4,
    title: str | None = None,
) -> str:
    """
    Convert a DataFrame to a compact Markdown table optimised for LLM tokens.

    - Numbers are rounded to *precision* digits.
    - Column / index names are shortened when possible.
    - Very wide frames get transposed automatically.
    """
    if df.empty:
        return "No data available."

    work = df.copy()

    # Round numeric columns
    for col in work.select_dtypes(include="number").columns:
        work[col] = work[col].round(precision)

    # Trim rows / cols
    if max_rows and len(work) > max_rows:
        work = work.tail(max_rows)
    if max_cols and len(work.columns) > max_cols:
        work = work.iloc[:, :max_cols]

    # Auto-transpose if very wide
    if len(work.columns) > 20 and len(work) <= 10:  # noqa
        work = work.T

    md = work.to_markdown()
    if title:
        md = f"### {title}\n\n{md}"
    return md


def trim_for_small_context(
    df: pd.DataFrame,
    *,
    years: int = 3,
    historical: bool = False,
) -> pd.DataFrame:
    """
    If the caller is a small-context model and *historical* is not explicitly
    True, keep only the last *years* worth of columns (assuming columns are
    date-like strings such as '2022', '2022Q3', '2022-06-30').
    """
    if historical or df.empty:
        return df

    # Try to parse column names as dates/years
    date_cols: list[tuple[Any, Any]] = []
    for col in df.columns:
        try:
            dt = pd.to_datetime(str(col))
            date_cols.append((col, dt))
        except Exception:
            logger.info(
                f"Column '{col}' is not date-like, skipping small-context trimming."
            )
            continue

    if not date_cols:
        # Try index-based trimming (economics-style: dates in index,
        # countries/metrics in columns)
        try:
            idx_dates = pd.to_datetime(df.index)
            cutoff = idx_dates.max() - pd.DateOffset(years=years)
            return df.loc[idx_dates >= cutoff]
        except Exception:
            logger.info("Index is not date-like, skipping small-context trimming.")
            pass

        return df

    date_cols.sort(key=lambda x: x[1])
    cutoff = date_cols[-1][1] - pd.DateOffset(years=years)
    keep = [c for c, dt in date_cols if dt >= cutoff]
    # Preserve non-date columns
    non_date = [c for c in df.columns if c not in {x[0] for x in date_cols}]
    return df[non_date + keep]


def format_result(
    result: Any,
    *,
    small_context: bool = False,
    historical: bool = False,
    precision: int = 4,
    title: str | None = None,
) -> str:
    """
    Universal formatter: takes any FinanceToolkit return value and produces
    a compact Markdown string ready for an LLM.

    A result with exactly one non-null value is returned as a labelled scalar
    (e.g. ``**economics.get_inflation_rate \u00b7 2025 \u00b7 United States:** 0.02089``)
    rather than a one-cell Markdown table.  Any result with more than one
    non-null value is always rendered as a Markdown table so that comparisons
    across years, quarters, companies, or countries are easy to read.
    """
    # ── Normalise Series → DataFrame so all tabular paths share one branch ──
    if isinstance(result, pd.Series):
        result = result.to_frame()

    if isinstance(result, pd.DataFrame):
        if small_context:
            result = trim_for_small_context(result, historical=historical)

        non_null = _non_null_count(result)

        if non_null == 0:
            return "No data available."
        if non_null == 1:
            # Single data point — a table adds no value; show as a labelled scalar.
            return _format_single_value(result, title=title, precision=precision)
        # Multiple data points — always use a table for easy comparison.
        return dataframe_to_markdown(result, precision=precision, title=title)

    if isinstance(result, dict):
        lines = []
        for k, v in result.items():
            if isinstance(v, pd.DataFrame):
                lines.append(
                    format_result(v, small_context=small_context, title=str(k))
                )
            else:
                lines.append(f"**{k}:** {v}")
        return "\n\n".join(lines)

    # Scalars / strings
    return str(result)
