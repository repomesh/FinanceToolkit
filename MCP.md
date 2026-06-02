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

# Installation

The installation process is designed to be as seamless as possible, with an interactive setup wizard that configures your clients and securely stores your API key. The server itself runs on demand via `uvx`, so no local installation is required for the clients.

> **Step 1: Run the Setup Wizard**

Clients are configured to launch the server on demand via [uvx](https://docs.astral.sh/uv/guides/tools/), so as long as [uv](https://docs.astral.sh/uv/getting-started/installation/) is installed, you can run the setup wizard directly with:

```
uvx --from "financetoolkit[mcp]" financetoolkit-mcp-setup
```

> **Step 2: Configure your client(s)**

The wizard asks for your FinancialModelingPrep API key which you can obtain from FinancialModelingPrep **<a href="https://www.jeroenbouma.com/fmp" target="_blank">here</a>**.

```bash
(base) jeroenbouma@Jeroens-MacBook-Pro FinanceToolkit % uvx --from "financetoolkit[mcp]" financetoolkit-mcp-setup
╭─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│                                                                                                                                 │
│  FinanceToolkit  ·  MCP Setup Wizard                                                                                            │
│  Transparent and Efficient Financial Analysis                                                                                   │
│                                                                                                                                 │
╰─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯

  ⚠  No API key found.  Get one at https://www.jeroenbouma.com/fmp  (15% discount)
  Press Enter to skip and configure via .env later.

  API Key  › YOUR_FINANCIAL_MODELING_PREP_API_KEY_HERE
```

The wizard securely stores it in a global config file on your system (never inside the project or any version-controlled file) and writes a config entry for each selected client that launches the server via `uvx`. It safely merges the `finance-toolkit` entry into any existing config without disturbing other server entries, and asks for confirmation before overwriting an entry that is already present.

Next up is deciding what client(s) you want to configure. You can select multiple clients at once (e.g. 23 for both Claude Code and VS Code) and the wizard will write the necessary config entries for each selected client to launch the MCP server on demand.

```bash
  ✔  API key saved to /Users/jeroenbouma/.config/financetoolkit/.env

╭────────────────────────────────────────────────────────────── Configure Clients ────────────────────────────────────────────────╮
│                                                                                                                                 │
│    1  Claude Desktop                                                                                                            │
│    2  Claude Code                                                                                                               │
│    3  VS Code                                                                                                                   │
│    4  Cursor                                                                                                                    │
│    5  Gemini                                                                                                                    │
│    6  Windsurf                                                                                                                  │
│                                                                                                                                 │
│    7  Remove configuration                                                                                                      │
│    0  Exit                                                                                                                      │
│                                                                                                                                 │
╰──────────────────────────────────────────────────── e.g. 23 for Claude Code + VS Code ──────────────────────────────────────────╯
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

> **Step 3: Start using the Tools!**

As seen above an optional SKILL.md file can be acquired, this creates a `finance-toolkit-analyst` skill in, for GitHub Copilot `.agents/skill` directory. It is possible your LLM will automatically select this skill when you ask financial questions, but if not you can explicitly invoke it by name (e.g. `/finance-toolkit-analyst What is the current P/E ratio of Apple?`).

You can ask your assistant questions about stocks, ETFs, macro conditions, and more all powered by the Finance Toolkit MCP. The LLM will automatically select the right tool and metric based on your question.

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

<br>

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

On purpose there exists no `--api-key` flag given that the create configuration will include a location to an `.env` file (e.g. `/Users/jeroenbouma/.config/financetoolkit/.env`) and therefore it is more secure to write the API key directly to that file instead of having it appear in the command history.

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