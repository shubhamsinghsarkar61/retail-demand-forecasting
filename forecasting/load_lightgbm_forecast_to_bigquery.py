from google.cloud import bigquery

PROJECT_ID = "sage-sylph-508507-m2"
DATASET_ID = "m5_raw"
TABLE_ID = "lightgbm_forecast"

client = bigquery.Client(project=PROJECT_ID)

file_path = "outputs/lightgbm_forecast.csv"

table_ref = f"{PROJECT_ID}.{DATASET_ID}.{TABLE_ID}"

job_config = bigquery.LoadJobConfig(
    source_format=bigquery.SourceFormat.CSV,
    skip_leading_rows=1,
    autodetect=True,
    write_disposition=bigquery.WriteDisposition.WRITE_TRUNCATE,
)

print("Loading LightGBM forecast into BigQuery...")

with open(file_path, "rb") as source_file:
    load_job = client.load_table_from_file(
        source_file,
        table_ref,
        job_config=job_config,
    )

load_job.result()

table = client.get_table(table_ref)

print(f"Loaded successfully: {table_ref}")
print(f"Rows: {table.num_rows}")
print(f"Columns: {len(table.schema)}")
print("Day 7 BigQuery forecast load completed successfully.")