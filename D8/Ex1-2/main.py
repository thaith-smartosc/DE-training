from pyspark.sql import SparkSession
from pyspark.sql.functions import col, sum, avg

def main():
    # Step 1: Initialize SparkSession
    spark = SparkSession.builder.appName("SalesData Analysis").getOrCreate()

    # Step 2: Load CSV file with header and inferSchema
    file_path = "SalesData.csv"
    df = spark.read.csv(file_path, header=True, inferSchema=True)

    # Step 3: Print schema and preview data
    print("📊 Original Data:")
    df.printSchema()
    df.show(truncate=False)

    # Step 4: Filter rows where Forecasted Monthly Revenue > 100000
    filtered_df = df.filter(col("Forecasted Monthly Revenue") > 100000)

    print("✅ Filtered Data (Forecasted Revenue > 100000):")
    filtered_df.show(truncate=False)

    # Step 5: Group by Region and Opportunity Stage, then aggregate
    grouped_df = filtered_df.groupBy("Region", "Opportunity Stage").agg(
        sum("Weighted Revenue").alias("Total Weighted Revenue"),
        avg("Weighted Revenue").alias("Average Weighted Revenue")
    )

    print("📈 Grouped and Aggregated Results:")
    grouped_df.show(truncate=False)

    # Optional: Save output to CSV
    grouped_df.coalesce(1).write.csv("output/grouped_sales", header=True, mode="overwrite")

    # Step 6: Stop SparkSession
    spark.stop()

if __name__ == "__main__":
    main()
