from kafka import KafkaProducer
from faker import Faker
import json
import time
import random

TOPIC = 'ecommerce_transactions'
producer = KafkaProducer(
    bootstrap_servers=['localhost:9094'],
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

fake = Faker()

def generate_transaction():
    return {
        'user_id': fake.random_int(min=1, max=100),
        'product_id': fake.random_int(min=1, max=20),
        'amount': round(random.uniform(1, 1000), 2),
        'timestamp': int(time.time())
    }

if __name__ == '__main__':
    while True:
        txn = generate_transaction()
        producer.send(TOPIC, txn)
        print("Produced:", txn)
        time.sleep(1)
