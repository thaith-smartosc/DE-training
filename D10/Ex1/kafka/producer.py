from kafka import KafkaProducer, KafkaAdminClient
from kafka.admin import NewTopic
from kafka.errors import TopicAlreadyExistsError
import random
import sys
import time
import datetime
import json

TOPIC_NAME = 'sensor-topic'
BROKER = 'localhost:9094'

# Step 1: Check and Create Topic if Not Exist
admin_client = KafkaAdminClient(bootstrap_servers=BROKER, client_id='sensor-producer')

existing_topics = admin_client.list_topics()

if TOPIC_NAME not in existing_topics:
    try:
        topic = NewTopic(name=TOPIC_NAME, num_partitions=4, replication_factor=1)
        admin_client.create_topics([topic])
        print(f"Created topic: {TOPIC_NAME}")
    except TopicAlreadyExistsError:
        print(f"Topic {TOPIC_NAME} already exists.")
else:
    print(f"Topic {TOPIC_NAME} already exists.")

# Step 2: Set up Kafka Producer
producer = KafkaProducer(
    bootstrap_servers=BROKER,
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

print(f"Connected to Kafka broker at {BROKER}")
print(f"Producing messages to topic: {TOPIC_NAME}")

# Step 3: Generate and Send Sensor Data
def generate_sensor_data():
    print("Generating sensor data...")
    return {
        'sensor_id': str(random.randint(1, 10)),
        'temperature': round(random.uniform(25.0, 35.0), 2),
        'humidity': round(random.uniform(30.0, 70.0), 2),
        'pressure': round(random.uniform(950.0, 1050.0), 2),
        'pm25': round(random.uniform(0.0, 100.0), 2),
        'pm10': round(random.uniform(0.0, 100.0), 2),
        'co2': round(random.uniform(400.0, 2000.0), 2),
        'timestamp': datetime.datetime.now().isoformat()
    }

try:
    while True:
        data = generate_sensor_data()
        print(f"Generated data: {data}")
        producer.send(TOPIC_NAME, data)
        print(f"Sent: {data}")
        time.sleep(1)
except KeyboardInterrupt:
    print("Stopping producer...")
finally:
    producer.flush()
    producer.close()
    sys.exit(0)