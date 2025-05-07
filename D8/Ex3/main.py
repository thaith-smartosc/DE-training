from pyspark.sql import SparkSession
from pyspark.sql.functions import col, sum, month, year, to_date, desc, row_number
from pyspark.sql.window import Window

def main():
    spark = SparkSession.builder.appName("SalesAnalysis").getOrCreate()

    sales_df = spark.read.option("header", True).csv("sales.csv", inferSchema=True)
    products_df = spark.read.option("header", True).csv("products.csv", inferSchema=True)
    stores_df = spark.read.option("header", True).csv("stores.csv", inferSchema=True)

    sales_joined = sales_df \
        .join(products_df, on="product_id", how="left") \
        .join(stores_df, on="store_id", how="left")

    # --- 1. Top 10 sản phẩm bán chạy theo vùng ---
    product_sales_by_region = sales_joined.groupBy("region", "product_id", "product_name").agg(sum("quantity").alias("total_quantity"))

    window_spec = Window.partitionBy("region").orderBy(desc("total_quantity"))
    top_10_products = product_sales_by_region.withColumn("rank", row_number().over(window_spec)).filter(col("rank") <= 10)
    top_10_products.write.mode("overwrite").parquet("output/top_10_products_by_region.parquet")
    
    # --- print top_10_products.show() ---
    print("Top 10 sản phẩm bán chạy theo vùng:")
    top_10_products.show()

    # --- 2. Phân tích doanh thu theo tháng và danh mục ---
    sales_with_date = sales_joined.withColumn("month", month(to_date("date"))).withColumn("year", year(to_date("date")))

    monthly_revenue_trend = sales_with_date.groupBy("year", "month", "category").agg(sum("revenue").alias("total_revenue")).orderBy("year", "month", "category")

    monthly_revenue_trend.write.mode("overwrite").parquet("output/monthly_revenue_trend.parquet")
    
    # --- print monthly_revenue_trend.show() ---
    print("Doanh thu theo tháng và danh mục:")
    monthly_revenue_trend.show()

    # --- 3. Cửa hàng hiệu suất cao và thấp ---
    store_performance = sales_joined.groupBy("store_id", "store_name", "region").agg(sum("revenue").alias("total_revenue"))

    top_store = store_performance.orderBy(desc("total_revenue")).limit(1)
    low_store = store_performance.orderBy("total_revenue").limit(1)

    top_store.write.mode("overwrite").parquet("output/top_store.parquet")
    low_store.write.mode("overwrite").parquet("output/low_store.parquet")
    
    # --- print top_store.show() ---
    print("Cửa hàng hiệu suất cao:")
    top_store.show()
    # --- print low_store.show() ---
    print("Cửa hàng hiệu suất thấp:")
    low_store.show()

    # spark.stop()

if __name__ == "__main__":
    main()
