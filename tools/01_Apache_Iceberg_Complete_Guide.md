# 🧊 Apache Iceberg - Complete Guide

> **"The open table format for analytic datasets"**

---

## 📑 Mục Lục

1. [Giới Thiệu & Lịch Sử](#-giới-thiệu--lịch-sử)
2. [Kiến Trúc Chi Tiết](#-kiến-trúc-chi-tiết)
3. [Core Concepts](#-core-concepts)
4. [Tính Năng Quan Trọng](#-tính-năng-quan-trọng)
5. [Hands-on Code Examples](#-hands-on-code-examples)
6. [Use Cases Thực Tế](#-use-cases-thực-tế)
7. [Best Practices](#-best-practices)
8. [Performance Tuning](#-performance-tuning)
9. [Troubleshooting](#-troubleshooting)
10. [Production Deployment](#-production-deployment)

---

## 🌟 Giới Thiệu & Lịch Sử

### Iceberg là gì?

Apache Iceberg là một **open table format** cho huge analytic datasets. Nó được thiết kế để mang lại sự tin cậy và đơn giản của SQL tables đến big data, đồng thời cho phép nhiều engines (Spark, Trino, Flink, Presto, Hive, Impala) làm việc an toàn với cùng một tables, tại cùng thời điểm.

### Lịch Sử Phát Triển

**2017** - Netflix bắt đầu phát triển Iceberg để thay thế Hive tables

**2018** - Open-source tại Netflix, giải quyết vấn đề petabyte-scale

**2019** - Donated cho Apache Software Foundation (Incubating)

**2020** - Graduated thành Top-Level Apache Project

**2021** - Apple, LinkedIn, Alibaba adoption; Version 0.12

**2022** - Version 1.0 - First stable release; Snowflake support

**2023** - Version 1.3-1.4; BigQuery, Athena native support

**2024** - Version 1.5-1.8; REST Catalog spec, PyIceberg maturity

**2025** - Version 1.10.0; Industry standard, universal adoption

### Tại sao Netflix tạo ra Iceberg?

**Vấn đề với Hive Tables:**
- Không có ACID transactions
- Partition pruning yêu cầu users biết physical layout
- Schema evolution khó khăn
- Slow listing operations trên S3
- Không reliable với concurrent writes

**Giải pháp của Iceberg:**
- ACID với optimistic concurrency
- Hidden partitioning
- Full schema evolution
- Metadata layer thay vì file listing
- Safe concurrent reads/writes

### Founders & Key Contributors

**Ryan Blue**
- Role: Creator, Lead Architect
- Journey: Netflix → Apple → Tabular

**Daniel Weeks**
- Role: Core contributor
- Organization: Netflix

**Owen O'Malley**
- Role: Contributor
- Organization: Apple

**Anton Okolnychyi**
- Role: Core contributor
- Organization: Apple

**Russell Spitzer**
- Role: Spark integration lead
- Organization: Datastax

**Szehon Ho**
- Role: Maintenance lead
- Organization: Apple

---

## 🏗️ Kiến Trúc Chi Tiết

### Tổng Quan Kiến Trúc

```
┌─────────────────────────────────────────────────────────────────────┐
│                        Query Engines                                 │
│         (Spark, Flink, Trino, Presto, Dremio, StarRocks)            │
└────────────────────────────┬────────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────────┐
│                         Iceberg API                                  │
│                  (Java, Python, Rust, Go, C++)                       │
└────────────────────────────┬────────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────────┐
│                          Catalog                                     │
│    (Hive Metastore, AWS Glue, REST, Nessie, JDBC, Hadoop, Custom)   │
└────────────────────────────┬────────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────────┐
│                      Iceberg Metadata                                │
│                                                                      │
│  ┌──────────────────────────────────────────────────────────────┐   │
│  │                    Catalog Pointer                            │   │
│  │                (points to current metadata)                   │   │
│  └──────────────────────────┬───────────────────────────────────┘   │
│                              ▼                                       │
│  ┌──────────────────────────────────────────────────────────────┐   │
│  │                  Metadata File (JSON)                         │   │
│  │  • Table schema                                               │   │
│  │  • Partition spec                                             │   │
│  │  • Current snapshot ID                                        │   │
│  │  • Snapshot history                                           │   │
│  │  • Properties                                                 │   │
│  └──────────────────────────┬───────────────────────────────────┘   │
│                              ▼                                       │
│  ┌──────────────────────────────────────────────────────────────┐   │
│  │                   Snapshot                                    │   │
│  │  • Snapshot ID                                                │   │
│  │  • Timestamp                                                  │   │
│  │  • Manifest list location                                     │   │
│  │  • Summary (added/deleted files)                              │   │
│  └──────────────────────────┬───────────────────────────────────┘   │
│                              ▼                                       │
│  ┌──────────────────────────────────────────────────────────────┐   │
│  │                   Manifest List (Avro)                        │   │
│  │  • List of manifest files                                     │   │
│  │  • Partition summaries per manifest                           │   │
│  └──────────────────────────┬───────────────────────────────────┘   │
│                              ▼                                       │
│  ┌──────────────────────────────────────────────────────────────┐   │
│  │                   Manifest Files (Avro)                       │   │
│  │  • Data file paths                                            │   │
│  │  • Partition values                                           │   │
│  │  • Column-level statistics (min/max/null count)               │   │
│  │  • File size, record count                                    │   │
│  └──────────────────────────────────────────────────────────────┘   │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────────┐
│                        Data Files                                    │
│              (Parquet, ORC, Avro on Object Storage)                  │
│                     (S3, GCS, ADLS, HDFS, MinIO)                     │
└─────────────────────────────────────────────────────────────────────┘
```

### Metadata Layer Chi Tiết

#### 1. Metadata File (JSON)

```json
{
  "format-version": 2,
  "table-uuid": "bf289591-dcc0-4234-ad4f-5c3ded97f4c0",
  "location": "s3://my-bucket/my-table",
  "last-sequence-number": 34,
  "last-updated-ms": 1702396800000,
  "last-column-id": 12,
  "current-schema-id": 0,
  "schemas": [...],
  "default-spec-id": 0,
  "partition-specs": [...],
  "default-sort-order-id": 0,
  "sort-orders": [...],
  "properties": {
    "write.format.default": "parquet",
    "write.metadata.compression-codec": "gzip"
  },
  "current-snapshot-id": 3051729675574597004,
  "refs": {
    "main": {
      "snapshot-id": 3051729675574597004,
      "type": "branch"
    }
  },
  "snapshots": [...],
  "snapshot-log": [...],
  "metadata-log": [...]
}
```

#### 2. Snapshot Structure

```json
{
  "snapshot-id": 3051729675574597004,
  "parent-snapshot-id": 3051729675574597003,
  "sequence-number": 34,
  "timestamp-ms": 1702396800000,
  "manifest-list": "s3://my-bucket/my-table/metadata/snap-3051729675574597004.avro",
  "summary": {
    "operation": "append",
    "added-data-files": "5",
    "added-records": "1000000",
    "added-files-size": "52428800"
  },
  "schema-id": 0
}
```

#### 3. Manifest List Entry

```
┌─────────────────────────────────────────────────────────────────┐
│ manifest_path: s3://bucket/table/metadata/manifest-abc123.avro  │
│ manifest_length: 8192                                           │
│ partition_spec_id: 0                                            │
│ content: DATA                                                   │
│ sequence_number: 34                                             │
│ min_sequence_number: 1                                          │
│ added_snapshot_id: 3051729675574597004                          │
│ added_files_count: 5                                            │
│ existing_files_count: 0                                         │
│ deleted_files_count: 0                                          │
│ added_rows_count: 1000000                                       │
│ existing_rows_count: 0                                          │
│ deleted_rows_count: 0                                           │
│ partitions: [                                                   │
│   {contains_null: false, lower_bound: "2024-01-01",             │
│    upper_bound: "2024-01-31"}                                   │
│ ]                                                               │
└─────────────────────────────────────────────────────────────────┘
```

#### 4. Manifest File Entry

```
┌─────────────────────────────────────────────────────────────────┐
│ status: ADDED                                                   │
│ data_file: {                                                    │
│   content: DATA                                                 │
│   file_path: s3://bucket/table/data/part-00001.parquet          │
│   file_format: PARQUET                                          │
│   partition: {date: "2024-01-15"}                               │
│   record_count: 200000                                          │
│   file_size_in_bytes: 10485760                                  │
│   column_sizes: {1: 2097152, 2: 1048576, ...}                   │
│   value_counts: {1: 200000, 2: 200000, ...}                     │
│   null_value_counts: {1: 0, 2: 500, ...}                        │
│   nan_value_counts: {}                                          │
│   lower_bounds: {1: "AAA", 2: 0, ...}                           │
│   upper_bounds: {1: "ZZZ", 2: 99999, ...}                       │
│   split_offsets: [4, 134217728, 268435456]                      │
│   sort_order_id: 0                                              │
│ }                                                               │
└─────────────────────────────────────────────────────────────────┘
```

---

## 📚 Core Concepts

### 1. Snapshots

**Snapshot** là một state của table tại một thời điểm cụ thể - danh sách tất cả data files tạo nên table.

```
Snapshot Timeline:
                                                        
    Snap-1        Snap-2        Snap-3        Snap-4   (current)
    ┌───┐         ┌───┐         ┌───┐         ┌───┐
    │ A │────────►│A+B│────────►│A+C│────────►│A+D│
    └───┘         └───┘         └───┘         └───┘
    (init)        (add B,       (delete B,   (add D)
                   append)       add C)

- Mỗi snapshot là immutable
- Snapshots cho phép time travel
- Old snapshots được cleanup bởi expiration
```

### 2. Partitioning

#### Traditional Partitioning (Hive-style) - VẤN ĐỀ

```sql
-- Users phải biết partition columns
SELECT * FROM events
WHERE year = 2024 AND month = 1 AND day = 15;

-- Nếu query sai format → full scan!
SELECT * FROM events
WHERE event_date = '2024-01-15';  -- FULL TABLE SCAN!
```

#### Iceberg Hidden Partitioning - GIẢI PHÁP

```sql
-- Iceberg tự động áp dụng partition transforms
CREATE TABLE events (
    event_id BIGINT,
    event_date DATE,
    event_type STRING,
    payload STRING
) USING iceberg
PARTITIONED BY (days(event_date));

-- Users chỉ cần query natural columns
SELECT * FROM events
WHERE event_date = '2024-01-15';  -- Iceberg tự động prune!

SELECT * FROM events
WHERE event_date BETWEEN '2024-01-01' AND '2024-01-31';  -- Cũng prune!
```

#### Partition Transforms

**identity** - Giữ nguyên value
- Example: `identity(country)` → "USA", "VN"

**year** - Extract year từ timestamp/date
- Example: `year(ts)` → 2024

**month** - Extract year-month
- Example: `month(ts)` → 2024-01

**day** - Extract year-month-day
- Example: `day(ts)` → 2024-01-15

**hour** - Extract đến hour
- Example: `hour(ts)` → 2024-01-15-08

**bucket** - Hash bucket cho high-cardinality columns
- Example: `bucket(16, user_id)` → 0-15

**truncate** - Truncate string/number
- Example: `truncate(10, name)` → first 10 chars

### 3. Schema Evolution

```sql
-- Add column
ALTER TABLE my_table ADD COLUMN new_col STRING;

-- Rename column
ALTER TABLE my_table RENAME COLUMN old_name TO new_name;

-- Drop column
ALTER TABLE my_table DROP COLUMN unused_col;

-- Reorder columns
ALTER TABLE my_table ALTER COLUMN col_a FIRST;
ALTER TABLE my_table ALTER COLUMN col_b AFTER col_a;

-- Change type (nếu compatible)
ALTER TABLE my_table ALTER COLUMN int_col TYPE BIGINT;
```

**Schema Evolution Rules:**
- ✅ Có thể add columns
- ✅ Có thể delete columns
- ✅ Có thể rename columns
- ✅ Có thể reorder columns
- ✅ Có thể widen types (int → long, float → double)
- ❌ KHÔNG thể narrow types hoặc change incompatible types

### 4. Partition Evolution

```sql
-- Initial partitioning: by month
CREATE TABLE events (...) PARTITIONED BY (month(event_date));

-- Sau này data tăng, cần partition by day
ALTER TABLE events ADD PARTITION FIELD day(event_date);
ALTER TABLE events DROP PARTITION FIELD month(event_date);

-- Không cần rewrite data cũ!
-- Data mới sẽ dùng partition mới
-- Query tự động handle cả hai layouts
```

### 5. Branching & Tagging

```sql
-- Create branch
ALTER TABLE my_table CREATE BRANCH audit_branch;

-- Write to branch
INSERT INTO my_table.branch_audit_branch VALUES (...);

-- Create tag (immutable reference)
ALTER TABLE my_table CREATE TAG release_v1 AS OF VERSION 12345;

-- Query from branch/tag
SELECT * FROM my_table VERSION AS OF 'audit_branch';
SELECT * FROM my_table VERSION AS OF 'release_v1';

-- Fast-forward merge
ALTER TABLE my_table 
  EXECUTE fast_forward('audit_branch');
```

---

## ⚡ Tính Năng Quan Trọng

### 1. Time Travel

```sql
-- Query tại snapshot ID
SELECT * FROM my_table VERSION AS OF 12345678901234;

-- Query tại timestamp
SELECT * FROM my_table TIMESTAMP AS OF '2024-01-15 10:30:00';
```

```python
# Spark DataFrameReader
spark.read \
    .option("snapshot-id", 12345678901234L) \
    .table("my_table")

spark.read \
    .option("as-of-timestamp", "1705312200000") \
    .table("my_table")
```

### 2. Rollback

```sql
-- Rollback to snapshot
CALL catalog.system.rollback_to_snapshot('db.my_table', 12345678901234);

-- Rollback to timestamp
CALL catalog.system.rollback_to_timestamp('db.my_table', TIMESTAMP '2024-01-15 10:30:00');

-- Set current snapshot (tương đương rollback)
CALL catalog.system.set_current_snapshot('db.my_table', 12345678901234);
```

### 3. Expressive SQL Operations

#### MERGE INTO (Upsert)

```sql
MERGE INTO target_table t
USING source_table s
ON t.id = s.id
WHEN MATCHED AND s.op = 'DELETE' THEN DELETE
WHEN MATCHED AND s.op = 'UPDATE' THEN UPDATE SET *
WHEN NOT MATCHED THEN INSERT *;
```

#### UPDATE

```sql
UPDATE my_table
SET status = 'processed', updated_at = current_timestamp()
WHERE status = 'pending' AND created_at < '2024-01-01';
```

#### DELETE

```sql
DELETE FROM my_table
WHERE event_date < '2023-01-01';
```

### 4. Incremental Read

```python
# Read changes between snapshots (Spark)
spark.read \
    .option("start-snapshot-id", 1234567890) \
    .option("end-snapshot-id", 9876543210) \
    .table("my_table")

# Streaming read của changes
spark.readStream \
    .option("stream-from-timestamp", "2024-01-01 00:00:00") \
    .table("my_table")
```

---

## 💻 Hands-on Code Examples

### PySpark Setup

```python
from pyspark.sql import SparkSession

# Tạo Spark session với Iceberg
spark = SparkSession.builder \
    .appName("IcebergExample") \
    .config("spark.jars.packages", 
            "org.apache.iceberg:iceberg-spark-runtime-3.5_2.12:1.10.0") \
    .config("spark.sql.extensions", 
            "org.apache.iceberg.spark.extensions.IcebergSparkSessionExtensions") \
    .config("spark.sql.catalog.spark_catalog", 
            "org.apache.iceberg.spark.SparkSessionCatalog") \
    .config("spark.sql.catalog.spark_catalog.type", "hive") \
    .config("spark.sql.catalog.local", 
            "org.apache.iceberg.spark.SparkCatalog") \
    .config("spark.sql.catalog.local.type", "hadoop") \
    .config("spark.sql.catalog.local.warehouse", "/tmp/warehouse") \
    .getOrCreate()
```

### Create Table

```python
# SQL way
spark.sql("""
    CREATE TABLE local.db.events (
        event_id BIGINT,
        event_type STRING,
        user_id BIGINT,
        event_time TIMESTAMP,
        properties MAP<STRING, STRING>
    )
    USING iceberg
    PARTITIONED BY (days(event_time), bucket(16, user_id))
    TBLPROPERTIES (
        'write.format.default' = 'parquet',
        'write.parquet.compression-codec' = 'zstd'
    )
""")
```

```python
# DataFrame way
from pyspark.sql.types import *

schema = StructType([
    StructField("event_id", LongType(), False),
    StructField("event_type", StringType(), True),
    StructField("user_id", LongType(), True),
    StructField("event_time", TimestampType(), True),
    StructField("properties", MapType(StringType(), StringType()), True)
])

df = spark.createDataFrame([], schema)
df.writeTo("local.db.events_v2") \
    .partitionedBy("days(event_time)", "bucket(16, user_id)") \
    .createOrReplace()
```

### Insert Data

```python
from datetime import datetime
from pyspark.sql import Row

# Create sample data
data = [
    Row(event_id=1, event_type="click", user_id=100, 
        event_time=datetime(2024, 1, 15, 10, 30), 
        properties={"page": "/home", "button": "signup"}),
    Row(event_id=2, event_type="view", user_id=101, 
        event_time=datetime(2024, 1, 15, 11, 0), 
        properties={"page": "/products"}),
    Row(event_id=3, event_type="purchase", user_id=100, 
        event_time=datetime(2024, 1, 15, 11, 30), 
        properties={"product_id": "ABC123", "amount": "99.99"})
]

df = spark.createDataFrame(data)

# Append data
df.writeTo("local.db.events").append()
```

### Query Data

```python
# Basic query
df = spark.table("local.db.events")
df.show()

# With filter (partition pruning tự động)
df = spark.sql("""
    SELECT event_type, COUNT(*) as count
    FROM local.db.events
    WHERE event_time >= '2024-01-15'
      AND event_time < '2024-01-16'
    GROUP BY event_type
""")
df.show()

# Time travel
df_yesterday = spark.sql("""
    SELECT * FROM local.db.events
    TIMESTAMP AS OF '2024-01-14 23:59:59'
""")
```

### Update & Delete

```python
# Update
spark.sql("""
    UPDATE local.db.events
    SET event_type = 'click_validated'
    WHERE event_type = 'click' AND user_id = 100
""")

# Delete
spark.sql("""
    DELETE FROM local.db.events
    WHERE event_time < '2024-01-01'
""")

# Merge (Upsert)
spark.sql("""
    MERGE INTO local.db.events t
    USING updates s
    ON t.event_id = s.event_id
    WHEN MATCHED THEN UPDATE SET *
    WHEN NOT MATCHED THEN INSERT *
""")
```

### Table Maintenance

```python
# Expire snapshots
spark.sql("""
    CALL local.system.expire_snapshots(
        table => 'db.events',
        older_than => TIMESTAMP '2024-01-01 00:00:00',
        retain_last => 5
    )
""")

# Remove orphan files
spark.sql("""
    CALL local.system.remove_orphan_files(
        table => 'db.events',
        older_than => TIMESTAMP '2024-01-01 00:00:00'
    )
""")

# Rewrite data files (compaction)
spark.sql("""
    CALL local.system.rewrite_data_files(
        table => 'db.events',
        options => map(
            'target-file-size-bytes', '134217728',
            'min-file-size-bytes', '104857600',
            'max-file-size-bytes', '180355072'
        )
    )
""")

# Rewrite manifests
spark.sql("""
    CALL local.system.rewrite_manifests('db.events')
""")
```

### PyIceberg Examples

```python
from pyiceberg.catalog import load_catalog
from pyiceberg.schema import Schema
from pyiceberg.types import NestedField, LongType, StringType, TimestampType
from pyiceberg.partitioning import PartitionSpec, PartitionField
from pyiceberg.transforms import DayTransform

# Load catalog
catalog = load_catalog(
    "my_catalog",
    **{
        "type": "rest",
        "uri": "http://localhost:8181",
        "s3.endpoint": "http://localhost:9000",
        "s3.access-key-id": "admin",
        "s3.secret-access-key": "password"
    }
)

# Create namespace
catalog.create_namespace("my_database")

# Define schema
schema = Schema(
    NestedField(1, "event_id", LongType(), required=True),
    NestedField(2, "event_type", StringType()),
    NestedField(3, "event_time", TimestampType())
)

# Define partition spec
partition_spec = PartitionSpec(
    PartitionField(
        source_id=3, 
        field_id=1000, 
        transform=DayTransform(), 
        name="event_day"
    )
)

# Create table
table = catalog.create_table(
    "my_database.events",
    schema=schema,
    partition_spec=partition_spec,
    properties={"write.format.default": "parquet"}
)

# Load and query table
table = catalog.load_table("my_database.events")
scan = table.scan(
    row_filter="event_time >= '2024-01-01'",
    selected_fields=["event_id", "event_type"]
)
df = scan.to_arrow().to_pandas()
```

### Flink SQL Examples

```sql
-- Create Iceberg catalog
CREATE CATALOG iceberg_catalog WITH (
    'type' = 'iceberg',
    'catalog-type' = 'hive',
    'uri' = 'thrift://localhost:9083',
    'warehouse' = 's3://my-bucket/warehouse'
);

USE CATALOG iceberg_catalog;
CREATE DATABASE my_db;
USE my_db;

-- Create table
CREATE TABLE events (
    event_id BIGINT,
    event_type STRING,
    event_time TIMESTAMP(3),
    WATERMARK FOR event_time AS event_time - INTERVAL '5' MINUTE
) WITH (
    'format-version' = '2',
    'write.format.default' = 'parquet'
);

-- Streaming insert from Kafka
INSERT INTO events
SELECT 
    CAST(JSON_VALUE(data, '$.event_id') AS BIGINT),
    JSON_VALUE(data, '$.event_type'),
    TO_TIMESTAMP(JSON_VALUE(data, '$.event_time'))
FROM kafka_source;
```

### Trino Examples

```sql
-- Create schema
CREATE SCHEMA iceberg.my_database
WITH (location = 's3://my-bucket/warehouse/my_database');

-- Create table
CREATE TABLE iceberg.my_database.events (
    event_id BIGINT,
    event_type VARCHAR,
    event_time TIMESTAMP(6)
)
WITH (
    format = 'PARQUET',
    partitioning = ARRAY['day(event_time)']
);

-- Query
SELECT * FROM iceberg.my_database.events
WHERE event_time >= TIMESTAMP '2024-01-15 00:00:00';

-- Time travel
SELECT * FROM iceberg.my_database.events
FOR VERSION AS OF 1234567890;

-- Show table history
SELECT * FROM iceberg.my_database."events$history";

-- Show snapshots
SELECT * FROM iceberg.my_database."events$snapshots";

-- Show files
SELECT * FROM iceberg.my_database."events$files";
```

---

## 🎯 Use Cases Thực Tế

### 1. Netflix - Original Use Case

**Problem:**
- Petabytes of data trên S3
- Slow queries do S3 listing
- Unreliable concurrent writes
- Expensive partition management

**Solution với Iceberg:**
- Snapshot isolation cho safe concurrent access
- Metadata tracking thay vì file listing
- Hidden partitioning giảm user errors
- Time travel cho debugging

**Scale:**
- Thousands of tables
- Petabytes of data
- Billions of files

### 2. Apple - iCloud Data Lake

**Use Case:**
- Unified analytics platform
- Multiple query engines (Spark, Trino)
- Strict data governance requirements

**Benefits:**
- Engine-agnostic format
- Schema evolution không downtime
- ACID guarantees cho critical data

### 3. LinkedIn - Real-time Analytics

**Architecture:**

```
┌─────────────────────────────────────────────────────────────────┐
│                    LinkedIn Analytics Pipeline                   │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│   Kafka ─────► Flink ─────► Iceberg Tables ─────► Trino/Spark   │
│                                   │                              │
│                                   ▼                              │
│                    ┌──────────────────────────┐                  │
│                    │  Data Scientists         │                  │
│                    │  BI Tools (dashboards)   │                  │
│                    └──────────────────────────┘                  │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### 4. E-commerce Event Tracking

```
┌──────────────────────────────────────────────────────────────────┐
│                     E-commerce Analytics                          │
├──────────────────────────────────────────────────────────────────┤
│                                                                   │
│   Website/App                                                     │
│       │                                                           │
│       ▼                                                           │
│   ┌───────────┐    ┌──────────┐    ┌─────────────────────┐       │
│   │   Kafka   │───►│  Flink   │───►│  Iceberg Tables     │       │
│   │  (events) │    │(process) │    │  - page_views       │       │
│   └───────────┘    └──────────┘    │  - clicks           │       │
│                                    │  - purchases        │       │
│                                    │  - user_sessions    │       │
│                                    └─────────┬───────────┘       │
│                                              │                    │
│                    ┌─────────────────────────┼─────────────────┐  │
│                    │                         │                 │  │
│                    ▼                         ▼                 ▼  │
│           ┌────────────────┐    ┌──────────────────┐    ┌──────┐  │
│           │  Real-time     │    │   Batch Reports   │    │  ML  │  │
│           │  Dashboards    │    │   (daily/weekly)  │    │Models│  │
│           │  (Trino)       │    │   (Spark)         │    │      │  │
│           └────────────────┘    └──────────────────┘    └──────┘  │
│                                                                   │
└──────────────────────────────────────────────────────────────────┘
```

### 5. CDC Pipeline

```python
# Debezium → Kafka → Flink → Iceberg

# Flink SQL cho CDC processing
"""
CREATE TABLE mysql_cdc (
    id BIGINT,
    name STRING,
    email STRING,
    updated_at TIMESTAMP(3),
    PRIMARY KEY (id) NOT ENFORCED
) WITH (
    'connector' = 'mysql-cdc',
    'hostname' = 'mysql-host',
    'port' = '3306',
    'database-name' = 'mydb',
    'table-name' = 'users'
);

-- Iceberg sink với UPSERT mode
CREATE TABLE iceberg_users (
    id BIGINT,
    name STRING,
    email STRING,
    updated_at TIMESTAMP(3),
    PRIMARY KEY (id) NOT ENFORCED
) WITH (
    'connector' = 'iceberg',
    'catalog-name' = 'iceberg_catalog',
    'database-name' = 'my_db',
    'table-name' = 'users',
    'upsert-enabled' = 'true'
);

INSERT INTO iceberg_users
SELECT * FROM mysql_cdc;
"""
```

---

## ✅ Best Practices

### 1. Partitioning Strategy

**DO:**
- ✅ Partition theo columns thường filter
- ✅ Sử dụng hidden partitioning (day, month, bucket)
- ✅ Giữ số partitions hợp lý (không quá nhiều small files)
- ✅ Dùng bucket cho high-cardinality columns
- ✅ Monitor partition sizes

**DON'T:**
- ❌ Over-partition (mỗi partition < 100MB)
- ❌ Partition theo columns không filter
- ❌ Dùng identity transform cho high-cardinality
- ❌ Quên partition evolution khi data patterns thay đổi

**Sizing Guidelines:**
- Target file size: 128MB - 512MB
- Target partition size: 1GB - 10GB
- Số partitions mỗi ngày: < 1000

### 2. File Size Optimization

```python
# Compaction configuration
spark.sql("""
    CALL system.rewrite_data_files(
        table => 'db.my_table',
        options => map(
            'target-file-size-bytes', '134217728',  -- 128MB
            'min-file-size-bytes', '104857600',     -- 100MB
            'max-file-size-bytes', '180355072'      -- ~172MB
        )
    )
""")

# Table properties cho writes
spark.sql("""
    ALTER TABLE db.my_table SET TBLPROPERTIES (
        'write.target-file-size-bytes' = '134217728',
        'write.distribution-mode' = 'hash'
    )
""")
```

### 3. Snapshot Management

```python
# Expire old snapshots (giữ 5 ngày, minimum 10 snapshots)
spark.sql("""
    CALL system.expire_snapshots(
        table => 'db.my_table',
        older_than => TIMESTAMP '2024-01-10 00:00:00',
        retain_last => 10,
        max_concurrent_deletes => 10
    )
""")

# Schedule expiration job - Chạy daily hoặc weekly
```

### 4. Orphan File Cleanup

```python
# Remove files không reference bởi metadata
spark.sql("""
    CALL system.remove_orphan_files(
        table => 'db.my_table',
        older_than => TIMESTAMP '2024-01-01 00:00:00',
        dry_run => true  -- Chạy dry run trước!
    )
""")
```

### 5. Write Optimization

```python
# Sorted writes cho better compression
df.sortWithinPartitions("user_id") \
    .writeTo("db.my_table") \
    .append()

# Table property
spark.sql("""
    ALTER TABLE db.my_table SET TBLPROPERTIES (
        'write.distribution-mode' = 'hash',
        'write.sort-order' = 'user_id ASC NULLS LAST'
    )
""")
```

### 6. Metadata Management

```python
# Table properties recommendations
table_properties = {
    # File format
    "write.format.default": "parquet",
    "write.parquet.compression-codec": "zstd",
    
    # File sizing
    "write.target-file-size-bytes": "134217728",
    
    # Metadata compression
    "write.metadata.compression-codec": "gzip",
    
    # History
    "history.expire.max-snapshot-age-ms": "432000000",  # 5 days
    "history.expire.min-snapshots-to-keep": "10",
    
    # Metrics
    "write.metadata.metrics.default": "truncate(16)",
    "write.metadata.metrics.column.properties": "full"
}
```

---

## 🚀 Performance Tuning

### 1. Query Planning Optimization

```python
# Enable vectorized reads
spark.conf.set("spark.sql.iceberg.vectorization.enabled", "true")

# Parallel planning
spark.conf.set("spark.sql.iceberg.planning.preserve-data-grouping", "true")

# Split size tuning
spark.conf.set("spark.sql.files.maxPartitionBytes", "134217728")  # 128MB
```

### 2. Predicate Pushdown

Iceberg tự động skip files dựa trên:
- Partition values
- Column min/max values
- Null counts

```python
# Ví dụ query sẽ skip files không match
df = spark.sql("""
    SELECT * FROM my_table
    WHERE user_id = 12345
      AND event_date = '2024-01-15'
      AND amount > 100
""")
# Iceberg sẽ:
# 1. Skip partitions không match event_date
# 2. Skip files có max(user_id) < 12345 hoặc min(user_id) > 12345
# 3. Skip files có max(amount) <= 100
```

### 3. Z-Order Clustering

```python
# Z-order cho multi-dimensional filtering
spark.sql("""
    CALL system.rewrite_data_files(
        table => 'db.my_table',
        strategy => 'sort',
        sort_order => 'zorder(user_id, event_type)'
    )
""")
```

### 4. Caching Strategies

```python
# Cache metadata trong Spark
spark.conf.set("spark.sql.catalog.spark_catalog.cache-enabled", "true")

# Cache table
spark.table("my_table").cache()
```

---

## 🔧 Troubleshooting

### 1. Too Many Small Files

**Symptoms:**
- Slow query planning
- High manifest file count
- Slow reads

**Solution:**
```python
# Compact small files
spark.sql("""
    CALL system.rewrite_data_files(
        table => 'db.my_table',
        options => map(
            'min-file-size-bytes', '104857600',
            'target-file-size-bytes', '134217728',
            'max-file-size-bytes', '180355072'
        )
    )
""")
```

### 2. Orphan Files Accumulating

**Symptoms:**
- Storage costs increasing
- Files không trong metadata

**Solution:**
```python
# First dry-run
spark.sql("""
    CALL system.remove_orphan_files(
        table => 'db.my_table',
        older_than => TIMESTAMP '2024-01-01',
        dry_run => true
    )
""")

# Then actual removal
spark.sql("""
    CALL system.remove_orphan_files(
        table => 'db.my_table',
        older_than => TIMESTAMP '2024-01-01'
    )
""")
```

### 3. Concurrent Write Conflicts

**Symptoms:**
- `CommitFailedException`
- Retries không thành công

**Solution:**
```python
# Increase retry attempts
spark.conf.set("spark.sql.iceberg.commit.retry.num-retries", "10")
spark.conf.set("spark.sql.iceberg.commit.retry.min-wait-ms", "100")
spark.conf.set("spark.sql.iceberg.commit.retry.max-wait-ms", "60000")
```

### 4. Slow Query Planning

**Symptoms:**
- Query mất lâu để start
- High metadata reads

**Solution:**
```python
# Rewrite manifests
spark.sql("CALL system.rewrite_manifests('db.my_table')")

# Enable manifest caching
spark.conf.set("spark.sql.catalog.spark_catalog.cache-enabled", "true")
```

### 5. Out of Memory During Compaction

**Solution:**
```python
# Process smaller batches
spark.sql("""
    CALL system.rewrite_data_files(
        table => 'db.my_table',
        options => map(
            'max-concurrent-file-group-rewrites', '5',
            'partial-progress.enabled', 'true',
            'partial-progress.max-commits', '10'
        )
    )
""")
```

---

## 🏭 Production Deployment

### Architecture Pattern

```
┌─────────────────────────────────────────────────────────────────┐
│                    Production Deployment                         │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌──────────────┐     ┌──────────────┐     ┌──────────────┐     │
│  │   Writers    │     │   Catalog    │     │   Readers    │     │
│  │ (Spark/Flink)│     │   (REST)     │     │(Trino/Spark) │     │
│  └──────┬───────┘     └──────┬───────┘     └──────┬───────┘     │
│         │                    │                    │              │
│         │    ┌───────────────┴───────────────┐    │              │
│         │    │        REST Catalog           │    │              │
│         │    │   (Tabular, Polaris, etc.)    │    │              │
│         │    └───────────────┬───────────────┘    │              │
│         │                    │                    │              │
│         └─────────────┬──────┴──────┬─────────────┘              │
│                       │             │                            │
│                       ▼             ▼                            │
│         ┌─────────────────────────────────────────┐              │
│         │            Object Storage               │              │
│         │         (S3 / GCS / ADLS)               │              │
│         └─────────────────────────────────────────┘              │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### Monitoring Metrics

**Key metrics to monitor:**
- `table_size_bytes` - Total data size
- `file_count` - Number of data files
- `manifest_count` - Number of manifest files
- `snapshot_count` - Number of snapshots
- `partition_count` - Number of partitions
- `avg_file_size` - Average file size
- `oldest_snapshot_age` - Age of oldest snapshot

```python
# Query from metadata tables
spark.sql("""
    SELECT 
        COUNT(*) as file_count,
        SUM(file_size_in_bytes) as total_size,
        AVG(file_size_in_bytes) as avg_size
    FROM my_catalog.my_db.my_table.files
""")
```

### Daily Maintenance Job

```python
def daily_maintenance(table_name):
    # 1. Expire old snapshots
    spark.sql(f"""
        CALL system.expire_snapshots(
            table => '{table_name}',
            older_than => TIMESTAMP '{five_days_ago}',
            retain_last => 10
        )
    """)
    
    # 2. Remove orphan files
    spark.sql(f"""
        CALL system.remove_orphan_files(
            table => '{table_name}',
            older_than => TIMESTAMP '{three_days_ago}'
        )
    """)
    
    # 3. Compact if needed
    file_count = spark.sql(f"""
        SELECT COUNT(*) FROM {table_name}.files
    """).collect()[0][0]
    
    if file_count > 1000:
        spark.sql(f"""
            CALL system.rewrite_data_files(
                table => '{table_name}',
                options => map(
                    'partial-progress.enabled', 'true',
                    'partial-progress.max-commits', '10'
                )
            )
        """)
```

---

## 📚 Resources

### Official
- Apache Iceberg Website: https://iceberg.apache.org/
- GitHub Repository: https://github.com/apache/iceberg
- Iceberg Specification: https://iceberg.apache.org/spec/

### Learning
- Iceberg Documentation: https://iceberg.apache.org/docs/latest/
- PyIceberg Documentation: https://py.iceberg.apache.org/
- Tabular Blog: https://tabular.io/blog/

### Community
- Apache Iceberg Slack: https://apache-iceberg.slack.com/
- Mailing Lists: https://iceberg.apache.org/community/
- YouTube Channel: https://www.youtube.com/@ApacheIceberg

### Papers
- "Apache Iceberg: An Open Table Format for Huge Analytic Datasets" - Ryan Blue et al.

---

> **Document Version**: 1.0  
> **Last Updated**: December 31, 2025  
> **Iceberg Version**: 1.10.0
