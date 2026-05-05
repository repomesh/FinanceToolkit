"""
FinanceToolkit MCP Setup Model

Helper functions that locate and write the MCP client configuration files for
VS Code, Cursor, and Claude Desktop. Each writer reads any existing file before
writing so that unrelated server entries are never disturbed, and prompts the
user for confirmation when a ``finance-toolkit`` entry is already present.
"""

import json
import os
import pathlib
import platform
from contextlib import suppress

# --- ANSI Styling Constants ---
CLR = "\033[0m"
BOLD = "\033[1m"
DIM = "\033[2m"
CYAN = "\033[36m"
GREEN = "\033[32m"
YELLOW = "\033[33m"
RED = "\033[31m"

BANNER = f"""
{CYAN}{BOLD}╔══════════════════════════════════════════════════════════╗
║       FinanceToolkit MCP Server  —  Setup Wizard         ║
╚══════════════════════════════════════════════════════════╝{CLR}"""

MENU = f"""
  {BOLD}Select MCP client(s) to configure:{CLR}
  {DIM}(e.g., '1' for Claude, or '12' for Claude + VS Code){CLR}

    {CYAN}1{CLR}  Claude Desktop
    {CYAN}2{CLR}  VS Code
    {CYAN}3{CLR}  Cursor

    {DIM}0  Exit{CLR}
"""


def get_claude_config_path() -> pathlib.Path:
    """
    Return the platform-specific path to the Claude Desktop configuration file.

    Returns:
        pathlib.Path: Absolute path to claude_desktop_config.json for the
            current operating system.
    """
    system = platform.system()
    if system == "Darwin":
        return (
            pathlib.Path.home()
            / "Library"
            / "Application Support"
            / "Claude"
            / "claude_desktop_config.json"
        )
    if system == "Windows":
        return (
            pathlib.Path(os.environ.get("APPDATA", "~"))
            / "Claude"
            / "claude_desktop_config.json"
        )
    return pathlib.Path.home() / ".config" / "claude" / "claude_desktop_config.json"


def write_vscode_config(api_key: str, target_dir: pathlib.Path) -> None:
    """
    Write (or merge) a .vscode/mcp.json file in the given directory.

    If the file already exists and the ``finance-toolkit`` entry is present, the
    user is shown the existing entry and asked to confirm before overwriting. All
    other existing server entries are always preserved.

    Args:
        api_key (str): FinancialModelingPrep API key to embed in the config. Pass
            an empty string to leave the placeholder comment in the file.
        target_dir (pathlib.Path): Directory in which .vscode/mcp.json is created.
    """
    vscode_dir = target_dir / ".vscode"
    vscode_dir.mkdir(exist_ok=True)
    config_path = vscode_dir / "mcp.json"

    existing: dict = {}
    if config_path.exists():
        with suppress(json.JSONDecodeError):
            existing = json.loads(config_path.read_text(encoding="utf-8"))

    current_entry = existing.get("servers", {}).get("finance-toolkit")
    if current_entry is not None:
        print(
            f"\n  {YELLOW}⚠{CLR}  An existing {BOLD}'finance-toolkit'{CLR} entry was "
            f"found in {CYAN}{config_path}{CLR}:"
        )
        print(f"  {DIM}{json.dumps(current_entry, indent=4)}{CLR}")
        confirm = input(f"\n  Overwrite this entry? {DIM}[y/N]{CLR} ").strip().lower()
        if confirm != "y":
            print(f"\n{DIM}Skipped — existing VS Code config left unchanged.{CLR}")
            return

    existing.setdefault("servers", {})
    existing["servers"]["finance-toolkit"] = {
        "command": "financetoolkit-mcp",
        "env": {"FINANCIAL_MODELING_PREP_API_KEY": api_key or "YOUR_API_KEY_HERE"},
    }

    config_path.write_text(json.dumps(existing, indent=2) + "\n", encoding="utf-8")
    print(f"{GREEN}✔{CLR} VS Code config written to {CYAN}{config_path}{CLR}")


