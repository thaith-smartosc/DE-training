from time import sleep
from json import dumps
from kafka import KafkaProducer
import json
import random
from datetime import datetime

# Sample clickstream data generator
def generate_click_event():
    user_ids = ['user1', 'user2', 'user3', 'user4', 'user5']
    pages = ['home', 'products', 'cart', 'checkout', 'confirmation']
    actions = ['click', 'view', 'scroll', 'add_to_cart', 'purchase']
    
    return {
        "user_id": random.choice(user_ids),
        "page": random.choice(pages),
        "action": random.choice(actions),
        "timestamp": datetime.now().isoformat(),
        "duration": random.randint(1, 60),
        "device": random.choice(['mobile', 'desktop', 'tablet'])
    }

# Create producer
producer = KafkaProducer(
    bootstrap_servers=['localhost:9092'],
    value_serializer=lambda x: dumps(x).encode('utf-8')
)

# Send data every second
if __name__ == "__main__":
    print("Starting Kafka producer...")
    while True:
        data = generate_click_event()
        producer.send('clickstream-topic', value=data)
        print(f"Sent: {data}")
        sleep(1)