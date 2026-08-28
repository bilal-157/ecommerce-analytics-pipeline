from kafka import KafkaProducer
import json
import random
import time
from datetime import datetime

producer = KafkaProducer(
    bootstrap_servers='localhost:9092',
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

products = [
    {"id": 1, "name": "Laptop", "price": 999.99},
    {"id": 2, "name": "Phone", "price": 599.99},
    {"id": 3, "name": "Book", "price": 29.99},
    {"id": 4, "name": "Headphones", "price": 149.99},
]

regions = ['North', 'South', 'East', 'West']  # ✅ ADDED
statuses = ['pending', 'completed', 'shipped', 'cancelled']

print("🚀 Streaming orders to Kafka...")
print("Press Ctrl+C to stop\n")

try:
    while True:
        product = random.choice(products)
        order = {
            'order_id': random.randint(10000, 99999),
            'customer_id': random.randint(1, 100),
            'product_id': product['id'],
            'product_name': product['name'],
            'order_amount': round(product['price'] * random.uniform(0.8, 1.2), 2),
            'order_status': random.choice(statuses),
            'region': random.choice(regions),  # ✅ ADDED
            'timestamp': datetime.now().isoformat()
        }
        producer.send('orders', order)
        print(f"📤 Order {order['order_id']}: ${order['order_amount']} - {order['order_status']} - {order['region']}")
        time.sleep(random.uniform(0.5, 2))
except KeyboardInterrupt:
    print("\n🛑 Stopping producer...")
finally:
    producer.close()
