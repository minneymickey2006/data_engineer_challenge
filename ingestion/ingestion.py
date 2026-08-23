import os
import sys

import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.engine import URL


# Keep the database settings outside the code so the script can run on different machines.
load_dotenv()

# Start from the main challenge CSV, but allow a different file when testing new data.
DEFAULT_CSV_PATH = "data/Data Engineer Challenge_input.csv"
CSV_PATH = os.getenv("CSV_PATH", DEFAULT_CSV_PATH)

# Full reload is used for the first import. Append keeps the raw history and adds newer rows.
LOAD_MODE = os.getenv("LOAD_MODE", "replace")

if len(sys.argv) > 1:
    CSV_PATH = sys.argv[1]

if len(sys.argv) > 2:
    LOAD_MODE = sys.argv[2]

# Database details are passed in from the environment so the script can run in different local setups.
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME")


DATABASE_URL = URL.create(
    drivername="postgresql+psycopg2",
    username=DB_USER,
    password=DB_PASSWORD,
    host=DB_HOST,
    port=int(DB_PORT),
    database=DB_NAME,
)

engine = create_engine(DATABASE_URL)


def ingest_csv():
    print(f"Reading CSV from: {CSV_PATH}")

    # The source file is a flat export, so we read it into a dataframe first and inspect it before loading.
    # The key type decisions are: bus_date is a date, venue_code and fp are whole numbers,
    # and turnover/gmp/games_played are decimals with currency-like precision.
    df = pd.read_csv(CSV_PATH)

    print(f"Rows read: {len(df)}")
    print(df.head())

    # Raw data is the landing table. We keep the full export there and decide how to handle it later.
    print(f"Loading into PostgreSQL using mode: {LOAD_MODE}")

    df.to_sql(
        name="game_performance",
        con=engine,
        schema="raw",
        if_exists=LOAD_MODE,
        index=False
    )

    print(f"CSV successfully loaded into PostgreSQL using {LOAD_MODE} mode.")


if __name__ == "__main__":
    ingest_csv()