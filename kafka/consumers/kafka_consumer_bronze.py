from kafka import KafkaConsumer
import json
import psycopg2
from datetime import datetime

print("📥 Listening for API data from Kafka...")

conn = psycopg2.connect(
    host='localhost',
    database='airflow',
    user='airflow',
    password='airflow',
    port='5432'
)
cur = conn.cursor()

# Create bronze orders table
cur.execute("""
CREATE TABLE IF NOT EXISTS bronze_orders (
    order_id INTEGER PRIMARY KEY,
    product_id INTEGER,
    product_name VARCHAR(500),
    price DECIMAL(10,2),
    category VARCHAR(100),
    quantity INTEGER,
    order_status VARCHAR(20),
    ingested_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
""")
conn.commit()

consumer = KafkaConsumer(
    'api-orders',
    bootstrap_servers='localhost:9092',
    auto_offset_reset='earliest',
    value_deserializer=lambda x: json.loads(x.decode('utf-8'))
)

for message in consumer:
    order = message.value
    cur.execute("""
        INSERT INTO bronze_orders (order_id, product_id, product_name, price, category, quantity, order_status)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (order_id) DO NOTHING
    """, (order['order_id'], order['product_id'], order['product_name'], 
          order['price'], order['category'], order['quantity'], order['order_status']))
    conn.commit()
    print(f"✅ Order {order['order_id']} saved to Bronze layer")
