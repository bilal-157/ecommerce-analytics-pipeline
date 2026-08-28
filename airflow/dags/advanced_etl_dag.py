from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.dummy import DummyOperator
from airflow.utils.trigger_rule import TriggerRule
import logging

logger = logging.getLogger(__name__)

default_args = {
    'owner': 'data_team',
    'depends_on_past': False,
    'start_date': datetime(2024, 1, 1),
    'retries': 2,
    'retry_delay': timedelta(minutes=5),
}

def extract_data():
    logger.info("📥 Extracting data from source...")
    return {"records": 1500, "status": "success"}

def transform_data(**context):
    logger.info("🔄 Transforming data...")
    ti = context['task_instance']
    extracted = ti.xcom_pull(task_ids='extract_data')
    return {"records": extracted['records'], "status": "success"}

def load_data(**context):
    logger.info("📤 Loading data to warehouse...")
    ti = context['task_instance']
    transformed = ti.xcom_pull(task_ids='transform_data')
    return {"records": transformed['records'], "status": "success"}

def quality_check(**context):
    logger.info("🔍 Running quality checks...")
    ti = context['task_instance']
    loaded = ti.xcom_pull(task_ids='load_data')
    if loaded['records'] > 0:
        logger.info("✅ Quality check passed!")
    else:
        raise ValueError("❌ Quality check failed!")
    return {"status": "passed"}

dag = DAG(
    'advanced_etl_pipeline',
    default_args=default_args,
    description='Advanced ETL Pipeline',
    schedule_interval='@daily',
    catchup=False,
    tags=['etl', 'advanced'],
)

start = DummyOperator(task_id='start', dag=dag)
extract = PythonOperator(task_id='extract_data', python_callable=extract_data, dag=dag)
transform = PythonOperator(task_id='transform_data', python_callable=transform_data, dag=dag)
quality = PythonOperator(task_id='quality_check', python_callable=quality_check, dag=dag)
load = PythonOperator(task_id='load_data', python_callable=load_data, dag=dag)
end = DummyOperator(task_id='end', dag=dag, trigger_rule=TriggerRule.ALL_DONE)

start >> extract >> transform >> quality >> load >> end
