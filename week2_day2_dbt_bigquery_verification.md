# Week 2 – Day 2
## Retail Demand Forecasting & Inventory Optimization

### Objective
Verify the dbt project setup and establish a working connection between dbt and Google BigQuery.

### Work Completed

1. Activated the existing Python virtual environment (`.venv`).

2. Verified dbt installation:
   - dbt Core: 1.12.5
   - dbt BigQuery adapter: 1.11.2

3. Verified the `retail_dbt` project structure.

4. Ran `dbt debug` to verify the BigQuery configuration and connection.

5. BigQuery connection test completed successfully:
   - Authentication: OAuth
   - GCP Project: sage-sylph-508507-m2
   - Dataset: m5_raw
   - Location: US
   - Result: All checks passed

6. Ran `dbt list` and verified that the dbt project resources were recognized successfully.

7. Ran `dbt run` to verify actual dbt execution in BigQuery.

### dbt Run Result

- 2 models executed successfully
- 1 table model created
- 1 view model created
- PASS = 2
- WARN = 0
- ERROR = 0
- SKIP = 0

### Day 2 Outcome

The dbt environment, project configuration, BigQuery connection, resource discovery, and dbt execution were successfully verified.