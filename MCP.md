[![FinanceToolkit](https://github.com/JerBouma/FinanceToolkit/assets/46355364/198d47bd-e1b3-492d-acc4-5d9f02d1d009)](https://github.com/JerBouma/FinanceToolkit)

[![GitHub Sponsors](https://img.shields.io/badge/Sponsor_this_Project-grey?logo=github)](https://github.com/sponsors/JerBouma)
[![Buy Me a Coffee](https://img.shields.io/badge/Buy_Me_a_Coffee-grey?logo=buymeacoffee)](https://www.buymeacoffee.com/jerbouma)
[![LinkedIn](https://img.shields.io/badge/LinkedIn-grey?logo=Linkedin&logoColor=white)](https://www.linkedin.com/in/boumajeroen/)
[![MCP Server](https://img.shields.io/badge/MCP_Server-grey?logo=modelcontextprotocol)](https://github.com/JerBouma/FinanceToolkit/blob/main/MCP.md)
[![Documentation](https://img.shields.io/badge/Documentation-grey?logo=readme)](https://www.jeroenbouma.com/projects/financetoolkit/docs)
[![Supported Python Versions](https://img.shields.io/pypi/pyversions/financetoolkit)](https://pypi.org/project/FinanceToolkit/)
[![PYPI Version](https://img.shields.io/pypi/v/FinanceToolkit)](https://pypi.org/project/FinanceToolkit/)
[![PYPI Downloads](https://static.pepy.tech/badge/financetoolkit/month)](https://pepy.tech/project/financetoolkit)

The Finance Toolkit MCP Server exposes 200+ pre-computed financial metrics, models, and economic indicators directly to any AI assistant that supports the [Model Context Protocol](https://modelcontextprotocol.io). This means you can ask Claude, Copilot, Cursor, or any other MCP-compatible assistant to analyse equities, benchmark performance, inspect macro conditions, and run technical indicators — all backed by the transparent, open-source calculation methods of the Finance Toolkit.

The server consolidates the entire Finance Toolkit surface into a small number of categorical master tools (e.g. `get_valuation_ratios`, `get_profitability_ratios`, `get_momentum_indicators`) so that the AI can discover and call the right metric without being overwhelmed by hundreds of individual function signatures.

# Table of Contents

- [Installation](#installation)
  - [Step 1: Run the Setup Wizard](#step-1-run-the-setup-wizard)
  - [Step 2: Configure your client(s)](#step-2-configure-your-clients)
  - [Step 3: Start using the Tools!](#step-3-start-using-the-tools)
- [Advanced Usage](#advanced-usage)
  - [Automating the MCP Server Setup](#automating-the-mcp-server-setup)
  - [Inspecting the Available Tools](#inspecting-the-available-tools)
- [How the MCP Server is Built](#how-the-mcp-server-is-built)
  - [Module Overview](#module-overview)
  - [Startup Sequence](#startup-sequence)
  - [The Router Pattern](#the-router-pattern)
  - [Dispatch Categories](#dispatch-categories)
  - [Utility Tools](#utility-tools)
  - [Setup Wizard](#setup-wizard)

# Installation

The installation process is designed to be as seamless as possible, with an interactive setup wizard that configures your clients and securely stores your API key. The server itself runs on demand via `uvx`, so no local installation is required for the clients.

## Step 1: Run the Setup Wizard

Clients are configured to launch the server on demand via [uvx](https://docs.astral.sh/uv/guides/tools/), so as long as [uv](https://docs.astral.sh/uv/getting-started/installation/) is installed, you can run the setup wizard directly with:

```
uvx --from "financetoolkit[mcp]" financetoolkit-mcp-setup
```

After the installation process is finished, it will automatically launch the setup wizard. **Continue to Step 2 if you've ran above command.**

If you prefer not to run the setup wizard, you can configure each client manually by editing its JSON configuration file. The `env` block accepts either of two environment variables — set whichever suits your workflow. When both are present the directly-set key takes priority.

- `FINANCIAL_MODELING_PREP_API_KEY`: your API key embedded directly in the config.
- `FINANCETOOLKIT_ENV_FILE`: an absolute path to a `.env` file that contains `FINANCIAL_MODELING_PREP_API_KEY=<your-key>`.

The command needing to boot up the MCP server is `uvx --from "financetoolkit[mcp]" financetoolkit-mcp`, where uvx should be set as the *command* and the rest as *args* in the config entry for each client.

The Claude Desktop configuration file lives at a platform-specific path:

| Platform | Path |
|:---|:---|
| macOS | `~/Library/Application Support/Claude/claude_desktop_config.json` |
| Windows | `%APPDATA%\Claude\claude_desktop_config.json` |
| Linux | `~/.config/claude/claude_desktop_config.json` |

Open (or create) that file and add the `finance-toolkit` entry inside `mcpServers`. To embed your API key directly:

```json
{
  "mcpServers": {
    "finance-toolkit": {
      "command": "uvx",
      "args": ["--from", "financetoolkit[mcp]", "financetoolkit-mcp"],
      "env": {
        "FINANCIAL_MODELING_PREP_API_KEY": "YOUR_API_KEY_HERE"
      }
    }
  }
}
```

Alternatively, if you prefer to keep the key in a `.env` file outside of the config (e.g. `~/.config/financetoolkit/.env`), replace the `env` block with:

```json
      "env": {
        "FINANCETOOLKIT_ENV_FILE": "/Users/you/.config/financetoolkit/.env"
      }
```

After saving, **restart Claude Desktop** and the Finance Toolkit tools will appear. For other platforms, please see below:

<details>
<summary><b>Claude Code</b></summary>
<br>

Edit `~/.claude.json` (create it if it does not exist) and add or merge the `finance-toolkit` entry inside `mcpServers`:

```json
{
  "mcpServers": {
    "finance-toolkit": {
      "command": "uvx",
      "args": ["--from", "financetoolkit[mcp]", "financetoolkit-mcp"],
      "env": {
        "FINANCIAL_MODELING_PREP_API_KEY": "YOUR_API_KEY_HERE"
      }
    }
  }
}
```

To use an env file instead, replace the `env` block with `"FINANCETOOLKIT_ENV_FILE": "/Users/you/.config/financetoolkit/.env"`.

</details>

<details>
<summary><b>VS Code</b></summary>
<br>

Create or edit `.vscode/mcp.json` in your workspace root. VS Code uses `servers` as the top-level key (not `mcpServers`):

```json
{
  "servers": {
    "finance-toolkit": {
      "command": "uvx",
      "args": ["--from", "financetoolkit[mcp]", "financetoolkit-mcp"],
      "env": {
        "FINANCIAL_MODELING_PREP_API_KEY": "YOUR_API_KEY_HERE"
      }
    }
  }
}
```

To use an env file instead, replace the `env` block with `"FINANCETOOLKIT_ENV_FILE": "/Users/you/.config/financetoolkit/.env"`.

</details>

<details>
<summary><b>Cursor</b></summary>
<br>

Create or edit `.cursor/mcp.json` in your workspace root:

```json
{
  "mcpServers": {
    "finance-toolkit": {
      "command": "uvx",
      "args": ["--from", "financetoolkit[mcp]", "financetoolkit-mcp"],
      "env": {
        "FINANCIAL_MODELING_PREP_API_KEY": "YOUR_API_KEY_HERE"
      }
    }
  }
}
```

To use an env file instead, replace the `env` block with `"FINANCETOOLKIT_ENV_FILE": "/Users/you/.config/financetoolkit/.env"`.

</details>

<details>
<summary><b>Gemini CLI</b></summary>
<br>

Edit `~/.gemini/settings.json` (create it if it does not exist):

```json
{
  "mcpServers": {
    "finance-toolkit": {
      "command": "uvx",
      "args": ["--from", "financetoolkit[mcp]", "financetoolkit-mcp"],
      "env": {
        "FINANCIAL_MODELING_PREP_API_KEY": "YOUR_API_KEY_HERE"
      }
    }
  }
}
```

To use an env file instead, replace the `env` block with `"FINANCETOOLKIT_ENV_FILE": "/Users/you/.config/financetoolkit/.env"`.

</details>

<details>
<summary><b>Windsurf</b></summary>
<br>

Edit `~/.codeium/windsurf/mcp_config.json` (create it if it does not exist):

```json
{
  "mcpServers": {
    "finance-toolkit": {
      "command": "uvx",
      "args": ["--from", "financetoolkit[mcp]", "financetoolkit-mcp"],
      "env": {
        "FINANCIAL_MODELING_PREP_API_KEY": "YOUR_API_KEY_HERE"
      }
    }
  }
}
```

To use an env file instead, replace the `env` block with `"FINANCETOOLKIT_ENV_FILE": "/Users/you/.config/financetoolkit/.env"`.

</details>

## Step 2: Configure your client(s)

The wizard asks for your FinancialModelingPrep API key which you can obtain from FinancialModelingPrep **<a href="https://www.jeroenbouma.com/fmp" target="_blank">here</a>**.

```bash
(base) jeroenbouma@Jeroens-MacBook-Pro FinanceToolkit % uvx --from "financetoolkit[mcp]" financetoolkit-mcp-setup
╭──────────────────────────────────────────────────────────────────────────────────────────╮
│                                                                                          │
│  FinanceToolkit  ·  MCP Setup Wizard                                                     │
│  Transparent and Efficient Financial Analysis                                            │
│                                                                                          │
╰──────────────────────────────────────────────────────────────────────────────────────────╯

  ⚠  No API key found.  Get one at https://www.jeroenbouma.com/fmp  (15% discount)
  Press Enter to skip and configure via .env later.

  API Key  › YOUR_FINANCIAL_MODELING_PREP_API_KEY_HERE
```

The wizard securely stores it in a global config file on your system (never inside the project or any version-controlled file) and writes a config entry for each selected client that launches the server via `uvx`. It safely merges the `finance-toolkit` entry into any existing config without disturbing other server entries, and asks for confirmation before overwriting an entry that is already present.

Next up is deciding what client(s) you want to configure. You can select multiple clients at once (e.g. 23 for both Claude Code and VS Code) and the wizard will write the necessary config entries for each selected client to launch the MCP server on demand.

```bash
  ✔  API key saved to /Users/jeroenbouma/.config/financetoolkit/.env

╭────────────────────────────────────────── Configure Clients ────────────────────────────╮
│                                                                                         │
│    1  Claude Desktop                                                                    │
│    2  Claude Code                                                                       │
│    3  VS Code                                                                           │
│    4  Cursor                                                                            │
│    5  Gemini                                                                            │
│    6  Windsurf                                                                          │
│                                                                                         │
│    7  Remove configuration                                                              │
│    0  Exit                                                                              │
│                                                                                         │
╰──────────────────────────────── e.g. 23 for Claude Code + VS Code ──────────────────────╯
```

It will inform you where it saved the files and ask if you want to install the optional SKILL.md analyst instructions for each client, which provides guidance to the LLM on how to use the tools and interpret the results. This greatly enhances the quality of the responses and ensures the LLM understands the unique formatting and response style of the Finance Toolkit MCP.

```bash
  › 23

  ✔  Claude Code config written to /Users/jeroenbouma/.claude.json
  ✔  VS Code config written to /Users/jeroenbouma/Documents/FinanceToolkit/.vscode/mcp.json

  Install the SKILL.md analyst instructions for VS Code? [y/n] (y): y
  ✔  Skill file written to /Users/jeroenbouma/Documents/FinanceToolkit/.agents/skills/finance-toolkit-analyst/SKILL.md

  Install the SKILL.md analyst instructions for Claude Code (.claude/skills/)? [y/n] (y): y
  ✔  Claude Code skill file written to /Users/jeroenbouma/Documents/FinanceToolkit/.claude/skills/finance_toolkit.md
```

After the wizard completes, restart your AI client and the Finance Toolkit tools will appear.

## Step 3: Start using the Tools!

As seen above an optional SKILL.md file can be acquired, this creates a `finance-toolkit-analyst` skill in, for GitHub Copilot `.agents/skill` directory. It is possible your LLM will automatically select this skill when you ask financial questions, but if not you can explicitly invoke it by name (e.g. `/finance-toolkit-analyst What is the current P/E ratio of Apple?`).

Two results of a relatively advanced model (`Claude Sonnet 4.6`) shows how powerful models can layer in very detailed qualitative analysis and narrative synthesis with the information from the Finance Toolkit MCP.

<details><summary><b>Compare Apple with Microsoft, what company is the most profitable?</b></summary>
<i>

Across the five-year window from 2021 to 2025, Microsoft and Apple present genuinely different profitability profiles depending on the analytical lens applied — a nuance that institutional research rarely collapses into a single verdict. The data below, derived directly from the Finance Toolkit MCP server, covers gross margin, operating margin, and net profit margin across both companies from fiscal year 2021 through fiscal year 2025.
<br>

Microsoft commands a structurally superior margin stack at every level of the income statement. Its software and cloud-heavy revenue mix consistently produces gross margins in the 68–70% range, reflecting the near-zero marginal cost of licensing and Azure compute, while Apple's hardware-weighted mix constrains gross margins to the 42–47% band despite meaningful Services segment expansion.

| Metric | Company | 2021 | 2022 | 2023 | 2024 | 2025 |
|:--|:--|--:|--:|--:|--:|--:|
| Gross Margin | AAPL | 41.78% | 43.31% | 44.13% | 46.21% | 46.91% |
| Gross Margin | MSFT | 68.93% | 68.40% | 68.92% | 69.76% | 68.82% |
| Operating Margin | AAPL | 29.78% | 30.29% | 29.82% | 31.51% | 31.97% |
| Operating Margin | MSFT | 41.59% | 42.06% | 41.77% | 44.64% | 45.62% |
| Net Profit Margin | AAPL | 25.88% | 25.31% | 25.31% | 23.97% | 26.92% |
| Net Profit Margin | MSFT | 36.45% | 36.69% | 34.15% | 35.96% | 36.15% |

The margin story, however, is not the complete picture. When shifting from income-statement efficiency to capital deployment efficiency, Apple's financial engineering inverts the comparison dramatically. Apple carries a deliberately compressed equity base — the result of decades of aggressive share repurchases — which mechanically inflates its Return on Equity to levels that appear extraordinary, consistently exceeding 170% in recent years. The following table captures ROE, Return on Invested Capital, and Return on Assets for the same period.

| Metric | Company | 2022 | 2023 | 2024 | 2025 |
|:--|:--|--:|--:|--:|--:|
| Return on Equity | AAPL | 175.46% | 171.95% | 157.41% | 171.42% |
| Return on Equity | MSFT | 47.15% | 38.82% | 37.13% | 33.28% |
| Return on Invested Capital | AAPL | 59.90% | 60.68% | 60.19% | 70.38% |
| Return on Invested Capital | MSFT | 38.73% | 34.74% | 33.71% | 30.64% |
| Return on Assets | AAPL | 28.36% | 27.50% | 26.13% | 30.93% |
| Return on Assets | MSFT | 20.82% | 18.63% | 19.07% | 18.00% |

The verdict depends precisely on what one means by "most profitable." On a pure income statement basis — gross, operating, and net margins — **Microsoft is unambiguously the more profitable business**, generating roughly 22 percentage points more net income per dollar of revenue than Apple in fiscal year 2025 (36.15% vs. 26.92%). This structural advantage reflects Microsoft's software and cloud economics, where incremental revenue has near-zero marginal cost.

Apple, by contrast, leads on every capital efficiency metric: its ROIC of 70.38% in 2025 versus Microsoft's 30.64% indicates that Apple extracts significantly more economic value from each dollar of invested capital. Its ROA advantage (30.93% vs. 18.00%) is similarly consistent across the full sample. The ROE comparison is analytically distorted by Apple's balance sheet structure and is better set aside in favor of ROIC as the cleanest apples-to-apples measure.

For a more complete picture, the analysis could be extended into DuPont decomposition to isolate whether Apple's ROIC lead is driven by asset turnover, operational leverage, or financial leverage — all of which the Finance Toolkit supports natively.
</details>
</i>

<details><summary><b>When looking at biggest banks in Europe, which one seems to be the most solvent?</b></summary>
<i>

Assessing solvency across Europe's nine largest listed banking groups — HSBC, BNP Paribas (BNPQY), Deutsche Bank (DB), Banco Santander (SAN), Barclays (BCS), UniCredit (UNCRY), Société Générale (SCGLY), ING, and Intesa Sanpaolo (ISNPY) — requires examining leverage in multiple dimensions simultaneously. Because banks operate with inherently high financial leverage by design, the equity multiplier and debt-to-assets ratio are the most discriminating solvency signals, with the debt service coverage ratio providing a cash-flow-based cross-check. Taken together, the data point to **UniCredit** and **Intesa Sanpaolo** as the standout names for solvency quality within this cohort.

The debt-to-equity ratio captures the proportion of debt relative to shareholders' equity. A lower reading indicates a more conservative capital structure relative to the equity cushion available to absorb losses. The six-year progression below reveals a clear dispersion across the group, with BNP Paribas and Santander consistently carrying the heaviest debt loads relative to equity, while HSBC and Intesa Sanpaolo trend toward the lower end.

| Ticker | 2020 | 2021 | 2022 | 2023 | 2024 | 2025 |
|:-------|-----:|-----:|-----:|-----:|-----:|-----:|
| ISNPY  | 1.62 | 1.58 | 1.61 | 2.22 | 2.24 | 2.13 |
| HSBC   | 1.85 | 1.91 | 1.10 | 2.22 | 1.26 | 2.68 |
| UNCRY  | 2.24 | 2.01 | 1.82 | 1.91 | 1.95 | 2.57 |
| BCS    | 2.15 | 2.38 | 2.65 | 2.46 | 2.56 | 2.81 |
| DB     | 3.28 | 2.30 | 2.70 | 1.93 | 1.91 | 3.18 |
| SCGLY  | 2.31 | 2.13 | 2.11 | 2.38 | 2.30 | 4.12 |
| ING    | 1.42 | 2.12 | 2.37 | 2.87 | 3.34 | 3.32 |
| SAN    | 3.53 | 3.45 | 4.36 | 2.98 | 4.50 | 4.40 |
| BNPQY  | 6.40 | 6.34 | 2.56 | 5.23 | 5.43 | 6.22 |

The equity multiplier — total assets divided by equity — provides a balance-sheet-wide view of financial leverage and is a core input into DuPont decomposition. A lower multiplier implies a thicker equity buffer relative to the entire asset base. The 2025 cross-section is particularly telling: UniCredit stands at just 12.6x, the lowest among all nine peers, followed closely by Intesa Sanpaolo at 14.5x and Santander at 16.8x. By contrast, BNP Paribas (20.7x), Société Générale (21.0x), Barclays (20.3x), and ING (20.3x) are meaningfully more leveraged. Importantly, UniCredit's multiplier has compressed steadily from 15.1x in 2021 to 12.6x in 2025, signalling a deliberate and sustained de-leveraging trajectory.

| Ticker | 2021 | 2022 | 2023 | 2024 | 2025 |
|:-------|-----:|-----:|-----:|-----:|-----:|
| UNCRY  | 15.10 | 14.09 | 12.85 | 12.34 | 12.64 |
| ISNPY  | 15.86 | 16.33 | 15.46 | 14.66 | 14.50 |
| SAN    | 16.48 | 17.09 | 17.49 | 17.18 | 16.82 |
| HSBC   | 14.43 | 15.11 | 15.89 | 15.73 | 16.57 |
| DB     | 20.38 | 18.97 | 17.99 | 17.50 | 17.69 |
| ING    | 17.11 | 18.24 | 18.94 | 19.27 | 20.31 |
| BCS    | 19.97 | 20.74 | 21.18 | 20.75 | 20.30 |
| BNPQY  | 23.21 | 23.24 | 21.55 | 20.14 | 20.67 |
| SCGLY  | 21.10 | 20.46 | 20.33 | 20.08 | 20.96 |

The debt-to-assets ratio corroborates this ranking. HSBC (0.153), Deutsche Bank (0.178), and Intesa Sanpaolo (0.145) hold the smallest debt loads as a share of the total balance sheet in 2025, while BNP Paribas (0.294) and Santander (0.266) are again the outliers on the high end. The debt service coverage ratio provides the critical cash-flow validation: UniCredit (0.228) and Intesa Sanpaolo (0.181) post the highest readings in 2025, meaning their operating earnings are most comfortably covering their debt obligations — a distinction that separates balance-sheet strength from earnings-backed solvency capacity.

| Ticker | D/A 2025 | Equity Mult 2025 | DSCR 2025 |
|:-------|----------:|-----------------:|----------:|
| UNCRY  | 0.201 | 12.64 | 0.228 |
| ISNPY  | 0.145 | 14.50 | 0.181 |
| HSBC   | 0.153 | 16.57 | 0.120 |
| DB     | 0.178 | 17.69 | 0.010 |
| BCS    | 0.142 | 20.30 | 0.013 |
| SCGLY  | 0.186 | 20.96 | 0.012 |
| ING    | 0.161 | 20.31 | 0.011 |
| SAN    | 0.266 | 16.82 | 0.014 |
| BNPQY  | 0.294 | 20.67 | 0.013 |

Synthesizing across all three dimensions, **UniCredit (UNCRY)** emerges as the most solvent major European bank. Its equity multiplier of 12.6x is the lowest in the peer group by a meaningful margin, its trend has been consistently improving over six years, and its debt service coverage ratio of 0.228 is the highest in the cohort — confirming that the balance-sheet strength is underpinned by genuine earnings power rather than accounting structure alone. **Intesa Sanpaolo (ISNPY)** is the clear runner-up, posting the second-best equity multiplier and second-best DSCR. At the other end of the spectrum, BNP Paribas is the most leveraged name across nearly every metric, and Société Générale's equity multiplier spiked to 21.0x in 2025, flagging elevated structural leverage risk in that institution.

Logical extensions of this analysis within the Finance Toolkit ecosystem would include examining capital allocation quality via return on equity and return on invested capital for these same banks, running a rolling volatility and maximum drawdown comparison to understand how solvency strength translates into price resilience, or stress-testing via the Altman Z-Score model where data coverage permits.
</details>
</i>

<details><summary><b>Tell me something about the Semiconductor industry, is it overbought?</b></summary>
<i>

The following analysis covers eight representative semiconductor names spanning the full value chain — fabless designers (NVDA, AMD, QCOM), integrated device manufacturers (INTC, MU), a pure-play foundry (TSM), a diversified chip infrastructure leader (AVGO), and the European lithography monopoly (ASML) — using RSI momentum, trailing P/E multiples, and risk-adjusted Sharpe ratios sourced entirely from the Finance Toolkit MCP server.

**Momentum: The Sector Was Overbought in May — and Has Since Corrected**

The most telling technical story of 2026 is a sharp but short-lived overbought surge in May, now substantially unwound as of the June 4 close. The table below presents trailing 14-day RSI readings across the cohort for the last ten trading sessions. Readings above 70 flag overbought conditions; readings below 30 indicate oversold pressure.

| Date       | NVDA  | AMD   | INTC  | QCOM  | AVGO  | TSM   | MU    | ASML  | SPY (Benchmark) |
|:-----------|------:|------:|------:|------:|------:|------:|------:|------:|----------------:|
| 2026-05-19 | 58.45 | 66.12 | 60.91 | 62.48 | 52.18 | 49.43 | 67.19 | 55.28 | 67.57 |
| 2026-05-20 | 69.80 | 68.27 | 65.02 | 58.07 | 50.13 | 52.43 | 69.30 | 58.35 | 67.79 |
| 2026-05-21 | 66.66 | 67.75 | 62.29 | 62.11 | 47.27 | 54.00 | 69.58 | 61.87 | 67.52 |
| 2026-05-22 | 62.51 | 75.22 | 66.19 | 70.96 | 49.00 | 51.24 | 66.21 | 67.74 | 71.84 |
| 2026-05-26 | 63.94 | 77.28 | 61.71 | 69.59 | 47.68 | 57.60 | 70.64 | 64.79 | 71.48 |
| 2026-05-27 | 54.20 | 67.28 | 57.01 | 62.13 | 48.42 | 51.57 | 70.92 | 54.65 | 65.84 |
| 2026-05-28 | 52.51 | 74.45 | 59.39 | 62.11 | 56.65 | 55.36 | 72.68 | 58.08 | 71.16 |
| 2026-05-29 | 46.25 | 66.97 | 39.94 | 60.01 | 57.75 | 53.26 | 70.09 | 52.15 | 68.77 |
| 2026-06-03 | 41.65 | 74.14 | 42.23 | 61.96 | 73.63 | 64.73 | 74.99 | 65.57 | 61.53 |
| 2026-06-04 | **35.85** | 67.01 | 45.42 | 64.32 | **43.84** | 61.77 | 68.09 | 67.54 | 59.15 |

The data paints a diverging picture within the sector. NVDA is the clearest outlier: its RSI has collapsed from a local peak of ~70 in mid-May to 35.85 on June 4, approaching oversold territory and suggesting near-term selling pressure has been substantial. AVGO echoes a similar dynamic, dropping from an intraday peak above 73 to 43.84 in just two sessions, possibly reflecting rotation out of AI-infrastructure adjacent names. In contrast, AMD, QCOM, MU, and ASML remain in the 60–75 band — elevated but not technically overbought as of the last close. The broader SPY benchmark sits at 59.15, meaning several semiconductor names (AMD at 67, QCOM at 64, MU at 68, ASML at 68) are trading with more momentum than the broad market, but not yet at alarming levels. Notably, the sector as a whole touched genuinely overbought readings of 80–89 on INTC, QCOM, and MU in the first two weeks of May, coinciding with the US-China trade truce news and renewed AI capex guidance from hyperscalers. That wave has receded.

**Valuation: Multiples Remain Structurally Elevated for AI-Exposed Names**

The overbought question cannot be answered through momentum alone — RSI describes the speed of price change, not whether the underlying business justifies the price. The following table presents trailing annual P/E ratios for the cohort from 2021 through 2026 (2026 where available).

| Ticker | 2021  | 2022  | 2023   | 2024   | 2025    | 2026  |
|:-------|------:|------:|-------:|-------:|--------:|------:|
| NVDA   | 170.5 | 38.0  | 284.3  | 112.5  | 63.5    | 44.6  |
| AMD    | 55.9  | 77.1  | 280.5  | 120.5  | 80.8    |       |
| AVGO   | 44.3  | 21.1  | 33.8   | 187.9  | 72.6    |       |
| ASML   | 49.0  | 36.3  | 34.4   | 34.6   | 36.9    |       |
| MU     | 18.1  | 6.5   | —      | 120.9  | 37.6    |       |
| QCOM   | 23.2  | 9.7   | 22.5   | 17.1   | 34.1    |       |
| TSM    | 29.1  | 11.9  | 19.4   | 29.0   | 28.4    |       |
| INTC   | 10.6  | 13.6  | 125.3  | —      | —       |       |

NVDA's P/E compression from its stratospheric 284x in 2023 to 44.6x on a current-year basis is meaningful progress, but at 44x it still prices in enormous earnings growth expectations that leave little room for execution disappointment. AMD at 80.8x and AVGO at 72.6x for 2025 are similarly demanding. In contrast, TSM trades at a comparatively modest 28x, QCOM at 34x, and ASML at 37x — multiples that, while not cheap, are more defensible given their structural moat positions in leading-edge foundry, mobile/auto connectivity, and EUV lithography respectively. INTC remains the sector's distressed outlier, posting deeply negative earnings in 2024 and 2025 as its restructuring and process-technology catch-up remains unresolved.

**Risk-Adjusted Returns: The Sector Has Not Rewarded Shareholders Proportionally**

Sharpe ratios on an annual basis tell a sobering story. The table below shows risk-adjusted excess return (versus the risk-free rate) for each name since 2021.

| Year | NVDA   | AMD    | INTC   | QCOM   | AVGO   | TSM    | MU     | ASML   |
|:-----|-------:|-------:|-------:|-------:|-------:|-------:|-------:|-------:|
| 2021 | -0.38  | -0.46  | -0.70  | -0.62  | -0.70  | -0.66  | -0.53  | -0.51  |
| 2022 | -0.79  | -0.82  | -1.27  | -1.03  | -1.23  | -1.19  | -1.04  | -0.93  |
| 2023 | -1.10  | -1.20  | -1.49  | -1.90  | -1.77  | -1.91  | -1.59  | -1.90  |
| 2024 | -1.13  | -1.39  | -1.40  | -1.71  | -1.14  | -1.53  | -1.27  | -1.48  |
| 2025 | -1.32  | -1.05  | -0.98  | -1.75  | -1.22  | -1.57  | -0.94  | -1.61  |
| 2026 | -1.73  | -0.74  | -0.57  | -1.03  | -1.41  | -1.53  | -0.59  | -1.24  |

These uniformly negative Sharpe ratios indicate that, in every period, volatility has outpaced risk-compensated returns across the cohort. NVDA stands out negatively in 2026 with a Sharpe of -1.73, confirming that its recent price drawdown has been accompanied by elevated volatility — consistent with the RSI collapse observed above. AMD and MU register the least-negative 2026 ratios (-0.74 and -0.59 respectively), suggesting comparatively less turbulent price action relative to their returns. QCOM and INTC are also showing improvement in 2026 versus 2025, which aligns with their RSI readings reflecting a less extended momentum condition.

**Synthesis: Mixed Signals — Sector Was Overbought, Now Normalizing**

The semiconductor sector is not uniformly overbought as of June 4, 2026. The data reveals a sector mid-cycle in a technical correction from a genuine May overbought peak. NVDA and AVGO have unwound their momentum surges most aggressively and now flash caution signals in the opposite direction, with NVDA approaching oversold territory. AMD, MU, QCOM, and ASML remain mildly elevated on momentum but well below the threshold that would warrant an overbought classification. Valuations remain the persistent structural concern: NVDA, AMD, and AVGO carry multiples that require continued AI-driven earnings acceleration to justify, while ASML, QCOM, and TSM offer more moderate entry points from a fundamental standpoint. For investors monitoring the sector, the logical next steps within the Finance Toolkit ecosystem would include drilling into individual-name volatility profiles using GARCH forecasts, running rolling Sharpe analyses to capture momentum-regime shifts, or examining sector-level factor exposures through Fama-French decomposition to isolate whether excess returns are attributable to market beta, size, or value factors.
</details>
</i>

Furthermore, I wanted the MCP model to not be only useful for expensive and detailed models. Even a Nano or Mini model can provide valuable insights. A few example prompts using a simple model (`GPT-5 mini`) are shown below.

<details><summary><b>Compare the P/E ratios of Apple, Microsoft, and Google over the last 5 years.</b></summary>
<i>
Apple, Microsoft, and Google's P/E ratios over the last five years show that Microsoft started at the highest valuation in 2021, compressed sharply in 2022, then largely recovered, Apple dipped in 2022 before rebounding to a 2024 peak, and Google remained the cheapest overall but recovered noticeably by 2025. The yearly P/E ratios for 2021–2025 are shown below.

|       |    2021 |    2022 |    2023 |    2024 |    2025 |
|:------|--------:|--------:|--------:|--------:|--------:|
| AAPL  | 31.6299 | 21.254  | 31.3868 | 41.1631 | 36.418  |
| GOOGL | 25.8204 | 19.3593 | 24.082  | 23.5345 | 28.9627 |
| MSFT  | 41.7607 | 24.8598 | 38.8299 | 35.7197 | 35.4526 |
</details>
</i>

<details><summary><b>What is the current Sharpe ratio for Tesla compared to the S&P 500?</b></summary>
<i>
Over the available yearly series, Tesla’s Sharpe ratio is negative but consistently higher (less negative) than the S&P 500 (proxied by `SPY`), indicating Tesla delivered better risk‑adjusted returns than the S&P 500 in each year shown.

Yearly Sharpe ratios (TSLA vs SPY):
| Date   |    TSLA |     SPY |
|:-------|--------:|--------:|
| 2021   | -0.3537 | -1.5987 |
| 2022   | -0.7606 | -1.8078 |
| 2023   | -1.0402 | -4.0283 |
| 2024   | -0.9845 | -4.8964 |
| 2025   | -1.0411 | -3.4406 |
| 2026   | -1.7836 | -4.6496 |
</details>
</i>

<details><summary><b>Compare the financial performance of Alibaba and Amazon over the last 5 years</b></summary>
<br>
<i>
Over the last five years Amazon has outgrown Alibaba in absolute scale and delivered larger revenue and market‑cap expansion, while Alibaba showed steadier margin improvement and a sharp profitability rebound by 2025.  

Below are the core yearly figures (2021–2025) used to compare scale and bottom‑line performance; revenue and net income are in USD and rounded to one decimal where helpful.

Looking at revenue and net income, Amazon is much larger in absolute revenue and produced a large net‑income rebound after 2022.

| Year | AMZN Revenue (bn) | BABA Revenue (bn) | AMZN Net Income (bn) | BABA Net Income (bn) |
|:-----|------------------:|------------------:|---------------------:|---------------------:|
| 2021 | 469.8             | 112.5             | 33.4                 | 23.6                 |
| 2022 | 514.0             | 122.5             | -2.7                 | 8.9                  |
| 2023 | 574.8             | 122.2             | 30.4                 | 10.2                 |
| 2024 | 638.0             | 128.9             | 59.2                 | 10.9                 |
| 2025 | 716.9             | 142.4             | 77.8                 | 18.5                 |

When we compare per‑share and profitability metrics, both companies recovered after mid‑period weakness but Amazon delivered higher EPS and stronger returns on capital in recent years.

Looking at EPS (annual):

| Year | AMZN EPS | BABA EPS |
|:-----|---------:|---------:|
| 2021 | 3.24     | 55.60    |
| 2022 | -0.27    | 22.96    |
| 2023 | 2.90     | 27.68    |
| 2024 | 5.53     | 31.60    |
| 2025 | 7.17     | 55.12    |

Return on equity (ROE) shows Amazon moving to materially higher ROE from 2023 onward; Alibaba improved but stayed below Amazon’s peak ROE.

| Year | AMZN ROE | BABA ROE |
|:-----|---------:|---------:|
| 2021 |         |         |
| 2022 | -0.0191 | 0.0546  |
| 2023 | 0.1749  | 0.0650  |
| 2024 | 0.2429  | 0.0702  |
| 2025 | 0.2229  | 0.1199  |

Return on invested capital (ROIC) follows the same pattern: Amazon shows larger ROIC from 2023 while Alibaba’s ROIC notably improved by 2025.

| Year | AMZN ROIC | BABA ROIC |
|:-----|----------:|----------:|
| 2021 |           |          |
| 2022 | -0.0101  | 0.0468   |
| 2023 | 0.0976   | 0.0556   |
| 2024 | 0.1571   | 0.0730   |
| 2025 | 0.1584   | 0.1219   |

Market capitalization (year‑end) shows Amazon’s much larger market value throughout the period.

| Year | AMZN Market Cap (bn) | BABA Market Cap (bn) |
|:-----|---------------------:|---------------------:|
| 2021 | 1717.2               | 326.4                |
| 2022 | 855.9                | 239.9                |
| 2023 | 1594.2               | 204.6                |
| 2024 | 2352.1               | 215.8                |
| 2025 | 2499.1               | 354.0                |

Amazon is the dominant scale and value creator by revenue and market cap and converted that scale into rising ROE/ROIC and large net income gains after 2022, while Alibaba delivered steadier margin improvement and a notable profitability recovery by 2025 but remained materially smaller in absolute terms.
</details>
</i>

<details><summary><b>Show me the unemployment rate for the United States and Germany since 2010.</b></summary>
<i>
Since 2010 Germany's unemployment rate fell from about 6.6% to roughly 3.0% and has stayed near that level, while the United States fell from about 9.6% in 2010, spiked in 2020, and averaged roughly 4.3% by 2026. The table below shows the annual unemployment rates (percent) for the United States and Germany from 2010 through 2026.

|      |   Germany |   United States |
|:-----|----------:|----------------:|
| 2010 |     6.575 |           9.608 |
| 2011 |     5.517 |           8.933 |
| 2012 |     5.083 |           8.075 |
| 2013 |     4.95  |           7.358 |
| 2014 |     4.708 |           6.158 |
| 2015 |     4.367 |           5.275 |
| 2016 |     3.908 |           4.875 |
| 2017 |     3.567 |           4.358 |
| 2018 |     3.208 |           3.892 |
| 2019 |     2.975 |           3.675 |
| 2020 |     3.625 |           8.092 |
| 2021 |     3.575 |           5.35  |
| 2022 |     3.067 |           3.633 |
| 2023 |     3.025 |           3.625 |
| 2024 |     3.352 |           4.081 |
| 2025 |     3.152 |           4.369 |
| 2026 |     3.061 |           4.307 |
</details>
</i>

<details><summary><b>Calculate the WACC for Amazon and explain what it means.</b></summary>
<i>
Amazon's WACC is elevated historically, driven by a high implied cost of equity compared with its low cost of debt; the model shows WACC around 19–32% across 2021–2025 with a 2025 WACC of 19.23%. Below is the model output used to calculate Amazon's WACC (values in USD for market values, rates in decimal form).

|                                  |        2021 |         2022 |        2023 |        2024 |        2025 |
|:---------------------------------|------------:|-------------:|------------:|------------:|------------:|
| Market Value Equity              | 1.71722e+12 |  8.55876e+11 | 1.59415e+12 | 2.35208e+12 | 2.49909e+12 |
| Market Value Debt                | 1.16395e+11 |  1.40118e+11 | 1.35611e+11 | 1.309e+11   | 1.52987e+11 |
| Cost of Equity                   | 0.2774      | -0.3418      | 0.3477      | 0.3349      | 0.2033      |
| Cost of Debt                     | 0.0155      |  0.0169      | 0.0235      | 0.0184      | 0.0149      |
| Corporate Tax Rate               | 0.1256      |  0.5417      | 0.1896      | 0.1352      | 0.1973      |
| Weighted Average Cost of Capital | 0.2607      | -0.2926      | 0.3219      | 0.3181      | 0.1923      |

The WACC represents the blended after-tax cost of the capital providers (equity and debt) and is the discount rate a company must earn on its existing asset base to satisfy its investors. Amazon's high reported cost of equity in several years makes the WACC unusually large relative to typical large-cap firms, indicating investors require high returns for bearing equity risk; by contrast, Amazon's cost of debt is low, so debt contributes little to WACC because equity dominates the capital structure by market value. 
</details>
</i>

<details><summary><b>What is the RSI for NVIDIA right now and is it overbought?</b></summary>
<i>
NVIDIA's 14‑day RSI fell from extreme overbought readings in late April and is now in neutral territory near 59.8 as of 2026-05-07.

The last ten trading-day 14‑day RSI values for NVIDIA are shown below.

| Date       |   NVDA |
|:-----------|-------:|
| 2026-04-24 | 86.6826 |
| 2026-04-27 | 88.7971 |
| 2026-04-28 | 81.6663 |
| 2026-04-29 | 74.7558 |
| 2026-04-30 | 59.7435 |
| 2026-05-01 | 58.0771 |
| 2026-05-04 | 51.9935 |
| 2026-05-05 | 47.5831 |
| 2026-05-06 | 57.9211 |
| 2026-05-07 | 59.8245 |

The most recent RSI on 2026-05-07 is 59.82, which is below the common overbought threshold of 70 and therefore indicates NVIDIA is not currently overbought; the series shows it moved out of extreme overbought conditions after late‑April peaks above 90.
</details>
</i>

<details><summary><b>When looking at the Semiconductor industry, what company seems to be the most sustainable?</b></summary>
<i>
I'll fetch ESG scores for a set of leading semiconductor companies (NVDA, AMD, INTC, ASML, TSM, TXN, QCOM, AVGO, MRVL, ON) to identify the most sustainable firm.

ASML clearly stands out as the most sustainable company in this semiconductor sample, scoring far higher on the Finance Toolkit ESG metric than its peers in 2026.

The latest (2026) ESG scores for the sampled semiconductor companies are shown below.

| Ticker |   ESG Score (2026) |
|:-------|-------------------:|
| ASML   |             95.65  |
| TSM    |             83.13  |
| INTC   |             80.08  |
| TXN    |             78.38  |
| AMD    |             78.02  |
| NVDA   |             67.99  |
| MRVL   |             67.59  |
| ON     |             68.06  |
| QCOM   |             67.36  |
| AVGO   |             62.56  |

ASML’s lead is supported by very strong component scores in 2026, which indicate balanced performance across environmental, social, and governance factors.

| Score Type       | 2026 |
|:-----------------|-----:|
| Environmental    | 95.84 |
| Social           | 98.92 |
| Governance       | 92.20 |
</details>
</i>

# Advanced Usage

The setup wizard provides a user-friendly way to configure the MCP server, but for advanced users looking to automate the process or integrate it into a larger setup script, the `financetoolkit-mcp-setup` command accepts various arguments that allow you to bypass the interactive prompts and directly configure the server for specific clients and options.

## Automating the MCP Server Setup

When looking to automate the setup process, this can be done through arguments passed to the `financetoolkit-mcp-setup` command. For example, to bypass the setup wizard and directly configure the MCP server for Claude Code, you can run:

```
uvx --from "financetoolkit[mcp]" financetoolkit-mcp-setup --client claude-code --include-skills
```

The following arguments are available:

- `--client`: Install the MCP server for a specific client. The choices are `claude-desktop`, `claude-code`, `vscode`, `cursor`, `gemini`, and `windsurf`.
- `--include-skills`: Whether to install the optional SKILL.md analyst instructions that guide the LLM on how to use the tools effectively.
- `--overwrite`: Whether to overwrite existing config entries if they are already present.

On purpose there exists no `--api-key` flag given that the configuration will include a location to an `.env` file (e.g. `/Users/jeroenbouma/.config/financetoolkit/.env`) and therefore it is more secure to write the API key directly to that file instead of having it appear in the command history.

## Inspecting the Available Tools

The server exposes tools grouped into categories. Use the built-in `list_categories` tool to see all categories and their tool counts, or `search_metrics` to find a specific indicator by keyword. To properly inspect these tools use the interactive Inspector UI by running `uvx --from "financetoolkit[mcp]" financetoolkit-mcp-inspector` which allows you to explore the tools, their parameters, and example calls in a user-friendly way.

Each tool accepts an `indicator` parameter that selects the exact metric to compute. For example, to get the Price-to-Earnings ratio you would call `get_valuation_ratios` with `indicator='get_price_to_earnings_ratio'`. The AI assistant handles this routing automatically, simply ask your question in plain English and the assistant will select the right tool and indicator.

Tools that operate on equities accept a `tickers` parameter (comma-separated list, e.g. `tickers='AAPL,MSFT'`). Tools that operate on macro data accept a `countries` parameter (e.g. `countries='United States,Germany'`). All tools accept `start_date`, `end_date`, and `quarterly` to control the time range and periodicity.

Find below a full list of available tools and their descriptions, all tools return data in a standardized Markdown format.

<details>
  <summary><b>Fundamentals</b></summary>

  These tools provide a wide range of fundamental data points and financial metrics for companies, including historical prices, financial statements, company profiles, ESG scores, and performance/risk metrics.

| Tool | Description |
|:---|:---|
| `get_discovery` | Stock and ETF screener, gainers/losers, most active |
| `get_toolkit_data` | Historical prices, financial statements, company profile, real-time quote |
| `get_environment` | ESG scores, carbon footprint, renewable energy usage |
| `get_performance` | Sharpe ratio, Sortino ratio, Alpha, Beta, CAPM, Fama-French |
| `get_risk` | Value at Risk, CVaR, GARCH volatility, max drawdown, skewness, kurtosis |
| `get_options` | Black-Scholes pricing, binomial tree, Greeks, implied volatility |

</details>

<details>
  <summary><b>Financial Ratios and Models</b></summary>

  These tools compute a wide range of financial ratios and models that are commonly used for fundamental analysis, valuation, and credit risk assessment. They can be applied to any company with available financial statement data.

| Tool | Description |
|:---|:---|
| `get_efficiency_ratios` | Asset/inventory turnover, days of sales outstanding, cash conversion cycle |
| `get_liquidity_ratios` | Current ratio, quick ratio, cash ratio, working capital |
| `get_profitability_ratios` | Gross/net/operating margin, ROE, ROA, ROIC, ROCE |
| `get_solvency_ratios` | Debt-to-equity, interest coverage, net debt to EBITDA |
| `get_valuation_ratios` | P/E, EPS, EV/EBITDA, P/B, P/S, dividend yield, free cash flow yield |
| `get_models` | WACC, DuPont analysis, Altman Z-Score, Piotroski F-Score, intrinsic value |

</details>

<details>
  <summary><b>Technical Indicators</b></summary>

  These tools compute a wide range of technical indicators used for momentum, trend, volatility, and breadth analysis. They can be applied to any instrument with historical price data.

| Tool | Description |
|:---|:---|
| `get_momentum_indicators` | RSI, MACD, Stochastic oscillator, Williams %R, Aroon |
| `get_overlap_indicators` | SMA, EMA, Bollinger Bands, Keltner Channels |
| `get_volatility_indicators` | Average True Range, True Range, volatility series |
| `get_breadth_indicators` | McClellan oscillator, OBV, Advance/Decline line, Chaikin |

</details>

<details>
  <summary><b>Macro Economics and Fixed Income</b></summary>

  These tools provide insights into the broader economic environment and fixed income valuations, helping you understand the macro conditions that can impact financial markets.

| Tool | Description |
|:---|:---|
| `get_general_economy` | GDP, CPI, inflation, trade balances, investment, consumption |
| `get_government_economy` | Government debt, deficit, expenditure, revenue, tax rates |
| `get_jobs_and_society` | Unemployment, population, poverty, income inequality |
| `get_interest_rates` | Central bank rates, government bond yields, EURIBOR |
| `get_fixed_income_valuations` | Bond duration, present value, YTM, derivative pricing |

</details>

<details>
  <summary><b>Utility Tools</b></summary>

These tools help you navigate the available functionality before making any data call.

| Tool | Description |
|:---|:---|
| `get_analyst_guidelines` | Returns the full analyst instructions and response style guide |
| `list_categories` | Lists all registered categories and the number of tools each contains |
| `list_metrics_by_category` | Lists every metric available within a given category |
| `search_metrics` | Fuzzy keyword search across all metrics with typo tolerance |
| `search_instruments` | Look up ticker symbols by company name, ISIN, CIK, CUSIP, or symbol |

</details>
<br>

# How the MCP Server is Built

The MCP server lives entirely inside `financetoolkit/mcp_server/` and is structured around a **router pattern**: rather than exposing every one of the 200+ Finance Toolkit methods as a separate MCP tool (which would overwhelm an LLM's tool list), the server groups them into ~21 categorical master tools. Each master tool accepts an `indicator` parameter that selects the exact metric at call time.

## Module Overview

| Module | Role |
|:---|:---|
| `mcp_controller.py` | Entry points (`main`, `setup`, `inspector`), config loading, server assembly |
| `registry_controller.py` | Builds and registers the categorical router tools on the FastMCP instance |
| `inspection_controller.py` | Static introspection of controller classes: method discovery and signature building |
| `provider_model.py` | Routes tool calls to the correct Finance Toolkit module; manages Toolkit instance caching |
| `cache_model.py` | Thread-safe SQLite cache for DataFrame results with TTL-based eviction |
| `tools_model.py` | Registers the four built-in utility tools (list, search, instrument lookup) |
| `formatting_model.py` | Converts any Finance Toolkit result (DataFrame, Series, dict, scalar) to Markdown |
| `coercion_model.py` | Best-effort type coercion for string values arriving from LLMs |
| `setup_model.py` | Interactive and CLI setup wizard: writes client configs and SKILL.md files |

## Startup Sequence

When the server process starts (`uvx … financetoolkit-mcp`), `mcp_controller._build_mcp_app()` runs the following steps in order:

1. **Load environment** — resolves the FMP API key from the process environment, a local `.env` file, or the global Finance Toolkit config path (`~/.config/financetoolkit/.env`).
2. **Read `config.yaml`** — a single YAML file in the same package directory drives all registration: which controller classes exist (`module_class_map`), which methods to skip (`skip_methods`), which parameters the wrapper always handles (`init_handled_params`), and the full ordered list of tool groups (`tool_groups`).
3. **Instantiate subsystems** — a `ToolkitProvider` (with its `SQLiteCache`), a `ControllerInspector`, a `ToolRegistry`, and a `UtilityToolRegistry` are all constructed and wired together.
4. **Register tools** — `ToolRegistry.register_all_tools()` registers the router groups, then `UtilityToolRegistry.register_all_tools()` registers the four utility tools. The server is then ready to serve requests over stdio (or whichever transport `MCP_TRANSPORT` specifies).

## The Router Pattern

`ToolRegistry` reads the `tool_groups` list from `config.yaml`. Each entry is converted to a `RouterGroupSpec` NamedTuple that describes one master tool — its name, the controller class to introspect, and how methods are discovered.

For each group, `ControllerInspector` either:
- **Parses the source** of a nominated `collect_*` method on the controller class to find every `self.get_*()` call in the order they appear, or
- **Falls back** to an alphabetical scan of all `get_` methods on the class.

This produces an ordered list of indicator names. `_build_router_wrapper()` then constructs a single `wrapper(**kwargs)` closure that:

1. Reads the `indicator` argument and matches it to the method list (with fuzzy-match suggestions on typos).
2. Coerces all typed parameters from strings via `coercion_model.coerce_value()`.
3. Validates required inputs (`tickers` for equity tools, date formats).
4. Delegates to `ToolkitProvider.call_method()`.
5. Passes the result through `formatting_model.format_result()` and returns a Markdown string.

The wrapper's `__signature__` is replaced with a proper `inspect.Signature` so that FastMCP can introspect it and generate accurate JSON Schema for the LLM.

## Dispatch Categories

Every tool group has a `category` that controls how `ToolkitProvider` routes the call:

| Category | Behaviour |
|:---|:---|
| `ticker` | Instantiates a `Toolkit(tickers=…)` object and calls a method on one of its sub-modules (e.g. `ratios`, `models`, `options`) |
| `toolkit` | Same Toolkit instance, but calls a method directly on the `Toolkit` class (e.g. `get_historical_data`) |
| `standalone` | Instantiates `Economics` or `FixedIncome` directly — no tickers required |
| `discovery` | Instantiates `Discovery(api_key=…)` — no tickers or dates required |
| `mixed` | Per-method routing table: each indicator maps to its own `(module, category)` pair |

`ToolkitProvider` caches `Toolkit` instances by a key derived from tickers, date range, quarterly flag, and a hash of the API key, so repeated calls for the same parameters reuse an existing instance. Standalone module instances are cached the same way. Full DataFrame results are written to and read from `SQLiteCache` with configurable TTL.

## Utility Tools

`UtilityToolRegistry` registers four tools that operate on the tool index rather than routing to a controller:

- `get_analyst_guidelines` — returns the full analyst SKILL.md instructions so the LLM always has the response style guide available.
- `list_categories`* — returns a Markdown table of all registered categories and tool counts.
- `list_metrics_by_category` — lists every indicator within a given category.
- `search_metrics` — token-based fuzzy search across all tool names and descriptions, with typo tolerance via `difflib.get_close_matches`.
- `search_instruments` — proxies a live `Discovery.search_instruments()` call for ticker/ISIN/name lookups.

## Setup Wizard

`setup_model.py` powers both the interactive wizard (`financetoolkit-mcp-setup`) and the non-interactive `--client` CLI path. It locates and merges the `finance-toolkit` MCP entry into each client's JSON config file without disturbing other server entries, writes the FMP API key to `~/.config/financetoolkit/.env`, and optionally copies the `SKILL.md` analyst instructions to the location expected by each client (`.agents/skills/` for VS Code/Cursor, `.claude/skills/` for Claude Code, etc.).