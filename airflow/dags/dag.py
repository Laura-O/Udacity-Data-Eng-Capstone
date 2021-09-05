import requests
import ssl
import os
ssl._create_default_https_context = ssl._create_unverified_context
from airflow import DAG
from datetime import datetime, timedelta
from airflow.operators.python_operator import PythonOperator
from airflow.providers.postgres.hooks.postgres import PostgresHook
from airflow.providers.postgres.operators.postgres import PostgresOperator

from includes.download_data import download_binance, download_fear_greed

default_args = {
    "owner": "airflow",
    "depends_on_past": False,
    "start_date": datetime(2021, 9, 4),
    "retries": 0,
    "retry_delay": timedelta(minutes=5),
}

dag = DAG("data_processing", default_args=default_args, schedule_interval=timedelta(1))

def write_data():
    conn = PostgresHook(postgres_conn_id='postgres').get_conn()
    cur = conn.cursor()

    SQL_STATEMENT = """
        COPY tokens (ts, date, symbol, open, high, low, close, volume_btc, volume_usdt, tradecount)
        FROM STDIN WITH CSV HEADER
        """

    file_list = os.listdir("data/tokens/")

    for file in file_list:
        with open('/opt/airflow/data/tokens/' + file, 'r') as f:
            cur.copy_expert(SQL_STATEMENT, f)
            conn.commit()

download_binance = PythonOperator(
    task_id='download_binance',
    python_callable=download_binance,
    dag=dag)

download_fear_greed = PythonOperator(
    task_id='download_fear_greed',
    python_callable=download_fear_greed,
    dag=dag)

create_table = PostgresOperator(
    task_id="create_table",
    postgres_conn_id="postgres",
    sql="""
    DROP TABLE tokens;
    CREATE TABLE IF NOT EXISTS tokens (
        ts FLOAT,
        date TIMESTAMP ,
        symbol VARCHAR(10),
        open FLOAT,
        high FLOAT ,
        low FLOAT ,
        close FLOAT,
        volume_btc FLOAT,
        volume_usdt FLOAT,
        tradecount TEXT,
        PRIMARY KEY(ts, symbol)
    )
    """,
    dag=dag,
)

fill_table = PythonOperator(
        task_id='copy_data',
        python_callable=write_data,
        dag=dag)


download_binance >> create_table
create_table >> fill_table