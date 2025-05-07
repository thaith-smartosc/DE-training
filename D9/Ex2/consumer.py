from kafka import KafkaConsumer
import json

consumer = KafkaConsumer(
    'sensor-avg',
    bootstrap_servers='localhost:9094',
    value_deserializer=lambda m: json.loads(m.decode('utf-8')),
    auto_offset_reset='earliest',
    group_id='avg-consumers'
)

print('Listening for aggregated sensor averages...')
for message in consumer:
    print("Avg record:", message.value)
