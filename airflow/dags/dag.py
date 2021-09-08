import requests
import ssl
import os
ssl._create_default_https_context = ssl._create_unverified_context
from airflow import DAG
from datetime import datetime, timedelta
from airflow.operators.python_operator import PythonOperator
from airflow.providers.postgres.hooks.postgres import PostgresHook
from airflow.providers.postgres.operators.postgres import PostgresOperator

from includes.fill_db import write_data
from includes.download_data import download_fear_greed, download_historical, download_binance, download_ftx
from includes.quality_check import check_greater_than_zero

default_args = {
    "owner": "airflow",
    "depends_on_past": False,
    "start_date": datetime(2021, 9, 4),
    "retries": 0,
    "retry_delay": timedelta(minutes=5),
}

dag = DAG("data_processing", default_args=default_args, schedule_interval=timedelta(1))


download_fear_greed = PythonOperator(
    task_id='download_fear_greed',
    python_callable=download_fear_greed,
    dag=dag)

download_binance = PythonOperator(
    task_id='download_binance',
    python_callable=download_binance,
    dag=dag)

download_ftx = PythonOperator(
    task_id='download_ftx',
    python_callable=download_ftx,
    dag=dag)

download_historical = PythonOperator(
    task_id='download_historical',
    python_callable=download_historical,
    dag=dag)

fill_database = PythonOperator(
    task_id='fill_database',
    python_callable=write_data,
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
    DROP TABLE IF EXISTS futures;
    CREATE TABLE IF NOT EXISTS futures (
        date TIMESTAMP,
        symbol VARCHAR,
        open FLOAT,
        high FLOAT,
        low FLOAT,
        close FLOAT,
        volume_token FLOAT,
        volume_usd FLOAT,
        exchange VARCHAR,
        PRIMARY KEY(date, symbol, exchange)
    );
    DROP TABLE IF EXISTS fg;
    CREATE TABLE IF NOT EXISTS fg (
        ts TIMESTAMP,
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

check_tables = PythonOperator(
    task_id='check_data',
    python_callable=check_greater_than_zero,
    provide_context=True,
    params={
        'tables': ['tokens', 'fg'],
    },
    dag=dag
)


[download_historical, download_binance, download_ftx, download_fear_greed] >> create_tables
create_tables >> fill_database
fill_database >> check_tables