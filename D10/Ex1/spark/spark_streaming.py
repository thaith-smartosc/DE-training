from pyspark.sql import SparkSession
from pyspark.sql.types import StructType, StructField, StringType, DoubleType
from pyspark.sql.functions import from_json, col, window

BROKER = 'localhost:9094'
TOPIC_NAME = 'sensor-topic'

# Define schema matching your producer's JSON structure
schema = StructType([
    StructField("sensor_id", StringType(), True),
    StructField("temperature", DoubleType(), True),
    StructField("humidity", DoubleType(), True),
    StructField("pressure", DoubleType(), True),
    StructField("pm25", DoubleType(), True),
    StructField("pm10", DoubleType(), True),
    StructField("co2", DoubleType(), True),
    StructField("timestamp", StringType(), True)
])

# Create Spark session
spark = SparkSession.builder.appName("SensorDataStream") \
    .config("spark.jars.packages", "org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.0") \
    .getOrCreate()

# Read the stream from Kafka
df_raw = (
    spark.readStream
        .format("kafka")
        .option("kafka.bootstrap.servers", BROKER)
        .option("subscribe", TOPIC_NAME)
        .load()
)

# Convert JSON in 'value' column to structured columns
df = df_raw.select(
    from_json(col("value").cast("string"), schema).alias("data")
).select("data.*")


# Write results to console
query = (
    df.writeStream \
        .outputMode("append")
        .format("console")
        .option("truncate", False)
        .start()
)

query.awaitTermination()
