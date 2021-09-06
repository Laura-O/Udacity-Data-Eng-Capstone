import requests
import ssl
import os
ssl._create_default_https_context = ssl._create_unverified_context
from airflow import DAG
from datetime import datetime, timedelta
from airflow.operators.python_operator import PythonOperator
from airflow.providers.postgres.hooks.postgres import PostgresHook
from airflow.providers.postgres.operators.postgres import PostgresOperator

from includes.download_data import download_fear_greed, download_historical
from includes.quality_check import check_greater_than_zero

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
        COPY tokens (date, price, volume_24h, market_cap, symbol)
        FROM STDIN WITH CSV HEADER
        """

    file_list = os.listdir("data/tokens/")

    for file in file_list:
        with open('/opt/airflow/data/tokens/' + file, 'r') as f:
             cur.copy_expert(SQL_STATEMENT, f)
             conn.commit()


    SQL_STATEMENT2 = """
            COPY fg (id, value, value_classification, ts, time_until_update)
            FROM STDIN WITH CSV HEADER
            """
    with open('data/index/fear_greed.csv', 'r') as f:
        cur.copy_expert(SQL_STATEMENT2, f)
        conn.commit()


download_fear_greed = PythonOperator(
    task_id='download_fear_greed',
    python_callable=download_fear_greed,
    dag=dag)

download_historical = PythonOperator(
    task_id='download_historical',
    python_callable=download_historical,
    dag=dag)


create_tables = PostgresOperator(
    task_id="create_table",
    postgres_conn_id="postgres",
    sql="""
    DROP TABLE IF EXISTS tokens;
    CREATE TABLE IF NOT EXISTS tokens (
        date TIMESTAMP,
        symbol VARCHAR,
        price FLOAT,
        volume_24h BIGINT,
        market_cap BIGINT,
        PRIMARY KEY(date, symbol)
    );
    DROP TABLE IF EXISTS fg;
    CREATE TABLE IF NOT EXISTS fg (
        ts VARCHAR,
        id INTEGER,
        value INTEGER,
        value_classification VARCHAR,
        time_until_update VARCHAR,
        PRIMARY KEY(ts, id)
    );
    SET datestyle = dmy;
    """,
    dag=dag,
)

fill_table = PythonOperator(
        task_id='copy_data',
        python_callable=write_data,
        dag=dag)

check_tables = PythonOperator(
    task_id='check_data',
    python_callable=check_greater_than_zero,
    provide_context=True,
    params={
        'tables': ['tokens', 'fg'],
    },
    dag=dag
)


[download_historical, download_fear_greed] >> create_tables
create_tables >> fill_table
fill_table >> check_tables