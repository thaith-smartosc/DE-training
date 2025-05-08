import json
import time
import random
from kafka import KafkaProducer

# Kết nối tới Kafka broker
producer = KafkaProducer(
    bootstrap_servers='kafka:9092',    # dùng 'kafka:9092' nếu chạy bên trong container!
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

actions = ['login', 'logout', 'click', 'view']

for i in range(20):
    data = {
        'user_id': f'user_{random.randint(1, 5)}',
        'action': random.choice(actions),
        'timestamp': int(time.time())
    }
    producer.send('user-activity', value=data)
    print(f"Sent: {data}")
    time.sleep(1)

producer.flush()
producer.close()
