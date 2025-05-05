from google.cloud import bigquery

# Initialize BigQuery client
client = bigquery.Client()

# Define your variables
project_id = "kestra-thaith"
dataset_id = "sales_dataset"
table_id = "sales"
uri = "gs://data-bucket-050525/sample-data/SalesData.csv"

# Define the full table ID
full_table_id = f"{project_id}.{dataset_id}.{table_id}"

job_config = bigquery.LoadJobConfig(
    source_format=bigquery.SourceFormat.CSV,
    skip_leading_rows=1,
    autodetect=True,
)

load_job = client.load_table_from_uri(
    uri, full_table_id, job_config=job_config
)

load_job.result()

print(f"Loaded {load_job.output_rows} rows into {full_table_id}.")
