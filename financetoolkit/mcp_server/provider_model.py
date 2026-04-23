"""
Centralized FinanceToolkit provider with SQLite-backed caching.

Routes MCP tool calls to the correct FinanceToolkit module based on
category:

    ticker     → Instantiate Toolkit, access sub-module via property
    toolkit    → Instantiate Toolkit, call method directly
    standalone → Instantiate Economics or FixedIncome directly (no tickers)
    discovery  → Instantiate Discovery with api_key only

No Toolkit (or any controller) is instantiated at import time or during
provider construction — only when a tool is actually called.
"""

from __future__ import annotations

import hashlib
import inspect
import json
import logging
import os
import sqlite3
import time
from datetime import datetime
from io import StringIO
from threading import Lock
from typing import Any

import pandas as pd

from financetoolkit import Toolkit
from financetoolkit.discovery.discovery_controller import Discovery
from financetoolkit.economics.economics_controller import Economics
from financetoolkit.fixedincome.fixedincome_controller import FixedIncome

logger = logging.getLogger(__name__)

_DB_PATH = os.environ.get("FINANCE_MCP_CACHE_DB", "finance_cache.db")
_CACHE_TTL = int(os.environ.get("FINANCE_MCP_CACHE_TTL", "600"))  # 10 minutes


class _CacheDB:
    """Thread-safe SQLite cache for DataFrame API results."""

    def __init__(self, db_path: str = _DB_PATH) -> None:
        self._db_path = db_path
        self._lock = Lock()
        self._init_db()

    def _init_db(self) -> None:
        with self._lock, sqlite3.connect(self._db_path) as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS cache (
                    key    TEXT PRIMARY KEY,
                    value  TEXT NOT NULL,
                    ts     REAL NOT NULL
                )
                """
            )
            conn.execute("CREATE INDEX IF NOT EXISTS idx_cache_ts ON cache(ts)")

    @staticmethod
    def _make_key(namespace: str, params: dict[str, Any]) -> str:
        raw = json.dumps({"ns": namespace, **params}, sort_keys=True, default=str)
        return hashlib.sha256(raw.encode()).hexdigest()

    def get(
        self,
        namespace: str,
        params: dict[str, Any],
        ttl: int = _CACHE_TTL,
    ) -> pd.DataFrame | None:
        key = self._make_key(namespace, params)
        with self._lock, sqlite3.connect(self._db_path) as conn:
            row = conn.execute(
                "SELECT value, ts FROM cache WHERE key = ?",
                (key,),
            ).fetchone()
        if row is None:
            return None
        value_json, ts = row
        if time.time() - ts > ttl:
            return None
        try:
            return pd.read_json(StringIO(value_json), dtype=False)
        except Exception:
            return None

    def put(self, namespace: str, params: dict[str, Any], df: pd.DataFrame) -> None:
        key = self._make_key(namespace, params)
        try:
            value_json = df.to_json()
        except Exception:
            return
        with self._lock, sqlite3.connect(self._db_path) as conn:
            conn.execute(
                "INSERT OR REPLACE INTO cache (key, value, ts) VALUES (?, ?, ?)",
                (key, value_json, time.time()),
            )

    def clear(self) -> int:
        with self._lock, sqlite3.connect(self._db_path) as conn:
            cur = conn.execute("DELETE FROM cache")
            return cur.rowcount

    def evict_expired(self, ttl: int = _CACHE_TTL) -> int:
        cutoff = time.time() - ttl
        with self._lock, sqlite3.connect(self._db_path) as conn:
            cur = conn.execute("DELETE FROM cache WHERE ts < ?", (cutoff,))
            return cur.rowcount


# ══════════════════════════════════════════════════════════════════════
#  Provider
# ══════════════════════════════════════════════════════════════════════


def _is_cacheable(v: Any) -> bool:
    """Check if a value is safe to serialise into a cache key."""
    return isinstance(v, str | int | float | bool | type(None))


class ToolkitProvider:
    """
    Stateless provider that routes MCP tool calls to the appropriate
    FinanceToolkit module.

    Key design principles:
    - **No instantiation at startup** — Toolkit / Economics / FixedIncome
      are created lazily, only when a tool is actually called.
    - **Category-aware routing** — four dispatch paths for ticker modules,
      Toolkit direct methods, standalone modules, and Discovery.
    - **SQLite result caching** with configurable TTL.
    - **Instance caching** for Toolkit and standalone controllers,
      keyed by (tickers, date range, quarterly).
    """

    def __init__(
        self,
        api_key: str | None = None,
        cache_ttl: int = _CACHE_TTL,
        db_path: str = _DB_PATH,
    ) -> None:
        self._api_key = api_key or os.environ.get("FMP_API_KEY", "DEMO")
        self._cache_ttl = cache_ttl
        self._cache = _CacheDB(db_path)
        self._toolkit_cache: dict[str, Any] = {}
        self._standalone_cache: dict[str, Any] = {}
        self._lock = Lock()

    def call_method(
        self,
        module_name: str,
        method_name: str,
        category: str,
        tickers: list[str] | None = None,
        countries: list[str] | None = None,
        start_date: str = "2015-01-01",
        end_date: str | None = None,
        quarterly: bool = False,
        benchmark_ticker: str = "SPY",
        **method_kwargs: Any,
    ) -> Any:
        """
        Route a tool call to the correct FinanceToolkit module.

        Parameters
        ----------
        module_name : str
            Logical module name (e.g. "ratios", "economics", "toolkit").
        method_name : str
            Public method to invoke on the module.
        category : str
            One of "ticker", "toolkit", "standalone", "discovery".
        tickers : list[str] | None
            Comma-split ticker list (ignored for standalone / discovery).
        countries : list[str] | None
            Country filter list (standalone/economics modules only).
        start_date, end_date : str
            Date range for data retrieval.
        quarterly : bool
            Whether to use quarterly data granularity.
        benchmark_ticker : str
            Benchmark symbol (ticker modules only).
        **method_kwargs
            Additional keyword arguments forwarded to the underlying method.
        """
        if end_date is None:
            end_date = datetime.now().strftime("%Y-%m-%d")

        # ── Result cache lookup ───────────────────────────────────
        cache_params = {
            "module": module_name,
            "method": method_name,
            "tickers": sorted(t.upper() for t in tickers) if tickers else [],
            "countries": sorted(countries) if countries else [],
            "start": start_date,
            "end": end_date,
            "quarterly": quarterly,
            **{k: v for k, v in method_kwargs.items() if _is_cacheable(v)},
        }

        cached = self._cache.get(module_name, cache_params, ttl=self._cache_ttl)
        if cached is not None:
            logger.debug("Cache HIT: %s.%s", module_name, method_name)
            return cached

        logger.debug("Cache MISS: %s.%s — calling API", module_name, method_name)

        if category == "ticker":
            result = self._call_ticker_module(
                module_name,
                method_name,
                tickers or ["AAPL"],
                start_date,
                end_date,
                quarterly,
                benchmark_ticker,
                **method_kwargs,
            )
        elif category == "toolkit":
            result = self._call_toolkit_direct(
                method_name,
                tickers or ["AAPL"],
                start_date,
                end_date,
                quarterly,
                benchmark_ticker,
                **method_kwargs,
            )
        elif category == "standalone":
            result = self._call_standalone(
                module_name,
                method_name,
                start_date,
                end_date,
                quarterly,
                countries=countries,
                **method_kwargs,
            )
        elif category == "discovery":
            result = self._call_discovery(method_name, **method_kwargs)
        else:
            raise ValueError(
                f"Unknown category '{category}' for module '{module_name}'"
            )

        if isinstance(result, pd.Series):
            result = result.to_frame()
        if isinstance(result, pd.DataFrame):
            self._cache.put(module_name, cache_params, result)

        return result

    def clear_cache(self) -> int:
        """Clear all caches. Returns number of evicted DB rows."""
        with self._lock:
            self._toolkit_cache.clear()
            self._standalone_cache.clear()
        return self._cache.clear()

    def evict_expired(self) -> int:
        return self._cache.evict_expired(ttl=self._cache_ttl)

    def _get_toolkit(
        self,
        tickers: list[str],
        start_date: str,
        end_date: str,
        quarterly: bool,
        benchmark_ticker: str,
    ) -> Any:
        """Return a (potentially cached) Toolkit instance."""
        cache_key = (
            f"{','.join(sorted(t.upper() for t in tickers))}"
            f"|{start_date}|{end_date}|{quarterly}"
        )
        with self._lock:
            if cache_key in self._toolkit_cache:
                return self._toolkit_cache[cache_key]

        tk = Toolkit(
            tickers=tickers,
            api_key=self._api_key,
            start_date=start_date,
            end_date=end_date,
            quarterly=quarterly,
            benchmark_ticker=benchmark_ticker,
        )

        with self._lock:
            self._toolkit_cache[cache_key] = tk
        return tk

    def _get_standalone(
        self,
        module_name: str,
        start_date: str,
        end_date: str,
        quarterly: bool,
    ) -> Any:
        """Return a (potentially cached) standalone controller instance."""
        cache_key = f"{module_name}|{start_date}|{end_date}|{quarterly}"

        with self._lock:
            if cache_key in self._standalone_cache:
                return self._standalone_cache[cache_key]

        if module_name == "economics":
            instance = Economics(
                start_date=start_date,
                end_date=end_date,
                quarterly=quarterly,
            )
        elif module_name == "fixedincome":

            instance = FixedIncome(
                start_date=start_date,
                end_date=end_date,
                quarterly=quarterly,
            )
        else:
            raise ValueError(f"Unknown standalone module: {module_name}")

        with self._lock:
            self._standalone_cache[cache_key] = instance
        return instance

    def _call_ticker_module(
        self,
        module_name: str,
        method_name: str,
        tickers: list[str],
        start_date: str,
        end_date: str,
        quarterly: bool,
        benchmark_ticker: str,
        **kwargs: Any,
    ) -> Any:
        """Ticker-based modules: accessed via Toolkit property."""
        tk = self._get_toolkit(
            tickers,
            start_date,
            end_date,
            quarterly,
            benchmark_ticker,
        )
        module = getattr(tk, module_name)
        method = getattr(module, method_name)
        return method(**kwargs)

    def _call_toolkit_direct(
        self,
        method_name: str,
        tickers: list[str],
        start_date: str,
        end_date: str,
        quarterly: bool,
        benchmark_ticker: str,
        **kwargs: Any,
    ) -> Any:
        """Toolkit direct methods: called on the Toolkit instance itself."""
        tk = self._get_toolkit(
            tickers,
            start_date,
            end_date,
            quarterly,
            benchmark_ticker,
        )
        method = getattr(tk, method_name)
        return method(**kwargs)

    def _call_standalone(
        self,
        module_name: str,
        method_name: str,
        start_date: str,
        end_date: str,
        quarterly: bool,
        countries: list[str] | None = None,
        **kwargs: Any,
    ) -> Any:
        """Standalone modules (Economics, FixedIncome): no tickers required."""
        instance = self._get_standalone(
            module_name,
            start_date,
            end_date,
            quarterly,
        )
        method = getattr(instance, method_name)

        # Only pass countries if the method accepts it
        if countries:
            sig = inspect.signature(method)
            if "countries" in sig.parameters:
                kwargs["countries"] = countries

        return method(**kwargs)

    def _call_discovery(self, method_name: str, **kwargs: Any) -> Any:
        """Discovery module: requires only api_key."""
        instance = Discovery(api_key=self._api_key)
        method = getattr(instance, method_name)
        return method(**kwargs)
