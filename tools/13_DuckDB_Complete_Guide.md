# 🦆 DuckDB - Complete Guide

> In-Process OLAP Database — SQLite for Analytics

---

## 📋 Mục Lục

1. [Giới Thiệu](#phần-1-giới-thiệu)
2. [Kiến Trúc](#phần-2-kiến-trúc)
3. [Core SQL Features](#phần-3-core-sql-features)
4. [Python Integration](#phần-4-python-integration)
5. [File Formats & Cloud](#phần-5-file-formats--cloud)
6. [Extensions](#phần-6-extensions)
7. [Data Pipeline Patterns](#phần-7-data-pipeline-patterns)
8. [MotherDuck](#phần-8-motherduck)
9. [Performance Tuning](#phần-9-performance-tuning)
10. [DuckDB vs Alternatives](#phần-10-duckdb-vs-alternatives)
11. [Hands-on Labs](#phần-11-hands-on-labs)

---

## PHẦN 1: GIỚI THIỆU

### 1.1 DuckDB là gì?

DuckDB là **embedded OLAP database** — tương tự SQLite nhưng thiết kế cho **analytics workloads** thay vì OLTP.

**Core Design Principles:**
- **In-process** — Chạy trong process của app (Python, R, Node.js), không cần server
- **Column-oriented** — Columnar storage format, tối ưu cho aggregate queries
- **Vectorized execution** — Process data in batches (2048 rows), tận dụng CPU SIMD
- **Zero dependencies** — Single binary/library, no external dependencies
- **ACID compliant** — Full transaction support
- **Zero-copy** — Integrate with Arrow, Pandas, Polars without copying data

### 1.2 DuckDB vs Traditional Databases

| Feature | DuckDB | SQLite | PostgreSQL | BigQuery |
|---------|--------|--------|------------|----------|
| **Type** | Embedded OLAP | Embedded OLTP | Server OLTP+OLAP | Cloud DWH |
| **Setup** | `pip install duckdb` | Built-in | Server install | Cloud account |
| **Storage** | Columnar | Row-based | Row-based | Columnar |
| **Best For** | Analytics, local | Mobile, simple | Production OLTP | Petabyte analytics |
| **Concurrency** | Single writer | Single writer | Multi-user | Massive |
| **10GB CSV aggregate** | ~2 seconds | Very slow | ~30 seconds | ~2 seconds |
| **Cost** | Free | Free | Free | Pay-per-query |

### 1.3 When to Use DuckDB

```mermaid
graph TD
    Start[Need to Analyze Data?] --> Size{Data Size?}
    
    Size -->|"< 100 GB"| Users{Users?}
    Size -->|"> 100 GB"| BigData[Use Trino/Spark/BigQuery]
    
    Users -->|"1 user (local)"| DuckDB[🦆 DuckDB<br/>Perfect fit!]
    Users -->|"Multiple users"| Concurrent{Concurrent writes?}
    
    Concurrent -->|"Yes"| PG[PostgreSQL / DWH]
    Concurrent -->|"No, read-only"| DuckDB
    
    DuckDB --> UseCases["Use Cases:<br/>• Ad-hoc analysis<br/>• Local dev/testing<br/>• ETL preprocessing<br/>• Data exploration<br/>• CI/CD data tests"]
    
    style DuckDB fill:#fdd835
```

### 1.4 Who Uses DuckDB

| Company | Use Case |
|---------|----------|
| **dbt Labs** | dbt-duckdb adapter for local development |
| **Motherduck** | Cloud-hosted DuckDB (hybrid execution) |
| **Evidence** | BI reporting tool powered by DuckDB |
| **Rill Data** | Real-time metrics dashboard |
| **Observable** | Interactive notebooks |
| **Google (Magika)** | File type detection engine |

---

## PHẦN 2: KIẾN TRÚC

### 2.1 Architecture Overview

```mermaid
graph TB
    subgraph App[" "]
        App_title["📱 Application Process"]
        style App_title fill:none,stroke:none,color:#333,font-weight:bold
        subgraph DuckDB[" "]
            DuckDB_title["🦆 DuckDB Library"]
            style DuckDB_title fill:none,stroke:none,color:#333,font-weight:bold
            Parser[SQL Parser<br/>PostgreSQL-compatible]
            Optimizer[Query Optimizer<br/>Cost-based]
            Executor[Vectorized Executor<br/>Batch processing]
            Storage[Storage Engine<br/>Columnar + Compressed]
            IO[I/O Layer<br/>Multi-format reader]
        end
    end

    subgraph DataSources[" "]
        DataSources_title["📁 Data Sources"]
        style DataSources_title fill:none,stroke:none,color:#333,font-weight:bold
        Local[Local Files<br/>CSV, Parquet, JSON]
        Cloud[Cloud Storage<br/>S3, GCS, Azure]
        DB[Attached DBs<br/>PostgreSQL, MySQL, SQLite]
        Memory[In-Memory<br/>Arrow, Pandas, Polars]
    end

    Parser --> Optimizer --> Executor
    Executor --> Storage
    Executor --> IO
    IO --> DataSources

    style DuckDB fill:#fff9c4
```

### 2.2 Vectorized Execution Engine

```mermaid
graph LR
    subgraph Traditional[" "]
        Traditional_title["Row-at-a-time (PostgreSQL)"]
        style Traditional_title fill:none,stroke:none,color:#333,font-weight:bold
        R1[Row 1] --> P1[Process] --> O1[Output 1]
        R2[Row 2] --> P2[Process] --> O2[Output 2]
        R3[Row N] --> P3[Process] --> O3[Output N]
    end

    subgraph Vectorized[" "]
        Vectorized_title["Vectorized (DuckDB)"]
        style Vectorized_title fill:none,stroke:none,color:#333,font-weight:bold
        Batch["Batch of 2048 rows<br/>[val1, val2, ... val2048]"]
        SIMD["SIMD Processing<br/>CPU parallel ops"]
        Result["Batch output<br/>[res1, res2, ... res2048]"]
        Batch --> SIMD --> Result
    end

    style Traditional fill:#ffcdd2
    style Vectorized fill:#c8e6c9
```

**Why vectorized is faster:**
- **CPU cache locality** — Batch fits in L1/L2 cache
- **SIMD instructions** — Process 4/8/16 values in single CPU op
- **Reduced interpretation overhead** — Per-batch, not per-row
- **Branch prediction** — Fewer conditionals per value

### 2.3 Storage Format

```mermaid
graph TB
    subgraph File[" "]
        File_title["DuckDB File (.duckdb)"]
        style File_title fill:none,stroke:none,color:#333,font-weight:bold
        Header[File Header<br/>Magic number, version]
        
        subgraph RowGroups[" "]
            RowGroups_title["Row Groups (~122K rows each)"]
            style RowGroups_title fill:none,stroke:none,color:#333,font-weight:bold
            RG1["Row Group 1"]
            RG2["Row Group 2"]
            RGN["Row Group N"]
        end
        
        subgraph Columns[" "]
            Columns_title["Per Column in Row Group"]
            style Columns_title fill:none,stroke:none,color:#333,font-weight:bold
            Meta[Column Metadata<br/>Min/Max, null count]
            Compressed[Compressed Data<br/>Dictionary, RLE, BitPacking]
        end
        
        Header --> RowGroups
        RG1 --> Columns
    end
```

**Compression algorithms used:**
- **Constant** — All values same → store once
- **Dictionary** — Low cardinality → map to integers
- **Run-Length Encoding (RLE)** — Repeated values → count
- **BitPacking** — Small integers → fewer bits
- **FSST** — Fast Static Symbol Table (strings)
- **Chimp/Patas** — Floating point compression

### 2.4 Query Processing Pipeline

```mermaid
graph LR
    SQL[SQL Query] --> Parse[Parser<br/>PostgreSQL dialect]
    Parse --> Bind[Binder<br/>Resolve names,<br/>check types]
    Bind --> Logical[Logical Plan<br/>Relational algebra]
    Logical --> Optimize[Optimizer<br/>Join reorder,<br/>filter pushdown,<br/>projection pushdown]
    Optimize --> Physical[Physical Plan<br/>Hash join, sort,<br/>scan strategy]
    Physical --> Execute[Vectorized<br/>Execution<br/>Pipeline]
    Execute --> Result[Results]
```

---

## PHẦN 3: CORE SQL FEATURES

### 3.1 DDL & Basic Queries

```sql
-- ============================================================
-- CREATE TABLE
-- ============================================================
CREATE TABLE sales (
    id INTEGER PRIMARY KEY,
    product VARCHAR NOT NULL,
    category VARCHAR,
    amount DECIMAL(10, 2),
    quantity INTEGER,
    sale_date DATE,
    customer_id INTEGER,
    region VARCHAR
);

-- CREATE TABLE AS SELECT (CTAS)
CREATE TABLE monthly_summary AS
SELECT
    date_trunc('month', sale_date) AS month,
    category,
    SUM(amount) AS total_revenue,
    COUNT(*) AS order_count
FROM sales
GROUP BY 1, 2;

-- Create from file (powerful!)
CREATE TABLE raw_events AS
SELECT * FROM 'events/*.parquet';

-- Temporary table (session-scoped)
CREATE TEMP TABLE staging AS
SELECT * FROM 'incoming_data.csv';


-- ============================================================
-- INSERT
-- ============================================================
INSERT INTO sales VALUES
    (1, 'Widget', 'Electronics', 99.99, 2, '2024-01-15', 101, 'US'),
    (2, 'Gadget', 'Electronics', 199.99, 1, '2024-01-16', 102, 'EU'),
    (3, 'Book', 'Media', 29.99, 3, '2024-01-17', 103, 'US');

-- INSERT from query
INSERT INTO sales
SELECT * FROM 'new_sales.parquet'
WHERE sale_date = CURRENT_DATE;


-- ============================================================
-- UPDATE & DELETE
-- ============================================================
UPDATE sales SET amount = amount * 1.1 WHERE region = 'EU';
DELETE FROM sales WHERE sale_date < DATE '2023-01-01';


-- ============================================================
-- UPSERT (INSERT OR REPLACE)
-- ============================================================
INSERT OR REPLACE INTO sales
SELECT * FROM staging;
```

### 3.2 Advanced Aggregations

```sql
-- ============================================================
-- GROUP BY with GROUPING SETS / CUBE / ROLLUP
-- ============================================================

-- ROLLUP: Hierarchical subtotals
SELECT
    region,
    category,
    SUM(amount) AS revenue
FROM sales
GROUP BY ROLLUP(region, category);
-- Returns: (region, category), (region, NULL), (NULL, NULL)

-- CUBE: All combinations
SELECT
    region,
    category,
    SUM(amount) AS revenue
FROM sales
GROUP BY CUBE(region, category);

-- GROUPING SETS: Custom combinations
SELECT
    region,
    category,
    date_trunc('month', sale_date) AS month,
    SUM(amount) AS revenue
FROM sales
GROUP BY GROUPING SETS (
    (region, category),
    (region, month),
    (category),
    ()
);


-- ============================================================
-- HAVING + complex aggregates
-- ============================================================
SELECT
    customer_id,
    COUNT(*) AS order_count,
    SUM(amount) AS total_spent,
    AVG(amount) AS avg_order,
    MAX(amount) AS largest_order,
    MEDIAN(amount) AS median_order,
    QUANTILE_CONT(amount, 0.95) AS p95_order,
    STDDEV(amount) AS stddev_order,
    LIST(DISTINCT category) AS categories_purchased,
    MODE(category) AS favorite_category
FROM sales
GROUP BY customer_id
HAVING total_spent > 1000
ORDER BY total_spent DESC;
```

### 3.3 Window Functions

```sql
-- ============================================================
-- Ranking
-- ============================================================
SELECT
    product,
    category,
    amount,
    ROW_NUMBER() OVER (PARTITION BY category ORDER BY amount DESC) AS row_num,
    RANK() OVER (PARTITION BY category ORDER BY amount DESC) AS rank,
    DENSE_RANK() OVER (PARTITION BY category ORDER BY amount DESC) AS dense_rank,
    NTILE(4) OVER (ORDER BY amount) AS quartile,
    PERCENT_RANK() OVER (ORDER BY amount) AS percentile
FROM sales;

-- ============================================================
-- Running aggregates
-- ============================================================
SELECT
    sale_date,
    amount,
    SUM(amount) OVER (ORDER BY sale_date) AS running_total,
    AVG(amount) OVER (
        ORDER BY sale_date
        ROWS BETWEEN 6 PRECEDING AND CURRENT ROW
    ) AS rolling_7day_avg,
    COUNT(*) OVER (
        ORDER BY sale_date
        RANGE BETWEEN INTERVAL 30 DAY PRECEDING AND CURRENT ROW
    ) AS orders_last_30d
FROM sales;

-- ============================================================
-- LAG / LEAD for comparison
-- ============================================================
SELECT
    sale_date,
    daily_revenue,
    LAG(daily_revenue, 1) OVER (ORDER BY sale_date) AS yesterday,
    LAG(daily_revenue, 7) OVER (ORDER BY sale_date) AS last_week,
    daily_revenue - LAG(daily_revenue, 1) OVER (ORDER BY sale_date) AS day_change,
    (daily_revenue - LAG(daily_revenue, 7) OVER (ORDER BY sale_date)) * 100.0 /
        LAG(daily_revenue, 7) OVER (ORDER BY sale_date) AS wow_change_pct
FROM daily_revenue;

-- ============================================================
-- FIRST_VALUE / LAST_VALUE / NTH_VALUE
-- ============================================================
SELECT
    customer_id,
    sale_date,
    product,
    FIRST_VALUE(product) OVER (
        PARTITION BY customer_id ORDER BY sale_date
    ) AS first_purchase,
    LAST_VALUE(product) OVER (
        PARTITION BY customer_id ORDER BY sale_date
        ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING
    ) AS last_purchase,
    NTH_VALUE(product, 2) OVER (
        PARTITION BY customer_id ORDER BY sale_date
    ) AS second_purchase
FROM sales;

-- ============================================================
-- Top-N per group
-- ============================================================
SELECT * FROM (
    SELECT
        category,
        product,
        SUM(amount) AS total_sales,
        ROW_NUMBER() OVER (
            PARTITION BY category ORDER BY SUM(amount) DESC
        ) AS rn
    FROM sales
    GROUP BY category, product
) WHERE rn <= 3;
```

### 3.4 List & Struct (Nested Types)

```sql
-- ============================================================
-- LIST (array) type
-- ============================================================

-- Create list
SELECT [1, 2, 3, 4, 5] AS my_list;
SELECT LIST_VALUE(1, 2, 3) AS my_list;

-- Aggregate into list
SELECT
    customer_id,
    LIST(product ORDER BY sale_date) AS purchase_history,
    LIST(DISTINCT category) AS categories
FROM sales
GROUP BY customer_id;

-- List functions
SELECT
    list_value AS arr,
    LEN(arr) AS length,
    arr[1] AS first_element,
    arr[-1] AS last_element,
    LIST_CONTAINS(arr, 'target') AS has_target,
    LIST_SORT(arr) AS sorted,
    LIST_DISTINCT(arr) AS unique_vals,
    LIST_FILTER(arr, x -> x > 10) AS filtered,
    LIST_TRANSFORM(arr, x -> x * 2) AS doubled,
    LIST_REDUCE(arr, (a, b) -> a + b) AS total,
    ARRAY_TO_STRING(arr, ', ') AS joined
FROM my_table;

-- UNNEST (explode list to rows)
SELECT customer_id, UNNEST(tags) AS tag
FROM customer_tags;

-- ============================================================
-- STRUCT (named tuple / JSON-like)
-- ============================================================

-- Create struct
SELECT {'name': 'Alice', 'age': 30, 'city': 'NYC'} AS person;

-- Access struct fields
SELECT
    person.name,
    person.age,
    person['city']
FROM my_table;

-- Aggregate into struct
SELECT
    customer_id,
    {'total': SUM(amount), 'count': COUNT(*)} AS stats
FROM sales
GROUP BY customer_id;

-- STRUCT + LIST = nested data!
SELECT
    customer_id,
    LIST({'product': product, 'amount': amount, 'date': sale_date}) AS orders
FROM sales
GROUP BY customer_id;
```

### 3.5 Common Table Expressions (CTEs)

```sql
-- ============================================================
-- Recursive CTE
-- ============================================================
WITH RECURSIVE hierarchy AS (
    -- Base case: root nodes
    SELECT id, name, parent_id, 0 AS depth, name AS path
    FROM categories
    WHERE parent_id IS NULL
    
    UNION ALL
    
    -- Recursive case
    SELECT c.id, c.name, c.parent_id, h.depth + 1,
           h.path || ' > ' || c.name
    FROM categories c
    JOIN hierarchy h ON c.parent_id = h.id
)
SELECT * FROM hierarchy ORDER BY path;

-- ============================================================
-- Generate date series
-- ============================================================
WITH RECURSIVE dates AS (
    SELECT DATE '2024-01-01' AS dt
    UNION ALL
    SELECT dt + INTERVAL 1 DAY FROM dates WHERE dt < DATE '2024-12-31'
)
SELECT dt FROM dates;

-- Or simpler with generate_series:
SELECT UNNEST(generate_series(DATE '2024-01-01', DATE '2024-12-31', INTERVAL 1 DAY)) AS dt;
```

### 3.6 Pivoting & Unpivoting

```sql
-- ============================================================
-- PIVOT (rows → columns)
-- ============================================================
PIVOT sales
ON category
USING SUM(amount)
GROUP BY region;
-- Creates: region | Electronics | Media | Clothing | ...

-- With specific values
PIVOT sales
ON category IN ('Electronics', 'Media', 'Clothing')
USING SUM(amount) AS total, COUNT(*) AS cnt
GROUP BY region;

-- ============================================================
-- UNPIVOT (columns → rows)
-- ============================================================
UNPIVOT monthly_data
ON jan, feb, mar, apr, may, jun
INTO NAME month VALUE revenue;
```

### 3.7 Advanced: QUALIFY, SAMPLE, ASOF JOIN

```sql
-- ============================================================
-- QUALIFY — filter on window functions (no subquery needed!)
-- ============================================================
SELECT
    customer_id,
    product,
    amount,
    ROW_NUMBER() OVER (PARTITION BY customer_id ORDER BY amount DESC) AS rn
FROM sales
QUALIFY rn = 1;  -- Top purchase per customer, no subquery!


-- ============================================================
-- SAMPLE — random sample
-- ============================================================
SELECT * FROM sales USING SAMPLE 10%;        -- 10% of rows
SELECT * FROM sales USING SAMPLE 1000 ROWS;  -- Exact 1000 rows
SELECT * FROM sales TABLESAMPLE RESERVOIR(5%); -- Reservoir sampling


-- ============================================================
-- ASOF JOIN — time-series join (nearest match)
-- ============================================================
-- Find the exchange rate closest to each sale
SELECT s.*, r.rate
FROM sales s
ASOF JOIN exchange_rates r
ON s.currency = r.currency
AND s.sale_date >= r.effective_date;
-- Matches each sale to the most recent rate <= sale_date


-- ============================================================
-- LATERAL JOIN — correlated subquery as join
-- ============================================================
SELECT c.*, recent_orders.*
FROM customers c,
LATERAL (
    SELECT * FROM sales
    WHERE customer_id = c.id
    ORDER BY sale_date DESC
    LIMIT 3
) recent_orders;
```

---

## PHẦN 4: PYTHON INTEGRATION

### 4.1 Basic Usage

```python
import duckdb

# ============================================================
# In-memory database
# ============================================================
con = duckdb.connect()  # Or duckdb.connect(":memory:")

# Execute + fetch
result = con.execute("SELECT 42 AS answer").fetchall()
# [(42,)]

# Execute + DataFrame
df = con.execute("SELECT * FROM range(10)").fetchdf()

# DuckDB relational API
rel = con.sql("SELECT * FROM 'data.parquet'")
rel.filter("amount > 100").aggregate("region, SUM(amount)").show()


# ============================================================
# Persistent database
# ============================================================
con = duckdb.connect("my_analytics.duckdb")

con.execute("""
    CREATE TABLE IF NOT EXISTS events AS
    SELECT * FROM 'raw_events/*.parquet'
""")

# Close connection
con.close()

# Context manager (auto-close)
with duckdb.connect("my_analytics.duckdb") as con:
    result = con.execute("SELECT count(*) FROM events").fetchone()
    print(f"Total events: {result[0]}")
```

### 4.2 Pandas Integration

```python
import duckdb
import pandas as pd

# Create Pandas DataFrame
df = pd.DataFrame({
    "user_id": [1, 2, 3, 4, 5],
    "name": ["Alice", "Bob", "Charlie", "Diana", "Eve"],
    "amount": [100, 200, 150, 300, 250],
    "date": pd.date_range("2024-01-01", periods=5)
})

# ============================================================
# Query Pandas DataFrames directly (no copy!)
# ============================================================
result = duckdb.sql("""
    SELECT
        name,
        amount,
        SUM(amount) OVER (ORDER BY date) AS running_total
    FROM df
    WHERE amount > 100
""")

# Return as Pandas
pandas_result = result.df()

# Return as Polars
polars_result = result.pl()

# Return as Arrow
arrow_result = result.arrow()

# Return as NumPy
numpy_result = result.fetchnumpy()

# ============================================================
# Multiple DataFrames in same query
# ============================================================
orders = pd.DataFrame({"order_id": [1,2], "user_id": [1,2], "amount": [99, 199]})
users = pd.DataFrame({"user_id": [1,2], "name": ["Alice", "Bob"]})

duckdb.sql("""
    SELECT u.name, SUM(o.amount) AS total_spent
    FROM orders o
    JOIN users u ON o.user_id = u.user_id
    GROUP BY u.name
""").show()
```

### 4.3 Polars Integration

```python
import duckdb
import polars as pl

# Polars DataFrame
df = pl.DataFrame({
    "category": ["A", "B", "A", "B", "C"],
    "value": [10, 20, 30, 40, 50]
})

# Query Polars directly (zero-copy via Arrow!)
result = duckdb.sql("""
    SELECT category, SUM(value) AS total
    FROM df
    GROUP BY category
    ORDER BY total DESC
""")

# Return as Polars
pl_result = result.pl()

# Polars LazyFrame → DuckDB
lf = pl.scan_parquet("data.parquet")
df_eager = lf.collect()
duckdb.sql("SELECT * FROM df_eager LIMIT 10").show()
```

### 4.4 Apache Arrow Integration

```python
import duckdb
import pyarrow as pa
import pyarrow.parquet as pq

# ============================================================
# Zero-copy from Arrow
# ============================================================
arrow_table = pa.table({
    "id": [1, 2, 3],
    "name": ["Alice", "Bob", "Charlie"],
    "score": [95.5, 87.3, 92.1]
})

result = duckdb.sql("SELECT * FROM arrow_table WHERE score > 90")
print(result.fetchall())

# ============================================================
# Return as Arrow (zero-copy)
# ============================================================
arrow_result = duckdb.sql("SELECT * FROM 'data.parquet'").arrow()

# Arrow RecordBatchReader (streaming)
reader = duckdb.sql("SELECT * FROM 'huge_data.parquet'").fetch_arrow_reader(batch_size=100_000)
for batch in reader:
    process(batch)

# ============================================================
# Arrow Flight integration
# ============================================================
# DuckDB can serve as Arrow Flight endpoint
# Useful for distributed queries
```

### 4.5 Functional API (Relational)

```python
import duckdb

# DuckDB relational API (method chaining)
rel = (
    duckdb.sql("SELECT * FROM 'sales.parquet'")
    .filter("amount > 100")
    .project("region, category, amount")
    .aggregate("region, category, SUM(amount) AS total, COUNT(*) AS cnt")
    .order("total DESC")
    .limit(20)
)

rel.show()
df = rel.df()
```

---

## PHẦN 5: FILE FORMATS & CLOUD

### 5.1 Parquet (Primary Format)

```sql
-- ============================================================
-- Read Parquet
-- ============================================================

-- Single file
SELECT * FROM 'data.parquet';
SELECT * FROM read_parquet('data.parquet');

-- Multiple files (glob)
SELECT * FROM 'data/**/*.parquet';
SELECT * FROM read_parquet(['file1.parquet', 'file2.parquet']);

-- Hive-partitioned directory
SELECT * FROM read_parquet('data/year=*/month=*/*.parquet', hive_partitioning=true);

-- Schema inspection
SELECT * FROM parquet_metadata('data.parquet');
SELECT * FROM parquet_schema('data.parquet');
SELECT * FROM parquet_file_metadata('data.parquet');

-- Filename as column
SELECT *, filename FROM read_parquet('data/*.parquet', filename=true);


-- ============================================================
-- Write Parquet
-- ============================================================

-- Simple export
COPY sales TO 'output.parquet' (FORMAT PARQUET);

-- With compression
COPY sales TO 'output.parquet' (FORMAT PARQUET, COMPRESSION ZSTD);

-- Partitioned output (hive-style)
COPY sales TO 'output/' (
    FORMAT PARQUET,
    PARTITION_BY (region, year),
    COMPRESSION ZSTD,
    ROW_GROUP_SIZE 100000
);

-- Per-thread output (parallel write)
COPY sales TO 'output/' (
    FORMAT PARQUET,
    PER_THREAD_OUTPUT true
);
```

### 5.2 CSV

```sql
-- Read CSV with auto-detection
SELECT * FROM 'data.csv';
SELECT * FROM read_csv('data.csv');

-- With options
SELECT * FROM read_csv('data.csv',
    header=true,
    delim=',',
    dateformat='%Y-%m-%d',
    timestampformat='%Y-%m-%d %H:%M:%S',
    null_padding=true,
    ignore_errors=true,
    sample_size=10000,
    all_varchar=false  -- auto-detect types
);

-- Multiple CSVs
SELECT * FROM read_csv('data/*.csv', union_by_name=true);

-- Write CSV
COPY sales TO 'output.csv' (HEADER, DELIMITER ',');
```

### 5.3 JSON

```sql
-- Read JSON / NDJSON (newline-delimited)
SELECT * FROM 'data.json';
SELECT * FROM read_json('data.ndjson', format='newline_delimited');

-- Auto-detect nested schema
SELECT * FROM read_json_auto('data.json');

-- Write JSON
COPY sales TO 'output.json';
COPY sales TO 'output.ndjson' (FORMAT JSON, ARRAY false);
```

### 5.4 Cloud Storage

```sql
-- ============================================================
-- AWS S3
-- ============================================================
INSTALL httpfs;
LOAD httpfs;

-- Credentials
SET s3_region = 'us-east-1';
SET s3_access_key_id = 'AKIAIOSFODNN7EXAMPLE';
SET s3_secret_access_key = 'wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY';

-- Or use default AWS credentials chain
SET s3_url_style = 'path';  -- For MinIO compatibility
CALL load_aws_credentials();

-- Query S3 directly
SELECT * FROM 's3://my-bucket/data/*.parquet';

-- Copy from S3
CREATE TABLE local_copy AS SELECT * FROM 's3://bucket/data.parquet';

-- Write to S3
COPY sales TO 's3://bucket/output.parquet' (FORMAT PARQUET);


-- ============================================================
-- Google Cloud Storage
-- ============================================================
SET s3_endpoint = 'storage.googleapis.com';
SET s3_access_key_id = 'GOOG...';
SET s3_secret_access_key = '...';

-- Or with HMAC keys
SELECT * FROM 'gs://bucket/data.parquet';


-- ============================================================
-- Azure Blob Storage
-- ============================================================
INSTALL azure;
LOAD azure;

SET azure_account_name = 'myaccount';
SET azure_account_key = '...';
-- Or
-- SET azure_connection_string = '...';

SELECT * FROM 'azure://container/data.parquet';


-- ============================================================
-- HTTP/HTTPS (public files)
-- ============================================================
SELECT * FROM 'https://example.com/data.parquet';
SELECT * FROM 'https://data.gov/datasets/file.csv';
```

### 5.5 Iceberg & Delta Lake

```sql
-- ============================================================
-- Apache Iceberg
-- ============================================================
INSTALL iceberg;
LOAD iceberg;

-- Read Iceberg table
SELECT * FROM iceberg_scan('s3://bucket/warehouse/db/table');

-- Iceberg metadata
SELECT * FROM iceberg_snapshots('s3://bucket/warehouse/db/table');

-- ============================================================
-- Delta Lake
-- ============================================================
INSTALL delta;
LOAD delta;

-- Read Delta table
SELECT * FROM delta_scan('s3://bucket/delta_table/');

-- With time travel
SELECT * FROM delta_scan('s3://bucket/delta_table/', version=5);
```

---

## PHẦN 6: EXTENSIONS

### 6.1 Extension System

```sql
-- List available extensions
SELECT * FROM duckdb_extensions();

-- List installed extensions
SELECT extension_name, installed, loaded
FROM duckdb_extensions()
WHERE installed;

-- Install + Load
INSTALL httpfs;  LOAD httpfs;   -- S3/GCS/Azure/HTTP
INSTALL json;    LOAD json;     -- Advanced JSON
INSTALL parquet; LOAD parquet;  -- Parquet (built-in)
INSTALL icu;     LOAD icu;      -- Unicode collation
INSTALL fts;     LOAD fts;      -- Full-text search
INSTALL spatial; LOAD spatial;  -- Geospatial (PostGIS-like)
INSTALL excel;   LOAD excel;    -- Excel files
INSTALL sqlite;  LOAD sqlite;   -- Attach SQLite DBs
INSTALL postgres; LOAD postgres; -- Attach PostgreSQL
INSTALL mysql;   LOAD mysql;     -- Attach MySQL
INSTALL tpch;    LOAD tpch;     -- TPC-H benchmark
INSTALL tpcds;   LOAD tpcds;    -- TPC-DS benchmark
INSTALL iceberg; LOAD iceberg;  -- Iceberg tables
INSTALL delta;   LOAD delta;    -- Delta Lake tables
INSTALL azure;   LOAD azure;    -- Azure Blob storage
INSTALL aws;     LOAD aws;      -- AWS credentials helper
INSTALL substrait; LOAD substrait; -- Substrait query plans
```

### 6.2 PostgreSQL Scanner

```sql
INSTALL postgres;
LOAD postgres;

-- Attach PostgreSQL database
ATTACH 'host=localhost port=5432 dbname=mydb user=reader password=pass'
AS pg (TYPE postgres);

-- Query PostgreSQL tables from DuckDB!
SELECT * FROM pg.public.users LIMIT 10;

-- Cross-database join: PostgreSQL + local Parquet
SELECT
    u.name,
    u.email,
    e.event_count
FROM pg.public.users u
JOIN (
    SELECT user_id, COUNT(*) AS event_count
    FROM 'events/*.parquet'
    GROUP BY user_id
) e ON u.id = e.user_id
ORDER BY e.event_count DESC;

-- Copy PostgreSQL → DuckDB (for faster repeated queries)
CREATE TABLE local_users AS SELECT * FROM pg.public.users;
```

### 6.3 SQLite Scanner

```sql
INSTALL sqlite;
LOAD sqlite;

ATTACH 'app.db' AS sqlite_db (TYPE sqlite);

-- Query SQLite from DuckDB
SELECT * FROM sqlite_db.main.users;

-- Migrate SQLite → Parquet (common pattern)
COPY (SELECT * FROM sqlite_db.main.events)
TO 'events.parquet' (FORMAT PARQUET);
```

### 6.4 Spatial Extension

```sql
INSTALL spatial;
LOAD spatial;

-- Create geometric data
SELECT ST_Point(40.7128, -74.0060) AS nyc;
SELECT ST_GeomFromText('POLYGON((0 0, 1 0, 1 1, 0 1, 0 0))') AS square;

-- Distance calculation
SELECT ST_Distance(
    ST_Point(40.7128, -74.0060),
    ST_Point(51.5074, -0.1278)
) AS distance_nyc_london;

-- Read GeoJSON / Shapefiles
SELECT * FROM ST_Read('boundaries.geojson');
SELECT * FROM ST_Read('districts.shp');

-- Spatial join
SELECT
    p.name,
    d.district_name
FROM points p, districts d
WHERE ST_Contains(d.geom, p.geom);
```

### 6.5 Full-Text Search

```sql
INSTALL fts;
LOAD fts;

CREATE TABLE articles (id INTEGER, title VARCHAR, content VARCHAR);
INSERT INTO articles VALUES
    (1, 'DuckDB Guide', 'DuckDB is an in-process OLAP database'),
    (2, 'Pandas Tutorial', 'Pandas is a Python data analysis library'),
    (3, 'SQL Mastery', 'SQL is essential for data engineering');

-- Create FTS index
PRAGMA create_fts_index('articles', 'id', 'title', 'content');

-- Search
SELECT id, title, score
FROM (
    SELECT *, fts_main_articles.match_bm25(id, 'DuckDB database') AS score
    FROM articles
)
WHERE score IS NOT NULL
ORDER BY score DESC;
```

---

## PHẦN 7: DATA PIPELINE PATTERNS

### 7.1 ETL Preprocessing

```python
"""
Pattern: Use DuckDB to preprocess raw files before loading to warehouse
"""
import duckdb

def preprocess_sales(input_path: str, output_path: str):
    """Clean raw CSV → Parquet with transformations."""
    duckdb.sql(f"""
        COPY (
            SELECT
                -- Clean IDs
                CAST(order_id AS INTEGER) AS order_id,
                CAST(customer_id AS INTEGER) AS customer_id,
                
                -- Clean strings
                TRIM(LOWER(product_name)) AS product_name,
                UPPER(LEFT(category, 1)) || LOWER(SUBSTR(category, 2)) AS category,
                
                -- Clean amounts
                CAST(REPLACE(REPLACE(amount, '$', ''), ',', '') AS DECIMAL(10,2)) AS amount,
                
                -- Parse dates
                STRPTIME(order_date, '%m/%d/%Y')::DATE AS order_date,
                
                -- Add computed columns
                EXTRACT(YEAR FROM STRPTIME(order_date, '%m/%d/%Y')::DATE) AS year,
                EXTRACT(MONTH FROM STRPTIME(order_date, '%m/%d/%Y')::DATE) AS month,
                
                -- Add metadata
                CURRENT_TIMESTAMP AS processed_at
                
            FROM read_csv('{input_path}',
                ignore_errors=true,
                null_padding=true
            )
            WHERE order_id IS NOT NULL
              AND amount IS NOT NULL
        )
        TO '{output_path}' (
            FORMAT PARQUET,
            COMPRESSION ZSTD,
            PARTITION_BY (year, month)
        )
    """)

preprocess_sales('raw/sales_*.csv', 'processed/sales/')
```

### 7.2 Data Quality Checks

```python
"""
Pattern: Use DuckDB for data quality validation in CI/CD
"""
import duckdb

def validate_data(file_path: str) -> dict:
    """Run data quality checks on a Parquet file."""
    checks = {}
    
    # Row count
    count = duckdb.sql(f"SELECT COUNT(*) FROM '{file_path}'").fetchone()[0]
    checks["row_count"] = count
    checks["row_count_ok"] = count > 0
    
    # Null checks
    nulls = duckdb.sql(f"""
        SELECT
            SUM(CASE WHEN order_id IS NULL THEN 1 ELSE 0 END) AS null_order_id,
            SUM(CASE WHEN amount IS NULL THEN 1 ELSE 0 END) AS null_amount,
            SUM(CASE WHEN customer_id IS NULL THEN 1 ELSE 0 END) AS null_customer_id
        FROM '{file_path}'
    """).fetchone()
    checks["null_order_id"] = nulls[0]
    checks["null_amount"] = nulls[1]
    checks["nulls_ok"] = all(n == 0 for n in nulls)
    
    # Uniqueness
    dups = duckdb.sql(f"""
        SELECT COUNT(*) - COUNT(DISTINCT order_id)
        FROM '{file_path}'
    """).fetchone()[0]
    checks["duplicates"] = dups
    checks["unique_ok"] = dups == 0
    
    # Range checks
    range_check = duckdb.sql(f"""
        SELECT
            MIN(amount) AS min_amount,
            MAX(amount) AS max_amount,
            SUM(CASE WHEN amount < 0 THEN 1 ELSE 0 END) AS negative_amounts
        FROM '{file_path}'
    """).fetchone()
    checks["min_amount"] = range_check[0]
    checks["max_amount"] = range_check[1]
    checks["range_ok"] = range_check[2] == 0
    
    # Freshness
    freshness = duckdb.sql(f"""
        SELECT MAX(order_date) AS latest_date,
               CURRENT_DATE - MAX(order_date) AS days_stale
        FROM '{file_path}'
    """).fetchone()
    checks["latest_date"] = str(freshness[0])
    checks["days_stale"] = freshness[1]
    checks["freshness_ok"] = freshness[1] is not None and freshness[1] <= 2
    
    checks["all_passed"] = all(v for k, v in checks.items() if k.endswith("_ok"))
    return checks

result = validate_data("processed/sales/**/*.parquet")
print(result)
```

### 7.3 dbt-duckdb (Local Development)

```yaml
# profiles.yml
my_project:
  target: dev
  outputs:
    dev:
      type: duckdb
      path: dev.duckdb
      threads: 4
      extensions:
        - httpfs
        - parquet
      settings:
        s3_region: us-east-1

    # Or in-memory (for CI/CD testing)
    test:
      type: duckdb
      path: ":memory:"
```

```sql
-- models/staging/stg_sales.sql
SELECT
    order_id,
    customer_id,
    product_name,
    CAST(amount AS DECIMAL(10, 2)) AS amount,
    order_date,
    region
FROM read_parquet('s3://my-bucket/raw/sales/**/*.parquet',
    hive_partitioning=true)
WHERE order_date >= '2024-01-01'
```

### 7.4 Jupyter Notebook Pattern

```python
"""
Pattern: DuckDB as the analysis engine in Jupyter
"""

import duckdb

# Persistent connection for notebook session
con = duckdb.connect()  # in-memory, fast

# Load data once
con.execute("""
    CREATE TABLE events AS
    SELECT * FROM read_parquet('s3://bucket/events/**/*.parquet',
        hive_partitioning=true)
    WHERE event_date >= '2024-01-01';
""")

# Quick analysis — use magic!
# %load_ext duckdb.magic  # If using Jupyter magic

# Cell 1: Overview
con.sql("""
    SELECT
        date_trunc('week', event_date) AS week,
        event_type,
        COUNT(*) AS count,
        COUNT(DISTINCT user_id) AS unique_users
    FROM events
    GROUP BY 1, 2
    ORDER BY 1
""").show()

# Cell 2: Export for visualization
df = con.sql("""
    SELECT event_date, COUNT(*) AS daily_events
    FROM events
    GROUP BY 1 ORDER BY 1
""").df()

import matplotlib.pyplot as plt
df.plot(x='event_date', y='daily_events', kind='line', figsize=(12, 4))
plt.title("Daily Events")
plt.show()
```

### 7.5 CLI Usage

```bash
# Start interactive CLI
duckdb

# Or with persistent database
duckdb my_analytics.duckdb

# One-liner queries
duckdb -c "SELECT count(*) FROM 'data.parquet'"

# Pipe data
cat data.csv | duckdb -c "SELECT * FROM read_csv('/dev/stdin') LIMIT 10"

# Output modes
duckdb -c "SELECT * FROM 'data.parquet' LIMIT 5" -csv
duckdb -c "SELECT * FROM 'data.parquet' LIMIT 5" -json
duckdb -c "SELECT * FROM 'data.parquet' LIMIT 5" -markdown

# Export
duckdb -c "COPY (SELECT * FROM 'input.csv' WHERE amount > 100) TO 'filtered.parquet' (FORMAT PARQUET)"
```

---

## PHẦN 8: MOTHERDUCK

### 8.1 What is MotherDuck?

```mermaid
graph LR
    subgraph Local[" "]
        Local_title["💻 Local Machine"]
        style Local_title fill:none,stroke:none,color:#333,font-weight:bold
        LocalDuck[DuckDB<br/>In-process]
        LocalFiles[Local Files]
    end

    subgraph Cloud[" "]
        Cloud_title["☁️ MotherDuck Cloud"]
        style Cloud_title fill:none,stroke:none,color:#333,font-weight:bold
        CloudDuck[Cloud DuckDB<br/>Serverless compute]
        CloudStorage[Cloud Storage<br/>Persistent databases]
        Sharing[Shared Databases<br/>Team collaboration]
    end

    LocalDuck <-->|"Hybrid Execution"| CloudDuck
    LocalFiles --> LocalDuck
    CloudDuck --> CloudStorage
    CloudStorage --> Sharing
```

**MotherDuck = Cloud DuckDB** with:
- **Hybrid execution** — Query runs locally + cloud simultaneously
- **Persistent cloud databases** — Always-on, no server management
- **Data sharing** — Share databases and queries across team
- **Web UI** — Browser-based SQL editor
- **Python SDK** — Same duckdb API, just different connection string

### 8.2 Getting Started

```python
import duckdb

# Connect to MotherDuck (first time: opens browser for auth)
con = duckdb.connect("md:")

# Or with token
con = duckdb.connect("md:?motherduck_token=YOUR_TOKEN")

# Create cloud database
con.execute("CREATE DATABASE IF NOT EXISTS analytics")
con.execute("USE analytics")

# Upload local data to cloud
con.execute("""
    CREATE TABLE events AS
    SELECT * FROM 'local_events/*.parquet'
""")

# Query cloud data
con.execute("SELECT count(*) FROM events").show()
```

### 8.3 Hybrid Execution

```python
# MotherDuck can split queries between local and cloud
con = duckdb.connect("md:analytics")

# Join local file with cloud table
con.execute("""
    SELECT
        c.customer_name,
        c.tier,
        e.event_count,
        e.last_event
    FROM 'local_customers.parquet' c
    JOIN (
        SELECT customer_id, COUNT(*) AS event_count, MAX(event_date) AS last_event
        FROM analytics.events
        GROUP BY customer_id
    ) e ON c.id = e.customer_id
""").show()
# Local file scanned locally, cloud table scanned in cloud
# Join happens where it's most efficient
```

### 8.4 Data Sharing

```sql
-- Create a shareable database
CREATE SHARE my_analytics_share FROM analytics;

-- Team member can attach the share
ATTACH 'md:_share/org_name/my_analytics_share' AS shared_data;
SELECT * FROM shared_data.events LIMIT 10;
```

### 8.5 MotherDuck Pricing

| Plan | Storage | Compute | Features |
|------|---------|---------|----------|
| **Free** | 10 GB | Limited | Personal use |
| **Pro** | Pay per GB | Pay per compute | Teams, sharing |
| **Enterprise** | Custom | Custom | SSO, SLA, support |

---

## PHẦN 9: PERFORMANCE TUNING

### 9.1 Query Optimization

```sql
-- ============================================================
-- 1. Use Parquet instead of CSV
-- ============================================================
-- ❌ Slow: CSV (full scan, type inference)
SELECT * FROM 'data.csv' WHERE date >= '2024-01-01';

-- ✅ Fast: Parquet (column pruning, row group filtering)
SELECT * FROM 'data.parquet' WHERE date >= '2024-01-01';


-- ============================================================
-- 2. Partition data (Hive-style)
-- ============================================================
-- Write partitioned
COPY sales TO 'data/' (FORMAT PARQUET, PARTITION_BY (year, month));

-- Read with partition pruning
SELECT * FROM read_parquet('data/year=2024/month=01/*.parquet');


-- ============================================================
-- 3. Use projection pushdown
-- ============================================================
-- ❌ SELECT * reads all columns
SELECT * FROM 'data.parquet' WHERE id = 1;

-- ✅ Select only needed columns
SELECT id, name, amount FROM 'data.parquet' WHERE id = 1;


-- ============================================================
-- 4. EXPLAIN ANALYZE
-- ============================================================
EXPLAIN ANALYZE
SELECT region, SUM(amount) FROM sales GROUP BY region;


-- ============================================================
-- 5. Pragma for tuning
-- ============================================================
PRAGMA threads=8;                     -- Number of threads
PRAGMA memory_limit='4GB';            -- Memory limit
PRAGMA temp_directory='/tmp/duckdb';   -- Temp dir for spill
PRAGMA enable_object_cache=true;       -- Cache Parquet metadata
PRAGMA enable_progress_bar=true;       -- Show progress
```

### 9.2 Memory Management

```python
import duckdb

# Set memory limit
con = duckdb.connect()
con.execute("PRAGMA memory_limit='8GB'")
con.execute("PRAGMA temp_directory='/mnt/ssd/duckdb-tmp'")

# For larger-than-memory queries:
# DuckDB automatically spills to disk when memory is exceeded
# The temp_directory should be on fast storage (SSD)

# Check memory usage
con.execute("PRAGMA database_size").show()
```

### 9.3 Parallel Execution

```python
# DuckDB uses all cores by default
import duckdb
import os

# Control thread count
os.environ["DUCKDB_NO_THREADS"] = "8"
# Or
con = duckdb.connect()
con.execute("PRAGMA threads=8")

# Parallel file reading
# DuckDB automatically parallelizes reading multiple files
result = con.execute("""
    SELECT * FROM read_parquet('data/*.parquet')
""")
# Each file processed by different thread
```

---

## PHẦN 10: DUCKDB VS ALTERNATIVES

### 10.1 Comparison Matrix

| Feature | DuckDB | Polars | SQLite | PostgreSQL | Spark |
|---------|--------|--------|--------|------------|-------|
| **API** | SQL | DataFrame | SQL | SQL | Both |
| **Deployment** | Embedded | Library | Embedded | Server | Cluster |
| **Best Size** | < 100 GB | < 100 GB | < 10 GB | Any | > 100 GB |
| **Speed (OLAP)** | ⚡⚡⚡ | ⚡⚡⚡ | ⚡ | ⚡⚡ | ⚡⚡ |
| **Concurrency** | Low | Single | Low | High | High |
| **Cloud Support** | MotherDuck | — | — | RDS/Cloud SQL | Databricks |
| **File Queries** | ✅ Native | ✅ scan | ❌ | ❌ | ✅ |
| **Zero-copy** | Arrow | Arrow | ❌ | ❌ | ❌ |

### 10.2 DuckDB + Polars Combo

```python
"""
Best practice: Use BOTH DuckDB and Polars together
- DuckDB for SQL queries, file reading, aggregation
- Polars for DataFrame transformations, complex logic
"""
import duckdb
import polars as pl

# DuckDB: Complex SQL aggregation
summary = duckdb.sql("""
    SELECT
        region,
        product_category,
        SUM(revenue) AS total_revenue,
        COUNT(DISTINCT customer_id) AS unique_customers,
        MEDIAN(order_value) AS median_order
    FROM 'sales/**/*.parquet'
    WHERE order_date >= '2024-01-01'
    GROUP BY 1, 2
    HAVING total_revenue > 10000
""").pl()  # Return as Polars DataFrame

# Polars: Complex transformation logic
result = (
    summary
    .with_columns([
        (pl.col("total_revenue") / pl.col("unique_customers")).alias("revenue_per_customer"),
        pl.col("total_revenue").rank(descending=True).over("region").alias("rank_in_region"),
    ])
    .filter(pl.col("rank_in_region") <= 5)
    .sort(["region", "rank_in_region"])
)

print(result)
```

---

## PHẦN 11: HANDS-ON LABS

### Lab 1: Local Analytics with DuckDB

```python
"""
Lab: Analyze TPC-H data with DuckDB
"""
import duckdb

con = duckdb.connect()

# Generate TPC-H data
con.execute("INSTALL tpch; LOAD tpch")
con.execute("CALL dbgen(sf=1)")  # 1 GB of data

# Explore
con.execute("SHOW TABLES").show()

# Query: Revenue by nation
con.execute("""
    SELECT
        n.n_name AS nation,
        SUM(l.l_extendedprice * (1 - l.l_discount)) AS revenue
    FROM lineitem l
    JOIN orders o ON l.l_orderkey = o.o_orderkey
    JOIN customer c ON o.o_custkey = c.c_custkey
    JOIN nation n ON c.c_nationkey = n.n_nationkey
    WHERE o.o_orderdate >= DATE '1994-01-01'
      AND o.o_orderdate < DATE '1995-01-01'
    GROUP BY n.n_name
    ORDER BY revenue DESC
    LIMIT 10
""").show()
```

### Lab 2: ETL Pipeline — CSV → Parquet → Analytics

```python
"""
Lab: Build a mini ETL pipeline with DuckDB
"""
import duckdb

con = duckdb.connect("lab.duckdb")

# Step 1: Ingest raw CSV
con.execute("""
    CREATE OR REPLACE TABLE raw_sales AS
    SELECT *
    FROM read_csv('https://raw.githubusercontent.com/datasciencedojo/datasets/master/titanic.csv')
""")

# Step 2: Transform
con.execute("""
    CREATE OR REPLACE TABLE passengers AS
    SELECT
        PassengerId AS passenger_id,
        Survived AS survived,
        Pclass AS class,
        Name AS name,
        CASE Sex WHEN 'male' THEN 'M' ELSE 'F' END AS gender,
        COALESCE(Age, 0) AS age,
        SibSp AS siblings,
        Parch AS parents,
        Fare AS fare,
        COALESCE(Embarked, 'Unknown') AS embarked
    FROM raw_sales
""")

# Step 3: Analyze
con.execute("""
    SELECT
        class,
        gender,
        COUNT(*) AS total,
        SUM(survived) AS survived,
        ROUND(AVG(survived) * 100, 1) AS survival_rate_pct,
        ROUND(AVG(age), 1) AS avg_age,
        ROUND(AVG(fare), 2) AS avg_fare
    FROM passengers
    WHERE age > 0
    GROUP BY ROLLUP(class, gender)
    ORDER BY class NULLS LAST, gender NULLS LAST
""").show()

# Step 4: Export
con.execute("""
    COPY passengers TO 'output/passengers.parquet' (FORMAT PARQUET, COMPRESSION ZSTD)
""")

con.close()
```

### Lab 3: Cross-Database Query

```python
"""
Lab: Join PostgreSQL + local Parquet + S3 data
"""
import duckdb

con = duckdb.connect()
con.execute("INSTALL postgres; LOAD postgres")
con.execute("INSTALL httpfs; LOAD httpfs")

# Attach PostgreSQL
con.execute("""
    ATTACH 'host=localhost dbname=app user=reader password=pass'
    AS pg (TYPE postgres)
""")

# Query across sources
result = con.execute("""
    SELECT
        u.name,
        u.email,
        local_events.event_count,
        local_events.last_event
    FROM pg.public.users u
    LEFT JOIN (
        SELECT
            user_id,
            COUNT(*) AS event_count,
            MAX(event_date) AS last_event
        FROM read_parquet('events/*.parquet')
        GROUP BY user_id
    ) local_events ON u.id = local_events.user_id
    ORDER BY local_events.event_count DESC NULLS LAST
    LIMIT 20
""")
result.show()
```

---

## 📦 Verified Resources

| Resource | Link | Note |
|----------|------|------|
| DuckDB GitHub | [duckdb/duckdb](https://github.com/duckdb/duckdb) | 28k⭐ Main repo |
| DuckDB Docs | [duckdb.org/docs](https://duckdb.org/docs/) | Official docs |
| DuckDB Python | [PyPI: duckdb](https://pypi.org/project/duckdb/) | Python package |
| MotherDuck | [motherduck.com](https://motherduck.com/) | Cloud DuckDB |
| dbt-duckdb | [duckdb/dbt-duckdb](https://github.com/duckdb/dbt-duckdb) | dbt adapter |
| DuckDB Blog | [duckdb.org/news](https://duckdb.org/news/) | Performance deep-dives |
| DuckDB Discord | [Discord invite](https://discord.duckdb.org/) | Community |
| DuckDB Extensions | [community-extensions](https://community-extensions.duckdb.org/) | Extension hub |

---

## 🔗 Liên Kết Nội Bộ

- [[12_Polars_Complete_Guide|Polars]] — DataFrame complement to DuckDB
- [[14_Trino_Presto_Complete_Guide|Trino]] — Distributed query engine (scale up)
- [[06_Apache_Spark_Complete_Guide|Apache Spark]] — Big data processing
- [[../fundamentals/06_Data_Formats_Storage|Data Formats]] — Parquet, ORC, Avro
- [[../fundamentals/13_Python_Data_Engineering|Python for DE]] — Python ecosystem

---

*Last Updated: February 2026*
*Coverage: Architecture, SQL, Python, Cloud, Extensions, Pipelines, MotherDuck*