def write_cursor_config(api_key: str, target_dir: pathlib.Path) -> None:
    """
    Write (or merge) a .cursor/mcp.json file in the given directory.

    If the file already exists and the ``finance-toolkit`` entry is present, the
    user is shown the existing entry and asked to confirm before overwriting. All
    other existing server entries are always preserved.

    Args:
        api_key (str): FinancialModelingPrep API key to embed in the config. Pass
            an empty string to leave the placeholder comment in the file.
        target_dir (pathlib.Path): Directory in which .cursor/mcp.json is created.
    """
    cursor_dir = target_dir / ".cursor"
    cursor_dir.mkdir(exist_ok=True)
    config_path = cursor_dir / "mcp.json"

    existing: dict = {}
    if config_path.exists():
        with suppress(json.JSONDecodeError):
            existing = json.loads(config_path.read_text(encoding="utf-8"))

    current_entry = existing.get("mcpServers", {}).get("finance-toolkit")
    if current_entry is not None:
        print(
            f"\n  {YELLOW}⚠{CLR}  An existing {BOLD}'finance-toolkit'{CLR} entry was "
            f"found in {CYAN}{config_path}{CLR}:"
        )
        print(f"  {DIM}{json.dumps(current_entry, indent=4)}{CLR}")
        confirm = input(f"\n  Overwrite this entry? {DIM}[y/N]{CLR} ").strip().lower()
        if confirm != "y":
            print(f"\n{DIM}Skipped — existing Cursor config left unchanged.{CLR}")
            return

    existing.setdefault("mcpServers", {})
    existing["mcpServers"]["finance-toolkit"] = {
        "command": "financetoolkit-mcp",
        "env": {"FINANCIAL_MODELING_PREP_API_KEY": api_key or "YOUR_API_KEY_HERE"},
    }

    config_path.write_text(json.dumps(existing, indent=2) + "\n", encoding="utf-8")
    print(f"{GREEN}✔{CLR} Cursor config written to {CYAN}{config_path}{CLR}")


def write_claude_config(api_key: str) -> None:
    """
    Patch the Claude Desktop configuration file to add the FinanceToolkit server.

    If the configuration file does not exist it is created from scratch, including
    any missing parent directories. If it already exists and the ``finance-toolkit``
    entry is present, the user is shown the existing entry and asked to confirm
    before overwriting. All other existing server entries are always preserved.

    Args:
        api_key (str): FinancialModelingPrep API key to embed in the config. Pass
            an empty string to leave the placeholder comment in the file.
    """
    config_path = get_claude_config_path()
    config_path.parent.mkdir(parents=True, exist_ok=True)

    existing: dict = {}
    if config_path.exists():
        with suppress(json.JSONDecodeError):
            existing = json.loads(config_path.read_text(encoding="utf-8"))

    current_entry = existing.get("mcpServers", {}).get("finance-toolkit")
    if current_entry is not None:
        print(
            f"\n  {YELLOW}⚠{CLR}  An existing {BOLD}'finance-toolkit'{CLR} entry was found in "
            f"{CYAN}{config_path}{CLR}:"
        )
        print(f"  {DIM}{json.dumps(current_entry, indent=4)}{CLR}")
        confirm = input(f"\n  Overwrite this entry? {DIM}[y/N]{CLR} ").strip().lower()
        if confirm != "y":
            print(
                f"\n{DIM}Skipped — existing Claude Desktop config left unchanged.{CLR}"
            )
            return

    existing.setdefault("mcpServers", {})
    existing["mcpServers"]["finance-toolkit"] = {
        "command": "financetoolkit-mcp",
        "env": {"FINANCIAL_MODELING_PREP_API_KEY": api_key or "YOUR_API_KEY_HERE"},
    }

    config_path.write_text(json.dumps(existing, indent=2) + "\n", encoding="utf-8")
    print(f"{GREEN}✔{CLR} Claude Desktop config written to {CYAN}{config_path}{CLR}")
