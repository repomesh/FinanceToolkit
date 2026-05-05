# FinanceToolkit — MCP Server

[![GitHub Sponsors](https://img.shields.io/badge/Sponsor_this_Project-grey?logo=github)](https://github.com/sponsors/JerBouma)
[![Buy Me a Coffee](https://img.shields.io/badge/Buy_Me_a_Coffee-grey?logo=buymeacoffee)](https://www.buymeacoffee.com/jerbouma)
[![LinkedIn](https://img.shields.io/badge/LinkedIn-grey?logo=Linkedin&logoColor=white)](https://www.linkedin.com/in/boumajeroen/)
[![Documentation](https://img.shields.io/badge/Documentation-grey?logo=readme)](https://www.jeroenbouma.com/projects/financetoolkit/docs)
[![Supported Python Versions](https://img.shields.io/pypi/pyversions/financetoolkit)](https://pypi.org/project/FinanceToolkit/)
[![PYPI Version](https://img.shields.io/pypi/v/FinanceToolkit)](https://pypi.org/project/FinanceToolkit/)
[![PYPI Downloads](https://static.pepy.tech/badge/financetoolkit/month)](https://pepy.tech/project/financetoolkit)

The FinanceToolkit MCP Server exposes 200+ pre-computed financial metrics, models, and economic indicators directly to any AI assistant that supports the [Model Context Protocol](https://modelcontextprotocol.io). This means you can ask Claude, Copilot, Cursor, or any other MCP-compatible assistant to analyse equities, benchmark performance, inspect macro conditions, and run technical indicators — all backed by the transparent, open-source calculation methods of the FinanceToolkit.

The server consolidates the entire FinanceToolkit surface into a small number of categorical master tools (e.g. `get_valuation_ratios`, `get_profitability_ratios`, `get_momentum_indicators`) so that the AI can discover and call the right metric without being overwhelmed by hundreds of individual function signatures.

___

<b><div align="center">Obtain a free API Key from FinancialModelingPrep <a href="https://www.jeroenbouma.com/fmp" target="_blank">here</a> to get started.</div></b>

___

# Table of Contents

1. [Installation](#installation)
2. [Quick Start](#quick-start)
3. [Setting Up VS Code](#setting-up-vs-code)
4. [Setting Up Claude Desktop](#setting-up-claude-desktop)
5. [Setting Up Cursor](#setting-up-cursor)
6. [Setting Up Other Clients](#setting-up-other-clients)
7. [CLI Commands](#cli-commands)
8. [Environment Variables and the API Key](#environment-variables-and-the-api-key)
9. [Available Tools](#available-tools)
10. [Testing the Server Interactively](#testing-the-server-interactively)

# Installation

The MCP server is an optional add-on to the FinanceToolkit. The core library installs without any MCP dependencies, keeping the footprint small for users who only need the Python API. To include the server, add the `[mcp]` extra:

```
pip install financetoolkit[mcp] -U
```

This pulls in the MCP SDK, `tabulate`, `python-dotenv`, and `PyYAML` on top of the standard FinanceToolkit dependencies. If you are using [`uv`](https://github.com/astral-sh/uv) instead:

```
uv add "financetoolkit[mcp]"
```

After installation, three new commands are available on your PATH:

| Command | Purpose |
|:---|:---|
| `financetoolkit-mcp` | Start the MCP server |
| `financetoolkit-mcp-setup` | Auto-generate client config files |
| `financetoolkit-mcp-inspector` | Open the interactive Inspector UI |

# Quick Start

The fastest path from installation to a working AI assistant is two steps.

**Step 1 — Install:**

```
pip install financetoolkit[mcp] -U
```

**Step 2 — Run the setup wizard:**

```
financetoolkit-mcp-setup
```

The wizard asks for your FinancialModelingPrep API key, then presents a numbered menu where you can configure each client in turn. Select the clients you need, then choose **0 — Exit** when done. Restart your AI client and the FinanceToolkit tools will appear.

___

<b><div align="center">If you prefer to configure clients manually, follow the platform-specific sections below.</div></b>

___

# Setting Up VS Code

VS Code reads MCP server definitions from a `.vscode/mcp.json` file at the root of your workspace. Run the setup wizard and choose option **2** when prompted:

```
financetoolkit-mcp-setup
```

```
╔══════════════════════════════════════════════════════════╗
║       FinanceToolkit MCP Server  —  Setup Wizard        ║
╚══════════════════════════════════════════════════════════╝

  Enter your FinancialModelingPrep API key: ••••••••••

  ┌──────────────────────────────────────────────────┐
  │  Select an MCP client to configure:              │
  │                                                  │
  │    1  Claude Desktop                             │
  │    2  VS Code                                    │
  │    3  Cursor                                     │
  │                                                  │
  │    0  Exit                                       │
  └──────────────────────────────────────────────────┘
  › 2
  ✔  VS Code config written to .vscode/mcp.json
```

If you prefer to create the file manually, add the following to `.vscode/mcp.json` in your project root:

```json
{
  "servers": {
    "finance-toolkit": {
      "command": "financetoolkit-mcp",
      "env": {
        "FINANCIAL_MODELING_PREP_API_KEY": "YOUR_API_KEY_HERE"
      }
    }
  }
}
```

Replace `YOUR_API_KEY_HERE` with your key from [FinancialModelingPrep](https://www.jeroenbouma.com/fmp). Alternatively, omit the `env` block entirely and set the key as a system environment variable or in a `.env` file in the project root instead — the server picks it up automatically via `python-dotenv`.

Once the file is in place, open the Copilot Chat panel in VS Code and the FinanceToolkit tools will be available. You can verify this by asking something like:

> "List the available financial metric categories."

# Setting Up Claude Desktop

Claude Desktop reads MCP server definitions from a central JSON configuration file. The location of this file depends on your operating system:

| Operating System | Configuration File Location |
|:---|:---|
| macOS | `~/Library/Application Support/Claude/claude_desktop_config.json` |
| Windows | `%APPDATA%\Claude\claude_desktop_config.json` |
| Linux | `~/.config/claude/claude_desktop_config.json` |

The setup wizard locates the correct path automatically and patches the file without overwriting your other server entries. Run the wizard and choose option **1**:

```
financetoolkit-mcp-setup
```

If you prefer to edit the file manually, add the `finance-toolkit` entry inside the `mcpServers` object:

```json
{
  "mcpServers": {
    "finance-toolkit": {
      "command": "financetoolkit-mcp",
      "env": {
        "FINANCIAL_MODELING_PREP_API_KEY": "YOUR_API_KEY_HERE"
      }
    }
  }
}
```

After saving, fully quit and reopen Claude Desktop. The FinanceToolkit tools will appear in the tools panel. You can verify by asking Claude:

> "What financial tools do you have access to?"

# Setting Up Cursor

Cursor reads project-level MCP definitions from a `.cursor/mcp.json` file. The setup wizard writes this file to the current working directory. Run the wizard and choose option **3**:

```
financetoolkit-mcp-setup
```

To configure it manually, create `.cursor/mcp.json` in your project root with the following content:

```json
{
  "mcpServers": {
    "finance-toolkit": {
      "command": "financetoolkit-mcp",
      "env": {
        "FINANCIAL_MODELING_PREP_API_KEY": "YOUR_API_KEY_HERE"
      }
    }
  }
}
```

Restart Cursor after saving. MCP tools appear in the Composer panel when the server connects successfully.

# Setting Up Other Clients

Any MCP-compatible client can connect to the FinanceToolkit server using the `stdio` transport. The general pattern for any client's configuration is:

```json
{
  "command": "financetoolkit-mcp",
  "env": {
    "FINANCIAL_MODELING_PREP_API_KEY": "YOUR_API_KEY_HERE"
  }
}
```

**Windsurf** uses the same format as Cursor. Add the entry to your Windsurf MCP configuration under `mcpServers`.

**Custom clients or scripts** can also invoke the server directly as a Python module, which is useful when you have cloned the repository and are not using a pip-installed package:

```
python -m financetoolkit.mcp_server
```

Or by running the controller file directly:

```
python financetoolkit/mcp_server/mcp_controller.py
```

Both approaches behave identically to the `financetoolkit-mcp` command.

# CLI Commands

After installation the following commands are available on your PATH.

### `financetoolkit-mcp`

Starts the MCP server over `stdio`, which is the standard transport used by all supported clients. The server blocks until the client disconnects.

```
financetoolkit-mcp
```

The transport can be changed via the `MCP_TRANSPORT` environment variable. Setting it to `sse` starts the server over Server-Sent Events, which is useful for HTTP-based integrations.

### `financetoolkit-mcp-setup`

Starts an interactive menu-driven wizard that generates or patches the MCP configuration files for Claude Desktop, VS Code, and Cursor. The wizard runs in a loop so you can configure multiple clients in a single session.

```
financetoolkit-mcp-setup
```

When started, the wizard first reads the `FINANCIAL_MODELING_PREP_API_KEY` environment variable. If the key is not set it prompts you to enter one (which you may leave blank and supply later). It then shows the following menu, repeating until you select **0**:

```
  ┌──────────────────────────────────────────────────┐
  │  Select an MCP client to configure:              │
  │                                                  │
  │    1  Claude Desktop                             │
  │    2  VS Code                                    │
  │    3  Cursor                                     │
  │                                                  │
  │    0  Exit                                       │
  └──────────────────────────────────────────────────┘
  ›
```

If a `finance-toolkit` entry is already present in the target configuration file, the wizard shows the existing entry and asks for confirmation before making any changes. This prevents accidental overwrites of a config you have already customised.

```
  An existing 'finance-toolkit' entry was found in .vscode/mcp.json:
  {
      "command": "financetoolkit-mcp",
      ...
  }

  Overwrite this entry? [y/N]:
```

### `financetoolkit-mcp-inspector`

Opens the [MCP Inspector](https://github.com/modelcontextprotocol/inspector) — a browser-based UI for exploring and testing every registered tool interactively. This is particularly useful when developing on top of the server or debugging tool behaviour. Node.js with `npx` must be available on your system.

```
financetoolkit-mcp-inspector
```

# Environment Variables and the API Key

The FinanceToolkit server connects to [FinancialModelingPrep](https://www.jeroenbouma.com/fmp) for fundamental financial data and requires a valid API key. The key can be provided in several ways, listed in order of precedence:

1. **Via the client config file** — pass the key in the `env` block of your MCP configuration as shown in the platform-specific sections above.
2. **Via a `.env` file** — create a `.env` file in the directory from which the server is started and add the following line. The server loads this file automatically via `python-dotenv`.

```
FINANCIAL_MODELING_PREP_API_KEY=YOUR_API_KEY_HERE
```

3. **Via the shell environment** — export the variable in your shell profile (`.zshrc`, `.bashrc`, etc.):

```bash
export FINANCIAL_MODELING_PREP_API_KEY=YOUR_API_KEY_HERE
```

If no API key is provided, the server still starts and tools that rely exclusively on Yahoo Finance or public economic data sources (such as OECD or ECB) will continue to work. Tools that require FinancialModelingPrep data will return a descriptive error rather than crashing.

___

<b><div align="center">Get a free API key and support the project via the affiliate link at <a href="https://www.jeroenbouma.com/fmp" target="_blank">jeroenbouma.com/fmp</a>.</div></b>

___

# Available Tools

The server exposes tools grouped into categories. Use the built-in `list_categories` tool to see all categories and their tool counts, or `search_metrics` to find a specific indicator by keyword.

### Utility Tools

These tools help you navigate the available functionality before making any data call.

| Tool | Description |
|:---|:---|
| `get_analyst_guidelines` | Returns the full analyst instructions and response style guide |
| `list_categories` | Lists all registered categories and the number of tools each contains |
| `list_metrics_by_category` | Lists every metric available within a given category |
| `search_metrics` | Fuzzy keyword search across all metrics with typo tolerance |
| `search_instruments` | Look up ticker symbols by company name, ISIN, CIK, CUSIP, or symbol |

### Ratios and Fundamentals

| Tool | Description |
|:---|:---|
| `get_efficiency_ratios` | Asset/inventory turnover, days of sales outstanding, cash conversion cycle |
| `get_liquidity_ratios` | Current ratio, quick ratio, cash ratio, working capital |
| `get_profitability_ratios` | Gross/net/operating margin, ROE, ROA, ROIC, ROCE |
| `get_solvency_ratios` | Debt-to-equity, interest coverage, net debt to EBITDA |
| `get_valuation_ratios` | P/E, EPS, EV/EBITDA, P/B, P/S, dividend yield, free cash flow yield |

### Financial Models

| Tool | Description |
|:---|:---|
| `get_models` | WACC, DuPont analysis, Altman Z-Score, Piotroski F-Score, intrinsic value |

### Risk and Performance

| Tool | Description |
|:---|:---|
| `get_performance` | Sharpe ratio, Sortino ratio, Alpha, Beta, CAPM, Fama-French |
| `get_risk` | Value at Risk, CVaR, GARCH volatility, max drawdown, skewness, kurtosis |

### Technical Indicators

| Tool | Description |
|:---|:---|
| `get_momentum_indicators` | RSI, MACD, Stochastic oscillator, Williams %R, Aroon |
| `get_overlap_indicators` | SMA, EMA, Bollinger Bands, Keltner Channels |
| `get_volatility_indicators` | Average True Range, True Range, volatility series |
| `get_breadth_indicators` | McClellan oscillator, OBV, Advance/Decline line, Chaikin |

### Options

| Tool | Description |
|:---|:---|
| `get_options` | Black-Scholes pricing, binomial tree, Greeks, implied volatility |

### Macro Economics and Fixed Income

| Tool | Description |
|:---|:---|
| `get_general_economy` | GDP, CPI, inflation, trade balances, investment, consumption |
| `get_government_economy` | Government debt, deficit, expenditure, revenue, tax rates |
| `get_jobs_and_society` | Unemployment, population, poverty, income inequality |
| `get_interest_rates` | Central bank rates, government bond yields, EURIBOR |
| `get_fixed_income_valuations` | Bond duration, present value, YTM, derivative pricing |

### Discovery

| Tool | Description |
|:---|:---|
| `get_discovery` | Stock and ETF screener, gainers/losers, most active |
| `get_environment` | ESG scores, carbon footprint, renewable energy usage |
| `get_toolkit_data` | Historical prices, financial statements, company profile, real-time quote |

### How Tools Work

Each tool accepts an `indicator` parameter that selects the exact metric to compute. For example, to get the Price-to-Earnings ratio you would call `get_valuation_ratios` with `indicator='get_price_to_earnings_ratio'`. The AI assistant handles this routing automatically — simply ask your question in plain English and the assistant will select the right tool and indicator.

Tools that operate on equities accept a `tickers` parameter (comma-separated list, e.g. `tickers='AAPL,MSFT'`). Tools that operate on macro data accept a `countries` parameter (e.g. `countries='United States,Germany'`). All tools accept `start_date`, `end_date`, and `quarterly` to control the time range and periodicity.

A few example prompts to get started:

> "Compare the P/E ratios of Apple, Microsoft, and Google over the last 5 years."

> "What is the current Sharpe ratio for Tesla compared to the S&P 500?"

> "Show me the unemployment rate for the United States and Germany since 2010."

> "Calculate the WACC for Amazon and explain what it means."

> "What is the RSI for NVIDIA right now and is it overbought?"

# Testing the Server Interactively

The MCP Inspector lets you call any tool directly from a browser interface without involving an AI assistant. This is the most efficient way to verify that the server is correctly installed and that your API key is working.

```
financetoolkit-mcp-inspector
```

The command opens a browser window where you can browse all registered tools, fill in parameters, and see the raw Markdown output returned by each tool. Node.js and `npx` must be available on your system. Install Node.js from [nodejs.org](https://nodejs.org) if needed.

For a lighter-weight sanity check, you can also confirm the server starts cleanly by running it directly and then interrupting it:

```
financetoolkit-mcp
```

If it starts without errors, the installation is complete. The server will sit idle waiting for a client connection — press `Ctrl+C` to stop it.
