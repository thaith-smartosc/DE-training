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
        "marital_status",
        "number_of_children",
        "education_level",
        "occupation",
        "customer_zip_code",
        "customer_city",
        "customer_state",
    ],
    
    "customer_behavior": [
        "customer_id",  # Foreign Key
        "purchase_frequency",
        "avg_purchase_value",
        "online_purchases",
        "in_store_purchases",
        "total_returned_items",
        "total_returned_value",
        "total_sales",
        "total_transactions",
        "total_items_purchased",
        "total_discounts_received",
        "customer_support_calls",
        "email_subscriptions",
        "app_usage",
        "website_visits",
        "social_media_engagement",
        "days_since_last_purchase"
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
        "month_of_year",
        "avg_items_per_transaction",
        "avg_transaction_value"
    ],
    
    "products": [
        "product_id",      # Primary Key
        "product_name",
        "product_category",
        "product_brand",
        "product_rating",
        "product_review_count",
        "product_stock",
        "product_return_rate",
        "product_size",
        "product_weight",
        "product_color",
        "product_material",
        "product_manufacture_date",
        "product_expiry_date",
        "product_shelf_life"
    ],
    
    "promotions": [
        "promotion_id",    # Primary Key
        "promotion_type",
        "promotion_start_date",
        "promotion_end_date",
        "promotion_effectiveness",
        "promotion_channel",
        "promotion_target_audience"
    ],
    
    "stores": [
        "store_location",  # Primary Key
        "store_zip_code",
        "store_city",
        "store_state",
        "distance_to_store"
    ],
    
    "time_dimensions": [
        "transaction_date", # Primary Key
        "holiday_season",
        "season",
        "weekend"
    ]
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