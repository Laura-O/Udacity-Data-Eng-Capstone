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

The crypto community focuses a lot on short-term data. A few days in crypto can feel like years. This is reasonable 
as the market changes quickly and new projects are founded every single day. However, looking into more historical 
data and understanding the bigger picture is clearly a requirement for a successful investment which is not just based on short-term luck.

There are countless data resources on the internet but they are rarely combined and matched. Considering the sheer 
amount of data this is definitely a mammoth task which would not be possible to do in a single ETL process.

## Step 2: Project scope and purpose

The data I finally used in this project contains different abbreviations and symbols for the tokens. For the ones 
saved in the same database, I am fixing this right after downloading the data from the API so the symbols are 
consistent in the database. To have a connection between the different tables, I decided to create a facts table 
containing all the used terms, a unique symbol and the full name.

## Step 3: Define the data model

![Database](assets/db.png?raw=true "ER Diagram")

The main tables in the database are setup as a fact and dimension schema. There is one fact table containing all 
the used symbols and abbreviations and dimension tables containing the associated information. This allows an easy 
connection between the different datasets as it connects the different identifiers and indexes and does not require 
additional `JOIN`s.

#### Table: `tokens`

| Column        | Description   | 
| ------------- |-------------| 
| id      | token name, primary key | 
| historical      | token name in historical data      | 
| futures | token name in futures data      |
| name | full name      |

#### Table: `fear and greed`

| Column        | Description   | 
| ------------- |-------------| 
| ts      | timestamp, primary key |
| value | index value      |
| value_classification | value class      |
| time_until_update | time until the the next entry      |

#### Table: `futures`

| Column        | Description   | 
| ------------- |-------------| 
| date          | timestamp, composite primary key | 
| symbol        | timestamp, composite primary key | 
| open | open price      |
| high      | maximum price | 
| low      | minimum price      | 
| close | closing price      | 
| volume_token      | volume of the token | 
| volume_usd      | volume in USD      | 
| exchange | exchange, composite primary key | 


#### Table: `historical`

| Column        | Description   | 
| ------------- |-------------| 
| date      | timestamp, composite primary key | 
| symbol      | token symbol, composite primary key      | 
| price | price      | 
| volume_24h      | volume in 24h      | 
| market_cap | market cap of token      | 


## Step 4: Run ETL to Model the Data

![Pipeline](assets/pipeline.png?raw=true "Pipeline")

* Load the datasets from various APIs
* Prepare the data
* Create database tables for historical data, futures, and the fear and greed index
* Insert the data into the database
* Check if the data was inserted correctly

## ETL results

This is an example query for the Bitcoin price and the fear and greed index for the last 7 days:

    SELECT date, symbol, price, value as fear_greed FROM historical h
    LEFT JOIN fg AS fg ON h.date = fg.ts
    WHERE symbol = 'btc-bitcoin' AND date > current_date - interval '8 days'


Visualizing this data in a plot:

![Plot](assets/btc-fg.png?raw=true "Plot")

# Tools

* A PostgreSQL database ([Docker image](https://hub.docker.com/_/postgres))

PostgreSQL is generally considered as the most powerful SQL database and is a standard for many use cases. Compared 
to other SQL databases it offers a lot of functionalities which make data processing easier. This includes checking 
constraints, partial indexes and also rich datatypes like arrays.

* Airflow ([Docker image](https://hub.docker.com/r/apache/airflow))

Airflow is a very helpful tool for ETL processes as it allows to set them up programmatically. This makes it 
possible to implement even complex structures and keep track of the changes by versioning them. Pipelines can be 
extended easily by adding or adjusting individual steps and without losing the history of the original pipeline.

Apart from that, Airflow has a very comfortable UI which does not only offer tools for visualizing the pipelines but 
also for debugging errors. It keeps a full log of outputs, so in case of errors, it takes a few seconds to identify 
the failed part of the pipeline and to open the log. 

## Setting up the database in Airflow and Dash

To connect the database to Airflow, you need to setup a PostgreSQL hook with the id `postgres`. To connect the 
database in Dash, please add an `.env` file with your connection parameters following the example given in `env.example`.

## Copying the DAG to airflow

To run the pipeline in your Airflow instance, just copy all files in `dags`.

## Installing and running the dashboard

Install the required packages:

    cd dash
    pip install -r requirements.txt

After this is finished, the dashboard can be started with `python app.py`.

![Dashboard](assets/dashboard.png?raw=true "Dashboard")

# Other scenarios

## The data was increased by 100x.

The data will naturally increase over time. This will clearly have an impact on the runtime of the individual steps 
of the pipeline and also on the required resources for the project.  At the moment, the database, Airflow and the 
dashboard can easily be run on a local computer. With the amount of data increased by 100x, the required space for 
the source files and also the database will increase significantly and might not be possible anymore. In this case 
it should be moved to a cloud environment.

Although PostgreSQL is capable of handling such a large amount of data, there are several ways how this could be 
improved. The easiest, most obvious solution would be scaling the database when required (i.e., when the workload is 
high). Additionally, [creating a cluster](https://www.postgresql.org/docs/9.1/sql-cluster.html) for the most used 
tables and indexes will also speed up database processed significantly. 

As the most time-consuming steps of the pipeline can be run in parallel, the runtime of the pipeline will be 
increased, but as it is run only once a day, this will not cause a problem.

## The pipelines would be run on a daily basis by 7 am every day.

The pipeline will work as planned.

## The database needed to be accessed by 100+ people.

When more users are accessing the dashboard, some caching solution should be added. Dash can be used with 
Flask-Caching to save results to either your filesystem or a Redis database. By adding this solution, the number of 
queries could be significantly reduced.

If direct database access is needed, it will be a good idea to separate the database for the dashboard and direct 
access by replicating it. Queries run by the dashboard are known and the workload for these can be tested  and 
predicted. Giving developers direct access to this database directly can cause unwanted peaks and might even make the 
dashboard unavailable. This could be prevented by using two separated databases. In this case, the replication could 
be a step in the Airflow pipeline. As an additional optimization step, this would also allow to implement specific 
improvements for both use cases.
