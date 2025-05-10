from pyflink.datastream import StreamExecutionEnvironment
from pyflink.datastream.connectors.kafka import FlinkKafkaConsumer
from pyflink.common.serialization import SimpleStringSchema
from google.cloud import bigquery
import json
import os

# Set up the execution environment
env = StreamExecutionEnvironment.get_execution_environment()

# Correct JAR paths
env.add_jars(
    "file:///opt/flink/usrlib/libs/flink-connector-base-1.17.1.jar",
    "file:///opt/flink/usrlib/libs/flink-connector-kafka-1.17.1.jar",
    "file:///opt/flink/usrlib/libs/kafka-clients-3.2.3.jar",
)

env.add_classpaths(
    "file:///opt/flink/usrlib/libs/flink-connector-base-1.17.1.jar",
    "file:///opt/flink/usrlib/libs/flink-connector-kafka-1.17.1.jar",
    "file:///opt/flink/usrlib/libs/kafka-clients-3.2.3.jar",
)

os.environ["FLINK_HOME"] = "/opt/flink"
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "/opt/flink/usrlib/src/main/resources/gcp_credentials.json"
os.environ["PYFLINK_EXECUTABLE"] = "/usr/bin/python3"
os.environ["PYFLINK_PYTHON"] = "/usr/bin/python3"

# Define Kafka consumer
kafka_consumer = FlinkKafkaConsumer(
    topics='clickstream-topic',
    deserialization_schema=SimpleStringSchema(),
    properties={
        'bootstrap.servers': 'kafka:29092',
        'group.id': 'flink-consumer'
    }
)

# Add source and process stream
stream = env.add_source(kafka_consumer)
parsed_stream = stream.map(lambda x: json.loads(x))

# Process data
def process_data(data):
    return {
        "user_id": data["user_id"],
        "page": data["page"],
        "action": data["action"],
        "count": 1,
        "total_duration": data["duration"],
        "processing_time": data["timestamp"],
        "device": data["device"]
    }
parsed_stream.print()
processed_stream = parsed_stream.map(process_data)

def sink_to_bigquery(row):
    client = bigquery.Client.from_service_account_json(
        '/opt/flink/usrlib/src/main/resources/gcp_credentials.json'
    )

    table_id = f"kestra-thaith.clickstream_dataset.user_activity"

    # Tạo bảng nếu chưa tồn tại
    try:
        client.get_table(table_id)
    except Exception as e:
        print("[BigQuerySink] Table not found, creating new one.")
        schema = [
            bigquery.SchemaField("user_id", "STRING"),
            bigquery.SchemaField("page", "STRING"),
            bigquery.SchemaField("action", "STRING"),
            bigquery.SchemaField("count", "INTEGER"),
            bigquery.SchemaField("total_duration", "FLOAT"),
            bigquery.SchemaField("processing_time", "TIMESTAMP"),
            bigquery.SchemaField("device", "STRING"),
        ]
        table = bigquery.Table(table_id, schema=schema)
        table = client.create_table(table)
        print(f"[BigQuerySink] Table created: {table.full_table_id}")

    # Insert row
    errors = client.insert_rows_json(table_id, [row])
    if errors:
        print(f"[BigQuerySink] Error inserting rows: {errors}")
    return row


# Then use this in your pipeline:
processed_stream.map(sink_to_bigquery)

# Execute the job
env.execute("Clickstream Processing Job")
