import logging

from airflow.providers.postgres.hooks.postgres import PostgresHook

def check_greater_than_zero(**kwargs):
    """ Check if data was copied into the table correctly. Copied from Udacity example code."""

    tables = kwargs["params"]["tables"]
    postgres = PostgresHook("postgres")

    for table in tables:
        records = postgres.get_records(f"SELECT COUNT(*) FROM {table}")

        if len(records) < 1 or len(records[0]) < 1:
            raise ValueError(f"Data quality check failed. {table} returned no results.")
        num_records = records[0][0]
        if num_records < 1:
            raise ValueError(f"Data quality check failed. {table} contained 0 rows.")
        logging.info(f"Data quality check on table {table} passed with {records[0][0]} records.")


def check_timeframe(**kwargs):
    """ Check if data contains a reasonable timespan."""

    tables = kwargs["params"]["tables"]
    postgres = PostgresHook("postgres")

    for table in tables:
        records = postgres.get_records(f"SELECT COUNT(*) FROM {table} WHERE date > CURRENT_TIMESTAMP")

        if len(records) > 1 or len(records[0]) > 1:
            raise ValueError(f"Data quality check failed. {table} has entries in the future.")

        logging.info(f"Data quality on table {table} check with all entries being historical values.")
