---
title: "Use liquid clustering for tables | Databricks on AWS"
source: "https://docs.databricks.com/aws/en/delta/clustering"
author:
published: 2026-03-13
created: 2026-03-31
description: "Use liquid clustering to simplify data layout decisions and optimize query performance without partitioning."
tags:
  - "clippings"
---
Liquid clustering is a data layout optimization technique that replaces table partitioning and `ZORDER`. It simplifies table management and optimizes query performance by automatically organizing data based on clustering keys.

Unlike traditional partitioning, you can redefine clustering keys without rewriting existing data. This allows your data layout to evolve alongside changing analytic needs. Liquid clustering applies to both streaming tables and materialized views.

> [!-info] -info
> important
> 
> Liquid clustering is generally available for Delta Lake tables and in Public Preview for managed Apache Iceberg tables. For Delta Lake tables, GA support is available with Databricks Runtime 15.2 and above. Databricks recommends using the latest Databricks Runtime for the best performance. For Apache Iceberg tables, Databricks Runtime 16.4 LTS and above is required.

## When to use liquid clustering

Databricks recommends liquid clustering for all new tables, including streaming tables and materialized views. The following scenarios particularly benefit from clustering:

- Tables that are often filtered by high cardinality columns.
- Tables that have skew in data distribution.
- Tables that grow quickly and require maintenance and tuning effort.
- Tables that have concurrent write requirements.
- Tables that have access patterns that change over time.
- Tables where a typical partition key could leave the table with too many or too few partitions.

## Enable liquid clustering

