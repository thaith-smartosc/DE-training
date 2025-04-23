from google.cloud import bigquery
import pandas as pd

# Load CSV into a DataFrame
df = pd.read_csv("products-1000.csv")

# Transform the DataFrame
# df.dropna(subset=["Price", "Stock"], inplace=True)
df["EAN"] = df["EAN"].astype(str)
df["Index"] = pd.to_numeric(df["Index"], errors="coerce")
df["Internal ID"] = pd.to_numeric(df["Internal ID"], errors="coerce")
df["Price"] = pd.to_numeric(df["Price"], errors="coerce")
df["Stock"] = pd.to_numeric(df["Stock"], errors="coerce")
df["TotalValue"] = df["Price"] * df["Stock"]
df_filtered = df[(df["Availability"] == "in_stock") & (df["Stock"] > 0)]

client = bigquery.Client.from_service_account_json("de-training-d2-dc0eb0f35277.json")
table_id = "de-training-d2.my_dataset.sales_data"

schema = [
    bigquery.SchemaField("Index", "INTEGER"),
    bigquery.SchemaField("Name", "STRING"),
    bigquery.SchemaField("Description", "STRING"),
    bigquery.SchemaField("Brand", "STRING"),
    bigquery.SchemaField("Category", "STRING"),
    bigquery.SchemaField("Price", "FLOAT"),
    bigquery.SchemaField("Currency", "STRING"),
    bigquery.SchemaField("Stock", "INTEGER"),
    bigquery.SchemaField("EAN", "STRING"),
    bigquery.SchemaField("Color", "STRING"),
    bigquery.SchemaField("Size", "STRING"),
    bigquery.SchemaField("Availability", "STRING"),
    bigquery.SchemaField("Internal ID", "INTEGER"),
    bigquery.SchemaField("TotalValue", "FLOAT"),
]

job_config = bigquery.LoadJobConfig(schema=schema, write_disposition="WRITE_TRUNCATE")

job = client.load_table_from_dataframe(df_filtered, table_id, job_config=job_config)
job.result()
print(f"✅ Data loaded into BigQuery table: {table_id}")



