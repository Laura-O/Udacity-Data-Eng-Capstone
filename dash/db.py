from datetime import date, timedelta
import pandas as pd
from sqlalchemy import create_engine

def connect_to_db():
	# https://www.tutorialspoint.com/postgresql/postgresql_python.htm
	return create_engine('postgresql://postgres:pspwd@localhost:5432/postgres')

def query_fg(days, selected_token, db):
	end_date = date.today()
	start_date = date.today() - timedelta(days=days)
	sql_statement = "SELECT * FROM fg WHERE ts >= '{start}' AND ts <= '{end}'".format(start=start_date, end=end_date)
	df_fg = pd.read_sql(sql_statement, db)

	print(''.join(selected_token))
	sql_statement2 = "SELECT * FROM tokens " \
					 "WHERE symbol = '{selected}' AND date >= '{start}' AND date <= '{end}'".format(selected=''.join(selected_token),start=start_date, end=end_date)
	df_tokens = pd.read_sql(sql_statement2, db)
	print(sql_statement2)

	return df_fg, df_tokens

def query_tokens(days, db):
	end_date = date.today()
	start_date = date.today() - timedelta(days=days)
	sql_statement = "SELECT * FROM tokens WHERE date >= '{start}' AND date <= '{end}'".format(start=start_date, end=end_date)

	df = pd.read_sql(sql_statement, db)
	return df