from confluent_kafka.avro import AvroConsumer
from confluent_kafka.avro.serializer import SerializerError

def get_avro_consumer():
    consumer_config = {
        'bootstrap.servers': 'localhost:9092',
        'schema.registry.url': 'http://localhost:8081',
        'group.id': 'user-consumer-group',
        'auto.offset.reset': 'earliest'
    }
    
    return AvroConsumer(consumer_config)

if __name__ == "__main__":
    consumer = get_avro_consumer()
    consumer.subscribe(['users'])
    
    print("Starting Avro consumer...")
    
    try:
        while True:
            try:
                msg = consumer.poll(1.0)
                if msg is None:
                    continue
                
                if msg.error():
                    print(f"Consumer error: {msg.error()}")
                    continue
                
                user = msg.value()
                print("Received user record:")
                print(f"  ID: {user['id']}")
                print(f"  Name: {user['name']}")
                print(f"  Email: {user['email']}")
                
                # Handle the new field in evolved schema
                if 'age' in user:
                    print(f"  Age: {user['age']}")
                
                print("-----------------------")
                
            except SerializerError as e:
                print(f"Message deserialization failed: {e}")
                
    except KeyboardInterrupt:
        pass
    
    finally:
        consumer.close()
