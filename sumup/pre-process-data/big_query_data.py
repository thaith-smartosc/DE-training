from pyspark.sql import SparkSession
from pyspark.sql.functions import (
    count, sum, round, datediff, max, min, col, coalesce, when, countDistinct, lit, to_timestamp, current_date
)
import os
from google.cloud import storage

def create_spark_session():
    """Create and configure Spark session"""
    # Set credentials path first
    credentials_path = os.path.abspath("gcp-credentials-key.json")
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = credentials_path
    
    # Verify credentials
    try:
        storage_client = storage.Client()
        buckets = list(storage_client.list_buckets())
        print("GCP credentials verified successfully")
    except Exception as e:
        print(f"GCP credentials error: {e}")
        raise
    
    # Set up spark config
    spark = SparkSession.builder \
        .appName("Loyalty Analytics") \
        .config("spark.jars", "jars/spark-3.4-bigquery-0.34.1.jar,jars/gcs-connector-hadoop3-latest.jar,jars/spark-sql-kafka-0-10_2.12-3.4.0.jar") \
        .config("spark.hadoop.fs.gs.impl", "com.google.cloud.hadoop.fs.gcs.GoogleHadoopFileSystem") \
        .config("spark.hadoop.fs.AbstractFileSystem.gs.impl", "com.google.cloud.hadoop.fs.gcs.GoogleHadoopFS") \
        .config("spark.hadoop.google.cloud.auth.service.account.enable", "true") \
        .config("spark.hadoop.google.cloud.auth.service.account.json.keyfile", credentials_path) \
        .config("spark.driver.memory", "8g") \
        .config("spark.executor.memory", "8g") \
        .config("spark.driver.bindAddress", "127.0.0.1") \
        .config("spark.driver.host", "127.0.0.1") \
        .getOrCreate()
    
    return spark

def read_bigquery_tables(spark):
    """Read data from BigQuery tables"""
    customers_df = spark.read.format("bigquery") \
        .option("parentProject", "de-sumup") \
        .option("table", "de-sumup.store_dataset.customers") \
        .load()
        
    customers_df.show(5, truncate=False)
    customers_df.printSchema()

    transactions_df = spark.read.format("bigquery") \
        .option("table", "de-sumup.store_dataset.transactions") \
        .load()
        
    transactions_df.show(5, truncate=False)
    transactions_df.printSchema()

    return customers_df, transactions_df

def calculate_loyalty_metrics(transactions_df):
    """Calculate loyalty metrics from transactions"""
    
    # 1. Convert transaction_date to timestamp
    transactions_df = transactions_df.withColumn(
        "transaction_date",
        to_timestamp(col("transaction_date"))
    )
    
    # 2. Calculate base metrics with null checks
    customer_metrics = transactions_df.groupBy("customer_id").agg(
        countDistinct("transaction_id").alias("total_transactions"),
        sum("quantity").alias("total_items_purchased"),
        round(
            sum(col("quantity") * col("unit_price") * 
                (lit(1) - coalesce(col("discount_applied"), lit(0)))),
            2
        ).alias("total_purchased"),
        round(
            sum(col("quantity") * col("unit_price") * 
                coalesce(col("discount_applied"), lit(0))),
            2
        ).alias("total_discounts_received"),
        datediff(current_date(), max("transaction_date")).alias("days_since_last_purchase"),
        datediff(max("transaction_date"), min("transaction_date")).alias("days_between_purchases"),
        countDistinct("transaction_date").alias("unique_purchase_days")
    )

    
    # 4. Remove the problematic filter
    final_metrics = customer_metrics.select(
        "customer_id",
        "total_transactions",
        "total_items_purchased",
        "total_purchased",
        "total_discounts_received",
        "days_since_last_purchase"
    )
    
    # 5. Add debug prints
    print(f"Total records after grouping: {customer_metrics.count()}")
    print(f"Total records in final metrics: {final_metrics.count()}")
    
    final_metrics.show(5, truncate=False)
    final_metrics.printSchema()

    return final_metrics

def write_to_bigquery(df, table_name):
    """Write DataFrame to BigQuery"""
    df.write.format("bigquery") \
        .option("table", table_name) \
        .option("temporaryGcsBucket", "de-sumup-loyalty-data-lake") \
        .option("parentProject", "de-sumup") \
        .mode("overwrite") \
        .save()

def main():
    """Main execution function"""
    # Initialize Spark session
    spark = create_spark_session()
    spark.conf.set("temporaryGcsBucket", "de-sumup-loyalty-data-lake")
    
    try:
        # Read data from BigQuery
        customers_df, transactions_df = read_bigquery_tables(spark)

        # Calculate loyalty metrics
        loyalty_metrics = calculate_loyalty_metrics(transactions_df)

        # Write results to BigQuery
        write_to_bigquery(
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