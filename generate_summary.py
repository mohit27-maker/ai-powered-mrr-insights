import pandas as pd
from sqlalchemy import create_engine
from google import genai
from dotenv import load_dotenv
import os

# --- Step 1: Pull from SQL ---
load_dotenv()
engine = create_engine("mysql+pymysql://root:Root_123@localhost/saas_churn_analytics")
df = pd.read_sql("SELECT * FROM vw_mrr_waterfall_summary ORDER BY month_start", engine)

# --- Step 2: Pivot ---
pivot = df.pivot_table(
    index="month_start", columns="movement_type",
    values="total_mrr_delta", aggfunc="sum", fill_value=0
).reset_index()
pivot["net_mrr_change"] = pivot["New"] + pivot["Expansion"] + pivot["Contraction"] + pivot["Churn"]
pivot["ending_mrr"] = pivot["net_mrr_change"].cumsum()

# --- Step 3: Anomaly detection ---
def flag_anomalies(series, threshold=2):
    z_scores = (series - series.mean()) / series.std()
    return z_scores.abs() > threshold

for col in ["New", "Expansion", "Contraction", "Churn"]:
    pivot[f"{col}_anomaly"] = flag_anomalies(pivot[col])

# --- Step 4: LLM summary ---
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

stats_summary = pivot.to_string(index=False)
anomaly_months = pivot[pivot[["New_anomaly", "Expansion_anomaly", "Contraction_anomaly", "Churn_anomaly"]].any(axis=1)]

prompt = f"""
You are a SaaS business analyst. Below is monthly MRR movement data
(New, Expansion, Contraction, Churn, net change, ending MRR) for a
subscription business, Jan 2024-Dec 2025. Write a concise executive
summary (max 150 words) covering: overall MRR trend, the biggest driver
of growth or decline, and any flagged anomaly months. Only use the
numbers given below - do not estimate or invent any figures.

DATA:
{stats_summary}

FLAGGED ANOMALY MONTHS:
{anomaly_months.to_string(index=False) if not anomaly_months.empty else "None flagged."}
"""

response = client.models.generate_content(
    model="gemini-3.8-flash",
    contents=prompt
)
print(response.text)

with open("executive_summary.txt", "w") as f:
    f.write(response.text)

with pd.ExcelWriter("mrr_summary.xlsx", engine="openpyxl") as writer:
    pivot.to_excel(writer, sheet_name="MRR Summary", index=False)

with pd.ExcelWriter("mrr_summary.xlsx", engine="openpyxl") as writer:
    pivot.to_excel(writer, sheet_name="MRR Summary", index=False)
    pd.DataFrame({"Executive Summary": [response.text]}).to_excel(writer, sheet_name="Summary", index=False)