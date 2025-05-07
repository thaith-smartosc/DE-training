from kafka import KafkaConsumer
import json
from collections import defaultdict

TOPIC = 'ecommerce_transactions'
GROUP_ID = 'behavior_group'

consumer = KafkaConsumer(
    TOPIC,
    bootstrap_servers=['localhost:9094'],
    group_id=GROUP_ID,
    value_deserializer=lambda m: json.loads(m.decode('utf-8')),
    auto_offset_reset='earliest'
)

spending_by_user = defaultdict(float)

print("Starting consumer for user behavior analysis...")

for message in consumer:
    txn = message.value
    user_id = txn['user_id']
    amount = txn['amount']
    spending_by_user[user_id] += amount

    # Xác định khách hàng giá trị cao tạm thời nếu tiêu > 2000
    if spending_by_user[user_id] > 2000:
        print(f"HIGH VALUE USER! User {user_id}, spending: {spending_by_user[user_id]:.2f}")
