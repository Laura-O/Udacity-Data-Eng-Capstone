from datetime import date, timedelta
import pandas as pd
from sqlalchemy import create_engine

def connect_to_db():
	"""Connect to the database"""
	return create_engine('postgresql://postgres:pspwd@localhost:5432/postgres')

def query_fg(days, selected_token, db):
	"""
	Query database for fear & greed and selected token values.

	:param days: selected number of days
	:param selected_token: selected token
	:param db: database reference
	:return: dataframes containing the query result
	"""
	end_date = date.today()
	start_date = date.today() - timedelta(days=days)
	sql_statement = "SELECT * FROM fg WHERE ts >= '{start}' AND ts <= '{end}'".format(start=start_date, end=end_date)
	df_fg = pd.read_sql(sql_statement, db)

	sql_statement2 = "SELECT * FROM historical " \
					 "WHERE symbol = '{selected}' AND date >= '{start}' AND date <= '{end}'".format(selected=''.join(selected_token),start=start_date, end=end_date)
	df_tokens = pd.read_sql(sql_statement2, db)

	return df_fg, df_tokens

def query_tokens(days, db):
	"""
	Queries the database for the historical data for the selected timespan.
	
	:param days: selected number of days 
	:param db: database reference
	:return: dataframe containing the historical data for the selected timespan
	"""

	end_date = date.today()
	start_date = date.today() - timedelta(days=days)
	sql_statement = "SELECT * FROM historical WHERE date >= '{start}' AND date <= '{end}'".format(start=start_date, end=end_date)

	df = pd.read_sql(sql_statement, db)
	return df

def query_futures(days, future, db):
	"""
	Queries the database for the futures data for the selected timespan.

	:param days: selected number of days
	:param future: selected token
	:param db: database reference
	:return: dataframe containing the futures data for the selected timespan
	"""
	end_date = date.today()
	start_date = date.today() - timedelta(days=days)

	sql_statement = "SELECT * FROM futures WHERE symbol = '{future}' AND date >= '{start}' AND date <= '{end}'".format(future=''.join(future), start=start_date, end=end_date)
	df = pd.read_sql(sql_statement, db)
	return df