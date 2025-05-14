from google.cloud import bigquery
from google.cloud.exceptions import NotFound
import pandas as pd
import os

# Set the path to your service account key file
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "gcp-credentials-key.json"

# Initialize a BigQuery client
client = bigquery.Client()

project_id = "de-sumup"
dataset_id = "store_dataset"

# Read the CSV file
csv_file_path = "/home/thaith/Downloads/retail_data.csv"
df = pd.read_csv(csv_file_path)

# Display the first few rows of the DataFrame
print("DataFrame head:")
print(df.head())
print("\nDataFrame info:")
print(df.info())
print("\nDataFrame columns:")
print(df.columns)

# Define the table structures as dictionaries
tables = {
    "customers": [
        "customer_id",  # Primary Key
        "age",
        "gender",
        "income_bracket",
        "loyalty_program",
        "membership_years",
        "churned",
        "customer_zip_code",
        "customer_city",
        "customer_state",
    ],
    
    "transactions": [
        "transaction_id",  # Primary Key
        "customer_id",     # Foreign Key
        "product_id",      # Foreign Key
        "transaction_date",
        "quantity",
        "unit_price",
        "discount_applied",
        "payment_method",
        "store_location",
        "transaction_hour",
        "day_of_week",
        "week_of_year",
        "month_of_year"
    ],
}

# Function to create BigQuery table creation SQL
def generate_bigquery_schema(tables):
    for table_name, columns in tables.items():
        print(f"\n-- Table: {table_name}")

        table_id = f"{project_id}.{dataset_id}.{table_name}"
        table_df = df[columns].copy()
        
        table_schema = []

        for column in columns:
            data_type = "STRING"
            if "id" in column or "number" in column:
                data_type = "INT64"
            elif "date" in column:
                data_type = "DATETIME"
            elif column in ["unit_price", "discount_applied", "distance_to_store"]:
                data_type = "FLOAT64"

            table_schema.append(bigquery.SchemaField(column, data_type))
            
        # Check if the table exists
        try:
            client.get_table(table_id)
            print(f"Table {table_id} already exists.")
        except NotFound:
            print(f"Table {table_id} does not exist. Creating table...")
            # Create the table if it does not exist
            table = bigquery.Table(table_id, schema=table_schema)
            table = client.create_table(table)
            print(f"Created table {table_id}")
            
        # Load data into the table
        try:
            job = client.load_table_from_dataframe(
                dataframe=table_df,
                destination=table_id,
                job_config=bigquery.LoadJobConfig(
                    write_disposition=bigquery.WriteDisposition.WRITE_TRUNCATE,
                )
            )
            job.result()  # Wait for the job to complete
            print(f"Loaded {job.output_rows} rows into {table_id}.")
        except NotFound:
            print(f"Table {table_id} not found. Creating table...")
        
# Generate the SQL and create tables
generate_bigquery_schema(tables)