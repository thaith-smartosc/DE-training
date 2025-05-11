from confluent_kafka import avro
from confluent_kafka.avro import AvroProducer
import requests
import json

def load_avro_schema_from_file(schema_file):
    with open(schema_file, 'r') as f:
        return avro.loads(f.read())

def check_compatibility(schema_file, subject):
    with open(schema_file, 'r') as f:
        schema_str = f.read()
    
    url = f"http://localhost:8081/compatibility/subjects/{subject}/versions/latest"
    headers = {'Content-Type': 'application/vnd.schemaregistry.v1+json'}
    data = json.dumps({"schema": schema_str})
    
    response = requests.post(url, headers=headers, data=data)
    return response.json()

def get_avro_producer(schema_file):
    value_schema = load_avro_schema_from_file(schema_file)
    
    producer_config = {
        'bootstrap.servers': 'localhost:9092',
        'schema.registry.url': 'http://localhost:8081'
    }
    
    return AvroProducer(producer_config, 
                        default_value_schema=value_schema)

if __name__ == "__main__":
    # Check compatibility of evolved schema
    subject = "users-value"
    schema_file_v2 = "schemas/user_v2.avsc"
    
    print("Checking schema compatibility...")
    compatibility = check_compatibility(schema_file_v2, subject)
    print(f"Compatibility check result: {compatibility}")
    
    if compatibility.get('is_compatible', False):
        print("New schema is compatible. Creating producer with evolved schema.")
        
        # Create producer with evolved schema
        producer = get_avro_producer(schema_file_v2)
        
        # Send record with new field
        user_with_age = {
            "id": 3,
            "name": "Bob Johnson",
            "email": "bob.johnson@example.com",
            "age": 25
        }
        
        producer.produce(topic='users', value=user_with_age)
        producer.flush()
        print(f"Sent record with evolved schema: {user_with_age}")
    else:
        print("New schema is not compatible with existing schema.")
