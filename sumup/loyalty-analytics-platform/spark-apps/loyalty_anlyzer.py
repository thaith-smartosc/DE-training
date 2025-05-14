from pyspark.sql import SparkSession
from pyspark.sql.functions import *
from pyspark.sql.types import *
from datetime import datetime
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
    
    return SparkSession.builder \
        .appName("LoyaltyAnalytics") \
        .config("spark.jars", "jars/spark-3.4-bigquery-0.34.1.jar,jars/gcs-connector-hadoop3-latest.jar,jars/spark-sql-kafka-0-10_2.12-3.4.0.jar,jars/kafka-clients-3.4.0.jar") \
        .config("spark.hadoop.fs.gs.impl", "com.google.cloud.hadoop.fs.gcs.GoogleHadoopFileSystem") \
        .config("spark.hadoop.fs.AbstractFileSystem.gs.impl", "com.google.cloud.hadoop.fs.gcs.GoogleHadoopFS") \
        .config("spark.hadoop.google.cloud.auth.service.account.enable", "true") \
        .config("spark.hadoop.google.cloud.auth.service.account.json.keyfile", credentials_path) \
        .config("spark.driver.bindAddress", "127.0.0.1") \
        .config("spark.driver.host", "127.0.0.1") \
        .config("spark.sql.shuffle.partitions", "1") \
        .getOrCreate()

def define_transaction_schema():
    return StructType([
        StructField("transaction_id", StringType(), True),
        StructField("customer_id", StringType(), True),
        StructField("product_id", StringType(), True),
        StructField("transaction_date", TimestampType(), True),
        StructField("quantity", IntegerType(), True),
        StructField("unit_price", DoubleType(), True),
        StructField("discount_applied", DoubleType(), True),
        StructField("payment_method", StringType(), True),
        StructField("store_location", StringType(), True),
        StructField("transaction_hour", IntegerType(), True),
        StructField("day_of_week", IntegerType(), True),
        StructField("week_of_year", IntegerType(), True),
        StructField("month_of_year", IntegerType(), True)
    ])

def calculate_customer_metrics(transactions_df):
    return transactions_df \
        .withColumn("total_amount", col("unit_price") * col("quantity")) \
        .withColumn("net_amount", col("total_amount") - col("discount_applied")) \
        .groupBy("customer_id") \
        .agg(
            count("transaction_id").alias("total_transactions"),
            sum("net_amount").alias("total_sales"),
            avg("net_amount").alias("avg_transaction_value"),
            sum("quantity").alias("total_items_purchased"),
            sum("discount_applied").alias("total_discounts_received"),
            datediff(current_timestamp(), max("transaction_date")).alias("days_since_last_purchase"),
            max("transaction_date").alias("last_transaction_date"),
            approx_count_distinct("product_id").alias("unique_products_purchased")
        )

def identify_vip_customers(customer_metrics_df):
    return customer_metrics_df \
        .filter((col("total_sales") > 10000) | (col("total_transactions") > 50)) \
        .orderBy(desc("total_sales"))

def identify_churn_risk(customer_metrics_df):
    return customer_metrics_df \
        .filter(col("days_since_last_purchase") > 30) \
        .withColumn("churn_risk_score", 
                   when(col("days_since_last_purchase") > 90, "High")
                   .when(col("days_since_last_purchase") > 60, "Medium")
                   .otherwise("Low")) \
        .orderBy(desc("days_since_last_purchase"))

def write_to_bigquery(df, table_name, mode="append"):
    df.write \
        .format("bigquery") \
        .option("table", f"{table_name}") \
        .option("writeMethod", "direct") \
        .mode(mode) \
        .save()

def process_stream(spark):
    # Read from Kafka with watermark for late data handling
    df = spark \
        .readStream \
        .format("kafka") \
        .option("kafka.bootstrap.servers", "localhost:9092") \
        .option("subscribe", "transactions") \
        .option("startingOffsets", "latest") \
        .load()

    # Parse JSON data with schema validation
    raw_transactions = df.select(
        from_json(col("value").cast("string"), define_transaction_schema()).alias("data")
    ).select("data.*") \
    .withWatermark("transaction_date", "1 hour")  # Handle late arriving data

    # Enrich with calculated fields
    transactions = raw_transactions \
        .withColumn("processing_timestamp", current_timestamp()) \
        .withColumn("total_amount", col("unit_price") * col("quantity")) \
        .withColumn("net_amount", col("total_amount") - col("discount_applied")) \
        .withColumn("transaction_date", to_timestamp("transaction_date")) \
        .withColumn("transaction_hour", hour("transaction_date")) \
        .withColumn("day_of_week", dayofweek("transaction_date")) \
        .withColumn("week_of_year", weekofyear("transaction_date")) \
        .withColumn("month_of_year", month("transaction_date"))

    # Process each micro-batch
    def process_batch(batch_df, batch_id):
        # Cache the batch for multiple operations
        batch_df.cache()
        
        # Calculate metrics
        customer_metrics = calculate_customer_metrics(batch_df)
        
        # Business insights
        vip_customers = identify_vip_customers(customer_metrics)
        churn_risk = identify_churn_risk(customer_metrics)
        
        # Write to BigQuery
        write_to_bigquery(batch_df, "de-sumup.store_dataset.transactions")
        write_to_bigquery(customer_metrics, "de-sumup.loyalty_analytics.loyalty_analytics")
        write_to_bigquery(vip_customers, "de-sumup.loyalty_analytics.vip_customers", "overwrite")
        write_to_bigquery(churn_risk, "de-sumup.loyalty_analytics.churn_risk_customers", "overwrite")
        
        # Unpersist the cached data
        batch_df.unpersist()

    # Start the streaming query with checkpointing
    # query = transactions \
    #     .writeStream \
    #     .foreachBatch(process_batch) \
    #     .option("checkpointLocation", "gs://de-sumup-loyalty-data-lake/checkpoints/") \
    #     .outputMode("update") \
    #     .trigger(processingTime="1 minute") \
    #     .start()

    # Debug query to console (optional)
    debug_query = transactions \
        .writeStream \
        .outputMode("append") \
        .format("console") \
        .start()

    # Wait for termination
    # query.awaitTermination()
    debug_query.awaitTermination()

if __name__ == "__main__":
    spark = create_spark_session()
    process_stream(spark)