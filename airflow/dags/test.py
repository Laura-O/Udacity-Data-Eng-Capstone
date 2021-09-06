import os
import csv
from coinpaprika.client import Client

data_path = "../data/coinp"
token = 'btc-bitcoin'
file_path = os.path.join(data_path, token + ".csv")

p_client = Client()

raw_text = p_client.historical(token, start="2021-01-01", limit=5000, interval="1d")

keys = raw_text[0].keys()
with open(file_path, 'w', newline='') as output_file:
    dict_writer = csv.DictWriter(output_file, keys)
    dict_writer.writeheader()
    dict_writer.writerows(raw_text)