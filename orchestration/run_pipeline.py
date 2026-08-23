import subprocess
import sys
from pathlib import Path

# Project root and key file locations.
ROOT = Path(__file__).resolve().parent.parent
INGESTION_SCRIPT = ROOT / "ingestion" / "ingestion.py"
DBT_PROJECT = ROOT / "gaming_analytics"
REQUIREMENTS_FILE = ROOT / "requirements.txt"
DEFAULT_CSV_PATH = ROOT / "data" / "Data Engineer Challenge_input.csv"
DEFAULT_LOAD_MODE = "replace"


# Run a shell command and stop if it fails.
def run_command(command, cwd):
    print(f"\n>>> Running: {' '.join(command)}")
    result = subprocess.run(command, cwd=str(cwd), check=False)
    if result.returncode != 0:
        raise SystemExit(f"Command failed: {' '.join(command)}")


# Install the Python packages needed for the project before starting the job.
def install_requirements():
    if not REQUIREMENTS_FILE.exists():
        raise SystemExit(f"Requirements file not found: {REQUIREMENTS_FILE}")

    run_command([sys.executable, "-m", "pip", "install", "-r", str(REQUIREMENTS_FILE)], ROOT)


# Main flow: load the source data, then build and validate the dbt models.
def main():
    print("Starting data pipeline orchestration...")

    # Make sure the ingestion script is still where we expect it to be.
    if not INGESTION_SCRIPT.exists():
        raise SystemExit(f"Ingestion script not found: {INGESTION_SCRIPT}")

    # Always install the Python dependencies before running the pipeline.
    install_requirements()

    # Set the default CSV and mode, but allow the caller to override them if needed.
    csv_path = DEFAULT_CSV_PATH
    load_mode = DEFAULT_LOAD_MODE

    if len(sys.argv) > 1:
        csv_path = Path(sys.argv[1]).resolve()
    if len(sys.argv) > 2:
        load_mode = sys.argv[2]

    # Step 1: load the raw CSV into PostgreSQL.
    run_command([sys.executable, str(INGESTION_SCRIPT), str(csv_path), load_mode], ROOT)

    # Step 2: install dbt packages used in the transformation layer.
    run_command(["dbt", "deps"], DBT_PROJECT)

    # Step 3: check the dbt connection to Postgres before building models.
    run_command(["dbt", "debug"], DBT_PROJECT)

    # Step 4: build the staging and marts models from the cleaned raw data.
    run_command(["dbt", "run"], DBT_PROJECT)

    # Step 5: validate the data quality and business rules.
    run_command(["dbt", "test"], DBT_PROJECT)

    print("\nPipeline completed successfully.")


if __name__ == "__main__":
    main()
