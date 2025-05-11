from confluent_kafka import avro
from confluent_kafka.avro import AvroProducer
import json

# Load schema from file
def load_avro_schema_from_file(schema_file):
    with open(schema_file, 'r') as f:
        return avro.loads(f.read())

# Configure Avro producer
def get_avro_producer(schema_file):
    value_schema = load_avro_schema_from_file(schema_file)
    
    producer_config = {
        'bootstrap.servers': 'localhost:9092',
        'schema.registry.url': 'http://localhost:8081'
    }
    
    return AvroProducer(producer_config, 
                        default_value_schema=value_schema)

def send_record(producer, topic, record):
    producer.produce(topic=topic, value=record)
    producer.flush()
    print(f"Sent record to topic '{topic}': {record}")

if __name__ == "__main__":
    # Use the initial schema
    schema_file = 'schemas/user_v1.avsc'
    producer = get_avro_producer(schema_file)
    
    # Create and send a user record
    user = {
        "id": 1,
        "name": "John Doe",
        "email": "john.doe@example.com"
    }
    
    topic = 'users'
    send_record(producer, topic, user)
    
    # Send another record
    user2 = {
        "id": 2,
        "name": "Jane Smith",
        "email": "jane.smith@example.com"
    }
    
    send_record(producer, topic, user2)
