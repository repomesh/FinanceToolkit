"""
Type coercion and input normalisation utilities for the FinanceToolkit MCP server.

Provides best-effort conversion of LLM- or user-supplied string values to the
Python types required by controller methods, as well as date-string validation.
"""

from __future__ import annotations

import re
from typing import Any, Union, get_args, get_origin

from financetoolkit.utilities.logger_model import get_logger

logger = get_logger()

try:
    from types import UnionType
except ImportError:
    UnionType = None


def _try_parse_list_of_int(val: Any) -> list[int] | None:
    """Attempt to parse *val* as a list of integers.

    Accepts:
    - An existing ``list`` (elements coerced to ``int`` where possible).
    - A bracket-notation string such as ``"[1, 4]"`` or ``"1,4"``.

    Returns ``None`` if the input cannot be interpreted as a list of integers.
    """
    if isinstance(val, list):
        try:
            return [int(float(v)) for v in val]
        except (ValueError, TypeError):
            return None

    if isinstance(val, str):
        # Strip optional brackets
        stripped = val.strip().lstrip("[").rstrip("]").strip()
        if not stripped:
            return None
        parts = [p.strip() for p in stripped.split(",") if p.strip()]
        if len(parts) <= 1:
            return None  # A single value should be coerced as int, not list
        try:
            return [int(float(p)) for p in parts]
        except (ValueError, TypeError):
            return None

    return None


def coerce_value(val: Any, annotation: Any) -> Any:
    """
    Best-effort type coercion for values based on a type annotation.

    Treats None and empty strings as absent values (returning None). For boolean targets it
    delegates to to_boolean; for integers it attempts int(float(val)) to gracefully handle
    numeric strings with decimals; for floats it uses float(val). Optional/Union annotations
    (including PEP 604 ``int | None``) are unwrapped to their first non-None member.

    For ``int | list[int]`` annotations (used by the ``lag`` parameter), the value is first
    tried as a plain integer; if that fails it is tried as a comma-separated or bracket-
    notation list of integers before falling back to the original value.

    If conversion fails or the target type is not recognised, the original value is returned.

    Args:
        val (Any): The value to coerce. Often a string coming from an external source.
        annotation (Any): A type annotation (possibly from typing).

    Returns:
        Any: The coerced value on success, None for None/empty input, or the original
        value if conversion is not possible.
    """
    if val is None or val == "":
        return None

    origin = get_origin(annotation)
    is_union = origin is Union or (
        UnionType is not None and isinstance(annotation, UnionType)
    )
    if is_union:
        args = [a for a in get_args(annotation) if a is not type(None)]
        # Check whether any member of the union is list[int] (or list)
        has_list_int = any(get_origin(a) is list or a is list for a in args)
        int_args = [a for a in args if a is int]
        target = int_args[0] if int_args else (args[0] if args else str)
    else:
        has_list_int = get_origin(annotation) is list or annotation is list
        target = annotation

    if target is bool:
        return to_boolean(val)
    if target is int:
        # For int | list[int], try list parsing first when the raw value looks like a list
        if has_list_int:
            parsed_list = _try_parse_list_of_int(val)
            if parsed_list is not None:
                return parsed_list
        try:
            return int(float(val))
        except (ValueError, TypeError):
            return val
    if target is float:
        try:
            return float(val)
        except (ValueError, TypeError):
            return val
    return val


def to_boolean(value: str | int | float | bool) -> bool:
    """
    Coerce a value to a boolean, with support for common string representations.

    Args:
        value (Any): Value to coerce. If value is already a bool it is returned unchanged.
            For non-bool inputs the value is converted to a string and compared
            case-insensitively against recognized truthy values: "true", "1", and "yes".

    Returns:
        bool: Boolean interpretation of the input.
    """
    return (
        value if isinstance(value, bool) else str(value).lower() in ("true", "1", "yes")
    )


def validate_date(date_str: str, default_date: str) -> str:
    """Normalise a date string to YYYY-MM-DD or return a safe default.

    Args:
        date_str (str): Input date string to validate. Accepts both ``YYYY-MM-DD``
            and ``YYYY/MM/DD`` formats.
        default_date (str): Fallback date returned when ``date_str`` is absent or
            does not match the expected pattern.

    Returns:
        str: A validated ``YYYY-MM-DD`` date string, or ``default_date`` if
            validation fails.
    """
    if date_str:
        cleaned = date_str.replace("/", "-")
        if re.match(r"^\d{4}-\d{2}-\d{2}$", cleaned):
            return cleaned

    logger.warning(f"Invalid date input '{date_str}', defaulting to {default_date}")
    return default_date
