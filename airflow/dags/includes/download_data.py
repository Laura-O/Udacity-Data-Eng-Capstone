import requests
import os
import logging
import json
import pandas as pd

from coinpaprika.client import Client

def download_binance():
    data_path = "/opt/airflow/data/tokens"

    tokens = ["BTCUSDT", "SOLUSDT"]
    tick="d"

    for token in tokens:
        filename = "{}_{}.csv".format(token, tick)
        file_path = os.path.join(data_path, filename)

        url = "https://www.cryptodatadownload.com/cdd/Binance_{}_{}.csv".format(token, tick)

        logging.info(f"Retrieving Data from {url}")
        raw_text = requests.get(url, verify='dags/includes/consolidate.pem').text
        head, raw_text = raw_text.split('\n', 1)

        with open(file_path, 'w') as text_file:
            text_file.write(raw_text)

        print("Saved %s" % file_path)

def download_fear_greed():
    data_path = "/opt/airflow/data/index"
    file_path = os.path.join(data_path, "fear_greed.csv")

    url = "https://api.alternative.me/fng/?limit=0&date_format=us"
    logging.info(f"Retrieving Data from {url}")

    raw_text = requests.get(url, verify='dags/includes/consolidate_alt.pem').text
    raw_json = json.loads(raw_text)

    df = pd.DataFrame(raw_json['data'])

    df.to_csv(file_path)


def download_historical():
    data_path = "/opt/airflow/data/tokens"

    token_ids = ['btc-bitcoin', 'eth-ethereum',
                 'sol-solana', 'ada-cardano', 'xrp-xrp',
                 'doge-dogecoin', 'dot-polkadot',
                 'uni-uniswap', 'ltc-litecoin',
                 'luna-terra', 'link-chainlink',
                 'icp-internet-computer', 'matic-polygon',
                 'avax-avalanche', 'vet-vechain']

    for token in token_ids:
        file_path = os.path.join(data_path, token + ".csv")

        p_client = Client()
        raw_text = p_client.historical(token, start="2018-02-01", limit=5000, interval="1d")

        df = pd.DataFrame(raw_text)
        df['token'] = token
        df.to_csv(file_path, index=False)