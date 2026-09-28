# AI-Powered Insight Generator 🤖📊

A SQL → Python → LLM → Power BI pipeline that turns raw SaaS transaction data into a grounded, AI-generated executive summary — with automatic anomaly detection and a live dashboard. Built on top of the [SaaS Subscription Revenue & Churn Analytics](https://github.com/mohit27-maker/saas-churn-revenue-analytics) project's MySQL schema.

`SQL` `Python` `Gemini API` `Power BI` `Pandas` `MySQL`

![Dashboard](dashboard.png)

## 🎯 Problem

Every BI dashboard shows *what* happened — MRR went up, churn went up — but someone still has to manually read the charts, spot the outlier month, and write the narrative for stakeholders who won't open Power BI themselves. That's a repeated, low-value task sitting between "data is ready" and "leadership understands what to do about it."

## 💡 Solution

A pipeline that goes from raw MySQL data to a boardroom-ready summary with zero manual analysis:

- **SQL layer** — MRR waterfall logic (New / Expansion / Contraction / Churn) built with window functions (`LAG`, `LEAD`) and views, reconstructing each customer's plan history from event data
- **Python layer** — pulls the aggregated view via SQLAlchemy, pivots it into a monthly time series, and flags statistical anomalies (z-score method) per movement type
- **LLM layer** — Gemini API generates a plain-English executive summary, prompted with *only the computed statistics* (never raw rows), so the output can't hallucinate numbers that don't exist in the data
- **Power BI dashboard** — live waterfall chart + cumulative MRR trend line, connected directly to the SQL view
- **Excel export** — the full monthly breakdown plus the AI summary, in one shareable workbook

Data → SQL aggregation → Python stats & anomaly flags → LLM narrative → Dashboard + Excel. No manual write-up required.

## 📊 Key Findings (sample run, Jan 2024–Dec 2025)

- Ending MRR grew from **$16,880** to **$482,998** over 24 months — positive net change every single month
- **New MRR** was the primary growth driver, peaking at $39,238 in September 2025
- **Churn** was the largest drag on revenue, worsening steadily to −$18,759 by December 2025
- One statistical anomaly flagged: an **Expansion spike** in October 2025 ($7,340, more than 2 standard deviations above its own historical average) — automatically detected, not manually spotted

## 🖥️ Dashboard

![Waterfall Chart](waterfall_chart.png)

MRR movement waterfall (left) and cumulative ending-MRR trend (right), with a month-range slicer and the AI-generated executive summary displayed alongside.

## 🏗️ How It Works

```
MySQL (raw customers, subscriptions, plan_changes, payment_transactions)
        │
        ▼
SQL Views (calendar_months → plan_segments → monthly_mrr → mrr_movements)
        │
        ▼
vw_mrr_waterfall_summary   ──►   Power BI (live connection: waterfall + trend line)
        │
        ▼
Python (SQLAlchemy pull → pivot → z-score anomaly detection)
        │
        ▼
Grounded prompt (stats only, no raw rows)
        │
        ▼
Gemini API (gemini-3.8-flash)
        │
        ▼
Executive summary  ──►  Power BI text card  +  Excel export (mrr_summary.xlsx)
```

## 🛠️ Tech Stack

| Layer | Tools |
|---|---|
| Database | MySQL |
| SQL | Window functions (`LAG`, `LEAD`), CTEs, views |
| Orchestration | Python (Pandas, SQLAlchemy, PyMySQL) |
| Anomaly detection | Z-score (Pandas/NumPy) |
| LLM | Google Gemini API (`gemini-3.8-flash`) |
| Dashboard | Power BI Desktop |
| Export | openpyxl (Excel) |
| Config | python-dotenv |

## 🚀 Getting Started

### 1. Clone and install

```bash
git clone https://github.com/mohit27-maker/ai-insight-generator.git
cd ai-insight-generator
pip install -r requirements.txt
```

### 2. Set up the database

Run the SQL scripts in `sql/` against a MySQL instance loaded with the [SaaS Churn Analytics](https://github.com/mohit27-maker/saas-churn-revenue-analytics) dataset (or your own transaction data with a similar schema).

### 3. Add your Gemini API key

⚠️ Never hard-code API keys in source files.

Copy `.env.example` to `.env` and add your key:

```
GEMINI_API_KEY=your-key-here
```

Get a free-tier key at https://aistudio.google.com/apikey.

### 4. Update your database connection

In `generate_summary.py`, update the connection string with your own MySQL credentials:

```python
engine = create_engine("mysql+pymysql://username:password@localhost/saas_churn_analytics")
```

### 5. Run the pipeline

```bash
python generate_summary.py
```

This pulls the data, computes stats and anomalies, generates the executive summary, prints it to console, and writes `executive_summary.txt` + `mrr_summary.xlsx`.

### 6. Open the dashboard

Open `ai_insight_dashboard.pbix` in Power BI Desktop and point it at your MySQL instance to refresh with your own data.

## 📁 Project Structure

```
├── generate_summary.py          # Full pipeline: SQL pull → pivot → anomalies → LLM summary → Excel export
├── test_sql_connection.py       # Standalone SQL connection/pivot test script
├── sql/
│   └── mrr_waterfall.sql        # MRR waterfall views (calendar, plan segments, monthly MRR, movements)
├── ai_insight_dashboard.pbix    # Power BI dashboard
├── mrr_summary.xlsx             # Generated Excel export (data + AI summary)
├── executive_summary.txt        # Generated AI summary (latest run)
├── screenshots/
│   ├── dashboard.png
│   └── waterfall_chart.png
├── requirements.txt
├── .env.example
├── .gitignore
└── README.md
```

## 💡 Design Notes

- **Grounding, not hallucination**: the LLM only ever receives pre-computed aggregates (monthly totals, anomaly flags) — never raw transaction rows — so every number in the summary is traceable back to an actual SQL/Python calculation.
- **Explainable anomaly detection**: uses a simple z-score threshold rather than a black-box ML model, so the method is fully explainable in an interview setting.
- **Static vs. live summary**: the Power BI text card currently displays a manually-pasted copy of the latest summary. A production version would push the LLM output into a SQL table that Power BI reads live on refresh.

## 🎯 Use Cases

- **Analysts** — skip manual write-ups after every reporting cycle
- **Founders/leadership** — get a plain-English read on MRR health without opening a dashboard
- **Recruiters/interviewers** — demonstrates SQL, Python, LLM API integration, and BI tooling in a single connected pipeline
