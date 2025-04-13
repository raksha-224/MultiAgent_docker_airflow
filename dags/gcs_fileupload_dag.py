import logging
from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from datetime import datetime, timedelta

# 👇 Import your callable
from scripts.gcs_airflow import data_loading

# Set custom logging configuration
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

def run_script():
    logging.info("Calling data_loading from DAG...")
    data_loading()
    logging.info("Done running data_loading.")

# Default args for the DAG
default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2025, 4, 5),
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

# Define the DAG with every 10 mins scheduling
dag = DAG(
    'gcs_file_upload_dag',
    default_args=default_args,
    description='A DAG to upload files to GCS using native callable',
    schedule_interval='*/10 * * * *',
    catchup=False,
    tags=['gcs', 'upload']
)

# Define the task
task = PythonOperator(
    task_id='run_data_loading',
    python_callable=run_script,
    dag=dag,
)
