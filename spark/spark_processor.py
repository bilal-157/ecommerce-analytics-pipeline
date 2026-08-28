"""
Apache Spark Alternative - Data Processing with Python + Pandas
Now saving results to PostgreSQL for dashboard
"""
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random
import psycopg2

print("="*60)
print("🔥 SPARK-COMPATIBLE DATA PROCESSING")
print("="*60)

# 1. Generate large dataset
print("\n📊 Generating 10,000 orders for processing...")
np.random.seed(42)

data = {
    'order_id': range(1, 10001),
    'customer_id': np.random.randint(1, 101, 10000),
    'product_id': np.random.randint(1, 21, 10000),
    'order_amount': np.random.uniform(10, 500, 10000).round(2),
    'order_status': np.random.choice(['pending', 'completed', 'shipped', 'cancelled'], 
                                     10000, p=[0.15, 0.55, 0.25, 0.05]),
    'region': np.random.choice(['North', 'South', 'East', 'West'], 10000),
    'order_date': [datetime.now() - timedelta(days=random.randint(0, 180)) 
                   for _ in range(10000)]
}

df = pd.DataFrame(data)
print(f"✅ Generated {len(df):,} orders")

# 2. Data Processing
print("\n" + "="*60)
print("🔄 PROCESSING DATA (Spark-style transformations)")
print("="*60)

# Filter completed orders
completed_df = df[df['order_status'] == 'completed']
print(f"📌 Completed orders: {len(completed_df):,}")

# Group by region
region_stats = df.groupby('region').agg({
    'order_id': 'count',
    'order_amount': ['sum', 'mean']
}).round(2)
region_stats.columns = ['order_count', 'total_revenue', 'avg_order_value']
region_stats = region_stats.sort_values('total_revenue', ascending=False)
print("\n📊 Regional Stats:")
print(region_stats)

# 3. SAVE TO POSTGRESQL
print("\n" + "="*60)
print("💾 SAVING TO POSTGRESQL")
print("="*60)

try:
    # Connect to PostgreSQL
    conn = psycopg2.connect(
        host='localhost',
        database='airflow',
        user='airflow',
        password='airflow',
        port='5432'
    )
    cur = conn.cursor()
    
    # Clear existing orders (optional)
    cur.execute("TRUNCATE fact_orders RESTART IDENTITY;")
    print("✅ Cleared existing orders")
    
    # Insert 10,000 orders in batches
    batch_size = 500
    total_inserted = 0
    
    for i in range(0, len(df), batch_size):
        batch = df.iloc[i:i+batch_size]
        orders = []
        
        for _, row in batch.iterrows():
            orders.append((
                int(row['order_id']),
                int(row['customer_id']),
                int(row['product_id']),
                row['order_date'].date(),
                float(row['order_amount']),
                row['order_status'],
                row['region']
            ))
        
        cur.executemany("""
            INSERT INTO fact_orders 
            (order_id, customer_id, product_id, order_date, order_amount, order_status, region)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (order_id) DO NOTHING
        """, orders)
        conn.commit()
        total_inserted += len(orders)
        print(f"📥 Inserted {total_inserted:,} orders...")
    
    cur.close()
    conn.close()
    
    print(f"\n✅ Successfully saved {total_inserted:,} orders to PostgreSQL!")
    
except Exception as e:
    print(f"❌ Error saving to PostgreSQL: {e}")

# 4. Analytics Output
print("\n" + "="*60)
print("📊 ANALYTICS RESULTS")
print("="*60)

total_orders = len(df)
total_revenue = df[df['order_status'] == 'completed']['order_amount'].sum()
avg_order = df[df['order_status'] == 'completed']['order_amount'].mean()

print(f"📦 Total Orders:          {total_orders:,}")
print(f"💰 Total Revenue:         ${total_revenue:,.2f}")
print(f"📈 Average Order Value:   ${avg_order:.2f}")
print(f"👥 Unique Customers:      {df['customer_id'].nunique():,}")

print("\n📊 Order Status Distribution:")
status_dist = df['order_status'].value_counts()
for status, count in status_dist.items():
    pct = (count / len(df) * 100)
    print(f"  {status.capitalize():12}: {count:4} ({pct:.1f}%)")

print("\n" + "="*60)
print("✅ Processing complete!")
print("💡 Data saved to PostgreSQL - Refresh your dashboard!")
print("="*60)

# Save to CSV as backup
df.to_csv('processed_orders_10k.csv', index=False)
print("\n💾 Backup saved to: processed_orders_10k.csv")
