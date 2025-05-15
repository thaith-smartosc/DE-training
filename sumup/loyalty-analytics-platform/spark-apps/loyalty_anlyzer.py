from pyspark.sql import SparkSession
from pyspark.sql.functions import *
from pyspark.sql.types import *
from datetime import datetime
import os
from google.cloud import storage
from google.cloud.exceptions import NotFound
from google.cloud import bigquery

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
        .config("spark.jars",  """
                jars/spark-3.4-bigquery-0.34.1.jar,
                jars/gcs-connector-hadoop3-latest.jar,
                jars/spark-sql-kafka-0-10_2.12-3.4.0.jar,
                jars/kafka-clients-3.4.0.jar,
                jars/spark-token-provider-kafka-0-10_2.12-3.4.0.jar,
                jars/commons-pool2-2.11.1.jar
                """) \
        .config("spark.hadoop.fs.gs.impl", "com.google.cloud.hadoop.fs.gcs.GoogleHadoopFileSystem") \
        .config("spark.hadoop.fs.AbstractFileSystem.gs.impl", "com.google.cloud.hadoop.fs.gcs.GoogleHadoopFS") \
        .config("spark.hadoop.google.cloud.auth.service.account.enable", "true") \
        .config("spark.hadoop.google.cloud.auth.service.account.json.keyfile", credentials_path) \
        .config("spark.driver.bindAddress", "127.0.0.1") \
        .config("spark.driver.host", "127.0.0.1") \
        .config("spark.sql.shuffle.partitions", "4") \
        .getOrCreate()

