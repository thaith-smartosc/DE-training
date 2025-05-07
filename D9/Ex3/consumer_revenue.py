from kafka import KafkaConsumer
import json
from collections import defaultdict

TOPIC = 'ecommerce_transactions'
GROUP_ID = 'revenue_group'

consumer = KafkaConsumer(
    TOPIC,
    bootstrap_servers=['localhost:9094'],
    group_id=GROUP_ID,
    value_deserializer=lambda m: json.loads(m.decode('utf-8')),
    auto_offset_reset='earliest'
)

revenue_by_product = defaultdict(float)

print("Starting consumer for revenue aggregation per product...")

for message in consumer:
    txn = message.value
    product_id = txn['product_id']
    amount = txn['amount']
    revenue_by_product[product_id] += amount

    # In mẫu kết quả đơn giản
    print(f"Updated revenue for product {product_id}: {revenue_by_product[product_id]:.2f}")
