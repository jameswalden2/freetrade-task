# Freetrade Technical Test

Freetrade technical test background information.

## Storage Format

- Parquet, best used with larger files, data for 100 users is only about 20kb so inappropriate format here. When data volumes are much larger this would be more efficient for storage.
- CSV
- JSON, since the api is returning data in this format this seems like the most appropriate choice.
- <https://cloud.google.com/bigquery/docs/loading-data>
- Avro, ORC, haven't encountered either of these before, ORC seems more appropriate for the Hadoop ecosystem and Avro appears to also be better for larger datasets.