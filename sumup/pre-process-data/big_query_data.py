from pyspark.sql import SparkSession
from pyspark.sql.functions import *
from pyspark.sql.types import *
from datetime import datetime
import os
from google.cloud import storage
from google.cloud import bigquery
from google.cloud.exceptions import NotFound

def create_spark_session():
    """Create and configure Spark session"""
    # Set credentials path first
    credentials_path = os.path.abspath("gcp-credentials-key.json")
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = credentials_path
    
    try:
        storage_client = storage.Client()
        buckets = list(storage_client.list_buckets())
        print("GCP credentials verified successfully")
    except Exception as e:
        print(f"GCP credentials error: {e}")
        raise
    
    return SparkSession.builder \
        .appName("LoyaltyAnalytics") \
        .config("spark.jars", """
                jars/spark-3.4-bigquery-0.34.1.jar,
                jars/gcs-connector-hadoop3-latest.jar
                """) \
        .config("spark.hadoop.fs.gs.impl", "com.google.cloud.hadoop.fs.gcs.GoogleHadoopFileSystem") \
        .config("spark.hadoop.fs.AbstractFileSystem.gs.impl", "com.google.cloud.hadoop.fs.gcs.GoogleHadoopFS") \
        .config("spark.hadoop.google.cloud.auth.service.account.enable", "true") \
        .config("spark.hadoop.google.cloud.auth.service.account.json.keyfile", credentials_path) \
        .config("spark.driver.memory", "8g") \
        .config("spark.executor.memory", "8g") \
        .config("spark.driver.bindAddress", "127.0.0.1") \
        .config("spark.driver.host", "127.0.0.1") \
        .getOrCreate()

def read_bigquery_tables(spark):
    """Read data from BigQuery tables"""
    customers_df = spark.read.format("bigquery") \
        .option("parentProject", "de-sumup") \
        .option("table", "de-sumup.store_dataset.customers") \
        .load()
        
    transactions_df = spark.read.format("bigquery") \
        .option("table", "de-sumup.store_dataset.transactions") \
        .load()
    
    # Convert transaction_date to timestamp
    transactions_df = transactions_df.withColumn(
        "transaction_date",
        to_timestamp(col("transaction_date"))
    )
    
    return customers_df, transactions_df

def calculate_customer_metrics(transactions_df):
    """Calculate customer metrics from transactions"""
    customer_metric = transactions_df \
        .withColumn("total_amount", col("unit_price") * col("quantity").cast("double")) \
        .withColumn("net_amount", 
                   when(col("discount_applied").isNotNull(),
                       col("total_amount") * (lit(1) - col("discount_applied")))
                   .otherwise(col("total_amount"))) \
        .groupBy("customer_id") \
        .agg(
            count("transaction_id").cast("long").alias("total_transactions"),
            sum("net_amount").cast("double").alias("total_purchased"),
            sum("quantity").cast("long").alias("total_items_purchased"),
            sum(col("total_amount") * col("discount_applied")).cast("double").alias("total_discounts_received"),
            datediff(current_timestamp(), max("transaction_date")).cast("long").alias("days_since_last_purchase"),
            max("transaction_date").alias("last_update_time")
        )
    
    return customer_metric.select(
        "customer_id",
        "total_transactions",
        "total_purchased",
        "total_items_purchased",
        "total_discounts_received",
        "days_since_last_purchase",
        "last_update_time"
    )

def ensure_table_exists(client, table_name):
    """Ensure the BigQuery table exists with the correct schema"""
    schema = [
        bigquery.SchemaField("customer_id", "INTEGER", mode="REQUIRED"),
        bigquery.SchemaField("total_transactions", "INTEGER"),
        bigquery.SchemaField("total_purchased", "FLOAT"),
        bigquery.SchemaField("total_items_purchased", "INTEGER"),
        bigquery.SchemaField("total_discounts_received", "FLOAT"),
        bigquery.SchemaField("days_since_last_purchase", "INTEGER"),
        bigquery.SchemaField("last_update_time", "TIMESTAMP")
    ]
    
    try:
        client.get_table(table_name)
        print(f"Table {table_name} already exists")
    except NotFound:
        table = bigquery.Table(table_name, schema=schema)
        table.clustering_fields = ["customer_id"]
        table.time_partitioning = bigquery.TimePartitioning(
            type_=bigquery.TimePartitioningType.DAY,
            field="last_update_time"
        )
        client.create_table(table)
        print(f"Created table {table_name}")

def update_to_bigquery(df, table_name):
    """Update BigQuery table with new metrics using MERGE operation"""
    if df.isEmpty():
        print(f"DataFrame is empty, skipping write to {table_name}")
        return
    
    try:
        client = bigquery.Client()
        ensure_table_exists(client, table_name)
        
        # Write to temporary table
        df.write \
            .format("bigquery") \
            .option("table", table_name) \
            .option("writeMethod", "direct") \
            .option("createDisposition", "CREATE_IF_NEEDED") \
            .mode("overwrite") \
            .save()
            
    except Exception as e:
        print(f"Error in update_to_bigquery: {str(e)}")
        raise

def main():
    """Main execution function"""
    spark = create_spark_session()
    
    try:
        # Read data from BigQuery
        customers_df, transactions_df = read_bigquery_tables(spark)

        # Calculate loyalty metrics
        loyalty_metrics = calculate_customer_metrics(transactions_df)

        # Update results to BigQuery
        update_to_bigquery(
            loyalty_metrics, 
            "de-sumup.loyalty_analytics.loyalty_analytics"
        )

        print("Loyalty analytics processing completed successfully!")

    except Exception as e:
        print(f"Error processing loyalty analytics: {str(e)}")
        raise
    finally:
        spark.stop()

if __name__ == "__main__":
    main()
