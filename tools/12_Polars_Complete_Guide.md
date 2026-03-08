# 🐻‍❄️ Polars - Complete Guide

> Blazing-fast DataFrame Library — Written in Rust, Designed for Performance

---

## 📋 Mục Lục

1. [Giới Thiệu](#phần-1-giới-thiệu)
2. [Kiến Trúc](#phần-2-kiến-trúc)
3. [Core Concepts](#phần-3-core-concepts)
4. [Expression API](#phần-4-expression-api)
5. [Data I/O](#phần-5-data-io)
6. [Advanced Operations](#phần-6-advanced-operations)
7. [Window Functions](#phần-7-window-functions)
8. [Joins & Combine](#phần-8-joins--combine)
9. [Time Series & Temporal](#phần-9-time-series--temporal)
10. [Production Patterns](#phần-10-production-patterns)
11. [Polars vs Alternatives](#phần-11-polars-vs-alternatives)
12. [Hands-on Labs](#phần-12-hands-on-labs)

---

## PHẦN 1: GIỚI THIỆU

### 1.1 Polars là gì?

Polars là **high-performance DataFrame library** viết bằng **Rust**, cung cấp Python API.

**Tại sao Polars nhanh hơn Pandas:**
- **Rust core** — Memory-safe, zero-cost abstractions, no GIL
- **Apache Arrow backend** — Columnar memory format, zero-copy interop
- **Lazy evaluation** — Query optimization before execution
- **Multithreaded** — Parallel execution by default
- **Vectorized operations** — SIMD on columnar data
- **Predicate/projection pushdown** — Skip unnecessary work
- **Streaming** — Process larger-than-memory datasets

### 1.2 When to Use Polars

```mermaid
graph TD
    Start[Need to Process Data?] --> Lang{Language?}
    
    Lang -->|Python| Size{Data Size?}
    Lang -->|Other| Other["Use DuckDB (SQL)<br/>or Spark (JVM)"]
    
    Size -->|"< 1 GB"| Speed{Performance matters?}
    Size -->|"1-100 GB"| Polars["🐻‍❄️ Polars<br/>Best choice"]
    Size -->|"> 100 GB"| Big{Infrastructure?}
    
    Speed -->|"Yes"| Polars
    Speed -->|"Not really"| Pandas["Pandas<br/>More ecosystem/examples"]
    
    Big -->|"Single node"| Polars
    Big -->|"Cluster"| Spark["Apache Spark<br/>Distributed processing"]
    
    Polars --> UseCase["Use Cases:<br/>• ETL pipelines<br/>• Feature engineering<br/>• Data quality checks<br/>• Analytics preprocessing<br/>• ML data prep"]
    
    style Polars fill:#1e88e5,color:white
```

### 1.3 Installation

```bash
# Standard
pip install polars

# With all optional dependencies
pip install 'polars[all]'

# Specific extras
pip install 'polars[numpy,pandas,pyarrow,timezone,connectorx,xlsx2csv]'

# GPU support (cuDF interop)
pip install cudf-polars
```

### 1.4 Who Uses Polars

| Company | Use Case |
|---------|----------|
| **Hugging Face** | Dataset processing for ML |
| **Grafana Labs** | Log analytics pipelines |
| **Citadel** | Financial data processing |
| **Various fintechs** | Real-time analytics |

---

## PHẦN 2: KIẾN TRÚC

### 2.1 Architecture Overview

```mermaid
graph TB
    subgraph PythonAPI[" "]
        PythonAPI_title["🐍 Python API Layer"]
        style PythonAPI_title fill:none,stroke:none,color:#333,font-weight:bold
        Eager[Eager Mode<br/>DataFrame]
        Lazy[Lazy Mode<br/>LazyFrame]
        SQL[SQL Interface<br/>pl.sql]
    end

    subgraph RustCore[" "]
        RustCore_title["🦀 Rust Core Engine"]
        style RustCore_title fill:none,stroke:none,color:#333,font-weight:bold
        QueryPlanner[Query Planner<br/>Optimization]
        Executor[Execution Engine<br/>Multithreaded]
        Memory[Memory Manager<br/>Apache Arrow]
    end

    subgraph IO[" "]
        IO_title["📁 I/O Layer"]
        style IO_title fill:none,stroke:none,color:#333,font-weight:bold
        CSV[CSV Reader/Writer]
        Parquet[Parquet Reader/Writer]
        JSON[JSON/NDJSON]
        IPC[Arrow IPC]
        DB[ConnectorX<br/>Database]
        Delta[Delta Lake]
    end

    Eager --> Executor
    Lazy --> QueryPlanner
    SQL --> QueryPlanner
    QueryPlanner --> Executor
    Executor --> Memory
    Executor --> IO

    style RustCore fill:#dea584
```

### 2.2 Lazy vs Eager Execution

```mermaid
graph LR
    subgraph EagerMode[" "]
        EagerMode_title["Eager Mode (like Pandas)"]
        style EagerMode_title fill:none,stroke:none,color:#333,font-weight:bold
        E1["df.filter(...)"] --> E2["Intermediate\nDataFrame"]
        E2 --> E3["df.group_by(...)"]
        E3 --> E4["Intermediate\nDataFrame"]
        E4 --> E5["df.select(...)"]
        E5 --> E6["Result"]
    end

    subgraph LazyMode[" "]
        LazyMode_title["Lazy Mode (Recommended)"]
        style LazyMode_title fill:none,stroke:none,color:#333,font-weight:bold
        L1["lf.filter(...)"] --> L2["Query Plan\nNode"]
        L2 --> L3["lf.group_by(...)"]
        L3 --> L4["Query Plan\nNode"]
        L4 --> L5["lf.select(...)"]
        L5 --> L6["Optimizer"]
        L6 --> L7["Optimized\nExecution"]
        L7 --> L8["Result"]
    end

    style EagerMode fill:#ffcdd2
    style LazyMode fill:#c8e6c9
```

**Lazy optimizations:**
- **Predicate pushdown** — filter pushed before join/scan
- **Projection pushdown** — only read required columns
- **Type coercion** — minimal casting
- **Common subexpression elimination** — avoid redundant work
- **Parallel execution** — automatic parallelism
- **Join order optimization** — smaller tables first
- **Slice pushdown** — limit pushed to scan

```python
import polars as pl

# ============================================================
# Eager: Execute immediately (like Pandas)
# ============================================================
df = pl.read_parquet("data.parquet")       # Read entire file
filtered = df.filter(pl.col("amount") > 100)  # Execute now
result = filtered.select("id", "amount")       # Execute now

# ============================================================
# Lazy: Build plan, optimize, then execute
# ============================================================
result = (
    pl.scan_parquet("data.parquet")         # Don't read yet
    .filter(pl.col("amount") > 100)        # Add to plan
    .select("id", "amount")                # Add to plan
    .collect()                              # NOW execute (optimized)
)
# Optimizer: reads only 'id','amount' columns, filters during scan
```

### 2.3 Apache Arrow Memory Model

```mermaid
graph LR
    subgraph PandasMem[" "]
        PandasMem_title["Pandas Memory"]
        style PandasMem_title fill:none,stroke:none,color:#333,font-weight:bold
        PCol1["Column 1<br/>Python objects<br/>scattered in heap"]
        PCol2["Column 2<br/>NumPy array"]
    end

    subgraph ArrowMem[" "]
        ArrowMem_title["Polars/Arrow Memory"]
        style ArrowMem_title fill:none,stroke:none,color:#333,font-weight:bold
        ACol1["Column 1<br/>Contiguous buffer<br/>cache-friendly"]
        ACol2["Column 2<br/>Contiguous buffer<br/>null bitmap"]
    end

    style PandasMem fill:#ffcdd2
    style ArrowMem fill:#c8e6c9
```

**Why Arrow is faster:**
- Columns stored in **contiguous memory buffers**
- CPU cache lines hit sequentially (cache-friendly)
- **Null bitmap** — 1 bit per row, not Python None objects
- **Zero-copy** sharing between Polars, DuckDB, Spark, etc.
- **String dictionary encoding** — shared string pool

---

## PHẦN 3: CORE CONCEPTS

### 3.1 DataFrame & Series

```python
import polars as pl

# ============================================================
# Create DataFrame
# ============================================================

# From dict
df = pl.DataFrame({
    "name": ["Alice", "Bob", "Charlie", "Diana"],
    "age": [30, 25, 35, 28],
    "city": ["NYC", "LA", "NYC", "SF"],
    "salary": [80000, 65000, 95000, 72000]
})

# From records (list of dicts)
df = pl.DataFrame([
    {"name": "Alice", "age": 30},
    {"name": "Bob", "age": 25}
])

# With schema
df = pl.DataFrame(
    {"id": [1, 2, 3], "value": [1.5, 2.5, 3.5]},
    schema={"id": pl.Int64, "value": pl.Float32}
)

# ============================================================
# Inspect DataFrame
# ============================================================
print(df.shape)          # (4, 4)
print(df.columns)        # ['name', 'age', 'city', 'salary']
print(df.dtypes)         # [Utf8, Int64, Utf8, Int64]
print(df.schema)         # {'name': Utf8, 'age': Int64, ...}
df.describe()            # Statistics summary
df.head(5)               # First 5 rows
df.tail(5)               # Last 5 rows
df.sample(3)             # Random 3 rows
df.glimpse()             # Transposed view (wide DataFrames)
df.null_count()          # Null count per column
df.estimated_size("mb")  # Memory usage

# ============================================================
# Series (single column)
# ============================================================
s = pl.Series("ages", [30, 25, 35, 28])
print(s.mean())       # 29.5
print(s.median())     # 29.0
print(s.std())        # 4.20
print(s.min(), s.max())  # 25, 35
print(s.is_sorted())  # False
print(s.n_unique())   # 4
print(s.value_counts())  # Frequency table
```

### 3.2 Selecting & Filtering

```python
# ============================================================
# SELECT columns
# ============================================================

# By name
df.select("name", "age")
df.select(pl.col("name", "age"))

# By regex
df.select(pl.col("^salary.*$"))

# By type
df.select(pl.col(pl.Int64))          # All integer columns
df.select(cs.numeric())              # Using column selectors
df.select(cs.string())               # All string columns
df.select(cs.by_dtype(pl.Float64))   # By specific dtype

# All except
df.select(pl.exclude("salary"))

# With transformation
df.select(
    pl.col("name"),
    pl.col("age"),
    (pl.col("salary") / 12).round(2).alias("monthly_salary"),
    pl.col("city").str.to_uppercase().alias("city_upper")
)

# ============================================================
# FILTER rows
# ============================================================
df.filter(pl.col("age") > 30)
df.filter(pl.col("city") == "NYC")
df.filter(pl.col("city").is_in(["NYC", "SF"]))
df.filter(pl.col("name").str.starts_with("A"))

# Multiple conditions
df.filter(
    (pl.col("age") > 25) & (pl.col("salary") > 70000)
)
df.filter(
    (pl.col("city") == "NYC") | (pl.col("city") == "SF")
)

# Null handling
df.filter(pl.col("salary").is_not_null())
df.filter(pl.col("name").is_not_nan())
```

### 3.3 with_columns & Mutations

```python
# ============================================================
# Add / modify columns
# ============================================================
df = df.with_columns(
    # New computed column
    (pl.col("salary") * 0.3).alias("tax"),
    
    # Modify existing
    pl.col("name").str.to_uppercase(),
    
    # Conditional
    pl.when(pl.col("age") > 30)
      .then(pl.lit("Senior"))
      .otherwise(pl.lit("Junior"))
      .alias("level"),
    
    # Rank
    pl.col("salary").rank(descending=True).alias("salary_rank"),
    
    # Cumulative
    pl.col("salary").cum_sum().alias("running_total"),
    
    # Shift
    pl.col("salary").shift(1).alias("prev_salary"),
)

# ============================================================
# Rename
# ============================================================
df.rename({"name": "full_name", "city": "location"})

# ============================================================
# Cast types
# ============================================================
df.with_columns(
    pl.col("age").cast(pl.Float64),
    pl.col("salary").cast(pl.Utf8),
)

# ============================================================
# Drop columns
# ============================================================
df.drop("city", "salary")
```

---

## PHẦN 4: EXPRESSION API

### 4.1 Expression System Architecture

```mermaid
graph TB
    subgraph Expressions[" "]
        Expressions_title["Expression System"]
        style Expressions_title fill:none,stroke:none,color:#333,font-weight:bold
        Col["pl.col('x')<br/>Column reference"]
        Lit["pl.lit(42)<br/>Literal value"]
        When["pl.when(...)<br/>Conditional"]
        Agg["pl.sum, pl.mean<br/>Aggregation"]
        
        Col --> Chain["Method Chaining<br/>.str, .dt, .list, .struct"]
        Chain --> Alias[".alias('name')<br/>Output naming"]
    end
    
    subgraph Contexts[" "]
        Contexts_title["Expression Contexts"]
        style Contexts_title fill:none,stroke:none,color:#333,font-weight:bold
        Select[".select()<br/>Column selection"]
        Filter[".filter()<br/>Row filtering"]
        WithCol[".with_columns()<br/>Add/modify columns"]
        GroupBy[".group_by().agg()<br/>Aggregation"]
    end
    
    Expressions --> Contexts
```

### 4.2 String Expressions

```python
df = pl.DataFrame({
    "text": ["Hello World", "  POLARS  ", "data-engineering", "foo_bar_baz", None]
})

df.with_columns(
    # Basic transforms
    pl.col("text").str.to_lowercase().alias("lower"),
    pl.col("text").str.to_uppercase().alias("upper"),
    pl.col("text").str.strip_chars().alias("stripped"),
    
    # Length & contains
    pl.col("text").str.len_chars().alias("char_count"),
    pl.col("text").str.len_bytes().alias("byte_count"),
    pl.col("text").str.contains("World").alias("has_world"),
    pl.col("text").str.starts_with("Hello").alias("starts_hello"),
    pl.col("text").str.ends_with("ing").alias("ends_ing"),
    
    # Extract & replace
    pl.col("text").str.extract(r"(\w+)", 1).alias("first_word"),
    pl.col("text").str.replace("-", "_").alias("replaced"),
    pl.col("text").str.replace_all(r"[_-]", " ").alias("cleaned"),
    
    # Split
    pl.col("text").str.split("-").alias("split_list"),
    pl.col("text").str.split_exact("-", 2).alias("split_struct"),
    
    # Slice
    pl.col("text").str.slice(0, 5).alias("first_5"),
    
    # Pad
    pl.col("text").str.pad_start(20, " ").alias("padded"),
    
    # JSON
    # pl.col("json_col").str.json_decode().alias("parsed"),
)
```

### 4.3 Date/Time Expressions

```python
df = pl.DataFrame({
    "timestamp": [
        "2024-01-15 10:30:00",
        "2024-03-20 14:45:30",
        "2024-06-01 08:00:00",
        "2024-12-25 00:00:00",
    ]
}).with_columns(
    pl.col("timestamp").str.to_datetime("%Y-%m-%d %H:%M:%S")
)

df.with_columns(
    # Extract components
    pl.col("timestamp").dt.year().alias("year"),
    pl.col("timestamp").dt.month().alias("month"),
    pl.col("timestamp").dt.day().alias("day"),
    pl.col("timestamp").dt.hour().alias("hour"),
    pl.col("timestamp").dt.minute().alias("minute"),
    pl.col("timestamp").dt.weekday().alias("weekday"),  # 0=Monday
    pl.col("timestamp").dt.week().alias("iso_week"),
    pl.col("timestamp").dt.ordinal_day().alias("day_of_year"),
    pl.col("timestamp").dt.quarter().alias("quarter"),
    
    # Truncate
    pl.col("timestamp").dt.truncate("1h").alias("hourly"),
    pl.col("timestamp").dt.truncate("1d").alias("daily"),
    pl.col("timestamp").dt.truncate("1mo").alias("monthly"),
    pl.col("timestamp").dt.truncate("1w").alias("weekly"),
    
    # Arithmetic
    (pl.col("timestamp") + pl.duration(days=7)).alias("plus_7days"),
    (pl.col("timestamp") - pl.duration(hours=2)).alias("minus_2hrs"),
    
    # Difference
    (pl.col("timestamp").diff()).alias("time_diff"),
    
    # Epoch
    pl.col("timestamp").dt.epoch("s").alias("unix_seconds"),
    pl.col("timestamp").dt.epoch("ms").alias("unix_millis"),
    
    # Format
    pl.col("timestamp").dt.to_string("%Y/%m/%d").alias("formatted"),
)
```

### 4.4 List Expressions

```python
df = pl.DataFrame({
    "tags": [["python", "rust"], ["java", "python", "scala"], ["rust"]],
    "scores": [[90, 85, 92], [78, 88], [95, 91, 87, 82]]
})

df.with_columns(
    # Length
    pl.col("tags").list.len().alias("tag_count"),
    
    # Access
    pl.col("tags").list.first().alias("first_tag"),
    pl.col("tags").list.last().alias("last_tag"),
    pl.col("tags").list.get(1).alias("second_tag"),
    
    # Contains
    pl.col("tags").list.contains("python").alias("has_python"),
    
    # Aggregate
    pl.col("scores").list.mean().alias("avg_score"),
    pl.col("scores").list.sum().alias("total_score"),
    pl.col("scores").list.min().alias("min_score"),
    pl.col("scores").list.max().alias("max_score"),
    
    # Transform
    pl.col("scores").list.sort().alias("sorted_scores"),
    pl.col("scores").list.reverse().alias("reversed"),
    pl.col("tags").list.join(", ").alias("tags_str"),
    pl.col("tags").list.unique().alias("unique_tags"),
    
    # Set operations
    pl.col("tags").list.set_intersection(pl.lit(["python", "rust"])).alias("overlap"),
)

# Explode (unnest) list to rows
df.explode("tags")
```

### 4.5 Struct Expressions

```python
# Create struct column
df = pl.DataFrame({
    "id": [1, 2, 3],
    "info": [
        {"name": "Alice", "age": 30},
        {"name": "Bob", "age": 25},
        {"name": "Charlie", "age": 35}
    ]
})

df.with_columns(
    # Access struct fields
    pl.col("info").struct.field("name").alias("name"),
    pl.col("info").struct.field("age").alias("age"),
)

# Unnest struct to columns
df.unnest("info")
# Result: id | name | age

# Create struct from columns
df.select(
    pl.struct("id", "name").alias("person")
)
```

---

## PHẦN 5: DATA I/O

### 5.1 Parquet (Recommended)

```python
# ============================================================
# Read Parquet
# ============================================================

# Eager
df = pl.read_parquet("data.parquet")

# Lazy (recommended — enables pushdown optimizations)
lf = pl.scan_parquet("data.parquet")

# Multiple files
df = pl.read_parquet("data/*.parquet")
lf = pl.scan_parquet("data/**/*.parquet")

# With options
lf = pl.scan_parquet(
    "data/*.parquet",
    n_rows=10000,              # Read only first N rows
    row_index_name="row_nr",   # Add row index column
    hive_partitioning=True,    # Hive-style partitions
    rechunk=True,              # Rechunk for contiguous memory
)

# Read specific columns (without lazy)
df = pl.read_parquet("data.parquet", columns=["id", "name", "amount"])

# ============================================================
# Write Parquet
# ============================================================
df.write_parquet("output.parquet")
df.write_parquet(
    "output.parquet",
    compression="zstd",
    compression_level=3,
    row_group_size=100_000,
    statistics=True,       # Column stats for predicate pushdown
    use_pyarrow=True,      # Use PyArrow writer
)

# Streaming write (larger-than-memory)
lf.sink_parquet(
    "output.parquet",
    compression="zstd"
)

# Partitioned write
import pyarrow as pa
import pyarrow.parquet as pq

table = df.to_arrow()
pq.write_to_dataset(
    table,
    root_path="output/",
    partition_cols=["year", "month"]
)
```

### 5.2 CSV

```python
# Read CSV
df = pl.read_csv("data.csv")
lf = pl.scan_csv("data.csv")

# With options
df = pl.read_csv(
    "data.csv",
    separator=",",
    has_header=True,
    skip_rows=0,
    n_rows=10000,
    dtypes={"id": pl.Int64, "amount": pl.Float64},
    null_values=["NA", "null", ""],
    try_parse_dates=True,
    encoding="utf8",
    ignore_errors=True,
    low_memory=False,
)

# Write CSV
df.write_csv("output.csv")
df.write_csv("output.csv", separator="|", include_header=True)

# Streaming CSV
lf.sink_csv("output.csv")
```

### 5.3 JSON / NDJSON

```python
# JSON
df = pl.read_json("data.json")

# NDJSON (newline-delimited — better for large files)
df = pl.read_ndjson("data.ndjson")
lf = pl.scan_ndjson("data.ndjson")

# Write
df.write_json("output.json")
df.write_ndjson("output.ndjson")
lf.sink_ndjson("output.ndjson")
```

### 5.4 Database (ConnectorX)

```python
# Read from database (uses ConnectorX for speed)
df = pl.read_database(
    query="SELECT * FROM users WHERE active = true",
    connection="postgresql://user:pass@host:5432/db"
)

# Or with SQLAlchemy
from sqlalchemy import create_engine
engine = create_engine("postgresql://user:pass@host:5432/db")
df = pl.read_database(
    query="SELECT * FROM events LIMIT 100000",
    connection=engine
)

# Write to database
df.write_database(
    table_name="output_table",
    connection="postgresql://user:pass@host:5432/db",
    if_table_exists="replace"  # or "append"
)
```

### 5.5 Delta Lake

```python
# Read Delta Lake
df = pl.read_delta("s3://bucket/delta_table/")
lf = pl.scan_delta("s3://bucket/delta_table/")

# With time travel
lf = pl.scan_delta("delta_table/", version=5)

# Write Delta
df.write_delta("output_delta/", mode="overwrite")  # or "append"
```

### 5.6 Cloud Storage

```python
import polars as pl

# S3 (via fsspec or direct)
df = pl.read_parquet("s3://bucket/data.parquet",
    storage_options={
        "aws_access_key_id": "...",
        "aws_secret_access_key": "...",
        "aws_region": "us-east-1"
    }
)

# Lazy scan from S3
lf = pl.scan_parquet("s3://bucket/data/**/*.parquet",
    storage_options={"aws_region": "us-east-1"}
)

# GCS
df = pl.read_parquet("gs://bucket/data.parquet",
    storage_options={"token": "path/to/credentials.json"}
)

# Azure
df = pl.read_parquet("abfs://container/data.parquet",
    storage_options={"account_name": "...", "account_key": "..."}
)
```

---

## PHẦN 6: ADVANCED OPERATIONS

### 6.1 Group By & Aggregation

```python
# ============================================================
# Basic group_by
# ============================================================
df.group_by("category").agg(
    pl.col("amount").sum().alias("total_revenue"),
    pl.col("amount").mean().alias("avg_revenue"),
    pl.col("amount").median().alias("median_revenue"),
    pl.col("amount").std().alias("std_revenue"),
    pl.col("amount").min().alias("min_order"),
    pl.col("amount").max().alias("max_order"),
    pl.col("amount").quantile(0.95).alias("p95_order"),
    pl.col("order_id").n_unique().alias("unique_orders"),
    pl.col("customer_id").n_unique().alias("unique_customers"),
    pl.len().alias("row_count"),
)

# ============================================================
# Multiple group keys
# ============================================================
df.group_by("region", "category").agg(
    pl.col("amount").sum().alias("total"),
    pl.col("amount").count().alias("count"),
)

# ============================================================
# Dynamic group_by (time-based)
# ============================================================
df.group_by_dynamic(
    "timestamp",
    every="1h",         # Group by 1-hour windows
    period="2h",        # Window size (tumbling if = every)
    closed="left",
).agg(
    pl.col("value").mean().alias("avg_value"),
    pl.col("value").count().alias("count"),
)

# ============================================================
# Rolling group_by
# ============================================================
df.group_by_rolling(
    "date",
    period="7d",  # 7-day rolling window
).agg(
    pl.col("revenue").sum().alias("rolling_7d_revenue"),
    pl.col("orders").sum().alias("rolling_7d_orders"),
)

# ============================================================
# Aggregating into lists
# ============================================================
df.group_by("customer_id").agg(
    pl.col("product").alias("products_purchased"),  # List of products
    pl.col("amount").sort(descending=True).alias("ordered_amounts"),
    pl.col("product").n_unique().alias("unique_products"),
    pl.col("amount").sum().alias("total_spent"),
)
```

### 6.2 Pivot & Unpivot

```python
# ============================================================
# PIVOT (long → wide)
# ============================================================
df.pivot(
    on="category",        # Column to spread
    index="region",       # Row identifier
    values="amount",      # Values to aggregate
    aggregate_function="sum"
)

# Multiple aggregates
df.pivot(
    on="quarter",
    index="product",
    values="revenue",
    aggregate_function="sum"
)

# ============================================================
# UNPIVOT / MELT (wide → long)
# ============================================================
wide_df = pl.DataFrame({
    "product": ["Widget", "Gadget"],
    "jan": [100, 200],
    "feb": [150, 250],
    "mar": [120, 300],
})

long_df = wide_df.unpivot(
    on=["jan", "feb", "mar"],
    index="product",
    variable_name="month",
    value_name="revenue"
)
```

### 6.3 Sorting & Ranking

```python
# Sort
df.sort("amount", descending=True)
df.sort(["category", "amount"], descending=[False, True])

# Rank
df.with_columns(
    pl.col("amount").rank(method="ordinal").alias("rank_ordinal"),
    pl.col("amount").rank(method="dense").alias("rank_dense"),
    pl.col("amount").rank(method="average").alias("rank_avg"),
    pl.col("amount").rank(descending=True).alias("rank_desc"),
)
```

### 6.4 Null Handling

```python
# Check nulls
df.null_count()
df.select(pl.all().is_null().sum())

# Drop nulls
df.drop_nulls()
df.drop_nulls(subset=["amount", "date"])

# Fill nulls
df.with_columns(
    pl.col("amount").fill_null(0),
    pl.col("name").fill_null("Unknown"),
    pl.col("amount").fill_null(strategy="forward"),   # Forward fill
    pl.col("amount").fill_null(strategy="backward"),   # Backward fill
    pl.col("amount").fill_null(pl.col("amount").mean()),  # Mean imputation
)

# Interpolate
df.with_columns(
    pl.col("value").interpolate().alias("interpolated")
)
```

### 6.5 SQL Interface

```python
# Polars has a built-in SQL interface!
import polars as pl

df = pl.DataFrame({
    "name": ["Alice", "Bob", "Charlie"],
    "age": [30, 25, 35],
    "salary": [80000, 65000, 95000]
})

# Register and query with SQL
result = pl.SQLContext(frame=df).execute("""
    SELECT name, salary,
           salary - AVG(salary) OVER () AS diff_from_avg
    FROM frame
    WHERE age > 25
    ORDER BY salary DESC
""").collect()

# Or simpler:
result = df.sql("""
    SELECT *, salary * 0.3 AS tax
    FROM self
    WHERE age >= 30
""")
```

---

## PHẦN 7: WINDOW FUNCTIONS

### 7.1 over() — Polars Window Functions

```python
df = pl.DataFrame({
    "dept": ["Engineering", "Engineering", "Sales", "Sales", "Sales"],
    "name": ["Alice", "Bob", "Charlie", "Diana", "Eve"],
    "salary": [90000, 85000, 70000, 75000, 72000]
})

df.with_columns(
    # Aggregate per group (window)
    pl.col("salary").mean().over("dept").alias("dept_avg"),
    pl.col("salary").sum().over("dept").alias("dept_total"),
    pl.col("salary").max().over("dept").alias("dept_max"),
    pl.col("salary").min().over("dept").alias("dept_min"),
    pl.col("salary").count().over("dept").alias("dept_count"),
    
    # Rank within group
    pl.col("salary").rank(descending=True).over("dept").alias("rank_in_dept"),
    
    # Difference from group mean
    (pl.col("salary") - pl.col("salary").mean().over("dept")).alias("diff_from_dept_avg"),
    
    # Percentage of group total
    (pl.col("salary") / pl.col("salary").sum().over("dept") * 100).round(1).alias("pct_of_dept"),
)

# ============================================================
# Multiple partition keys
# ============================================================
df.with_columns(
    pl.col("amount").sum().over("region", "category").alias("group_total"),
    pl.col("amount").rank().over("region", "category").alias("rank_in_group"),
)
```

### 7.2 Rolling & Cumulative

```python
# Rolling window
df.with_columns(
    pl.col("value").rolling_mean(window_size=7).alias("rolling_7d_avg"),
    pl.col("value").rolling_sum(window_size=7).alias("rolling_7d_sum"),
    pl.col("value").rolling_std(window_size=30).alias("rolling_30d_std"),
    pl.col("value").rolling_min(window_size=7).alias("rolling_7d_min"),
    pl.col("value").rolling_max(window_size=7).alias("rolling_7d_max"),
    pl.col("value").rolling_median(window_size=7).alias("rolling_7d_median"),
)

# Cumulative
df.with_columns(
    pl.col("amount").cum_sum().alias("running_total"),
    pl.col("amount").cum_max().alias("running_max"),
    pl.col("amount").cum_min().alias("running_min"),
    pl.col("amount").cum_count().alias("running_count"),
    pl.col("amount").cum_prod().alias("running_product"),
)

# Shift / Lag
df.with_columns(
    pl.col("value").shift(1).alias("prev_value"),
    pl.col("value").shift(-1).alias("next_value"),
    (pl.col("value") - pl.col("value").shift(1)).alias("day_change"),
    ((pl.col("value") / pl.col("value").shift(1)) - 1).alias("pct_change"),
)
```

---

## PHẦN 8: JOINS & COMBINE

### 8.1 Join Types

```mermaid
graph LR
    subgraph JoinTypes[" "]
        JoinTypes_title["Polars Join Types"]
        style JoinTypes_title fill:none,stroke:none,color:#333,font-weight:bold
        Inner["inner<br/>Both match"]
        Left["left<br/>All left + match right"]
        Outer["full<br/>All from both"]
        Cross["cross<br/>Cartesian product"]
        Semi["semi<br/>Left where match exists"]
        Anti["anti<br/>Left where NO match"]
        AsOf["asof<br/>Nearest time match"]
    end
```

```python
orders = pl.DataFrame({
    "order_id": [1, 2, 3, 4],
    "customer_id": [101, 102, 103, 104],
    "amount": [99, 199, 149, 299]
})

customers = pl.DataFrame({
    "id": [101, 102, 105],
    "name": ["Alice", "Bob", "Eve"]
})

# Inner join
orders.join(customers, left_on="customer_id", right_on="id", how="inner")

# Left join
orders.join(customers, left_on="customer_id", right_on="id", how="left")

# Full outer join
orders.join(customers, left_on="customer_id", right_on="id", how="full")

# Semi join (keep left rows that have match)
orders.join(customers, left_on="customer_id", right_on="id", how="semi")

# Anti join (keep left rows that DON'T have match)
orders.join(customers, left_on="customer_id", right_on="id", how="anti")

# Cross join
orders.join(customers, how="cross")

# ============================================================
# ASOF join (time-series)
# ============================================================
trades = pl.DataFrame({
    "timestamp": [
        "2024-01-01 10:00:01",
        "2024-01-01 10:00:05",
        "2024-01-01 10:00:10",
    ],
    "price": [100.5, 101.0, 100.8],
}).with_columns(pl.col("timestamp").str.to_datetime())

quotes = pl.DataFrame({
    "timestamp": [
        "2024-01-01 10:00:00",
        "2024-01-01 10:00:03",
        "2024-01-01 10:00:07",
    ],
    "bid": [100.0, 100.5, 100.7],
}).with_columns(pl.col("timestamp").str.to_datetime())

# ASOF: Match each trade to the most recent quote
trades.join_asof(
    quotes,
    on="timestamp",
    strategy="backward"  # Match quote <= trade time
)

# ============================================================
# Multiple join keys
# ============================================================
df1.join(df2, on=["region", "date"], how="inner")
df1.join(df2, left_on=["col_a", "col_b"], right_on=["col_x", "col_y"])
```

### 8.2 Concatenation

```python
# Vertical stack (same columns)
pl.concat([df1, df2, df3])

# Horizontal stack (same rows)
pl.concat([df1, df2], how="horizontal")

# Diagonal (union — different schemas, fills missing with null)
pl.concat([df1, df2], how="diagonal")

# Align columns by name (even if order differs)
pl.concat([df1, df2], how="align")
```

---

## PHẦN 9: TIME SERIES & TEMPORAL

### 9.1 Date Range Generation

```python
# Generate date range
dates = pl.date_range(
    start=pl.date(2024, 1, 1),
    end=pl.date(2024, 12, 31),
    interval="1d",
    eager=True
)

# DateTime range
timestamps = pl.datetime_range(
    start=pl.datetime(2024, 1, 1),
    end=pl.datetime(2024, 1, 31),
    interval="1h",
    eager=True
)

# Business days
business_days = pl.business_day_count(
    start=pl.date(2024, 1, 1),
    end=pl.date(2024, 12, 31)
)
```

### 9.2 Resampling & Upsampling

```python
# Time series DataFrame
ts = pl.DataFrame({
    "timestamp": pl.datetime_range(
        pl.datetime(2024, 1, 1), pl.datetime(2024, 1, 31),
        interval="1h", eager=True
    ),
    "value": range(721)  # hourly data
}).with_columns(pl.col("timestamp").cast(pl.Datetime))

# Downsample: hourly → daily
daily = ts.group_by_dynamic("timestamp", every="1d").agg(
    pl.col("value").mean().alias("daily_avg"),
    pl.col("value").max().alias("daily_max"),
    pl.col("value").min().alias("daily_min"),
    pl.col("value").sum().alias("daily_sum"),
    pl.col("value").count().alias("count"),
)

# Upsample: fill gaps
ts_with_gaps = ts.filter(pl.col("timestamp").dt.hour() != 12)  # Remove noon
filled = ts_with_gaps.upsample("timestamp", every="1h").with_columns(
    pl.col("value").interpolate()
)
```

### 9.3 Time Series Analysis Patterns

```python
# ============================================================
# Moving averages
# ============================================================
df.with_columns(
    pl.col("price").rolling_mean(window_size=7).alias("sma_7"),
    pl.col("price").rolling_mean(window_size=30).alias("sma_30"),
    pl.col("price").ewm_mean(span=12).alias("ema_12"),  # Exponential
)

# ============================================================
# Year-over-Year comparison
# ============================================================
df.with_columns(
    pl.col("revenue").shift(365).over("store_id").alias("last_year_revenue"),
).with_columns(
    ((pl.col("revenue") / pl.col("last_year_revenue")) - 1).alias("yoy_growth")
)

# ============================================================
# Session detection (gap > 30 min = new session)
# ============================================================
events = events.sort("user_id", "timestamp").with_columns(
    (pl.col("timestamp").diff().over("user_id") > pl.duration(minutes=30))
    .fill_null(True)
    .cum_sum()
    .over("user_id")
    .alias("session_id")
)
```

---

## PHẦN 10: PRODUCTION PATTERNS

### 10.1 ETL Pipeline with Polars

```python
"""
Production ETL pipeline using Polars
"""
import polars as pl
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


def extract(source_path: str) -> pl.LazyFrame:
    """Extract raw data with lazy evaluation."""
    return pl.scan_parquet(
        source_path,
        hive_partitioning=True,
    )


def transform(lf: pl.LazyFrame) -> pl.LazyFrame:
    """Apply business transformations."""
    return (
        lf
        # Clean
        .filter(pl.col("amount").is_not_null())
        .filter(pl.col("amount") > 0)
        .with_columns(
            pl.col("email").str.to_lowercase().str.strip_chars(),
            pl.col("name").str.strip_chars(),
        )
        # Enrich
        .with_columns(
            pl.col("amount").sum().over("customer_id").alias("lifetime_value"),
            pl.col("order_id").count().over("customer_id").alias("order_count"),
            pl.col("order_date").max().over("customer_id").alias("last_order"),
        )
        # Classify
        .with_columns(
            pl.when(pl.col("lifetime_value") > 10000)
              .then(pl.lit("platinum"))
              .when(pl.col("lifetime_value") > 5000)
              .then(pl.lit("gold"))
              .when(pl.col("lifetime_value") > 1000)
              .then(pl.lit("silver"))
              .otherwise(pl.lit("bronze"))
              .alias("tier")
        )
        # Deduplicate
        .unique(subset=["order_id"], keep="last")
        # Add metadata
        .with_columns(
            pl.lit(datetime.utcnow()).alias("processed_at"),
            pl.lit("v2.0").alias("pipeline_version"),
        )
    )


def load(lf: pl.LazyFrame, output_path: str):
    """Materialize and write output."""
    lf.sink_parquet(
        output_path,
        compression="zstd",
    )
    logger.info(f"Written to {output_path}")


def run_pipeline(source: str, destination: str):
    """Main pipeline orchestration."""
    logger.info("Starting ETL pipeline")
    
    lf = extract(source)
    transformed = transform(lf)
    load(transformed, destination)
    
    logger.info("Pipeline completed successfully")
```

### 10.2 Data Quality with Polars

```python
"""
Data quality validation framework
"""
import polars as pl
from dataclasses import dataclass


@dataclass
class QualityCheck:
    name: str
    passed: bool
    details: str


def validate(df: pl.DataFrame) -> list[QualityCheck]:
    """Run data quality checks."""
    checks = []
    
    # 1. Row count
    count = df.height
    checks.append(QualityCheck(
        "row_count", count > 0, f"Rows: {count}"
    ))
    
    # 2. No nulls in required columns
    required = ["order_id", "customer_id", "amount"]
    null_counts = df.select(
        [pl.col(c).null_count().alias(c) for c in required]
    ).row(0)
    for col_name, null_count in zip(required, null_counts):
        checks.append(QualityCheck(
            f"not_null_{col_name}",
            null_count == 0,
            f"Null count: {null_count}"
        ))
    
    # 3. Uniqueness
    dup_count = df.height - df.select(pl.col("order_id").n_unique()).item()
    checks.append(QualityCheck(
        "unique_order_id",
        dup_count == 0,
        f"Duplicates: {dup_count}"
    ))
    
    # 4. Range check
    neg_amounts = df.filter(pl.col("amount") < 0).height
    checks.append(QualityCheck(
        "positive_amounts",
        neg_amounts == 0,
        f"Negative amounts: {neg_amounts}"
    ))
    
    # 5. Schema check
    expected_schema = {
        "order_id": pl.Int64,
        "customer_id": pl.Int64,
        "amount": pl.Float64,
    }
    schema_ok = all(
        df.schema.get(k) == v for k, v in expected_schema.items()
    )
    checks.append(QualityCheck(
        "schema_valid", schema_ok, f"Schema: {df.schema}"
    ))
    
    return checks
```

### 10.3 Airflow Integration

```python
"""
Polars task in Apache Airflow
"""
from airflow.decorators import task, dag
from datetime import datetime


@dag(schedule="@daily", start_date=datetime(2024, 1, 1))
def polars_etl():
    
    @task
    def extract(ds: str) -> str:
        import polars as pl
        
        source = f"s3://raw/events/dt={ds}/*.parquet"
        staging = f"/tmp/staging/{ds}.parquet"
        
        lf = pl.scan_parquet(source)
        lf.collect().write_parquet(staging)
        
        return staging
    
    @task
    def transform(staging_path: str) -> str:
        import polars as pl
        
        df = pl.read_parquet(staging_path)
        
        result = (
            df
            .filter(pl.col("event_type").is_in(["click", "purchase"]))
            .group_by("user_id", "event_type")
            .agg(
                pl.len().alias("count"),
                pl.col("timestamp").max().alias("last_event"),
            )
        )
        
        output = staging_path.replace("staging", "processed")
        result.write_parquet(output)
        return output
    
    @task
    def load(processed_path: str):
        import polars as pl
        
        df = pl.read_parquet(processed_path)
        df.write_database(
            table_name="daily_user_events",
            connection="postgresql://user:pass@host/db",
            if_table_exists="append"
        )
    
    staging = extract()
    processed = transform(staging)
    load(processed)


polars_etl()
```

### 10.4 Streaming (Larger-than-Memory)

```python
"""
Streaming mode for files larger than available RAM
"""
import polars as pl

# Streaming scan → process → sink
# Data processed in chunks, never fully loaded
(
    pl.scan_parquet("huge_dataset/**/*.parquet")
    .filter(pl.col("status") == "active")
    .select("user_id", "event_type", "timestamp", "value")
    .group_by("user_id", "event_type")
    .agg(
        pl.col("value").sum().alias("total_value"),
        pl.col("timestamp").max().alias("last_seen"),
        pl.len().alias("event_count"),
    )
    .sort("total_value", descending=True)
    .sink_parquet("output/user_events.parquet")
)

# Streaming CSV → Parquet conversion
(
    pl.scan_csv("huge_file.csv")
    .sink_parquet("huge_file.parquet", compression="zstd")
)
```

### 10.5 Testing Patterns

```python
"""
Testing Polars transformations with pytest
"""
import polars as pl
from polars.testing import assert_frame_equal


def test_customer_tier_classification():
    """Test tier assignment logic."""
    input_df = pl.DataFrame({
        "customer_id": [1, 2, 3],
        "lifetime_value": [15000, 3000, 500],
    })
    
    result = input_df.with_columns(
        pl.when(pl.col("lifetime_value") > 10000)
          .then(pl.lit("platinum"))
          .when(pl.col("lifetime_value") > 1000)
          .then(pl.lit("silver"))
          .otherwise(pl.lit("bronze"))
          .alias("tier")
    )
    
    expected = pl.DataFrame({
        "customer_id": [1, 2, 3],
        "lifetime_value": [15000, 3000, 500],
        "tier": ["platinum", "silver", "bronze"],
    })
    
    assert_frame_equal(result, expected)


def test_deduplication():
    """Test duplicate removal."""
    input_df = pl.DataFrame({
        "order_id": [1, 1, 2, 3],
        "amount": [100, 100, 200, 300],
        "updated_at": [
            "2024-01-01", "2024-01-02",
            "2024-01-01", "2024-01-01"
        ],
    }).with_columns(pl.col("updated_at").str.to_date())
    
    result = input_df.sort("updated_at").unique(
        subset=["order_id"], keep="last"
    )
    
    assert result.height == 3
    # Check that duplicate kept the latest
    order_1 = result.filter(pl.col("order_id") == 1)
    assert order_1["updated_at"].item() == pl.date(2024, 1, 2)


def test_lazy_optimization():
    """Verify lazy plan produces correct results."""
    lf = pl.LazyFrame({
        "a": [1, 2, 3, 4, 5],
        "b": [10, 20, 30, 40, 50],
    })
    
    result = (
        lf.filter(pl.col("a") > 2)
          .select("a", (pl.col("b") * 2).alias("b_doubled"))
          .collect()
    )
    
    assert result.height == 3
    assert result["b_doubled"].to_list() == [60, 80, 100]
```

---

## PHẦN 11: POLARS VS ALTERNATIVES

### 11.1 Polars vs Pandas

| Feature | Polars | Pandas |
|---------|--------|--------|
| **Language** | Rust (Python bindings) | C/Cython (Python) |
| **Memory** | Apache Arrow | NumPy arrays |
| **Multithreading** | ✅ Native | ❌ GIL limited |
| **Lazy eval** | ✅ LazyFrame | ❌ Always eager |
| **Null handling** | Arrow null bitmap (efficient) | NaN/None (inconsistent) |
| **String type** | Arrow StringArray (fast) | Python objects (slow) |
| **Index** | ❌ No index (by design) | ✅ Row index |
| **API style** | Expression-based | Method + bracket |
| **Ecosystem** | Growing | Massive |
| **1 GB CSV read** | ~1 second | ~10 seconds |
| **GroupBy 10M rows** | ~0.3 seconds | ~3 seconds |

### 11.2 Polars vs DuckDB

| Feature | Polars | DuckDB |
|---------|--------|--------|
| **API** | DataFrame | SQL |
| **Best for** | Transformations | Aggregations |
| **File queries** | scan_parquet | SELECT FROM file |
| **Database attach** | ConnectorX | Native (PG, MySQL, SQLite) |
| **Nested types** | ✅ struct, list | ✅ struct, list |
| **Window functions** | .over() | OVER() clause |
| **Streaming** | sink_parquet | Automatic spill |
| **WASM** | ❌ | ✅ |
| **Zero-copy interop** | ✅ Arrow | ✅ Arrow |

**Recommendation:** Use BOTH together. DuckDB for SQL queries, Polars for DataFrame transformations. They share Arrow memory with zero-copy.

### 11.3 Migration from Pandas

```python
# ============================================================
# Pandas → Polars cheat sheet
# ============================================================

# Read
# pd: pd.read_csv("f.csv")
# pl: pl.read_csv("f.csv") or pl.scan_csv("f.csv")

# Select columns
# pd: df[["a", "b"]]
# pl: df.select("a", "b")

# Filter rows
# pd: df[df["a"] > 10]
# pl: df.filter(pl.col("a") > 10)

# New column
# pd: df["c"] = df["a"] + df["b"]
# pl: df = df.with_columns((pl.col("a") + pl.col("b")).alias("c"))

# GroupBy
# pd: df.groupby("a")["b"].sum()
# pl: df.group_by("a").agg(pl.col("b").sum())

# Apply (avoid in both!)
# pd: df["a"].apply(func)
# pl: df.with_columns(pl.col("a").map_elements(func))
# Better: Use native expressions instead of apply/map!

# Sort
# pd: df.sort_values("a", ascending=False)
# pl: df.sort("a", descending=True)

# Rename
# pd: df.rename(columns={"old": "new"})
# pl: df.rename({"old": "new"})

# Drop duplicates
# pd: df.drop_duplicates(subset=["a"])
# pl: df.unique(subset=["a"])

# Fillna
# pd: df["a"].fillna(0)
# pl: df.with_columns(pl.col("a").fill_null(0))

# Merge
# pd: pd.merge(df1, df2, on="key")
# pl: df1.join(df2, on="key")

# Convert between
df_polars = pl.from_pandas(df_pandas)
df_pandas = df_polars.to_pandas()
```

---

## PHẦN 12: HANDS-ON LABS

### Lab 1: Basic Data Analysis

```python
"""
Lab: Analyze NYC Taxi data with Polars
"""
import polars as pl

# Read sample data (download from NYC TLC)
lf = pl.scan_parquet("yellow_tripdata_2024-01.parquet")

# Quick overview
print(lf.collect_schema())

# Analysis: Average fare by hour and day
result = (
    lf
    .with_columns(
        pl.col("tpep_pickup_datetime").dt.hour().alias("hour"),
        pl.col("tpep_pickup_datetime").dt.weekday().alias("weekday"),
    )
    .group_by("hour", "weekday")
    .agg(
        pl.col("fare_amount").mean().round(2).alias("avg_fare"),
        pl.col("trip_distance").mean().round(2).alias("avg_distance"),
        pl.len().alias("trip_count"),
    )
    .sort("hour", "weekday")
    .collect()
)

print(result)
```

### Lab 2: ETL with Streaming

```python
"""
Lab: Build a streaming ETL pipeline
"""
import polars as pl

# Process multiple large files with streaming
(
    pl.scan_parquet("raw_events/**/*.parquet")
    
    # Clean
    .filter(pl.col("user_id").is_not_null())
    .filter(pl.col("event_type") != "heartbeat")
    
    # Transform
    .with_columns(
        pl.col("timestamp").str.to_datetime(),
        pl.col("properties").str.json_decode(),
    )
    .with_columns(
        pl.col("timestamp").dt.date().alias("event_date"),
        pl.col("timestamp").dt.hour().alias("event_hour"),
    )
    
    # Aggregate
    .group_by("user_id", "event_date", "event_type")
    .agg(
        pl.len().alias("count"),
        pl.col("timestamp").min().alias("first_event"),
        pl.col("timestamp").max().alias("last_event"),
    )
    
    # Write (streaming — never loads full dataset)
    .sink_parquet(
        "processed/daily_events.parquet",
        compression="zstd"
    )
)

print("Streaming ETL complete!")
```

### Lab 3: Feature Engineering for ML

```python
"""
Lab: Feature engineering pipeline with Polars
"""
import polars as pl

def engineer_features(orders: pl.LazyFrame, users: pl.LazyFrame) -> pl.DataFrame:
    """Build ML features from order and user data."""
    
    # User-level features from orders
    user_features = (
        orders
        .group_by("user_id")
        .agg(
            # Recency
            (pl.lit(pl.date(2024, 12, 31)) - pl.col("order_date").max())
                .dt.total_days().alias("days_since_last_order"),
            
            # Frequency
            pl.len().alias("total_orders"),
            pl.col("order_id").n_unique().alias("unique_orders"),
            
            # Monetary
            pl.col("amount").sum().alias("total_spent"),
            pl.col("amount").mean().alias("avg_order_value"),
            pl.col("amount").std().alias("std_order_value"),
            pl.col("amount").median().alias("median_order_value"),
            pl.col("amount").max().alias("max_order_value"),
            
            # Diversity
            pl.col("category").n_unique().alias("categories_purchased"),
            pl.col("product_id").n_unique().alias("unique_products"),
            
            # Temporal
            pl.col("order_date").min().alias("first_order_date"),
            (pl.col("order_date").max() - pl.col("order_date").min())
                .dt.total_days().alias("customer_tenure_days"),
            
            # Order patterns
            pl.col("order_date").diff().dt.total_days().mean()
                .alias("avg_days_between_orders"),
        )
    )
    
    # Join with user demographics
    features = (
        user_features
        .join(users, left_on="user_id", right_on="id", how="left")
        .with_columns(
            # Derived features
            (pl.col("total_spent") / pl.col("total_orders")).alias("spend_per_order"),
            (pl.col("total_orders") / (pl.col("customer_tenure_days") + 1) * 30)
                .alias("orders_per_month"),
        )
        .collect()
    )
    
    return features

# Usage
orders = pl.scan_parquet("orders.parquet")
users = pl.scan_parquet("users.parquet")
features = engineer_features(orders, users)
print(features.describe())
```

---

## 📦 Verified Resources

| Resource | Link | Note |
|----------|------|------|
| Polars GitHub | [pola-rs/polars](https://github.com/pola-rs/polars) | 32k⭐ Main repo |
| Polars Docs | [docs.pola.rs](https://docs.pola.rs/) | Official documentation |
| Polars PyPI | [PyPI: polars](https://pypi.org/project/polars/) | Python package |
| Polars Book | [pola.rs/user-guide](https://docs.pola.rs/user-guide/) | User guide |
| Polars Blog | [pola.rs/posts](https://pola.rs/posts/) | Release notes |
| Polars Discord | [Discord](https://discord.gg/4UfP5cfBE7) | Community |
| Awesome Polars | [ddotta/awesome-polars](https://github.com/ddotta/awesome-polars) | Community resources |
| Polars Cookbook | [escobar-west/polars-cookbook](https://github.com/escobar-west/polars-cookbook) | Code examples |

---

## 🔗 Liên Kết Nội Bộ

- [[13_DuckDB_Complete_Guide|DuckDB]] — SQL complement to Polars
- [[06_Apache_Spark_Complete_Guide|Apache Spark]] — Distributed alternative
- [[../fundamentals/13_Python_Data_Engineering|Python for DE]] — Python ecosystem
- [[../fundamentals/06_Data_Formats_Storage|Data Formats]] — Parquet, Arrow, Avro
- [[../fundamentals/07_Batch_vs_Streaming|Batch vs Streaming]] — Processing patterns

---

*Last Updated: February 2026*
*Coverage: Architecture, Expressions, I/O, Window Functions, Joins, Time Series, Production, Testing*
