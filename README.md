# Gaming Analytics Data Challenge

This project is a small end-to-end data engineering challenge built around a CSV export. The flow is straightforward:

1. Load the raw CSV into PostgreSQL
2. Use dbt to clean and type the data in staging
3. Build a simple marts layer for reporting
4. Run tests to check business rules

The goal is to show a practical data pipeline from ingestion to reporting using Python, PostgreSQL, and dbt.

---

## Project structure

- `data/` – source CSV file
- `ingestion/ingestion.py` – script that reads the CSV and loads it into PostgreSQL
- `gaming_analytics/` – dbt project
  - `models/staging/` – cleaned and typed source data
  - `models/marts/` – business-ready aggregate views
  - `tests/` – validation checks
  - `dbt_project.yml` – dbt project config
- `.env` – local environment variables for database access
- `requirements.txt` – Python dependencies
- `orchestration/run_pipeline.py` – runs the full ingestion and dbt flow from one place

---

## Data source

The project reads a CSV file from:

- `data/Data Engineer Challenge_input.csv`

This file contains operational metrics for gaming machines, including date, venue, machine details, manufacturer, and performance numbers.

### Column types inferred from the CSV

These are the key type decisions used in the project:

- `bus_date` -> `DATE`
- `venue_code` -> `INTEGER`
- `egm_description` -> `TEXT`
- `manufacturer` -> `TEXT`
- `fp` -> `INTEGER`
- `turnover_sum` -> `NUMERIC(18,2)`
- `gmp_sum` -> `NUMERIC(18,2)`
- `games_played_sum` -> `NUMERIC(18,2)`

The reason for this is simple:

- dates are stored as date values, not strings
- IDs and counts are whole numbers
- turnover and revenue values need decimal precision so cents are preserved
- text fields like machine names and manufacturer names are not numeric and should stay as strings

---

## Installation

### 1. Install Python dependencies

From the project root, run:

```bash
pip install -r requirements.txt
```

The requirements include:

- pandas
- SQLAlchemy
- psycopg2-binary
- python-dotenv
- dbt-postgres

### 2. Set up PostgreSQL

Make sure PostgreSQL is installed and running locally.

Create a database for this project. For example:

```sql
CREATE DATABASE data_engineer_challenge;
```

Then create a schema called `raw` if needed:

```sql
CREATE SCHEMA raw;
```

### 3. Configure environment variables

Create or update the `.env` file in the project root with values like:

```env
DB_USER=postgres
DB_PASSWORD=your_password
DB_HOST=localhost
DB_PORT=5432
DB_NAME=data_engineer_challenge
```

This keeps database credentials out of the code and makes the script easier to run in different environments.

---

## Ingestion

The ingestion script is located at:

- `ingestion/ingestion.py`

What it does:

1. Loads the CSV using pandas
2. Inspects the file and the dataset structure
3. Connects to PostgreSQL using SQLAlchemy
4. Writes the raw table into the `raw` schema as `game_performance`

Run it with:

```bash
python ingestion/ingestion.py
```

This brings the raw source data into the database before any cleaning or modeling happens.

For the normal setup, the process is simple:

1. First run the script against the main challenge file to load the full raw dataset.
2. After that, if you are testing new rows or mock incremental data, run the same script again using the append mode so the historical raw data stays intact.
3. The raw table acts like a permanent landing layer, while the dbt staging model only processes new records that are newer than the latest date already in staging.

Example flow:

```powershell
python .\ingestion\ingestion.py ".\data\Data Engineer Challenge_input.csv" replace
python .\ingestion\ingestion.py ".\data\mock_incremental_rows.csv" append
```

This keeps the raw table complete while still giving you a realistic way to validate incremental behavior in the transformation layer.

---

## Testing with mock data

The incremental logic is best tested with a small set of future-dated rows. The mock file in the data folder contains a few records dated after the main dataset so they are clearly newer than the staging table's current max date.

The idea is straightforward:

1. load the full challenge CSV once so the raw layer has the base history
2. append the mock file to the raw table
3. rerun the staging model
4. confirm that only the new dates are picked up by the incremental filter

Example commands:

```powershell
git clone <repo-url>
cd <repo-folder>
python .\ingestion\ingestion.py ".\data\Data Engineer Challenge_input.csv" replace
python .\ingestion\ingestion.py ".\data\mock_incremental_rows.csv" append

cd .\gaming_analytics
dbt run --select stg_game_performance
```

