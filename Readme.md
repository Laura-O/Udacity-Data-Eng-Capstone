# Data used

* [Coinpaprika](https://coinpaprika.com/)
* [Cryptodatadownload](https://www.cryptodatadownload.com)
* [Fear and greed index](https://api.alternative.me/fng/)

# Code

* `/airflow` Airflow pipeline for downloading, preparing, checking and inserting the data in a PostgreSQL database
* `/dash` Dash dashboard for visualizing the data.

The code for querying the Coinpaprika API was copied from [https://github.com/s0h3ck/coinpaprika-api-python-client](https://github.com/s0h3ck/coinpaprika-api-python-client) (published under MIT License).

# Steps

## Step 1: Project scope and purpose

"If in doubt, zoom out"

The crypto community focuses a lot on short-term data. A few days in crypto can feel like years. This is reasonable as the market changes quickly and new projects are founded every single day. However, looking into more historical data and understanding the bigger picture is clearly a requirement for a successful investment which is not just based on short-term luck.

There are countless data resources on the internet but they are rarely combined and matched. Considering the sheer amount of data this is definitely a mammoth task which would not be possible to do in a single ETL process.

## Step 2: Project scope and purpose

The data I finally used in this project contains different abbreviations and symbols for the tokens. For the ones saved in the same database, I am fixing this right after downloading the data from the API so the symbols are consistent in the database. To have a connection between the different tables, I decided to create a facts table containing all the used terms, a unique symbol and the full name.

## Step 3: Define the data model

![Database](assets/db.png?raw=true "ER Diagram")

## Step 4: Run ETL to Model the Data

![Pipeline](assets/pipeline.png?raw=true "Pipeline")

* Load the datasets from various APIs
* Prepare the data
* Create database tables for historical data, futures, and the fear and greed index
* Insert the data into the database
* Check if the data was inserted correctly



# Prerequisites

* A PostgreSQL database ([Docker image](https://hub.docker.com/_/postgres))
* Airflow ([Docker image](https://hub.docker.com/r/apache/airflow))

## Setting up the database in Airflow and Dash

To connect the database to Airflow, you need to setup a PostgreSQL hook with the id `postgres`. To connect the database in Dash, please add an `.env` file with your connection parameters following the example given in `env.example`.

## Copying the DAG to airflow

To run the pipeline in your Airflow instance, just copy all files in `dags`.

## Installing and running the dashboard

Install the required packages:

    cd dash
    pip install -r requirements.txt

After this is finished, the dashboard can be started with `python app.py`.

![Dashboard](assets/dashboard.png?raw=true "Dashboard")

# Other scenarios

* The data was increased by 100x.

The data will naturally increase over time. This will clearly have an impact on the runtime of the individual steps of the pipeline. However, as the most time-consuming steps can be run in parallel, this will not cause an unexpected increase of the runtime.

* The pipelines would be run on a daily basis by 7 am every day.

The pipeline will work as planned.

* The database needed to be accessed by 100+ people.

When more users are accessing the dashboard, some caching solution should be added. Dash can be used with Flask-Caching to save results to either your filesystem or a Redis database. By adding this solution, the number of queries could be significantly reduced.