You can enable liquid clustering on an existing unpartitioned table or during table creation. Clustering is not compatible with partitioning or `ZORDER`. Databricks recommends allowing the platform to manage all layout and optimization operations for data in your table. After enabling liquid clustering, run `OPTIMIZE` jobs to incrementally cluster data. See [How to trigger clustering](https://docs.databricks.com/aws/en/delta/clustering#optimize).

### Create tables with clustering

To enable liquid clustering, add the `CLUSTER BY` phrase to a table creation statement, as in the examples below. In Databricks Runtime 14.2 and above, you can use DataFrame APIs and DeltaTable API in Python or Scala to enable liquid clustering for Delta Lake tables.

- SQL
- Python
- Scala

```sql
SQL-- Create an empty Delta table with clustering on col0
CREATE TABLE table1(col0 INT, col1 string) CLUSTER BY (col0);

-- Create table from existing data with clustering
-- Note: CLUSTER BY must appear after table name, not in SELECT clause
CREATE TABLE table2 CLUSTER BY (col0)
AS SELECT * FROM table1;

-- Copy table structure including clustering configuration
CREATE TABLE table3 LIKE table1;
```

> [!-info] -info
> important
> 
> When using DataFrame APIs to set clustering keys, you can only specify clustering columns during table creation or when using `overwrite` mode (such as with `CREATE OR REPLACE TABLE` operations). You cannot change clustering keys when using `append` mode.
> 
> To change clustering keys on an existing table while appending data, use SQL `ALTER TABLE` commands to modify the clustering configuration separately from your data write operations. See [Change clustering keys](https://docs.databricks.com/aws/en/delta/clustering#change-clustering-keys).

In Databricks Runtime 16.0 and above, you can create tables with liquid clustering enabled using Structured Streaming writes. Databricks recommends using Databricks Runtime 16.4 and above for the best performance, as in the following examples:

- SQL
- Python
- Scala

```sql
SQLCREATE TABLE table1 (
  col0 STRING,
  col1 DATE,
  col2 BIGINT
)
CLUSTER BY (col0, col1);
```

> [!-warning] -warning
> warning
> 
> Delta tables with liquid clustering enabled use Delta writer version 7 and reader version 3. Delta clients that don't support these protocols cannot read these tables. You cannot downgrade table protocol versions. See [Delta Lake feature compatibility and protocols](https://docs.databricks.com/aws/en/delta/feature-compatibility).
> 
> To override default feature enablement (such as deletion vectors), see [Override default feature enablement (optional)](https://docs.databricks.com/aws/en/delta/clustering#override).

### Enable on existing tables

Enable liquid clustering on an existing unpartitioned Delta table using the following syntax:

```sql
SQL-- Alter an existing table
ALTER TABLE <table_name>
CLUSTER BY (<clustering_columns>)
```

For Apache Iceberg, you must explicitly disable deletion vectors and Row IDs when enabling liquid clustering on an existing managed Iceberg table.

> [!-secondary] -secondary
> note
> 
> The default behavior does not apply clustering to previously written data. To force reclustering for all records, you must use `OPTIMIZE FULL`. See [Force reclustering for all records](https://docs.databricks.com/aws/en/delta/clustering#optimize-full).

### Remove clustering keys

To remove clustering keys, use the following syntax:

```sql
SQLALTER TABLE table_name CLUSTER BY NONE;
```

## Choose clustering keys

> [!-success] -success
> tip
> 
> Databricks recommends using automatic liquid clustering for supported tables, which intelligently selects clustering keys based on your query patterns. See [Automatic liquid clustering](https://docs.databricks.com/aws/en/delta/clustering#auto-liquid).

### Key selection guidelines

When you manually specify clustering keys, choose columns based on the columns most frequently used in query filters. You can define clustering keys in any order. If two columns are highly correlated, you only need to include one of them as a clustering key.

You can specify **up to four clustering keys**. For smaller tables (under 10 TB), using more clustering keys can degrade performance when filtering on a single column. For example, filtering with four keys performs worse than filtering with two keys. However, as table size increases, this performance difference becomes negligible for single-column queries.

Clustering keys must be columns that have statistics collected. By default, the first 32 columns in a Delta table have statistics collected. See [Specify statistics columns](https://docs.databricks.com/aws/en/delta/data-skipping#stats-cols).

### Supported data types

Clustering supports these data types for clustering keys:

- Date
- Timestamp
- TimestampNTZ (Databricks Runtime 14.3 LTS and above)
- String
- Integer, Long, Short, Byte
- Float, Double, Decimal

### Migrating from partitioning or Z-order

If you're converting an existing table, consider the following recommendations:

| Current data optimization technique | Recommendation for clustering keys |
| --- | --- |
| Hive-style partitioning | Use partition columns as clustering keys. |
| Z-order indexing | Use the `ZORDER BY` columns as clustering keys. |
| Hive-style partitioning and Z-order | Use both partition columns and `ZORDER BY` columns as clustering keys. |
| Generated columns to reduce cardinality (for example, date for a timestamp) | Use the original column as a clustering key, and don't create a generated column. |

## Automatic liquid clustering

In Databricks Runtime 15.4 LTS and above, you can enable automatic liquid clustering for Unity Catalog managed Delta tables. Automatic liquid clustering allows Databricks to intelligently choose clustering keys to optimize query performance, using the `CLUSTER BY AUTO` clause.

### How automatic liquid clustering works

Automatic liquid clustering provides intelligent optimization based on your usage patterns:

- **Requires predictive optimization**: Automatic key selection and clustering operations run asynchronously as a maintenance operation. See [Predictive optimization for Unity Catalog managed tables](https://docs.databricks.com/aws/en/optimizations/predictive-optimization).
- **Analyzes query workload**: Databricks analyzes the table's historical query workload and identifies the best candidate columns for clustering.
- **Adapts to changes**: If your query patterns or data distributions change over time, automatic liquid clustering selects new keys to optimize performance.
- **Cost-aware selection**: Databricks changes clustering keys only when the predicted cost savings from data skipping improvements outweigh the data clustering cost.

Automatic liquid clustering might not select keys for the following reasons:

- The table is too small to benefit from liquid clustering.
- The table already has an effective clustering scheme, either from previous manual keys or natural insertion order that matches query patterns.
- The table does not have frequent queries.
- You are not using Databricks Runtime 15.4 LTS or above.

You can apply automatic liquid clustering for all Unity Catalog managed tables, regardless of data and query characteristics. The heuristics decide whether it's cost-beneficial to select clustering keys.

### Databricks Runtime version compatibility

You can read or write tables with automatic clustering enabled from all Databricks Runtime versions that support liquid clustering. However, intelligent key selection relies on metadata introduced in Databricks Runtime 15.4 LTS.

Use Databricks Runtime 15.4 LTS or above to ensure that automatically selected keys benefit all of your workloads and that these workloads are considered when selecting new keys.

### Enable or disable automatic liquid clustering

To enable or disable automatic liquid clustering on a new or existing table, use the following syntax:

- SQL
- Python

```sql
SQL-- Create an empty table.
CREATE OR REPLACE TABLE table1(column01 int, column02 string) CLUSTER BY AUTO;

-- Enable automatic liquid clustering on an existing table,
-- including tables that previously had manually specified keys.
ALTER TABLE table1 CLUSTER BY AUTO;

-- Disable automatic liquid clustering on an existing table.
ALTER TABLE table1 CLUSTER BY NONE;

-- Disable automatic liquid clustering by setting the clustering keys
-- to chosen clustering columns or new columns.
ALTER TABLE table1 CLUSTER BY (column01, column02);
```

If you run `CREATE OR REPLACE table_name` without specifying `CLUSTER BY AUTO` and the table already exists and has automatic liquid clustering enabled, the `AUTO` setting is disabled and clustering columns are not preserved. To preserve automatic liquid clustering and any previously selected clustering columns, include `CLUSTER BY AUTO` in the replace statement. When preserved, predictive optimization maintains the historical query workload for the table to identify the best clustering keys.

### Check if automatic clustering is enabled

To check if a table has automatic liquid clustering enabled, use [`DESCRIBE TABLE`](https://docs.databricks.com/aws/en/sql/language-manual/sql-ref-syntax-aux-describe-table) or [`SHOW TBLPROPERTIES`](https://docs.databricks.com/aws/en/sql/language-manual/sql-ref-syntax-aux-show-tblproperties).

If automatic liquid clustering is enabled, the `clusterByAuto` property is set to `true`. The `clusteringColumns` property shows the current clustering columns that were automatically or manually selected.

### Limitations

Automatic liquid clustering is not available for Apache Iceberg.

## Write data to a clustered table

To write to a clustered Delta table, you must use a Delta writer client that supports all Delta write protocol table features used by liquid clustering. To write to a clustered Iceberg table, you can use Unity Catalog's Iceberg REST Catalog API. On Databricks, you must use Databricks Runtime 13.3 LTS and above.

### Operations that support clustering on write

Operations that cluster on write include the following:

- `INSERT INTO` operations
- `CTAS` and `RTAS` statements
- `COPY INTO` from Parquet format
- `spark.write.mode("append")`

### Size thresholds for clustering

Clustering on write only triggers when data in the transaction meets a size threshold. These thresholds vary by the number of clustering columns and are lower for Unity Catalog managed tables than other Delta tables.

| Number of clustering columns | Threshold size for Unity Catalog managed tables | Threshold size for other Delta tables |
| --- | --- | --- |
| 1 | 64 MB | 256 MB |
| 2 | 256 MB | 1 GB |
| 3 | 512 MB | 2 GB |
| 4 | 1 GB | 4 GB |

Because not all operations apply liquid clustering, Databricks recommends frequently running `OPTIMIZE` to ensure that all data is efficiently clustered.

### Streaming workloads

Structured Streaming workloads support clustering on write when you set the Spark config `spark.databricks.delta.liquid.eagerClustering.streaming.enabled` to `true`. Clustering for these workloads only triggers if at least one of the last five streaming updates exceeds a size threshold from the table above.

## How to trigger clustering

Predictive optimization automatically runs OPTIMIZE commands for enabled tables. See [Predictive optimization for Unity Catalog managed tables](https://docs.databricks.com/aws/en/optimizations/predictive-optimization). When using Predictive optimization, Databricks recommends disabling any scheduled OPTIMIZE jobs.

To trigger clustering, you must use Databricks Runtime 13.3 LTS or above. Databricks recommends Databricks Runtime 17.2 and above for faster OPTIMIZE performance on large tables. Use the `OPTIMIZE` command on your table:

```sql
SQLOPTIMIZE table_name;
```

Liquid clustering is **incremental**, meaning that `OPTIMIZE` only rewrites data as necessary to accommodate data that needs clustering. `OPTIMIZE` does not rewrite data files with clustering keys that do not match the data being clustered. See [Force reclustering for all records](https://docs.databricks.com/aws/en/delta/clustering#optimize-full).

If you are not using predictive optimization, Databricks recommends scheduling regular `OPTIMIZE` jobs to cluster data. For tables experiencing many updates or inserts, Databricks recommends scheduling an `OPTIMIZE` job every one or two hours. Because liquid clustering is incremental, most `OPTIMIZE` jobs for clustered tables run quickly.

## Force reclustering for all records

In Databricks Runtime 16.0 and above, you can force reclustering of all records in a table with the following syntax:

```sql
SQLOPTIMIZE table_name FULL;
```

> [!-info] -info
> important
> 
> Running `OPTIMIZE FULL` reclusters all existing data as necessary. For large tables that have not previously been clustered on the specified keys, this operation might take hours.

Run **`OPTIMIZE FULL`** when you enable clustering for the first time or change clustering keys. If you have previously run `OPTIMIZE FULL` and there has been no change to clustering keys, `OPTIMIZE FULL` runs the same as `OPTIMIZE`. In this scenario, `OPTIMIZE` uses an incremental approach and only rewrites files that haven't previously been compacted. Always use `OPTIMIZE FULL` to ensure that data layout reflects the current clustering keys.

## Read data from a clustered table

You can read data in a clustered Delta table using any Delta Lake client that supports reading deletion vectors. Using the Iceberg REST Catalog API, you can read data in a clustered Iceberg table. Liquid clustering improves query performance through automatic data skipping when filtering on clustering keys.

```sql
SQLSELECT * FROM table_name WHERE cluster_key_column_name = "some_value";
```

## Manage clustering keys

### See how a table is clustered

You can use `DESCRIBE` commands to see the clustering keys for a table, as in the following examples:

```sql
SQLDESCRIBE TABLE table_name;

DESCRIBE DETAIL table_name;
```

### Change clustering keys

You can change clustering keys for a table at any time by running an `ALTER TABLE` command, as in the following example:

```sql
SQLALTER TABLE table_name CLUSTER BY (new_column1, new_column2);
```

When you change clustering keys, subsequent `OPTIMIZE` and write operations use the new clustering approach, but existing data is not rewritten. To rewrite existing data with the updated clustering keys, see [Force reclustering for all records](https://docs.databricks.com/aws/en/delta/clustering#optimize-full).

You can also turn off clustering by setting the keys to `NONE`, as in the following example:

```sql
SQLALTER TABLE table_name CLUSTER BY NONE;
```

Setting cluster keys to `NONE` does not rewrite clustered data, but prevents future `OPTIMIZE` operations from using clustering keys.

## Use liquid clustering from an external engine

You can enable liquid clustering on managed Iceberg tables from external Iceberg engines. To enable liquid clustering, specify partition columns when creating a table. Unity Catalog interprets the partitions as clustering keys. For example, run the command below in OSS Spark:

```sql
SQLCREATE OR REPLACE TABLE main.schema.icebergTable
PARTITIONED BY c1;
```

You can disable liquid clustering:

```sql
SQLALTER TABLE main.schema.icebergTable DROP PARTITION FIELD c2;
```

You can change clustering keys using Iceberg partition evolution:

```sql
SQLALTER TABLE main.schema.icebergTable ADD PARTITION FIELD c2;
```

If you specify a partition using a bucket transform, Unity Catalog drops the expression and uses the column as a clustering key:

```sql
SQLCREATE OR REPLACE TABLE main.schema.icebergTable
PARTITIONED BY (bucket(c1, 10));
```

## Compatibility for tables with liquid clustering

Liquid clustering uses Delta table features that require specific Databricks Runtime versions for reading and writing. Tables created with liquid clustering in Databricks Runtime 14.1 and above use v2 checkpoints by default. You can read and write tables with v2 checkpoints in Databricks Runtime 13.3 LTS and above.

You can disable v2 checkpoints and downgrade table protocols to read tables with liquid clustering in Databricks Runtime 12.2 LTS and above. See [Drop a Delta Lake table feature and downgrade table protocol](https://docs.databricks.com/aws/en/delta/drop-feature).

## Override default feature enablement (optional)

You can override default Delta table feature enablement during liquid clustering enablement. This prevents the reader and writer protocols associated with those table features from being upgraded. You must have an existing table to complete the following steps:

1. Use `ALTER TABLE` to set the table property that disables one or more features. For example, to disable deletion vectors run the following:
	```sql
	SQLALTER TABLE table_name SET TBLPROPERTIES ('delta.enableDeletionVectors' = false);
	```
2. Enable liquid clustering on the table by running the following:
	```sql
	SQLALTER TABLE <table_name>
	CLUSTER BY (<clustering_columns>)
	```

The following table provides information on the Delta features you can override and how enablement impacts compatibility with Databricks Runtime versions.

| Delta feature | Runtime compatibility | Property to override enablement | Impact if disabled to liquid clustering |
| --- | --- | --- | --- |
| Deletion vectors | Reads and writes require Databricks Runtime 12.2 LTS and above. | `'delta.enableDeletionVectors' = false` | Disabling deletion vectors disables row-level concurrency, making transactions and clustering operations more likely to conflict. See [Row-level concurrency](https://docs.databricks.com/aws/en/optimizations/isolation/row-level-concurrency).  `DELETE`, `MERGE`, and `UPDATE` commands might run slower. |
| Row tracking | Writes require Databricks Runtime 13.3 LTS and above. Can be read from any Databricks Runtime version. | `'delta.enableRowTracking' = false` | Disabling row tracking disables row-level concurrency, making transactions and clustering operations more likely to conflict. See [Row-level concurrency](https://docs.databricks.com/aws/en/optimizations/isolation/row-level-concurrency). |
| Checkpoints V2 | Reads and writes require Databricks Runtime 13.3 LTS and above. | `'delta.checkpointPolicy' = 'classic'` | No impact on liquid clustering behavior. |

## Limitations

- **Databricks Runtime 15.1 and below**: Clustering on write does not support source queries that include filters, joins, or aggregations.
- **Databricks Runtime 15.4 LTS and below**: You cannot create a table with liquid clustering enabled using a Structured Streaming write. You can use Structured Streaming to write data to an existing table with liquid clustering enabled.
- **Apache Iceberg v2**: Row-level concurrency is not supported on managed Iceberg tables with Apache Iceberg v2, as deletion vectors and row tracking are not supported on Iceberg tables.