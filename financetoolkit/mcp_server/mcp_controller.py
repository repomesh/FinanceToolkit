"""
FinanceToolkit MCP Server
"""

import os
import pathlib
import subprocess
import sys

import yaml
from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP

from financetoolkit.mcp_server import setup_model
from financetoolkit.mcp_server.inspection_controller import ControllerInspector
from financetoolkit.mcp_server.provider_model import ToolkitProvider
from financetoolkit.mcp_server.registry_controller import ToolRegistry
from financetoolkit.mcp_server.tools_model import UtilityToolRegistry
from financetoolkit.utilities.logger_model import get_logger

load_dotenv()


def _build_mcp_app() -> FastMCP:
    """
    Bootstrap the MCP application and return the configured FastMCP instance.

    Reads the server configuration from config.yaml, instantiates the
    ToolkitProvider, ControllerInspector, ToolRegistry, and UtilityToolRegistry,
    registers all tools, and returns the ready-to-run FastMCP instance. The
    FINANCIAL_MODELING_PREP_API_KEY environment variable (or .env file via
    python-dotenv) is loaded before any component is initialized.

    Returns:
        FastMCP: A fully configured FastMCP instance with all toolkit and utility
            tools registered and ready to serve requests.
    """
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

    controller_inspector = ControllerInspector(
        categories=configuration["categories"],
        skip_params=configuration["skip_params"],
        init_handled_params=configuration["init_handled_params"],
    )

    toolkit_registry = ToolRegistry(
        mcp=mcp,
        provider=provider,
        inspector=controller_inspector,
        module_class_map=configuration["module_class_map"],
        skip_methods=configuration["skip_methods"],
        direct_methods=configuration["direct_methods"],
        tool_groups=configuration["tool_groups"],
        blocked_periods=configuration.get("blocked_periods", {}),
        response_guidelines=configuration.get("response_guidelines", ""),
    )

    utility_registry = UtilityToolRegistry(
        mcp=mcp,
        registry=toolkit_registry,
        provider=provider,
        search_stop_words=configuration["search_stop_words"],
        category_descriptions=configuration["category_descriptions"],
        response_guidelines=configuration.get("response_guidelines", ""),
        instructions=configuration.get("instructions", ""),
    )

    toolkit_count = toolkit_registry.register_all_tools()
    utility_count = utility_registry.register_all_tools()

    logger.info(
        f"FinanceToolkit MCP Server ready. Registered {toolkit_count} "
        f"router tools and {utility_count} utility tools."
    )

    return mcp


def main() -> None:
    """
    Start the FinanceToolkit MCP server.

    Bootstraps the MCP application via _build_mcp_app() and starts the server
    using the transport defined by the MCP_TRANSPORT environment variable.
    Defaults to stdio transport when MCP_TRANSPORT is not set, which is the
    correct setting for use with VS Code and other MCP clients.
    """
    mcp = _build_mcp_app()
    transport = os.environ.get("MCP_TRANSPORT", "stdio")
    get_logger().info(f"Starting MCP server on transport {transport}")
    mcp.run(transport=transport)


def inspector() -> None:
    """
    Launch the MCP Inspector UI for interactive testing of the server.

    Invokes the MCP Inspector via npx, pointing it at this module so that all
    registered tools can be explored and tested interactively in a browser.
    Exits with the same return code as the Inspector process.
    """
    server_path = str(pathlib.Path(__file__).resolve())
    sys.exit(
        subprocess.call(  # noqa
            ["npx", "@modelcontextprotocol/inspector", "python", server_path]  # noqa
        )
    )


