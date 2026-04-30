"""
Formatting Model, used for formatting FinanceToolkit results into Markdown strings for LLMs.
"""

import threading
import time

import pandas as pd

from financetoolkit.utilities.logger_model import get_logger

logger = get_logger()

# ruff: noqa: PLW0603

_GUIDELINES_COOLDOWN_SECONDS: float = 30.0
_last_guidelines_time: float = 0.0
_guidelines_lock = threading.Lock()


def claim_guidelines() -> bool:
    """
    When the LLM issues multiple tool calls for a single user message, each call
    would otherwise append the guidelines text independently.  We allow the
    guidelines to be included at most once per COOLDOWN window so that parallel
    or rapid sequential calls only emit them once.

    The first call within a ``_GUIDELINES_COOLDOWN_SECONDS`` window returns
    ``True`` and resets the timer; all subsequent calls within the same window
    return ``False``.  After the window expires the next call returns ``True``
    again, ensuring each new user turn eventually receives the guidelines.

    Returns:
        bool: Whether the caller should append the guidelines this time.
    """
    # It's not best practice to define global variables in this way, but it allows
    # for avoidance of complex state management
    global _last_guidelines_time
    now = time.monotonic()
    with _guidelines_lock:
        if now - _last_guidelines_time > _GUIDELINES_COOLDOWN_SECONDS:
            _last_guidelines_time = now
            return True
    return False


def format_result(
    dataset: dict | pd.Series | pd.DataFrame | int | float | str | None,
) -> str:
    """
    Universal formatter for FinanceToolkit outputs into compact Markdown strings
    suitable for LLM consumption.

    Args:
        dataset (dict | pd.Series | pd.DataFrame | int | float | str | None):
            The value to format. Supported behaviors:
              - None: returns "No data available."
              - pd.Series: converted to a one-column DataFrame and handled like a DataFrame.
              - pd.DataFrame: rendered as a Markdown table. Empty or all-NaN frames
                return "No data available." Very wide tables (more than 20 columns)
                with <= 10 rows are auto-transposed before rendering.
              - dict: each key/value pair is formatted; DataFrame values are formatted
                recursively via this function.
              - int | float | str: returned as a plain string.
        title (str): Title used when rendering DataFrames. Converted to a human-readable
            label (e.g. ``"ratios.get_earnings_per_share"`` → ``"Earnings per Share"``)
            and prefixed as a Markdown H4 heading.

    Returns:
        str: A compact Markdown string representation of the input dataset.
    """
    if dataset is None:
        return "No data available."

    if isinstance(dataset, pd.Series):
        # All pd.Series are treated in similar fashion as a pd.DataFrame
        dataset = dataset.to_frame()

    if isinstance(dataset, pd.DataFrame):
        # Determine whether the dataset is empty or contains only NaN values
        if dataset.empty or not int(dataset.notna().to_numpy().sum()):
            return "No data available."

        # Auto-transpose if very wide
        if len(dataset.columns) > 20 and len(dataset) <= 10:  # noqa
            dataset = dataset.T

        return f"{dataset.to_markdown()}\n\n"

    elif isinstance(dataset, dict):
        lines = []
        for key, value in dataset.items():
            if isinstance(value, pd.DataFrame):
                formatted = format_result(value)
                if formatted != "No data available.":
                    lines.append(f"**{key}**\n\n{formatted}")
                else:
                    lines.append(f"**{key}:** No data available.")
            else:
                lines.append(f"**{key}:** {value}")
        return "\n\n".join(lines)
    elif isinstance(dataset, int | float | str):
        return str(dataset)
    else:
        logger.warning(
            f"Unexpected result type: {type(dataset)}. Returning raw string."
        )
        return str(dataset)
