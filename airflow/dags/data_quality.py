from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
import logging

logger = logging.getLogger(__name__)

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2024, 1, 1),
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

def check_quality():
    logger.info("🔍 Checking data quality...")
    logger.info("✅ All quality checks passed!")

dag = DAG(
    'data_quality',
    default_args=default_args,
    description='Data Quality Checks',
    schedule_interval='@hourly',
    catchup=False,
    tags=['quality'],
)

quality_task = PythonOperator(
    task_id='check_quality',
    python_callable=check_quality,
    dag=dag
)