def setup() -> None:
    print(setup_model.BANNER)

    api_key: str = os.environ.get("FINANCIAL_MODELING_PREP_API_KEY", "")

    if api_key:
        masked_key = (
            f"{api_key[:4]}...{api_key[-4:]}" if len(api_key) > 8 else "****"  # noqa
        )
        print(
            f"\n{setup_model.GREEN}✔{setup_model.CLR} API key loaded: "
            f"{setup_model.DIM}{masked_key}{setup_model.CLR}"
        )
    else:
        print(
            f"\n  {setup_model.YELLOW}⚠{setup_model.CLR}  {setup_model.BOLD}"
            f"FinancialModelingPrep API key required{setup_model.CLR}"
        )
        print(
            f"     Get a 15% discount at: {setup_model.CYAN}"
            f"https://www.jeroenbouma.com/fmp{setup_model.CLR}"
        )
        print(
            f"     {setup_model.DIM}Press Enter to skip and "
            f"configure via .env later.{setup_model.CLR}"
        )
        api_key = input(
            f"\n  {setup_model.BOLD}Enter API key:{setup_model.CLR} "
        ).strip()

        if api_key:
            env_path = pathlib.Path.cwd() / ".env"
            env_key = "FINANCIAL_MODELING_PREP_API_KEY"
            env_line = f"{env_key}={api_key}\n"

            existing_lines: list[str] = []
            existing_index: int | None = None

            if env_path.exists():
                existing_lines = env_path.read_text(encoding="utf-8").splitlines(
                    keepends=True
                )
                for idx, line in enumerate(existing_lines):
                    if line.strip().startswith(f"{env_key}="):
                        existing_index = idx
                        break

            if existing_index is None:
                if existing_lines and not existing_lines[-1].endswith("\n"):
                    existing_lines[-1] += "\n"
                existing_lines.append(env_line)
                env_path.write_text("".join(existing_lines), encoding="utf-8")
                print(
                    f"{setup_model.GREEN}✔{setup_model.CLR} Added {setup_model.BOLD}{env_key}"
                    f"{setup_model.CLR} to {setup_model.CYAN}{env_path}{setup_model.CLR}."
                )
            else:
                overwrite = (
                    input(
                        f"{setup_model.YELLOW}⚠{setup_model.CLR} {setup_model.BOLD}{env_key}"
                        f"{setup_model.CLR} already exists in {setup_model.CYAN}{env_path}"
                        f"{setup_model.CLR}. Overwrite? {setup_model.DIM}[y/N]{setup_model.CLR} "
                    )
                    .strip()
                    .lower()
                )
                if overwrite in {"y", "yes"}:
                    existing_lines[existing_index] = env_line
                    env_path.write_text("".join(existing_lines), encoding="utf-8")
                    print(
                        f"{setup_model.GREEN}✔{setup_model.CLR} Updated {setup_model.BOLD}{env_key}"
                        f"{setup_model.CLR} in {setup_model.CYAN}{env_path}{setup_model.CLR}."
                    )
                else:
                    print(
                        f"{setup_model.DIM}Skipped updating {env_path}.{setup_model.CLR}"
                    )

    print(setup_model._MENU)
    choice_str = input(f"{setup_model.CYAN}›{setup_model.CLR} ").strip()

    if not choice_str or "0" in choice_str:
        print(f"\n{setup_model.DIM}Setup cancelled.{setup_model.CLR}\n")
        return

    cwd = pathlib.Path.cwd()

    # Extract unique valid choices from the input string (e.g., '12' -> ['1', '2'])
    valid_map = {
        "1": ("Claude Desktop", setup_model.write_claude_config),
        "2": ("VS Code", lambda k: setup_model.write_vscode_config(k, cwd)),
        "3": ("Cursor", lambda k: setup_model.write_cursor_config(k, cwd)),
    }

    # Filter only valid numeric choices from input
    to_process = [c for c in dict.fromkeys(choice_str) if c in valid_map]

    if not to_process:
        print(f"\n{setup_model.RED}✘ No valid options selected.{setup_model.CLR}")
        return

    print("")  # Spacer

    for char in to_process:
        name, func = valid_map[char]
        print(
            f"  {setup_model.CYAN}→{setup_model.CLR} Configuring {setup_model.BOLD}{name}{setup_model.CLR}..."
        )

        try:
            # Execute the specific config function
            if char == "1":
                func(api_key)
            else:
                func(api_key)
            print(
                f"{setup_model.GREEN}✔{setup_model.CLR} {name} configuration complete."
            )
        except Exception as e:
            print(f"{setup_model.RED}✘ Error configuring {name}:{setup_model.CLR} {e}")

    # Final Exit message
    print(
        f"\n{setup_model.GREEN}✔ All selected configurations updated!{setup_model.CLR}"
    )
    print("Restart your client(s) to apply changes.")
    print(
        f"Run {setup_model.BOLD}'financetoolkit-mcp-inspector'{setup_model.CLR} to test.\n"
    )


if __name__ == "__main__":
    main()
