from kafka import KafkaProducer
import json
import random
import time
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TransactionGenerator:
    def __init__(self, bootstrap_servers=['localhost:9092']):
        self.topic = 'transactions'
        self.bootstrap_servers = bootstrap_servers
        self.producer = None
        self._initialize_producer()

    def _initialize_producer(self):
        try:
            self.producer = KafkaProducer(
                bootstrap_servers=self.bootstrap_servers,
                value_serializer=lambda x: json.dumps(x).encode('utf-8'),
                api_version=(2, 8, 1),  # Specify your Kafka version
                retries=5,
                request_timeout_ms=30000,
                max_block_ms=60000
            )
            logger.info(f"Successfully connected to Kafka at {self.bootstrap_servers}")
        except Exception as e:
            logger.error(f"Failed to initialize Kafka producer: {str(e)}")
            raise

    def generate_transaction(self):
        current_time = datetime.now()
        
        payment_methods = ['CREDIT', 'DEBIT', 'CASH', 'MOBILE_PAYMENT']
        store_locations = ['NEW_YORK', 'LOS_ANGELES', 'CHICAGO', 'HOUSTON', 'PHOENIX']

        transaction = {
            'transaction_id': str(random.randint(1000000, 9999999)),
            'customer_id': str(random.randint(1000, 1000000)),
            'product_id': str(random.randint(1, 10000)),
            'transaction_date': current_time.isoformat(),
            'quantity': random.randint(1, 10),
            'unit_price': round(random.uniform(10, 1000), 2),
            'discount_percent': round(random.uniform(0, 0.3), 2),
            'payment_method': random.choice(payment_methods),
            'store_location': random.choice(store_locations),
            'transaction_hour': current_time.hour,
            'day_of_week': current_time.weekday(),  # 0-6 (Monday-Sunday)
            'week_of_year': int(current_time.strftime('%W')),
            'month_of_year': current_time.month
        }
        
        # Calculate absolute discount amount
        transaction['discount_amount'] = round(
            transaction['unit_price'] * transaction['discount_percent'] * transaction['quantity'], 
            2
        )
        transaction['net_amount'] = round(
            (transaction['unit_price'] * transaction['quantity']) - transaction['discount_amount'],
            2
        )
        
        return transaction

    def start_generating(self, interval=1, max_messages=None):
        message_count = 0
        try:
            while True:
                if max_messages and message_count >= max_messages:
                    logger.info(f"Reached max messages limit of {max_messages}")
                    break
                    
                transaction = self.generate_transaction()
                try:
                    future = self.producer.send(self.topic, transaction)
                    # Wait for message to be delivered (optional)
                    future.get(timeout=10)
                    logger.info(f"Sent transaction: {transaction['transaction_id']}")
                    message_count += 1
                except Exception as send_error:
                    logger.error(f"Failed to send message: {send_error}")
                    # Attempt to reconnect
                    self._initialize_producer()
                
                time.sleep(interval)
        except KeyboardInterrupt:
            logger.info("Shutting down producer...")
        finally:
            self.producer.flush()
            self.producer.close()
            logger.info("Producer closed.")

if __name__ == "__main__":
    # Try multiple common Kafka ports if localhost:9092 fails
    bootstrap_servers = [
        'localhost:9092',
        'kafka:9092',
        '127.0.0.1:9092'
    ]
    
    generator = TransactionGenerator(bootstrap_servers)
    try:
        generator.start_generating(interval=0.5, max_messages=100)
    except Exception as e:
        logger.error(f"Application error: {str(e)}")