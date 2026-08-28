from flask import Flask, jsonify, render_template
import psycopg2
from datetime import datetime
import random

app = Flask(__name__)

def get_db_connection():
    """Connect to PostgreSQL"""
    try:
        return psycopg2.connect(
            host='localhost',
            database='airflow',
            user='airflow',
            password='airflow',
            port='5432'
        )
    except Exception as e:
        print(f"Database connection error: {e}")
        return None

@app.route('/')
def dashboard():
    """Render the dashboard"""
    return render_template('dashboard.html')

@app.route('/api/metrics')
def get_metrics():
    """Get all metrics from database"""
    try:
        conn = get_db_connection()
        if not conn:
            return jsonify({'error': 'Database connection failed'}), 500
        
        cur = conn.cursor()
        
        # 1. Total orders
        cur.execute("SELECT COUNT(*) FROM fact_orders")
        total_orders = cur.fetchone()[0] or 0
        
        # 2. Total revenue (completed orders only)
        cur.execute("SELECT COALESCE(SUM(order_amount), 0) FROM fact_orders WHERE order_status = 'completed'")
        total_revenue = float(cur.fetchone()[0] or 0)
        
        # 3. Orders by status
        cur.execute("""
            SELECT order_status, COUNT(*) 
            FROM fact_orders 
            GROUP BY order_status 
            ORDER BY order_status
        """)
        status_counts = [{'status': s or 'unknown', 'count': c} for s, c in cur.fetchall()]
        
        # 4. Revenue by region
        cur.execute("""
            SELECT region, COALESCE(SUM(order_amount), 0) 
            FROM fact_orders 
            WHERE order_status = 'completed' 
            GROUP BY region 
            ORDER BY region
        """)
        region_revenue = [{'region': r or 'unknown', 'revenue': float(rev)} for r, rev in cur.fetchall()]
        
        # 5. Daily revenue (last 7 days)
        cur.execute("""
            SELECT DATE(order_date) as day, COALESCE(SUM(order_amount), 0) 
            FROM fact_orders 
            WHERE order_status = 'completed' 
            GROUP BY DATE(order_date) 
            ORDER BY day DESC 
            LIMIT 7
        """)
        daily_revenue = [{'date': str(d), 'revenue': float(rev)} for d, rev in cur.fetchall()]
        
        # 6. Recent orders (last 5)
        cur.execute("""
            SELECT order_id, order_amount, order_status, region, order_date 
            FROM fact_orders 
            ORDER BY order_date DESC 
            LIMIT 5
        """)
        recent_orders = [
            {
                'order_id': oid,
                'amount': float(amt),
                'status': st,
                'region': rg,
                'date': str(dt)
            } 
            for oid, amt, st, rg, dt in cur.fetchall()
        ]
        
        cur.close()
        conn.close()
        
        return jsonify({
            'total_orders': total_orders,
            'total_revenue': total_revenue,
            'status_counts': status_counts,
            'region_revenue': region_revenue,
            'daily_revenue': daily_revenue,
            'recent_orders': recent_orders,
            'updated_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'status': 'success'
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    print("="*60)
    print("📊 E-Commerce Analytics Dashboard")
    print("="*60)
    print(f"🌐 URL: http://localhost:5000")
    print(f"📡 API: http://localhost:5000/api/metrics")
    print("="*60)
    app.run(host='0.0.0.0', port=5000, debug=False)
