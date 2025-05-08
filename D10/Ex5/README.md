
# Spark Job for BigQuery Integration

This Spark job is designed to integrate with Google BigQuery, allowing for large-scale data processing and analysis using Apache Spark.

## Overview

The job performs the following steps:
1. **Extracts Data from BigQuery**: Retrieves data from a specified BigQuery table.
2. **Processes Data using Spark**: Applies complex data transformations and aggregations.
3. **Writes Results to BigQuery**: Saves the processed results back into BigQuery in an optimized format.
4. **Generates Reports**: Outputs results that can be used for business decision-making.

## Prerequisites

- **Python**: Ensure Python 3.x is installed.
- **PySpark**: Install PySpark for distributed data processing.
- **Google Cloud SDK**: Install and configure it to authenticate with BigQuery.
- **BigQuery Connector**: Download the `spark-bigquery-connector` jar.

## Setup

1. **Install Dependencies**:
   ```bash
   pip install pyspark google-cloud-bigquery
   ```

2. **Set Google Cloud Credentials**:
   - Download the service account key JSON file.
   - Set the `GOOGLE_APPLICATION_CREDENTIALS` environment variable:
     ```bash
     export GOOGLE_APPLICATION_CREDENTIALS="/path/to/your/service-account-file.json"
     ```

3. **Download BigQuery Connector**:
   - Obtain the jar from [Google Cloud's GitHub releases](https://github.com/GoogleCloudDataproc/spark-bigquery-connector/releases).

## Running the Job

1. **Configure and Run the Spark Job**:
   - Modify `spark_job.py` to point to the correct BigQuery table and dataset.
   - Run the job using `spark-submit`:
     ```bash
     spark-submit --jars /path/to/spark-bigquery-latest.jar spark_job.py
     ```

## How It Works

- **Data Extraction**: Uses the BigQuery connector to load data into a Spark DataFrame.
- **Data Processing**: Performs transformations such as aggregations and joins using Spark's DataFrame API.
- **Data Loading**: Writes the processed data back to BigQuery using an efficient format to optimize query performance.

## Troubleshooting

- Ensure that your environment variables are correctly set.
- Verify that the versions of Spark and the connector are compatible.
- Check network settings and permissions if you encounter connectivity issues.
