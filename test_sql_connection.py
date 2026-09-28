import pandas as pd
from sqlalchemy import create_engine

# MySQL connection
engine = create_engine(
    "mysql+pymysql://root:Root_123@localhost/saas_churn_analytics"
)

# Pull data from the existing SQL view
df = pd.read_sql(
    "SELECT * FROM vw_mrr_waterfall_summary ORDER BY month_start",
    engine
)

# Show the first 5 rows
print(df.head())

pivot = df.pivot_table(
    index="month_start",
    columns="movement_type",
    values="total_mrr_delta",
    aggfunc="sum",
    fill_value=0
).reset_index()

pivot["net_mrr_change"] = pivot["New"] + pivot["Expansion"] + pivot["Contraction"] + pivot["Churn"]
pivot["ending_mrr"] = pivot["net_mrr_change"].cumsum()  # running total — adjust if you have a true starting MRR

def flag_anomalies(series, threshold=2):
    z_scores = (series - series.mean()) / series.std()
    return z_scores.abs() > threshold

for col in ["New", "Expansion", "Contraction", "Churn"]:
    pivot[f"{col}_anomaly"] = flag_anomalies(pivot[col])

    print(pivot.head())