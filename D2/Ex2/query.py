from google.cloud import bigquery
import pandas as pd

# Load CSV into a DataFrame
df = pd.read_csv("products-1000.csv")

# Fix data types
df["EAN"] = df["EAN"].astype(str)
df["Index"] = pd.to_numeric(df["Index"], errors="coerce")
df["Internal ID"] = pd.to_numeric(df["Internal ID"], errors="coerce")
df["Price"] = pd.to_numeric(df["Price"], errors="coerce")
df["Stock"] = pd.to_numeric(df["Stock"], errors="coerce")

client = bigquery.Client.from_service_account_json("de-training-d2-dc0eb0f35277.json")

print(client.project)

# Average Price per Brand:
query_1 = """
    SELECT Brand, AVG(Price) AS avg_price
    FROM `de-training-d2.my_dataset.sales_data`
    WHERE Price IS NOT NULL
    GROUP BY Brand
    ORDER BY avg_price DESC
"""

df = client.query(query_1).to_dataframe()
df.to_csv("query_1_results.csv", index=False)

# Total Stock per Category:
query_2 = """
    SELECT Category, SUM(Stock) AS total_stock
    FROM `de-training-d2.my_dataset.sales_data`
    WHERE Stock IS NOT NULL
    GROUP BY Category
    ORDER BY total_stock DESC
"""
df = client.query(query_2).to_dataframe()
df.to_csv("query_2_results.csv", index=False)


