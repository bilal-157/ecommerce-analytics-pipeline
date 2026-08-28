from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.dummy import DummyOperator
import logging

logger = logging.getLogger(__name__)

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2024, 1, 1),
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

def extract():
    logger.info("📥 Extracting data...")
    return {"status": "extracted"}

def transform():
    logger.info("🔄 Transforming data...")
    return {"status": "transformed"}

def load():
    logger.info("📤 Loading data...")
    return {"status": "loaded"}

dag = DAG(
    'etl_pipeline',
    default_args=default_args,
    description='ETL Pipeline',
    schedule_interval='@daily',
    catchup=False,
    tags=['etl'],
)

start = DummyOperator(task_id='start', dag=dag)
extract_task = PythonOperator(task_id='extract', python_callable=extract, dag=dag)
transform_task = PythonOperator(task_id='transform', python_callable=transform, dag=dag)
load_task = PythonOperator(task_id='load', python_callable=load, dag=dag)
end = DummyOperator(task_id='end', dag=dag)

start >> extract_task >> transform_task >> load_task >> end
