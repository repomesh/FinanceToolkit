"""MCP controller tests."""

import importlib
import sys
import types


def test_build_mcp_app_uses_global_cache_path(monkeypatch, tmp_path):
    """Ensure the MCP bootstrap points SQLite cache storage at the global config dir."""

    captured = {}

    fastmcp_module = types.ModuleType("mcp.server.fastmcp")

    class StubFastMCP:
        def __init__(self, *args, **kwargs):
            pass

        def add_tool(self, *args, **kwargs):
            pass

    fastmcp_module.FastMCP = StubFastMCP
    server_module = types.ModuleType("mcp.server")
    server_module.fastmcp = fastmcp_module
    mcp_module = types.ModuleType("mcp")
    mcp_module.server = server_module
    monkeypatch.setitem(sys.modules, "mcp", mcp_module)
    monkeypatch.setitem(sys.modules, "mcp.server", server_module)
    monkeypatch.setitem(sys.modules, "mcp.server.fastmcp", fastmcp_module)
    for mod in [
        "financetoolkit.mcp_server.mcp_controller",
        "financetoolkit.mcp_server.registry_controller",
        "financetoolkit.mcp_server.tools_model",
    ]:
        sys.modules.pop(mod, None)

    mcp_controller = importlib.import_module("financetoolkit.mcp_server.mcp_controller")

    class DummyProvider:
        def __init__(self, *, api_key, cache_ttl, database_location):
            captured["api_key"] = api_key
            captured["cache_ttl"] = cache_ttl
            captured["database_location"] = database_location

    class DummyInspector:
        def __init__(self, *args, **kwargs):
            pass

    class DummyRegistry:
        def __init__(self, *args, **kwargs):
            pass

        def register_all_tools(self):
            return 0

    class DummyUtilityRegistry:
        def __init__(self, *args, **kwargs):
            pass

        def register_all_tools(self):
            return 0

    class DummyMCP:
        def __init__(self, *args, **kwargs):
            pass

    monkeypatch.delenv("FINANCE_TOOLKIT_CACHE_DB", raising=False)
    monkeypatch.setattr(
        mcp_controller.setup_model,
        "get_global_cache_db_path",
        lambda: tmp_path / "financetoolkit_cache.db",
    )
    monkeypatch.setattr(mcp_controller, "ToolkitProvider", DummyProvider)
    monkeypatch.setattr(mcp_controller, "ControllerInspector", DummyInspector)
    monkeypatch.setattr(mcp_controller, "ToolRegistry", DummyRegistry)
    monkeypatch.setattr(mcp_controller, "UtilityToolRegistry", DummyUtilityRegistry)
    monkeypatch.setattr(mcp_controller, "FastMCP", DummyMCP)

    mcp_controller._build_mcp_app()

    assert captured["database_location"] == str(tmp_path / "financetoolkit_cache.db")
    assert captured["cache_ttl"] > 0
