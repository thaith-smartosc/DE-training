from flask import Flask, request, jsonify
from google.cloud import storage, bigquery
import pandas as pd
from io import StringIO

# Initialize Flask app and Google Cloud clients
app = Flask(__name__)
storage_client = storage.Client()
bigquery_client = bigquery.Client()

# Set the name of your Google Cloud Storage bucket
bucket_name = 'd5-ex3-bucket'
bigquery_dataset_name = 'd5ex3dataset'
bigquery_table_name = 'sale'

# Function to upload CSV to Google Cloud Storage
def upload_file_to_gcs(file, destination_blob_name):
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(destination_blob_name)
    blob.upload_from_file(file)
    return f"gs://{bucket_name}/{destination_blob_name}"

# Function to read CSV from Google Cloud Storage
def read_csv_from_gcs(file_uri):
    bucket_name, file_name = file_uri.replace("gs://", "").split("/", 1)
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(file_name)
    data = blob.download_as_text()
    
    # Read CSV, treating the first row as headers
    df = pd.read_csv(StringIO(data), parse_dates=['Date'], header=0)

    # Handle case where columns may contain extra spaces
    df.columns = df.columns.str.strip()
    
    return df


# Function to transform the data (Calculate monthly revenue and filter out low-performing months)
def transform_data(df):
    # Ensure 'Date' is datetime
    df['Date'] = pd.to_datetime(df['Date'], errors='coerce')

    # Ensure 'Weighted Revenue' is a numeric type
    df['Weighted Revenue'] = pd.to_numeric(df['Weighted Revenue'], errors='coerce')

    # Drop rows where 'Weighted Revenue' is NaN (if necessary)
    df = df.dropna(subset=['Weighted Revenue'])

    # Calculate monthly revenue from 'Weighted Revenue'
    df['month'] = df['Date'].dt.to_period('M')
    monthly_revenue = df.groupby('month')['Weighted Revenue'].sum().reset_index()

    # Filter low-performing months (e.g., revenue below 10,000)
    threshold = 10000
    filtered_data = monthly_revenue[monthly_revenue['Weighted Revenue'] >= threshold]

    return filtered_data


# Function to load transformed data into BigQuery
def load_data_to_bigquery(dataframe):
    # Specify the table schema (adjust based on your table structure)
    schema = [
        bigquery.SchemaField("month", "STRING"),
        bigquery.SchemaField("Weighted Revenue", "FLOAT"),
    ]

    # Load the data into BigQuery
    table_ref = bigquery_client.dataset(bigquery_dataset_name).table(bigquery_table_name)
    job_config = bigquery.LoadJobConfig(schema=schema, write_disposition=bigquery.WriteDisposition.WRITE_APPEND, source_format=bigquery.SourceFormat.CSV)
    job_config.max_bad_records = 1
    
    # Convert the pandas dataframe to CSV and upload it to BigQuery
    csv_data = dataframe.to_csv(index=False)
    
    print("Uploading data to BigQuery...", csv_data)
    job = bigquery_client.load_table_from_file(
        StringIO(csv_data), table_ref, job_config=job_config
    )
    job.result()  # Wait for the job to complete

    print("Data uploaded to BigQuery")

# POST endpoint to upload a file
@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    # Upload the CSV file to GCS
    destination_blob_name = f"uploaded_files/{file.filename}"
    file_uri = upload_file_to_gcs(file, destination_blob_name)
    
    return jsonify({"message": "File uploaded successfully!", "file_uri": file_uri}), 200

# GET endpoint to trigger ETL process
@app.route('/etl', methods=['GET'])
def etl_process():
    # Get the file URI from GCS (it can be passed dynamically in the request, or use a fixed filename for simplicity)
    file_uri = f"gs://d5-ex3-bucket/uploaded_files/SalesData.csv"
    
    # Step 1: Extract - Read data from CSV file in GCS
    try:
        df = read_csv_from_gcs(file_uri)
    except Exception as e:
        return jsonify({"error": f"Error reading CSV from GCS: {str(e)}"}), 500
    
    # Step 2: Transform - Process data to calculate monthly revenue and filter low-performing months
    try:
        transformed_data = transform_data(df)
    except Exception as e:
        return jsonify({"error": f"Error transforming data: {str(e)}"}), 500
    
    # Step 3: Load - Upload the transformed data to BigQuery
    try:
        load_data_to_bigquery(transformed_data)
    except Exception as e:
        return jsonify({"error": f"Error uploading data to BigQuery: {str(e)}"}), 500
    
    return jsonify({"message": "ETL process completed successfully!"}), 200

if __name__ == '__main__':
    # Make sure to set the GOOGLE_APPLICATION_CREDENTIALS environment variable
    # to your service account key file.
    app.run(debug=True, host="0.0.0.0", port=5000)
