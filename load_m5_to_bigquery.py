
from google.cloud import bigquery

PROJECT_ID = "sage-sylph-508507-m2"
DATASET_ID = "m5_raw"

client = bigquery.Client(project=PROJECT_ID)

files_to_load = {
    "calendar.csv": "calendar",
    "sell_prices.csv": "sell_prices",
    "sales_train_validation.csv": "sales_train_validation",
    "sales_train_evaluation.csv": "sales_train_evaluation",
}

for filename, table_name in files_to_load.items():

    table_id = f"{PROJECT_ID}.{DATASET_ID}.{table_name}"

    job_config = bigquery.LoadJobConfig(
        source_format=bigquery.SourceFormat.CSV,
        skip_leading_rows=1,
        autodetect=True,
        write_disposition=bigquery.WriteDisposition.WRITE_TRUNCATE,
    )

    print(f"Loading {filename}...")

    with open(filename, "rb") as source_file:
        load_job = client.load_table_from_file(
            source_file,
            table_id,
            job_config=job_config,
        )

    load_job.result()

    table = client.get_table(table_id)

    print(
        f"Loaded {filename} -> {table_id} | "
        f"Rows: {table.num_rows} | Columns: {len(table.schema)}"
    )

print("All M5 raw files loaded successfully!")
