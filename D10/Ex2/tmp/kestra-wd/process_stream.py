from pyspark.sql import SparkSession
from pyspark.sql.functions import col, from_json
from pyspark.sql.types import StructType, StringType, LongType

# Tham số dòng lệnh
import argparse
parser = argparse.ArgumentParser()
parser.add_argument("--kafka-brokers", required=True)
parser.add_argument("--topic", required=True)
parser.add_argument("--output", required=True)
args = parser.parse_args()

# Schema cho dữ liệu trong Kafka message
schema = StructType() \
    .add("user_id", StringType()) \
    .add("action", StringType()) \
    .add("timestamp", LongType())

spark = SparkSession.builder.appName("KafkaToCSV").getOrCreate()

# Đọc dữ liệu từ Kafka
df = (
    spark.read.format("kafka")
    .option("kafka.bootstrap.servers", args.kafka_brokers)
    .option("subscribe", args.topic)
    .option("startingOffsets", "earliest") # batch, nên đọc từ đầu
    .load()
)

# Parse value (giả sử dữ liệu là JSON)
df_parsed = df.select(
    from_json(col("value").cast("string"), schema).alias("json")
).select("json.*")

# Đổi tên trường cho khớp Postgres table (vd: ts thay cho timestamp)
df_ready = (
    df_parsed
    .withColumnRenamed("timestamp", "ts")
    .select("user_id", "action", "ts")
)

# Lưu ra CSV
df_ready.coalesce(1).write.csv(args.output, header=True, mode="overwrite")

spark.stop()
