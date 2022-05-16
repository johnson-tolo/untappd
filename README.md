# Untappd
Data project pulling data from Untappd and visualizing it
1. Untappd API - use the Untappd API to incrementally pull the diff between the user's latest number of beers tracked and the current number tracked, and write to a CSV.
2. Database - Write data to a database (Redshift? BigQuery? Something else?) using either Python or DBT Seed
3. Schedule - Set up cron job or airflow dag to run the Python script every day and write to the database of choice
4. Data Viz - Visualize data using D3
