# 🔺 Delta Lake - Complete Guide

> **"Build Lakehouses with Delta Lake"**

---

## 📑 Mục Lục

1. [Giới Thiệu & Lịch Sử](#-giới-thiệu--lịch-sử)
2. [Kiến Trúc Chi Tiết](#-kiến-trúc-chi-tiết)
3. [Core Concepts](#-core-concepts)
4. [Delta UniForm](#-delta-uniform)
5. [Hands-on Code Examples](#-hands-on-code-examples)
6. [Use Cases Thực Tế](#-use-cases-thực-tế)
7. [Best Practices](#-best-practices)
8. [Performance Tuning](#-performance-tuning)
9. [Troubleshooting](#-troubleshooting)

---

## 🌟 Giới Thiệu & Lịch Sử

### Delta Lake là gì?

Delta Lake là một **open-source storage layer** mang đến reliability cho Data Lakes. Delta Lake cung cấp ACID transactions, scalable metadata handling, và unifies streaming and batch data processing. Delta Lake chạy trên top of data lake storage (S3, ADLS, GCS) và hoàn toàn compatible với Apache Spark APIs.

### Lịch Sử Phát Triển

**2016** - Databricks bắt đầu phát triển internal (Project "Tahoe")

**2017** - Debut tại Databricks platform

**2019** - Open-sourced Delta Lake 0.1.0 (April 2019)

**2020** - VLDB Paper: "Delta Lake: High-Performance ACID Table Storage"
- Version 0.7.0 - Improved merge, schema evolution

**2021** - Version 1.0 - First major stable release
- CIDR Paper: "Lakehouse: A New Generation..."

**2022** - Donated to Linux Foundation
- Version 2.0 - Change Data Feed, Z-Order clustering

**2023** - Version 3.0 - Delta UniForm (Iceberg/Hudi interop)
- Delta Kernel (universal reader)

**2024** - Version 3.1-3.2 - Improved UniForm, Liquid Clustering

**2025** - Version 4.0 - Spark 4.0 integration, mature UniForm

### Tại sao Databricks tạo ra Delta Lake?

**Vấn đề với Data Lakes truyền thống:**
- Không có transactions → data corruption
- No schema enforcement → schema drift
- Không reliable với concurrent writes
- Không support updates/deletes
- Batch và streaming pipeline riêng biệt

**Giải pháp của Delta Lake:**
- ACID transactions với optimistic concurrency
- Schema enforcement và evolution
- Support DML operations (UPDATE, DELETE, MERGE)
- Unified batch và streaming
- Time travel cho audit và rollback

### Key Contributors & Governance

**Databricks** - Primary sponsor, main contributor

**Linux Foundation** - Governance body (since 2022)

**Microsoft** - Major contributor (Azure integration)

**Other Contributors:**
- Apple
- Adobe
- Amazon
- Alibaba
- ByteDance
- And 70+ organizations

---

## 🏗️ Kiến Trúc Chi Tiết

### Tổng Quan Kiến Trúc

```
┌─────────────────────────────────────────────────────────────────────┐
│                        Application Layer                             │
│              (Spark, Flink, Trino, Presto, Redshift)                 │
└────────────────────────────┬────────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────────┐
│                         Delta Lake APIs                              │
│                    (Spark, Rust, Python, Java)                       │
└────────────────────────────┬────────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    Delta Transaction Log                             │
│                  (_delta_log directory)                              │
│                                                                      │
│  ┌──────────────────────────────────────────────────────────────┐   │
│  │                Transaction Log Files                          │   │
│  │  000000000000000000.json  ─► Initial table creation           │   │
│  │  000000000000000001.json  ─► First transaction                │   │
│  │  000000000000000002.json  ─► Second transaction               │   │
│  │  ...                                                          │   │
│  │  000000000000000010.checkpoint.parquet ─► Checkpoint          │   │
│  │  ...                                                          │   │
│  │  _last_checkpoint  ─► Points to latest checkpoint             │   │
│  └──────────────────────────────────────────────────────────────┘   │
│                                                                      │
│  Transaction Log Entry Contents:                                     │
│  ┌──────────────────────────────────────────────────────────────┐   │
│  │  • commitInfo: timestamp, operation, operationParameters      │   │
│  │  • add: file path, size, stats, partitionValues              │   │
│  │  • remove: file path, deletionTimestamp                       │   │
│  │  • metaData: schema, partitioning, format, properties        │   │
│  │  • protocol: minReaderVersion, minWriterVersion              │   │
│  │  • txn: appId, version (for streaming)                       │   │
│  └──────────────────────────────────────────────────────────────┘   │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────────┐
│                        Data Files (Parquet)                          │
│                                                                      │
│  my_table/                                                           │
│  ├── _delta_log/                                                     │
│  │   ├── 00000000000000000000.json                                   │
│  │   ├── 00000000000000000001.json                                   │
│  │   ├── ...                                                         │
│  │   ├── 00000000000000000010.checkpoint.parquet                     │
│  │   └── _last_checkpoint                                            │
│  ├── date=2024-01-15/                                                │
│  │   ├── part-00000-abc123.snappy.parquet                            │
│  │   └── part-00001-def456.snappy.parquet                            │
│  └── date=2024-01-16/                                                │
│      └── part-00000-ghi789.snappy.parquet                            │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────────┐
│                      Object Storage                                  │
│                 (S3, ADLS, GCS, HDFS, Local)                         │
└─────────────────────────────────────────────────────────────────────┘
```

### Transaction Log Chi Tiết

#### JSON Log Entry Example

```json
{
  "commitInfo": {
    "timestamp": 1702396800000,
    "operation": "WRITE",
    "operationParameters": {
      "mode": "Append",
      "partitionBy": "[\"date\"]"
    },
    "readVersion": 0,
    "isolationLevel": "WriteSerializable",
    "isBlindAppend": true,
    "operationMetrics": {
      "numFiles": "5",
      "numOutputRows": "1000000",
      "numOutputBytes": "52428800"
    },
    "engineInfo": "Apache-Spark/3.5.0 Delta-Lake/3.0.0"
  }
}
```

```json
{
  "add": {
    "path": "date=2024-01-15/part-00000-abc123.snappy.parquet",
    "partitionValues": {"date": "2024-01-15"},
    "size": 10485760,
    "modificationTime": 1702396800000,
    "dataChange": true,
    "stats": "{\"numRecords\":200000,\"minValues\":{\"id\":1},\"maxValues\":{\"id\":200000},\"nullCount\":{\"id\":0}}"
  }
}
```

#### Checkpoint File

Mỗi 10 commits (default), Delta Lake tạo checkpoint file (Parquet format):
- Consolidate tất cả log entries
- Speed up reads (không cần đọc tất cả JSON files)
- Contains current state của table

```json
// _last_checkpoint
{
  "version": 100,
  "size": 15000,
  "parts": 1,
  "sizeInBytes": 1048576,
  "numOfAddFiles": 500,
  "checkpointSchema": {...}
}
```

---

## 📚 Core Concepts

### 1. ACID Transactions

```
ACID Properties in Delta Lake:
┌─────────────────────────────────────────────────────────────────┐
│                                                                  │
│  Atomicity:     All operations trong transaction succeed hoặc   │
│                 fail together                                    │
│                                                                  │
│  Consistency:   Table luôn ở valid state                        │
│                                                                  │
│  Isolation:     Concurrent transactions không interfere         │
│                 (Serializable hoặc WriteSerializable)           │
│                                                                  │
│  Durability:    Committed transactions persist                  │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

#### Isolation Levels

**Serializable**
- Strongest isolation
- May retry more
- Use for: Critical data

**WriteSerializable (Default)**
- Allows more concurrency
- Use for: Most workloads

### 2. Schema Enforcement & Evolution

#### Schema Enforcement (Validation on Write)

```python
# Delta Lake rejects writes that don't match schema
df_wrong_schema = spark.createDataFrame([
    (1, "John", "extra_column")  # 3 columns
], ["id", "name", "invalid_col"])

# This will FAIL if table only has id, name
df_wrong_schema.write.format("delta").mode("append").save("/path/to/table")
# AnalysisException: A schema mismatch detected when writing to the Delta table
```

#### Schema Evolution

```python
# Enable auto merge
spark.conf.set("spark.databricks.delta.schema.autoMerge.enabled", "true")

# Or per-write
df_new_cols.write \
    .format("delta") \
    .mode("append") \
    .option("mergeSchema", "true") \
    .save("/path/to/table")
```

**Evolution operations supported:**
- ✅ Add columns
- ✅ Nested field changes
- ✅ Type widening (with compatible types)

### 3. Time Travel

```python
# Read by version
df_v5 = spark.read.format("delta").option("versionAsOf", 5).load("/path/to/table")

# Read by timestamp
df_past = spark.read.format("delta") \
    .option("timestampAsOf", "2024-01-15 10:30:00") \
    .load("/path/to/table")
```

```sql
-- SQL syntax
SELECT * FROM delta.`/path/to/table` VERSION AS OF 5;
SELECT * FROM delta.`/path/to/table` TIMESTAMP AS OF '2024-01-15';

-- View history
DESCRIBE HISTORY delta.`/path/to/table`;
```

### 4. Change Data Feed (CDF)

```python
# Enable CDF on table
spark.sql("""
    ALTER TABLE delta.`/path/to/table`
    SET TBLPROPERTIES (delta.enableChangeDataFeed = true)
""")

# Read changes
changes = spark.read.format("delta") \
    .option("readChangeFeed", "true") \
    .option("startingVersion", 5) \
    .option("endingVersion", 10) \
    .load("/path/to/table")

changes.show()
```

**Output columns:**
- `_change_type`: insert, update_preimage, update_postimage, delete
- `_commit_version`: Version number
- `_commit_timestamp`: Commit timestamp

```python
# Streaming CDF
stream_changes = spark.readStream.format("delta") \
    .option("readChangeFeed", "true") \
    .option("startingVersion", 0) \
    .load("/path/to/table")
```

### 5. Liquid Clustering (Delta 3.0+)

**Liquid Clustering** thay thế traditional partitioning và Z-ORDER:

```python
# Create table with Liquid Clustering
spark.sql("""
    CREATE TABLE my_table (
        id BIGINT,
        date DATE,
        category STRING,
        amount DOUBLE
    )
    USING DELTA
    CLUSTER BY (date, category)
""")

# Optimize tự động cluster data
spark.sql("OPTIMIZE my_table")

# Thay đổi clustering columns (no data rewrite needed)
spark.sql("""
    ALTER TABLE my_table
    CLUSTER BY (category, date)
""")
```

**Advantages:**
- ✅ Incremental clustering (không cần full rewrite)
- ✅ Flexible cluster key changes
- ✅ Better với high-cardinality columns
- ✅ Simpler than partitioning + Z-ORDER

---

## 🌐 Delta UniForm

### Giới Thiệu UniForm

Delta UniForm cho phép Delta tables được đọc bằng **Apache Iceberg** và **Apache Hudi** clients, không cần copy hay convert data.

```
┌─────────────────────────────────────────────────────────────────┐
│                     Delta UniForm                                │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│   ┌─────────────────────────────────────────────────────────┐   │
│   │                  Delta Table (Source)                    │   │
│   │            (Single copy of data)                         │   │
│   └───────────────────────┬─────────────────────────────────┘   │
│                           │                                      │
│          ┌────────────────┼────────────────┐                     │
│          ▼                ▼                ▼                     │
│   ┌────────────┐   ┌────────────┐   ┌────────────┐              │
│   │   Delta    │   │  Iceberg   │   │   Hudi     │              │
│   │  Metadata  │   │  Metadata  │   │  Metadata  │              │
│   │  (native)  │   │  (auto-gen)│   │  (auto-gen)│              │
│   └─────┬──────┘   └─────┬──────┘   └─────┬──────┘              │
│         │                │                │                      │
│         ▼                ▼                ▼                      │
│   ┌────────────┐   ┌────────────┐   ┌────────────┐              │
│   │   Spark    │   │   Trino    │   │   Presto   │              │
│   │   Flink    │   │   Athena   │   │ Other Hudi │              │
│   │   etc.     │   │  BigQuery  │   │  clients   │              │
│   └────────────┘   └────────────┘   └────────────┘              │
│                                                                  │
│   Benefits:                                                      │
│   ✅ Single copy of data                                         │
│   ✅ Automatic metadata sync                                     │
│   ✅ Multi-engine access                                         │
│   ✅ No ETL needed                                               │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### Enable UniForm

```python
# Create table with UniForm (Iceberg)
spark.sql("""
    CREATE TABLE my_catalog.my_db.uniform_table (
        id BIGINT,
        name STRING,
        created_at TIMESTAMP
    )
    USING DELTA
    TBLPROPERTIES (
        'delta.universalFormat.enabledFormats' = 'iceberg'
    )
""")

# Enable on existing table
spark.sql("""
    ALTER TABLE my_catalog.my_db.existing_table
    SET TBLPROPERTIES (
        'delta.universalFormat.enabledFormats' = 'iceberg'
    )
""")

# Enable both Iceberg and Hudi
spark.sql("""
    ALTER TABLE my_catalog.my_db.my_table
    SET TBLPROPERTIES (
        'delta.universalFormat.enabledFormats' = 'iceberg,hudi'
    )
""")
```

### Query UniForm Tables

```sql
-- Query from Trino với Iceberg connector
SELECT * FROM iceberg_catalog.my_db.uniform_table;

-- Query from Athena với Iceberg
SELECT * FROM "my_db"."uniform_table" 
FOR SYSTEM_VERSION AS OF 12345;

-- Query from BigQuery với BigLake Iceberg
SELECT * FROM `project.dataset.uniform_table`;
```

### Limitations

- ❌ UniForm is read-only for Iceberg/Hudi clients
- ❌ Writes must go through Delta
- ❌ Some advanced features may not translate
- ❌ Metadata sync có slight delay

---

## 💻 Hands-on Code Examples

### PySpark Setup

```python
from pyspark.sql import SparkSession

# Spark session với Delta Lake
spark = SparkSession.builder \
    .appName("DeltaLakeDemo") \
    .config("spark.jars.packages", "io.delta:delta-spark_2.12:3.0.0") \
    .config("spark.sql.extensions", "io.delta.sql.DeltaSparkSessionExtension") \
    .config("spark.sql.catalog.spark_catalog", 
            "org.apache.spark.sql.delta.catalog.DeltaCatalog") \
    .getOrCreate()
```

### Create & Write Table

```python
from pyspark.sql.types import *
from pyspark.sql.functions import *
from delta.tables import DeltaTable

# Create sample data
data = [
    (1, "Alice", "Engineering", 100000, "2024-01-15"),
    (2, "Bob", "Marketing", 80000, "2024-01-15"),
    (3, "Charlie", "Engineering", 120000, "2024-01-16"),
]

schema = StructType([
    StructField("id", IntegerType(), False),
    StructField("name", StringType(), True),
    StructField("department", StringType(), True),
    StructField("salary", IntegerType(), True),
    StructField("hire_date", StringType(), True)
])

df = spark.createDataFrame(data, schema)

# Write as Delta table (partitioned)
df.write \
    .format("delta") \
    .partitionBy("department") \
    .mode("overwrite") \
    .save("/tmp/delta/employees")

# Create managed table
df.write \
    .format("delta") \
    .saveAsTable("default.employees")
```

### Read Data

```python
# Read Delta table
df = spark.read.format("delta").load("/tmp/delta/employees")
df.show()

# Read with SQL
spark.sql("SELECT * FROM delta.`/tmp/delta/employees`").show()

# Time travel
df_v0 = spark.read.format("delta").option("versionAsOf", 0).load("/tmp/delta/employees")

df_past = spark.read.format("delta") \
    .option("timestampAsOf", "2024-01-15 10:00:00") \
    .load("/tmp/delta/employees")

# History
spark.sql("DESCRIBE HISTORY delta.`/tmp/delta/employees`").show(truncate=False)
```

### UPDATE Operations

```python
from delta.tables import DeltaTable

# Load Delta table
delta_table = DeltaTable.forPath(spark, "/tmp/delta/employees")

# Update with Python API
delta_table.update(
    condition="department = 'Engineering'",
    set={"salary": "salary * 1.1"}  # 10% raise
)

# SQL UPDATE
spark.sql("""
    UPDATE delta.`/tmp/delta/employees`
    SET salary = salary * 1.05
    WHERE department = 'Marketing'
""")
```

### DELETE Operations

```python
# Delete with Python API
delta_table.delete("id = 3")

# SQL DELETE
spark.sql("""
    DELETE FROM delta.`/tmp/delta/employees`
    WHERE hire_date < '2024-01-01'
""")
```

### MERGE (Upsert) Operations

```python
# Source data (updates and new records)
updates = spark.createDataFrame([
    (1, "Alice Smith", "Engineering", 110000, "2024-01-15"),  # Update
    (4, "Diana", "Sales", 90000, "2024-01-20"),  # Insert
], schema)

# Merge operation
delta_table.alias("target").merge(
    updates.alias("source"),
    "target.id = source.id"
).whenMatchedUpdate(
    set={
        "name": "source.name",
        "salary": "source.salary"
    }
).whenNotMatchedInsert(
    values={
        "id": "source.id",
        "name": "source.name",
        "department": "source.department",
        "salary": "source.salary",
        "hire_date": "source.hire_date"
    }
).execute()
```

```sql
-- SQL MERGE
MERGE INTO delta.`/tmp/delta/employees` AS target
USING updates AS source
ON target.id = source.id
WHEN MATCHED THEN
    UPDATE SET target.name = source.name, target.salary = source.salary
WHEN NOT MATCHED THEN
    INSERT *;

-- CDC-style merge (with delete)
MERGE INTO target_table t
USING source_cdc s
ON t.id = s.id
WHEN MATCHED AND s.operation = 'DELETE' THEN DELETE
WHEN MATCHED AND s.operation = 'UPDATE' THEN UPDATE SET *
WHEN NOT MATCHED AND s.operation = 'INSERT' THEN INSERT *;
```

### Streaming

```python
# Write stream to Delta
stream = spark.readStream \
    .format("rate") \
    .option("rowsPerSecond", 100) \
    .load()

query = stream.writeStream \
    .format("delta") \
    .outputMode("append") \
    .option("checkpointLocation", "/tmp/checkpoints/rate_stream") \
    .start("/tmp/delta/streaming_table")

# Read stream from Delta
df_stream = spark.readStream \
    .format("delta") \
    .load("/tmp/delta/streaming_table")

# Stream với Change Data Feed
changes_stream = spark.readStream \
    .format("delta") \
    .option("readChangeFeed", "true") \
    .option("startingVersion", 0) \
    .load("/tmp/delta/employees")

changes_stream.writeStream \
    .format("console") \
    .start()
```

### Table Maintenance

```python
# OPTIMIZE (compaction)
spark.sql("OPTIMIZE delta.`/tmp/delta/employees`")

# OPTIMIZE with Z-ORDER
spark.sql("""
    OPTIMIZE delta.`/tmp/delta/employees`
    ZORDER BY (department, hire_date)
""")

# VACUUM (remove old files)
spark.sql("VACUUM delta.`/tmp/delta/employees` RETAIN 168 HOURS")

# Set retention (default 7 days)
spark.sql("""
    ALTER TABLE delta.`/tmp/delta/employees`
    SET TBLPROPERTIES (
        delta.logRetentionDuration = 'interval 30 days',
        delta.deletedFileRetentionDuration = 'interval 7 days'
    )
""")

# RESTORE to previous version
spark.sql("RESTORE delta.`/tmp/delta/employees` TO VERSION AS OF 5")
spark.sql("RESTORE delta.`/tmp/delta/employees` TO TIMESTAMP AS OF '2024-01-15'")
```

### Python (delta-rs) Examples

```python
# pip install deltalake
import deltalake
from deltalake import DeltaTable, write_deltalake
import pandas as pd

# Write data
df = pd.DataFrame({
    'id': [1, 2, 3],
    'name': ['Alice', 'Bob', 'Charlie'],
    'salary': [100000, 80000, 120000]
})

write_deltalake(
    "/tmp/delta/employees_rust",
    df,
    mode="overwrite",
    partition_by=["department"]
)

# Read table
dt = DeltaTable("/tmp/delta/employees_rust")
df = dt.to_pandas()

# Time travel
dt.load_version(5)
df_old = dt.to_pandas()

# History
history = dt.history()

# Vacuum
dt.vacuum(retention_hours=168, dry_run=False)

# Compact
dt.optimize.compact()

# Z-Order
dt.optimize.z_order(["department", "name"])
```

---

## 🎯 Use Cases Thực Tế

### 1. Databricks - Internal Use

**Use Case:**
- Core storage format cho Databricks Lakehouse
- Powers Delta Live Tables (declarative ETL)
- Unified batch và streaming

**Scale:**
- Exabytes of data
- Millions of tables
- Thousands of concurrent users

### 2. Comcast - Media Analytics

```
┌─────────────────────────────────────────────────────────────┐
│                  Comcast Media Analytics                     │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│   Set-top Boxes         Streaming Apps                       │
│       │                      │                               │
│       └──────────┬───────────┘                               │
│                  ▼                                           │
│           ┌────────────┐                                     │
│           │   Kafka    │                                     │
│           └─────┬──────┘                                     │
│                 │                                            │
│       ┌─────────┴─────────┐                                  │
│       ▼                   ▼                                  │
│ ┌───────────┐      ┌───────────┐                             │
│ │  Streaming│      │   Batch   │                             │
│ │  (Spark)  │      │  (Spark)  │                             │
│ └─────┬─────┘      └─────┬─────┘                             │
│       │                  │                                   │
│       └────────┬─────────┘                                   │
│                ▼                                             │
│        ┌─────────────┐                                       │
│        │ Delta Lake  │                                       │
│        │  (unified)  │                                       │
│        └──────┬──────┘                                       │
│               ▼                                              │
│    ┌──────────────────────┐                                  │
│    │   BI / ML / Reports  │                                  │
│    └──────────────────────┘                                  │
│                                                              │
│   Results:                                                   │
│   • 10x faster pipelines                                     │
│   • Single source of truth                                   │
│   • Real-time dashboards                                     │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

### 3. CDC Pipeline cho Order Management

```python
# CDC Pipeline: MySQL → Debezium → Kafka → Spark Streaming → Delta Lake

# Spark Streaming code
orders_stream = spark.readStream \
    .format("kafka") \
    .option("kafka.bootstrap.servers", "localhost:9092") \
    .option("subscribe", "orders_cdc") \
    .load()

# Parse CDC events
parsed = orders_stream.select(
    from_json(col("value").cast("string"), order_schema).alias("data")
).select("data.*")

# MERGE into Delta table
def upsert_to_delta(batch_df, batch_id):
    delta_table = DeltaTable.forPath(spark, "/delta/orders")
    
    delta_table.alias("target").merge(
        batch_df.alias("source"),
        "target.order_id = source.order_id"
    ).whenMatchedUpdateAll() \
     .whenNotMatchedInsertAll() \
     .execute()

parsed.writeStream \
    .foreachBatch(upsert_to_delta) \
    .option("checkpointLocation", "/checkpoints/orders") \
    .start()
```

### 4. Financial Services - Transaction Processing

```python
# ACID transactions cho financial data
# Requirements:
# - No data loss
# - Exactly-once processing
# - Audit trail (time travel)
# - Regulatory compliance

# Write với idempotent processing
transactions = spark.readStream \
    .format("kafka") \
    .load()

def process_transactions(batch_df, batch_id):
    # Deduplicate
    deduped = batch_df.dropDuplicates(["transaction_id"])
    
    # Write với txn tracking
    delta_table = DeltaTable.forPath(spark, "/delta/transactions")
    
    delta_table.alias("t").merge(
        deduped.alias("s"),
        "t.transaction_id = s.transaction_id"
    ).whenNotMatchedInsertAll() \
     .execute()

# Enable CDF cho audit
spark.sql("""
    ALTER TABLE delta.`/delta/transactions`
    SET TBLPROPERTIES (delta.enableChangeDataFeed = true)
""")

# Audit query
spark.sql("""
    SELECT * FROM table_changes('delta.`/delta/transactions`', 0, 100)
    WHERE _change_type = 'insert'
""")
```

---

## ✅ Best Practices

### 1. Partitioning Strategy

**DO:**
- ✅ Partition cho filter-heavy columns
- ✅ Use Liquid Clustering for modern approach
- ✅ Target partition size: 1GB+

**DON'T:**
- ❌ Over-partition (too many small files)
- ❌ Partition granularity quá nhỏ

```python
# Good
df.write.format("delta") \
    .partitionBy("date", "region") \
    .save("/delta/events")

# Better (Liquid Clustering)
spark.sql("""
    CREATE TABLE events USING DELTA
    CLUSTER BY (date, user_id)
""")
```

### 2. File Size Optimization

```python
# Target file size settings
spark.conf.set("spark.databricks.delta.optimizeWrite.enabled", "true")
spark.conf.set("spark.databricks.delta.autoCompact.enabled", "true")

# Table properties
spark.sql("""
    ALTER TABLE my_table SET TBLPROPERTIES (
        delta.targetFileSize = '128mb',
        delta.autoOptimize.optimizeWrite = true,
        delta.autoOptimize.autoCompact = true
    )
""")

# Manual OPTIMIZE
spark.sql("OPTIMIZE my_table")
spark.sql("OPTIMIZE my_table WHERE date >= '2024-01-01'")
```

### 3. Z-ORDER và Clustering

```python
# Z-ORDER cho frequently filtered columns
spark.sql("""
    OPTIMIZE my_table
    ZORDER BY (user_id, event_type)
""")
```

**Best practices:**
- Z-ORDER trên columns hay filter together
- Max 4-5 columns
- High-cardinality columns benefit most
- Run sau batch writes

### 4. VACUUM và Retention

```python
# Configure retention
spark.sql("""
    ALTER TABLE my_table SET TBLPROPERTIES (
        delta.logRetentionDuration = 'interval 30 days',
        delta.deletedFileRetentionDuration = 'interval 7 days'
    )
""")

# VACUUM định kỳ (default: 7 days retention)
spark.sql("VACUUM my_table")
```

### 5. Concurrency Settings

```python
# Isolation level
spark.conf.set("spark.databricks.delta.isolationLevel", "WriteSerializable")

# Retry configuration
spark.conf.set("spark.databricks.delta.retryWriteConflict.enabled", "true")
spark.conf.set("spark.databricks.delta.retryWriteConflict.limit", "3")
```

---

## 🚀 Performance Tuning

### 1. Write Optimization

```python
# Optimize write (auto-coalesce small files)
spark.conf.set("spark.databricks.delta.optimizeWrite.enabled", "true")

# Auto compact
spark.conf.set("spark.databricks.delta.autoCompact.enabled", "true")
spark.conf.set("spark.databricks.delta.autoCompact.minNumFiles", "50")

# Adaptive Query Execution (Spark 3.0+)
spark.conf.set("spark.sql.adaptive.enabled", "true")
spark.conf.set("spark.sql.adaptive.coalescePartitions.enabled", "true")
```

### 2. Read Optimization

```python
# Data skipping (automatic với stats)
# Predicate pushdown
df = spark.read.format("delta").load("/delta/events") \
    .filter("date = '2024-01-15' AND user_id = 12345")

# Cache frequently accessed data
df = spark.read.format("delta").load("/delta/dimension_table")
df.cache()
```

### 3. MERGE Optimization

```python
# For large source:
# 1. Filter source to only relevant records
# 2. Use appropriate partition predicates
# 3. Enable optimizeWrite

# Partition-based merge (faster)
spark.sql("""
    MERGE INTO target t
    USING source s
    ON t.date = s.date AND t.id = s.id  -- Include partition column
    WHEN MATCHED THEN UPDATE SET *
    WHEN NOT MATCHED THEN INSERT *
""")
```

---

## 🔧 Troubleshooting

### 1. Small Files Problem

**Symptoms:**
- Many small files
- Slow queries

**Solution:**
```python
# OPTIMIZE
spark.sql("OPTIMIZE my_table")

# Enable auto-optimization
spark.sql("""
    ALTER TABLE my_table SET TBLPROPERTIES (
        delta.autoOptimize.optimizeWrite = true,
        delta.autoOptimize.autoCompact = true
    )
""")

# Repartition before write
df.repartition(10).write.format("delta").mode("append").save(path)
```

### 2. Concurrent Write Conflicts

**Error:** `ConcurrentModificationException`

**Solution:**
```python
# Retry logic
from time import sleep

def write_with_retry(df, path, max_retries=3):
    for attempt in range(max_retries):
        try:
            df.write.format("delta").mode("append").save(path)
            return
        except Exception as e:
            if "ConcurrentModification" in str(e) and attempt < max_retries - 1:
                sleep(2 ** attempt)  # Exponential backoff
            else:
                raise
```

### 3. Schema Mismatch

**Error:** `AnalysisException: A schema mismatch detected`

**Solution:**
```python
# Enable schema merge
df.write.format("delta") \
    .option("mergeSchema", "true") \
    .mode("append") \
    .save(path)

# Overwrite schema
df.write.format("delta") \
    .option("overwriteSchema", "true") \
    .mode("overwrite") \
    .save(path)
```

### 4. Storage Bloat

**Symptoms:** Storage growing despite deletes

**Solution:**
```python
# VACUUM
spark.sql("VACUUM my_table RETAIN 168 HOURS")

# Check what will be deleted (dry run)
spark.sql("VACUUM my_table RETAIN 168 HOURS DRY RUN")
```

---

## 📚 Resources

### Official
- Delta Lake Website: https://delta.io/
- GitHub Repository: https://github.com/delta-io/delta
- Documentation: https://docs.delta.io/

### Papers
- "Delta Lake: High-Performance ACID Table Storage over Cloud Object Stores" - VLDB 2020
- "Lakehouse: A New Generation of Open Platforms..." - CIDR 2021

### Community
- Delta Lake Slack: https://go.delta.io/slack
- Mailing Lists: https://delta.io/community

---

> **Document Version**: 1.0  
> **Last Updated**: December 31, 2025  
> **Delta Lake Version**: 4.0
