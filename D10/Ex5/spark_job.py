from pyspark.sql import SparkSession
from pyspark.sql.functions import col, sum as _sum

# Config
PROJECT_ID = "kestra-thaith"
DATASET = "sales_dataset"
TABLE = "sales"
BQ_INPUT = f"{PROJECT_ID}.{DATASET}.{TABLE}"
BQ_OUTPUT = f"{PROJECT_ID}:{DATASET}.sales_summary"
TEMP_GCS_BUCKET = "d5-ex3-bucket"  # thay bằng GCS bucket của bạn

# Tạo Spark session
spark = SparkSession.builder \
    .appName("BigQuery Spark Job - Sales Analysis") \
    .config("spark.jars.packages", "com.google.cloud.spark:spark-bigquery-with-dependencies_2.12:0.32.2") \
    .getOrCreate()

# Đọc dữ liệu từ BigQuery
df = spark.read.format("bigquery") \
    .option("project", PROJECT_ID) \
    .option("table", BQ_INPUT) \
    .load()

# In schema để xác nhận
df.printSchema()

# Phân tích: Tổng doanh thu dự báo và doanh thu trọng số theo Salesperson & Region
summary_df = df.filter(
    (col("Active Opportunity") == True) & 
    (col("Closed Opportunity") == False)
).groupBy("Salesperson", "Region") \
    .agg(
        _sum("Forecasted Monthly Revenue").alias("total_forecasted_revenue"),
        _sum("Weighted Revenue").alias("total_weighted_revenue")
    ).orderBy(col("total_forecasted_revenue").desc())

# Ghi kết quả về BigQuery
summary_df.write \
    .format("bigquery") \
    .option("writeMethod", "direct") \
    .option("table", BQ_OUTPUT) \
    .mode("overwrite") \
    .save()

spark.stop()
