import requests
import os
import logging
import json
import pandas as pd
import io

from coinpaprika.client import Client

def download_binance():
    data_path = "/opt/airflow/data/binance"
    tokens = ["BTCUSDT", "ETHUSDT", "XRPUSDT", "LINKUSDT", "LTCUSDT", "ADAUSDT",
              "EOSUSDT", "BNBUSDT"]

    for token in tokens:
        filename = "{}.csv".format(token)
        file_path = os.path.join(data_path, filename)

        url = "https://www.cryptodatadownload.com/cdd/{}_Binance_futures_data_day.csv".format(token)

        logging.info(f"Retrieving Data from {url}")
        raw_text = requests.get(url, verify='dags/includes/consolidate.pem').content

        df = pd.read_csv(io.StringIO(raw_text.decode('utf-8')), skiprows=1)
        df.columns = ['unix', 'date', 'symbol', 'open', 'high', 'low', 'close', 'volume_token', 'volume_usd',
                      'tradecount']
        df = df.drop('tradecount', 1)
        df = df.drop('unix', 1)
        df['exchange'] = 'binance'

        dict = {'BTC/USDT': 'BTC-PERP', 'ETH/USDT': 'ETH-PERP', 'XRP/USDT': 'XRP-PERP', 'LINK/USDT': 'LINK-PERP',
                'LTC/USDT': 'LTC-PERP', 'ADA/USDT': 'ADA-PERP', 'EOS/USDT': 'EOS-PERP', 'BNB/USDT': 'BNB-PERP'}

        df['symbol'] = df['symbol'].map(dict)

        df.to_csv(file_path, index=False)

        logging.info("Saved %s" % file_path)

def download_ftx():
    data_path = "/opt/airflow/data/ftx"
    tokens = ["BTCPERP", "ETHPERP", "XRPPERP", "LINKPERP", "LTCPERP",
              "ADAPERP", "EOSPERP", "BNBPERP"]

    for token in tokens:
        filename = "{}.csv".format(token)
        file_path = os.path.join(data_path, filename)

        url = "https://www.cryptodatadownload.com/cdd/FTX_Futures_{}_d.csv".format(token)

        logging.info(f"Retrieving Data from {url}")
        raw_text = requests.get(url, verify='dags/includes/consolidate.pem').content

        df = pd.read_csv(io.StringIO(raw_text.decode('utf-8')), skiprows=1)
        df.columns = ['unix', 'date', 'symbol', 'open', 'high', 'low', 'close', 'volume_token', 'volume_usd']
        df = df.drop('unix', 1)
        df['exchange'] = 'ftx'

        df.to_csv(file_path, index=False)

        logging.info("Saved %s" % file_path)

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