import psycopg2
import random
from datetime import datetime, timedelta

# Connect to PostgreSQL
conn = psycopg2.connect(
    host='localhost',
    database='airflow',
    user='airflow',
    password='airflow',
    port='5432'
)
cur = conn.cursor()

# Realistic data
products = [
    (1, 'Laptop Pro', 'Electronics', 1299.99),
    (2, 'Smartphone X', 'Electronics', 899.99),
    (3, 'Wireless Headphones', 'Electronics', 199.99),
    (4, 'Smart Watch', 'Electronics', 349.99),
    (5, 'Tablet Pro', 'Electronics', 649.99),
    (6, 'Fitness Tracker', 'Electronics', 99.99),
    (7, 'Gaming Mouse', 'Electronics', 79.99),
    (8, 'Mechanical Keyboard', 'Electronics', 149.99),
    (9, 'USB-C Hub', 'Electronics', 59.99),
    (10, 'External SSD', 'Electronics', 129.99),
    (11, 'Business Book', 'Books', 29.99),
    (12, 'Fiction Novel', 'Books', 19.99),
    (13, 'Programming Book', 'Books', 49.99),
    (14, 'Self-Help Book', 'Books', 24.99),
    (15, 'Cookbook', 'Books', 34.99),
    (16, 'T-Shirt', 'Clothing', 24.99),
    (17, 'Jeans', 'Clothing', 59.99),
    (18, 'Jacket', 'Clothing', 89.99),
    (19, 'Sneakers', 'Clothing', 119.99),
    (20, 'Backpack', 'Clothing', 49.99),
]

customers = [
    (1, 'John Doe', 'Premium', 'North'),
    (2, 'Jane Smith', 'Regular', 'South'),
    (3, 'Bob Johnson', 'Premium', 'East'),
    (4, 'Alice Brown', 'Regular', 'West'),
    (5, 'Charlie Wilson', 'Premium', 'North'),
    (6, 'Diana Miller', 'Regular', 'South'),
    (7, 'Eve Davis', 'Premium', 'East'),
    (8, 'Frank Garcia', 'Regular', 'West'),
    (9, 'Grace Lee', 'Premium', 'North'),
    (10, 'Henry Kim', 'Regular', 'South'),
]

statuses = ['pending', 'completed', 'shipped', 'cancelled']
status_weights = [0.15, 0.55, 0.25, 0.05]

# Get current max order_id
cur.execute("SELECT COALESCE(MAX(order_id), 0) FROM fact_orders")
max_id = cur.fetchone()[0]
start_id = max_id + 1

# Generate 500 orders
orders = []
start_date = datetime.now() - timedelta(days=180)

for i in range(start_id, start_id + 500):
    customer = random.choice(customers)
    product = random.choice(products)
    status = random.choices(statuses, weights=status_weights)[0]
    quantity = random.randint(1, 3)
    amount = round(product[3] * quantity * random.uniform(0.9, 1.1), 2)
    days_ago = random.randint(0, 180)
    order_date = start_date + timedelta(days=days_ago)
    
    orders.append((
        i,
        customer[0],
        product[0],
        order_date.date(),
        amount,
        status,
        customer[3]  # region
    ))

# Insert in batches
batch_size = 50
for i in range(0, len(orders), batch_size):
    batch = orders[i:i+batch_size]
    cur.executemany("""
        INSERT INTO fact_orders 
        (order_id, customer_id, product_id, order_date, order_amount, order_status, region)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (order_id) DO NOTHING
    """, batch)

conn.commit()

# Insert dimension tables
# Customers
for customer in customers:
    cur.execute("""
        INSERT INTO dim_customer_scd 
        (customer_sk, customer_id, customer_name, region, customer_segment, valid_from, valid_to, is_current)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (customer_sk) DO UPDATE SET
            customer_name = EXCLUDED.customer_name,
            region = EXCLUDED.region,
            customer_segment = EXCLUDED.customer_segment
    """, (customer[0], customer[0], customer[1], customer[3], customer[2], '2024-01-01', '9999-12-31', True))

# Products
for product in products:
    cur.execute("""
        INSERT INTO dim_product (product_id, product_name, category, unit_price)
        VALUES (%s, %s, %s, %s)
        ON CONFLICT (product_id) DO UPDATE SET
            product_name = EXCLUDED.product_name,
            category = EXCLUDED.category,
            unit_price = EXCLUDED.unit_price
    """, product)

conn.commit()

# Get statistics
cur.execute("""
    SELECT 
        COUNT(*) as total_orders,
        COALESCE(SUM(CASE WHEN order_status = 'completed' THEN order_amount ELSE 0 END), 0) as total_revenue,
        COALESCE(AVG(CASE WHEN order_status = 'completed' THEN order_amount ELSE NULL END), 0) as avg_order,
        COUNT(DISTINCT customer_id) as unique_customers
    FROM fact_orders
""")
stats = cur.fetchone()

print("\n" + "="*60)
print("📊 DATA GENERATED SUCCESSFULLY!")
print("="*60)
print(f"📦 Total Orders:        {stats[0]:,}")
print(f"💰 Total Revenue:       ${stats[1]:,.2f}")
print(f"📈 Average Order Value: ${stats[2]:,.2f}")
print(f"👥 Unique Customers:    {stats[3]:,}")
print("="*60)

# Show distribution
cur.execute("""
    SELECT order_status, COUNT(*) 
    FROM fact_orders 
    GROUP BY order_status 
    ORDER BY COUNT(*) DESC
""")
print("\n📊 Order Status Distribution:")
total = sum(c for _, c in cur.fetchall())
cur.execute("""
    SELECT order_status, COUNT(*) 
    FROM fact_orders 
    GROUP BY order_status 
    ORDER BY COUNT(*) DESC
""")
for status, count in cur.fetchall():
    pct = (count / stats[0] * 100) if stats[0] > 0 else 0
    print(f"  {status.capitalize():12}: {count:3} ({pct:.1f}%)")

cur.execute("""
    SELECT region, COUNT(*), COALESCE(SUM(order_amount), 0) 
    FROM fact_orders 
    WHERE order_status = 'completed'
    GROUP BY region 
    ORDER BY SUM(order_amount) DESC
""")
print("\n🌍 Revenue by Region:")
for region, count, revenue in cur.fetchall():
    print(f"  {region:10}: ${revenue:,.2f} ({count} orders)")

cur.close()
conn.close()
print("\n✅ Done! Refresh your dashboard at http://localhost:5000")