def define_transaction_schema():
    return StructType([
        StructField("transaction_id", IntegerType(), True),
        StructField("customer_id", IntegerType(), False),
        StructField("product_id", IntegerType(), True),
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
    customer_metric = transactions_df \
        .withColumn("total_amount", col("unit_price") * col("quantity").cast("double")) \
        .withColumn("net_amount", col("total_amount") - col("discount_applied")) \
        .groupBy("customer_id") \
        .agg(
            count("transaction_id").cast("long").alias("total_transactions"),
            sum("net_amount").cast("double").alias("total_purchased"),
            avg("net_amount").cast("double").alias("avg_transaction_value"),
            sum("quantity").cast("long").alias("total_items_purchased"),
            sum("discount_applied").cast("double").alias("total_discounts_received"),
            datediff(current_timestamp(), max("transaction_date")).cast("long").alias("days_since_last_purchase"),
            max("transaction_date").alias("last_update_time")  # Add timestamp for partitioning
        )
    # Ensure all columns have correct types
    return customer_metric.select(
        col("customer_id").cast("integer"),
        col("total_transactions").cast("integer"),
        col("total_purchased").cast("float"),
        col("total_items_purchased").cast("integer"),
        col("total_discounts_received").cast("float"),
        col("days_since_last_purchase").cast("integer"),
        col("last_update_time").cast("timestamp")
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
        # Check if table exists
        client.get_table(table_name)
        print(f"Table {table_name} already exists")
    except NotFound:
        # Create table if it doesn't exist
        table = bigquery.Table(table_name, schema=schema)
        # Add clustering by customer_id for better query performance
        table.clustering_fields = ["customer_id"]
        # Add time partition
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
    
    print(f"\nUpdating table: {table_name}")

    try:
        # Create BigQuery client
        client = bigquery.Client()
        
        # Ensure destination table exists
        ensure_table_exists(client, table_name)
        
        # Create temporary table name
        temp_table = f"{table_name}_temp_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Write the new metrics to temporary table
        df.write \
            .format("bigquery") \
            .option("table", temp_table) \
            .option("writeMethod", "direct") \
            .option("createDisposition", "CREATE_IF_NEEDED") \
            .mode("overwrite") \
            .save()
        
        # Perform MERGE operation with explicit column types
        merge_query = f"""
            MERGE INTO `{table_name}` T
            USING (
                SELECT 
                    CAST(customer_id AS INT64) as customer_id,
                    CAST(total_transactions AS INT64) as total_transactions,
                    CAST(total_purchased AS FLOAT64) as total_purchased,
                    CAST(total_items_purchased AS INT64) as total_items_purchased,
                    CAST(total_discounts_received AS FLOAT64) as total_discounts_received,
                    CAST(days_since_last_purchase AS INT64) as days_since_last_purchase,
                    CAST(last_update_time AS TIMESTAMP) as last_update_time
                FROM `{temp_table}`
            ) S
            ON T.customer_id = S.customer_id
            WHEN MATCHED THEN
                UPDATE SET
                    total_transactions = S.total_transactions + T.total_transactions,
                    total_purchased = S.total_purchased + T.total_purchased,
                    total_items_purchased = S.total_items_purchased + T.total_items_purchased,
                    total_discounts_received = S.total_discounts_received + T.total_discounts_received,
                    days_since_last_purchase = S.days_since_last_purchase,
                    last_update_time = S.last_update_time
            WHEN NOT MATCHED THEN
                INSERT (
                    customer_id,
                    total_transactions,
                    total_purchased,
                    total_items_purchased,
                    total_discounts_received,
                    days_since_last_purchase,
                    last_update_time
                )
                VALUES (
                    S.customer_id,
                    S.total_transactions,
                    S.total_purchased,
                    S.total_items_purchased,
                    S.total_discounts_received,
                    S.days_since_last_purchase,
                    S.last_update_time
                )
        """
        
        # Execute MERGE query with error handling
        try:
            job = client.query(merge_query)
            job.result()  # Wait for the query to complete
            print(f"Successfully merged data into {table_name}")
            
        except Exception as e:
            print(f"Error during MERGE operation: {str(e)}")
            raise
            
        finally:
            # Clean up temporary table
            try:
                client.delete_table(temp_table, not_found_ok=True)
                print(f"Cleaned up temporary table {temp_table}")
            except Exception as e:
                print(f"Warning: Could not delete temporary table: {str(e)}")
                
    except Exception as e:
        print(f"Error in update_to_bigquery: {str(e)}")
        raise
        

def write_to_bigquery(df, table_name, mode="append"):
    if df.isEmpty():
        print(f"DataFrame is empty, skipping write to {table_name}")
        return
    
    # Debug: Print schema before writing
    print(f"\nWriting to table: {table_name}")
    
    # Write DataFrame to BigQuery
    df.write \
        .format("bigquery") \
        .option("table", table_name) \
        .option("writeMethod", "direct") \
        .option("createDisposition", "CREATE_IF_NEEDED") \
        .option("partitionField", "last_update_time") \
        .option("partitionType", "DAY") \
        .mode(mode) \
        .save()

def process_stream(spark):
    # Read from Kafka with watermark for late data handling
    df = spark \
        .readStream \
        .format("kafka") \
        .option("kafka.bootstrap.servers", "localhost:9092") \
        .option("subscribe", "raw_1_transactions") \
        .option("startingOffsets", "latest") \
        .load()

    # Parse JSON data with schema validation
    raw_transactions = df.select(
        from_json(col("value").cast("string"), define_transaction_schema()).alias("data")
    ).select("data.*")

    # Process each micro-batch
    def process_batch(batch_df, batch_id):
        try:
            if batch_df.isEmpty():
                print("Empty batch, skipping...")
                return
                
            # Add processing timestamp
            batch_df = batch_df.withColumn("processing_time", current_timestamp())
            
            # Cache the batch for multiple operations
            batch_df.cache()
            
            # Calculate metrics
            customer_metrics = calculate_customer_metrics(batch_df)
            
            batch_df.show(5, truncate=False)
            
            # Write to BigQuery
            write_to_bigquery(batch_df, "de-sumup.loyalty_analytics.stream_transactions")
            update_to_bigquery(customer_metrics, "de-sumup.loyalty_analytics.loyalty_analytics")
            
            # Unpersist the cached data
            batch_df.unpersist()
        except Exception as e:
            print(f"Error processing batch {batch_id}: {str(e)}")
            raise

    # Start the streaming query with checkpointing
    query = raw_transactions \
        .writeStream \
        .foreachBatch(process_batch) \
        .option("checkpointLocation", "gs://de-sumup-loyalty-data-lake/checkpoints/") \
        .outputMode("update") \
        .trigger(processingTime="1 minute") \
        .start()

    # Debug query to console (optional)
    debug_query = raw_transactions \
        .writeStream \
        .outputMode("append") \
        .format("console") \
        .start()

    # Wait for termination
    query.awaitTermination()
    debug_query.awaitTermination()

if __name__ == "__main__":
    spark = create_spark_session()
    process_stream(spark)