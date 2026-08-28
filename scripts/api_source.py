import requests
import json
import psycopg2
from datetime import datetime

print("📡 Fetching data from FakeStore API...")

# 1. Fetch products from public API
response = requests.get('https://fakestoreapi.com/products')
products = response.json()
print(f"✅ Fetched {len(products)} products")

# 2. Fetch users/customers
response = requests.get('https://fakestoreapi.com/users')
customers = response.json()
print(f"✅ Fetched {len(customers)} customers")

# 3. Save to PostgreSQL (Bronze Layer)
conn = psycopg2.connect(
    host='localhost',
    database='airflow',
    user='airflow',
    password='airflow',
    port='5432'
)
cur = conn.cursor()

# Create bronze tables
cur.execute("""
CREATE TABLE IF NOT EXISTS bronze_products (
    product_id INTEGER PRIMARY KEY,
    title VARCHAR(500),
    price DECIMAL(10,2),
    description TEXT,
    category VARCHAR(100),
    image_url VARCHAR(500),
    fetched_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
""")

# Insert products
for p in products:
    cur.execute("""
        INSERT INTO bronze_products (product_id, title, price, description, category, image_url)
        VALUES (%s, %s, %s, %s, %s, %s)
        ON CONFLICT (product_id) DO NOTHING
    """, (p['id'], p['title'], p['price'], p['description'], p['category'], p['image']))

conn.commit()
cur.close()
conn.close()

print("✅ API data saved to bronze_products table in PostgreSQL!")
