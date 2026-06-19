# MCP Bundle

This directory contains the source for `financetoolkit.mcpb`, an [MCP Bundle](https://github.com/modelcontextprotocol/mcpb) that installs the Finance Toolkit MCP Server into any compatible AI client (Claude Desktop, Claude Code, and others) with a single click — no Python environment or manual configuration required.

## Installing

1. Download the latest `financetoolkit.mcpb` from the releases page [here](https://github.com/JerBouma/FinanceToolkit/releases/latest/download/financetoolkit.mcpb)
2. Double-click `financetoolkit.mcpb` which will open Claude Desktop, this will open a prompt whether you want to install the bundle, click "Install".
3. A prompt will appear asking you to confirm the installation, click "Install" again.
4. The bundle will ask you to provide a Financial Modeling Prep API key (obtain one [here](https://www.jeroenbouma.com/fmp)) and click "Save".
5. Enable the bundle by toggling the switch which says "Disabled" to "Enabled".
6. Restart Claude Desktop and the Finance Toolkit MCP Server will be available for use in your conversations.

## Building and Testing Locally

1. Pull in the repository with `git pull https://github.com/JerBouma/FinanceToolkit`
2. Install required dependencies with `uv sync`
3. Build the MCP bundle with `bash financetoolkit/mcp_server/mcpb/build-mcpb.sh`
4. Find the generated `financetoolkit.mcpb` in the `dist/` directory
5. Double-click it to install it into Claude Desktop.