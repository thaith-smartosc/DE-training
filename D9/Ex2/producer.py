from kafka import KafkaProducer
import random
import time
import json

producer = KafkaProducer(
    bootstrap_servers='localhost:9094',
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

def generate_sensor_data():
    return {
        'sensor_id': str(random.randint(1, 10)),
        'value': random.uniform(20.0, 100.0)
    }

while True:
    data = generate_sensor_data()
    producer.send('sensor-data', data)
    print(f"Sent: {data}")
    time.sleep(10)
