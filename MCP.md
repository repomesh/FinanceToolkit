[![FinanceToolkit](https://github.com/JerBouma/FinanceToolkit/assets/46355364/198d47bd-e1b3-492d-acc4-5d9f02d1d009)](https://github.com/JerBouma/FinanceToolkit)

[![GitHub Sponsors](https://img.shields.io/badge/Sponsor_this_Project-grey?logo=github)](https://github.com/sponsors/JerBouma)
[![Buy Me a Coffee](https://img.shields.io/badge/Buy_Me_a_Coffee-grey?logo=buymeacoffee)](https://www.buymeacoffee.com/jerbouma)
[![LinkedIn](https://img.shields.io/badge/LinkedIn-grey?logo=Linkedin&logoColor=white)](https://www.linkedin.com/in/boumajeroen/)
[![MCP Server](https://img.shields.io/badge/MCP_Server-grey?logo=modelcontextprotocol)](https://github.com/JerBouma/FinanceToolkit/blob/main/MCP.md)
[![Documentation](https://img.shields.io/badge/Documentation-grey?logo=readme)](https://www.jeroenbouma.com/projects/financetoolkit/docs)
[![Supported Python Versions](https://img.shields.io/pypi/pyversions/financetoolkit)](https://pypi.org/project/FinanceToolkit/)
[![PYPI Version](https://img.shields.io/pypi/v/FinanceToolkit)](https://pypi.org/project/FinanceToolkit/)
[![PYPI Downloads](https://static.pepy.tech/badge/financetoolkit/month)](https://pepy.tech/project/financetoolkit)

The FinanceToolkit MCP Server exposes 200+ pre-computed financial metrics, models, and economic indicators directly to any AI assistant that supports the [Model Context Protocol](https://modelcontextprotocol.io). This means you can ask Claude, Copilot, Cursor, or any other MCP-compatible assistant to analyse equities, benchmark performance, inspect macro conditions, and run technical indicators — all backed by the transparent, open-source calculation methods of the FinanceToolkit.

The server consolidates the entire FinanceToolkit surface into a small number of categorical master tools (e.g. `get_valuation_ratios`, `get_profitability_ratios`, `get_momentum_indicators`) so that the AI can discover and call the right metric without being overwhelmed by hundreds of individual function signatures.

# Table of Contents

1. [Installation](#installation)
2. [Shortest Path to a Working Finance Assistant](#shortest-path-to-a-working-finance-assistant)
3. [Manual Client Configuration](#manual-client-configuration)
4. [Available Tools](#available-tools)

# Installation


The MCP server is an optional add-on to the FinanceToolkit. The core library installs without any MCP dependencies, keeping the footprint small for users who want to work with the Finance Toolkit directly. To include the server, add the `[mcp]` extra:

```
pip install financetoolkit[mcp] -U
```

This pulls in `mcp`, `tabulate`, `python-dotenv`, and `PyYAML` on top of the standard FinanceToolkit dependencies.

After installation, three new commands are available on your PATH:

| Command | Purpose |
|:---|:---|
| `financetoolkit-mcp` | Start the MCP server |
| `financetoolkit-mcp-setup` | Auto-generate client config files |
| `financetoolkit-mcp-inspector` | Open the interactive Inspector UI |

To be able to get setup the MCP server, you need to obtain an API Key from FinancialModelingPrep. This is used to gain access to 30+ years of financial statement both annually and quarterly. Note that the Free plan is limited to 250 requests each day, 5 years of data and only features companies listed on US exchanges.

___ 

<b><div align="center">Obtain an API Key from FinancialModelingPrep <a href="https://www.jeroenbouma.com/fmp" target="_blank">here</a>.</div></b>
___

Through the link you are able to subscribe for the free plan and also premium plans at a **15% discount**. This is an affiliate link and thus supports the project at the same time.

# Shortest Path to a Working Finance Assistant

The fastest path from installation to a working AI assistant is two (or actually three) steps.

> **Step 1: Install**

```
pip install financetoolkit[mcp] -U
```

> **Step 2: Run the Setup Wizard**

```
financetoolkit-mcp-setup
```

The wizard asks for your FinancialModelingPrep API key, then presents a menu where you select which clients to configure. You can configure multiple clients at once by entering their numbers together (e.g. `23` for Claude Code + VS Code).

The wizard stores the API key in a dedicated global config file on your system (never inside the project or any version-controlled file) and writes a config entry for each selected client that points to it. It safely merges the `finance-toolkit` entry into any existing config without disturbing other server entries, and asks for confirmation before overwriting an entry that is already present.

See below:

```bash
(financetoolkit) (base) jeroenbouma@Jeroens-MacBook-Pro FinanceToolkit % financetoolkit-mcp-setup
╭───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│                                                                                                                                               │
│  FinanceToolkit  ·  MCP Setup Wizard                                                                                                          │
│  Transparent and Efficient Financial Analysis                                                                                                 │
│                                                                                                                                               │
╰───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯

  ⚠  No API key found.  Get one at https://www.jeroenbouma.com/fmp  (15% discount)
  Press Enter to skip and configure via .env later.

  API Key  › YOUR_FINANCIAL_MODELING_PREP_API_KEY_HERE
  ✔  API key saved to /Users/jeroenbouma/.config/financetoolkit/.env

╭────────────────────────────────────────────────────────────── Configure Clients ──────────────────────────────────────────────────────────────╮
│                                                                                                                                               │
│    1  Claude Desktop                                                                                                                          │
│    2  Claude Code                                                                                                                             │
│    3  VS Code                                                                                                                                 │
│    4  Cursor                                                                                                                                  │
│                                                                                                                                               │
│    5  Remove configuration                                                                                                                    │
│    0  Exit                                                                                                                                    │
│                                                                                                                                               │
╰──────────────────────────────────────────────────── e.g. 13 for Claude Desktop + VS Code ─────────────────────────────────────────────────────╯

  › 23

  ✔  Claude Code config written to /Users/jeroenbouma/.claude.json
  ✔  VS Code config written to /Users/jeroenbouma/Documents/FinanceToolkit/.vscode/mcp.json

  Install the SKILL.md analyst instructions for VS Code? [y/n] (y): y
  ✔  Skill file written to /Users/jeroenbouma/Documents/FinanceToolkit/.agents/skills/finance-toolkit-analyst/SKILL.md

  Install the SKILL.md analyst instructions for Claude Code (.claude/skills/)? [y/n] (y): y
  ✔  Claude Code skill file written to /Users/jeroenbouma/Documents/FinanceToolkit/.claude/skills/finance-toolkit-analyst.md

───────────────────────────────────────────────────────────────────── Done ──────────────────────────────────────────────────────────────────────

  ✔  All selected configurations updated!
  Restart your client(s) to apply changes.
  Run financetoolkit-mcp-inspector to test the connection.

(financetoolkit) (base) jeroenbouma@Jeroens-MacBook-Pro FinanceToolkit %    
```

After the wizard completes, restart your AI client and the FinanceToolkit tools will appear.

> **Step 3: Start using the Tools!**

As seen above an optional SKILL.md file can be acquired, this creates a `finance-toolkit-analyst` skill in the `.agents/skill` directory. It is possible your LLM will automatically select this skill when you ask financial questions, but if not you can explicitly invoke it by name (e.g. `/finance-toolkit-analyst What is the current P/E ratio of Apple?`).

You can ask your assistant questions about stocks, ETFs, macro conditions, and more all powered by the FinanceToolkit server. The LLM will automatically select the right tool and metric based on your question.

A few example prompts using a simple model (`GPT-5 mini`) are shown below. The MCP server is explicitly modelled to work well with simpler models to limit costs and token usage. Feel free to try them out in your preferred environment to see the full interactivity!

<details><summary><b>Compare the P/E ratios of Apple, Microsoft, and Google over the last 5 years.</b></summary>
<hr>
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
<hr>
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
<hr>
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
<hr>
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
<hr>
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
<hr>
<i>
I'll fetch ESG scores for a set of leading semiconductor companies (NVDA, AMD, INTC, ASML, TSM, TXN, QCOM, AVGO, MRVL, ON) to identify the most sustainable firm.

ASML clearly stands out as the most sustainable company in this semiconductor sample, scoring far higher on the FinanceToolkit ESG metric than its peers in 2026.

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

<br>

# Manual Client Configuration

The setup wizard (`financetoolkit-mcp-setup`) is the recommended way to configure any supported client. It writes the correct config file in the correct location for each platform automatically. Manual configuration is also possible — refer to the MCP documentation for each client for the exact file path and format:

- **VS Code** — [MCP in VS Code](https://code.visualstudio.com/docs/copilot/chat/mcp-servers)
- **Claude Desktop** — [MCP in Claude Desktop](https://modelcontextprotocol.io/quickstart/user)
- **Cursor** — [MCP in Cursor](https://cursor.com/docs/mcp)
- **Windsurf** — [MCP in Windsurf](https://docs.windsurf.com/windsurf/cascade/mcp#model-context-protocol-mcp)

Regardless of the client, the setup wizard generates a config entry that looks like this — pointing the server to the global key file rather than embedding the key directly:

```json
{
  "command": "financetoolkit-mcp",
  "env": {
    "FINANCETOOLKIT_ENV_FILE": "/path/to/.config/financetoolkit/.env"
  }
}
```

The path is determined automatically per operating system:

| OS | Global key file location |
|:---|:---|
| macOS / Linux | `~/.config/financetoolkit/.env` |
| Windows | `%APPDATA%\financetoolkit\.env` |

If you prefer to configure clients manually and supply the key directly, you can also pass it in the `env` block. The server resolves the key in this order at runtime: local `.env` in the working directory (highest priority) → `FINANCETOOLKIT_ENV_FILE` → global config file → system environment variable.

```json
{
  "command": "financetoolkit-mcp",
  "env": {
    "FINANCIAL_MODELING_PREP_API_KEY": "YOUR_API_KEY_HERE"
  }
}
```

The setup wizard (`financetoolkit-mcp-setup`) handles key discovery automatically. When run, it searches for an existing key in the global config file first, then the local `.env`, then the shell environment — and only prompts you to enter one if none is found. If the key is discovered in a local `.env` or the shell but the global config file does not yet contain it, the wizard syncs it there automatically and informs you.

# Available Tools

The server exposes tools grouped into categories. Use the built-in `list_categories` tool to see all categories and their tool counts, or `search_metrics` to find a specific indicator by keyword. 

___

<b><div align="center">To properly inspect these tools use the interactive Inspector UI by running `financetoolkit-mcp-inspector`</div></b>

___

Each tool accepts an `indicator` parameter that selects the exact metric to compute. For example, to get the Price-to-Earnings ratio you would call `get_valuation_ratios` with `indicator='get_price_to_earnings_ratio'`. The AI assistant handles this routing automatically, simply ask your question in plain English and the assistant will select the right tool and indicator.

Tools that operate on equities accept a `tickers` parameter (comma-separated list, e.g. `tickers='AAPL,MSFT'`). Tools that operate on macro data accept a `countries` parameter (e.g. `countries='United States,Germany'`). All tools accept `start_date`, `end_date`, and `quarterly` to control the time range and periodicity.

Find below a full list of available tools and their descriptions.


<details>
  <summary><b>Fundamentals</b></summary>

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

| Tool | Description |
|:---|:---|
| `get_momentum_indicators` | RSI, MACD, Stochastic oscillator, Williams %R, Aroon |
| `get_overlap_indicators` | SMA, EMA, Bollinger Bands, Keltner Channels |
| `get_volatility_indicators` | Average True Range, True Range, volatility series |
| `get_breadth_indicators` | McClellan oscillator, OBV, Advance/Decline line, Chaikin |

</details>

<details>
  <summary><b>Macro Economics and Fixed Income</b></summary>

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

All tools return data in a standardized Markdown format.