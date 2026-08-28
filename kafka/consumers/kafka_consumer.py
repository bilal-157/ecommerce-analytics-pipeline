from kafka import KafkaConsumer
import json
import psycopg2
from datetime import datetime

conn = psycopg2.connect(
    host='localhost',
    database='airflow',
    user='airflow',
    password='airflow',
    port='5432'
)
cur = conn.cursor()

consumer = KafkaConsumer(
    'orders',
    bootstrap_servers='localhost:9092',
    auto_offset_reset='earliest',
    value_deserializer=lambda x: json.loads(x.decode('utf-8'))
)

print("📥 Listening for orders...")
for message in consumer:
    order = message.value
    
    # ✅ Handle missing region
    region = order.get('region', 'Unknown')
    
    cur.execute("""
        INSERT INTO fact_orders (order_id, customer_id, product_id, order_date, order_amount, order_status, region)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (order_id) DO NOTHING
    """, (order['order_id'], order['customer_id'], order['product_id'],
          datetime.now().date(), order['order_amount'], order['order_status'], region))
    conn.commit()
    print(f"✅ Order {order['order_id']} saved (region: {region})")
