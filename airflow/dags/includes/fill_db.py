import os
from airflow.providers.postgres.hooks.postgres import PostgresHook
import logging

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


    SQL_STATEMENT3 = """
                    COPY futures (date, symbol, open, high, low, close, volume_token, volume_usd, exchange)
                    FROM STDIN WITH CSV HEADER
                    """

    file_list_binance = os.listdir("data/binance/")
    logging.info(f"Import binance files: {file_list_binance}")

    for file in file_list_binance:
        with open('/opt/airflow/data/binance/' + file, 'r') as f:
            cur.copy_expert(SQL_STATEMENT3, f)
            conn.commit()

    file_list_ftx = os.listdir("data/ftx/")
    logging.info(f"Import ftx files: {file_list_ftx}")

    for file in file_list_ftx:
        with open('/opt/airflow/data/ftx/' + file, 'r') as f:
            cur.copy_expert(SQL_STATEMENT3, f)
            conn.commit()