The key thing to check is that the mock records are not being treated as a full reload. They should only appear in staging because they are newer than the latest date already in the table.
---

## Staging layer

The dbt project is under:

- `gaming_analytics/`

The staging model is:

- `gaming_analytics/models/staging/stg_game_performance.sql`

This is the main incremental staging model. It uses a composite key made up of:

- `bus_date`
- `venue_code`
- `egm_description`
- `manufacturer`
- `fp`

The model is configured as an incremental table, which means it only brings in rows that are newer than the latest date already in staging. This helps keep the warehouse efficient and avoids reprocessing the full raw dataset every run.

Example configuration:

```sql
config(
    materialized='incremental',
    unique_key=['bus_date', 'venue_code', 'egm_description', 'manufacturer', 'fp']
)
```

The incremental filter is:

```sql
where cast(bus_date as date) > (
    select max(cast(bus_date as date))
    from {{ this }}
)
```

This layer is also responsible for:

- casting date fields as `DATE`
- keeping identifiers as integers
- converting financial values to `NUMERIC(18,2)`
- ensuring the data is ready for downstream reporting

Example cast decisions in the staging model:

```sql
cast(bus_date as date) as bus_date
cast(turnover_sum as numeric(18,2)) as turnover_sum
cast(gmp_sum as numeric(18,2)) as gmp_sum
cast(games_played_sum as numeric(18,2) as games_played_sum
```

This matters because raw CSV values are often read as text or floats, and we want the final warehouse tables to behave consistently and predictably.

---

## Mart layer

The marts layer contains reporting-ready models:

- `daily_summary.sql` – daily totals for turnover, revenue, and games played
- `venue_turnover.sql` – total turnover grouped by venue
- `egm_venue_revenue.sql` – total revenue grouped by venue and machine

These models aggregate the cleaned staging data into business-friendly outputs for reporting and basic analysis.

---

## Tests

The project includes data quality checks for:

- valid date formats in the `bus_date` column
- positive values for `turnover_sum` and `games_played_sum`
- no missing values in key operational fields
- row completeness checks between raw and staging
- incremental logic validation with future-dated mock rows

These checks matter because invalid dates, negative operational values, or missing business keys can cause wrong reporting and break downstream logic.

The main example checks are in:

- `gaming_analytics/tests/positive_turnover.sql`
- `gaming_analytics/tests/raw_to_staging_completeness.sql`
- `gaming_analytics/models/staging/staging.yml`

The basic rule is:

```sql
where turnover_sum <= 0
```

The project also validates that the raw-to-staging row counts are complete and that the staging model behaves correctly when newer mock dates are appended.

---

## Running the full pipeline

Clone the repository to any local folder, then run the project from the repo root:

```powershell
git clone <repo-url>
cd <repo-folder>
python .\orchestration\run_pipeline.py
```

This script does the following in order:

1. Loads the main challenge file into PostgreSQL as the first raw dataset
2. Installs Python dependencies from `requirements.txt`
3. Installs the dbt package dependencies
4. Runs `dbt debug` to confirm the project is configured correctly
5. Runs `dbt run` to build the staging and mart models
6. Runs `dbt test` to validate the business checks

This is the recommended orchestration step in the project flow. It is useful because it gives one command that handles the full journey from ingestion to validation. For a normal first-time setup, you should load the challenge CSV once with the full replace mode. After that, if you want to test additional rows or mock future dates, append those rows instead of replacing the raw table. That keeps the complete raw history available while letting the incremental staging logic process only the new records.

If you want to run the steps manually instead of using the script, use:

```bash
python ingestion/ingestion.py ".\data\Data Engineer Challenge_input.csv" replace
cd gaming_analytics
dbt deps
dbt debug
dbt run
dbt test
```

If you want to run only the marts layer:

```bash
dbt run --select tag:marts
```

---

## Why this project is useful

This challenge shows a realistic workflow for a data engineering project:

- raw files are ingested from source
- data is loaded into a database
- dbt applies business logic and typing
- reporting models are built on top of cleaned data
- tests protect data quality and key business assumptions

It is a simple but strong example of building a trustworthy analytics pipeline.

## End result

The project produces a clean data pipeline that moves from raw CSV ingestion to warehouse-ready analytics models, with data validation included at the transformation stage.
