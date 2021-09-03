from urllib import request
import ssl
ssl._create_default_https_context = ssl._create_unverified_context
from airflow import DAG
from datetime import datetime, timedelta
from airflow.operators.python_operator import PythonOperator


default_args = {
    "owner": "airflow",
    "depends_on_past": False,
    "start_date": datetime(2015, 6, 1),
    "retries": 1,
    "retry_delay": timedelta(minutes=5),
}

dag = DAG("data_processing", default_args=default_args, schedule_interval=timedelta(1))

def download_file():
    remote_url = 'https://www.cryptodatadownload.com/cdd/Binance_BTCUSDT_minute.csv'
    local_file_path = './tmp/btc.csv' 
    request.urlretrieve(remote_url, local_file_path)

download_data = PythonOperator(
    task_id='download_data',
    python_callable=download_file,
    dag=dag)
