"""
FinanceToolkit MCP Server
"""

import os
import pathlib

import yaml
from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP

from financetoolkit.mcp_server.inspection_controller import ControllerInspector
from financetoolkit.mcp_server.provider_model import ToolkitProvider
from financetoolkit.mcp_server.registry_controller import ToolRegistry
from financetoolkit.mcp_server.tools_model import UtilityToolRegistry
from financetoolkit.utilities.logger_model import get_logger

load_dotenv()
logger = get_logger()

configuration_path = pathlib.Path(__file__).parent / "config.yaml"

with open(configuration_path, encoding="utf-8") as _f:
    configuration: dict = yaml.safe_load(_f)

provider = ToolkitProvider(
    api_key=os.environ.get("FINANCIAL_MODELING_PREP_API_KEY", ""),
    cache_ttl=configuration["cache"]["ttl_seconds"],
    database_location=configuration["cache"]["database_location"],
)

mcp = FastMCP(
    name="FinanceToolkit Analyst",
    instructions=configuration["instructions"],
)

inspector = ControllerInspector(
    categories=configuration["categories"],
    skip_params=configuration["skip_params"],
    init_handled_params=configuration["init_handled_params"],
)

toolkit_registry = ToolRegistry(
    mcp=mcp,
    provider=provider,
    inspector=inspector,
    module_class_map=configuration["module_class_map"],
    skip_methods=configuration["skip_methods"],
    direct_methods=configuration["direct_methods"],
    tool_groups=configuration["tool_groups"],
)

utility_registry = UtilityToolRegistry(
    mcp=mcp,
    registry=toolkit_registry,
    provider=provider,
    search_stop_words=configuration["search_stop_words"],
    category_descriptions=configuration["category_descriptions"],
)

toolkit_count = toolkit_registry.register_all_tools()
utility_count = utility_registry.register_all_tools()

logger.info(
    f"FinanceToolkit MCP Server ready. Registered {toolkit_count} "
    f"router tools and {utility_count} utility tools."
)

if __name__ == "__main__":
    transport = os.environ.get("MCP_TRANSPORT", "stdio")
    logger.info(f"Starting MCP server on transport {transport}")
    mcp.run(transport=transport)
