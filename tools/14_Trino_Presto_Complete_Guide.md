# 🔷 Trino & Presto - Complete Guide

> Distributed SQL Query Engine — Federated Analytics at Scale

---

## 📋 Mục Lục

1. [Giới Thiệu & History](#phần-1-giới-thiệu--history)
2. [Kiến Trúc Core](#phần-2-kiến-trúc-core)
3. [Query Execution Deep Dive](#phần-3-query-execution-deep-dive)
4. [Connectors & Catalogs](#phần-4-connectors--catalogs)
5. [SQL Features](#phần-5-sql-features)
6. [Performance Tuning](#phần-6-performance-tuning)
7. [Deployment](#phần-7-deployment)
8. [Security](#phần-8-security)
9. [Monitoring & Operations](#phần-9-monitoring--operations)
10. [Real-World Use Cases](#phần-10-real-world-use-cases)
11. [Trino vs Alternatives](#phần-11-trino-vs-alternatives)
12. [Hands-on Labs](#phần-12-hands-on-labs)

---

## PHẦN 1: GIỚI THIỆU & HISTORY

### 1.1 Trino là gì?

Trino (formerly PrestoSQL) là **distributed SQL query engine** thiết kế để query data trực tiếp tại nguồn — không cần ETL dữ liệu vào một nơi trước. Trino xử lý queries trên petabytes dữ liệu với latency từ milliseconds đến minutes.

**Core Philosophy:**
- **Query data where it lives** — No data movement needed
- **Federated queries** — JOIN across MySQL, S3, Kafka, etc. in 1 query
- **ANSI SQL** — Standard SQL, không cần học ngôn ngữ mới
- **Interactive performance** — Seconds, not hours
- **Separation of compute and storage** — Scale independently

### 1.2 History: Presto → Trino

```mermaid
timeline
    title Presto/Trino Timeline
    2012 : Facebook creates Presto
         : Internal query engine
    2013 : Open sourced as prestodb
         : Community begins growing
    2018 : Presto Foundation at Linux Foundation
         : Enterprise adoption grows
    2019 : Founders leave Facebook
         : Fork PrestoDB vs PrestoSQL
    2020 : PrestoSQL rebrands to Trino
         : Trademark dispute resolved
    2022 : Trino Gateway for load balancing
         : Fault-tolerant execution
    2024 : Trino 450+ release
         : Polymorphic table functions
    2025 : Trino v460+
         : Improved Iceberg and Delta support
```

```mermaid
graph TB
    subgraph Origin[" "]
        Origin_title["📜 2012: Presto at Facebook"]
        style Origin_title fill:none,stroke:none,color:#333,font-weight:bold
        FB[Facebook Presto<br/>Internal Tool]
    end

    subgraph Fork[" "]
        Fork_title["⚔️ 2019: The Fork"]
        style Fork_title fill:none,stroke:none,color:#333,font-weight:bold
        PrestoDB[PrestoDB<br/>Meta / Linux Foundation<br/>prestodb.io]
        PrestoSQL[PrestoSQL<br/>Original Founders<br/>Martin, Dain, David]
    end

    subgraph Modern[" "]
        Modern_title["🚀 2020+: Modern Era"]
        style Modern_title fill:none,stroke:none,color:#333,font-weight:bold
        Presto[Presto<br/>Meta-backed<br/>AWS Athena v2]
        Trino[Trino<br/>Community-driven<br/>Starburst Enterprise]
    end

    FB --> PrestoDB & PrestoSQL
    PrestoDB --> Presto
    PrestoSQL -->|"Rebrand 2020"| Trino

    style Trino fill:#4285f4,color:#fff
    style Presto fill:#f4b400,color:#000
```

### 1.3 Trino vs PrestoDB — Which to Use?

| Feature | Trino | PrestoDB |
|---------|-------|----------|
| **Governance** | Community-driven | Meta + Linux Foundation |
| **Commercial** | Starburst | Ahana (now IBM) |
| **Releases** | Frequent (weekly) | Less frequent |
| **Connectors** | 40+ | 30+ |
| **Fault Tolerance** | ✅ Built-in | ⚠️ Limited |
| **Dynamic Filtering** | ✅ Advanced | ✅ Basic |
| **Table Functions** | ✅ Polymorphic | ❌ |
| **Iceberg Support** | ✅ Deep | ✅ Good |
| **AWS Integration** | Via Starburst/self-host | Athena (managed) |
| **Community Size** | Larger (GitHub ⭐) | Smaller |

**Recommendation:** Dùng **Trino** cho hầu hết use cases. Dùng **PrestoDB** (via AWS Athena) nếu đã deep trong AWS ecosystem và muốn serverless.

### 1.4 Who Uses Trino?

| Company | Scale | Use Case |
|---------|-------|----------|
| **Netflix** | 10+ PB queried/day | Ad-hoc analytics on S3 |
| **LinkedIn** | 30+ PB data lake | Interactive BI queries |
| **Lyft** | Thousands of users | Data discovery + analytics |
| **Airbnb** | Multi-PB data lake | Federated queries |
| **Shopify** | E-commerce analytics | Cross-source queries |
| **Comcast** | Media analytics | Real-time + batch queries |

---

## PHẦN 2: KIẾN TRÚC CORE

### 2.1 Cluster Architecture

```mermaid
graph TB
    subgraph Clients[" "]
        Clients_title["👥 Clients"]
        style Clients_title fill:none,stroke:none,color:#333,font-weight:bold
        CLI[Trino CLI]
        JDBC[JDBC/ODBC]
        BI[BI Tools<br/>Superset/Metabase]
        SDK[Python/Go SDK]
    end

    subgraph Coordinator[" "]
        Coordinator_title["🧠 Coordinator Node"]
        style Coordinator_title fill:none,stroke:none,color:#333,font-weight:bold
        Parser[SQL Parser]
        Analyzer[Semantic Analyzer]
        Planner[Query Planner<br/>Cost-Based Optimizer]
        Scheduler[Scheduler<br/>Stage Assignment]
        Meta[Metadata Manager]
    end

    subgraph Workers[" "]
        Workers_title["⚙️ Worker Nodes"]
        style Workers_title fill:none,stroke:none,color:#333,font-weight:bold
        W1[Worker 1]
        W2[Worker 2]
        W3[Worker 3]
        WN[Worker N]
    end

    subgraph Connectors[" "]
        Connectors_title["🔌 Connector Layer"]
        style Connectors_title fill:none,stroke:none,color:#333,font-weight:bold
        C1[Hive<br/>HDFS/S3]
        C2[Iceberg<br/>Data Lake]
        C3[MySQL<br/>OLTP]
        C4[Kafka<br/>Streaming]
        C5[PostgreSQL<br/>OLTP]
    end

    Clients --> Coordinator
    Coordinator --> Workers
    W1 & W2 & W3 & WN --> Connectors

    style Coordinator fill:#e8f5e9
    style Workers fill:#e3f2fd
```

### 2.2 Component Deep Dive

**Coordinator Node:**
- Nhận SQL từ client, parse và analyze
- Cost-based optimizer tạo execution plan
- Phân chia query thành stages, giao cho workers
- Chỉ có **1 coordinator** per cluster (SPOF — cần HA setup)
- KHÔNG xử lý data (trừ final aggregation)

**Worker Nodes:**
- Thực thi tasks được coordinator giao
- Fetch data từ connectors (parallel)
- Xử lý operators: filter, project, join, aggregate
- Exchange data giữa các workers (shuffle)
- Scale horizontally (thêm workers = nhanh hơn)

**Discovery Service:**
- Workers register với coordinator via REST API
- Heartbeat mỗi vài seconds
- Coordinator biết cluster health + capacity

**Connectors (SPI):**
- Plugin architecture — mỗi data source 1 connector
- Implement metadata API (tables, columns, types)
- Implement data read API (splits, pages)
- Implement pushdown API (predicates, projections)
- Có thể viết custom connector

### 2.3 Memory Architecture

```mermaid
graph TB
    subgraph JVM[" "]
        JVM_title["JVM Heap (16-64 GB typical)"]
        style JVM_title fill:none,stroke:none,color:#333,font-weight:bold
        subgraph UserMem[" "]
            UserMem_title["User Memory Pool"]
            style UserMem_title fill:none,stroke:none,color:#333,font-weight:bold
            Hash[Hash Tables<br/>JOIN buffers]
            Agg[Aggregation States]
            Sort[Sort Buffers]
        end
        subgraph SystemMem[" "]
            SystemMem_title["System Memory Pool"]
            style SystemMem_title fill:none,stroke:none,color:#333,font-weight:bold
            IO[I/O Buffers]
            Exchange[Exchange Buffers<br/>Worker-to-Worker]
            Meta2[Metadata Cache]
        end
        Reserved[Reserved Pool<br/>For largest query<br/>Prevents deadlock]
    end

    subgraph Spill[" "]
        Spill_title["💾 Spill to Disk"]
        style Spill_title fill:none,stroke:none,color:#333,font-weight:bold
        SpillDir[/mnt/ssd/trino-spill/]
    end

    UserMem -->|"Out of memory"| Spill
```

```properties
# Memory configuration

# === jvm.config ===
-Xmx16G                              # JVM heap (70-80% of machine RAM)
-XX:+UseG1GC                         # GC algorithm
-XX:G1HeapRegionSize=32M
-XX:+ExplicitGCInvokesConcurrent
-XX:+ExitOnOutOfMemoryError
-XX:-UseBiasedLocking
-XX:ReservedCodeCacheSize=512M

# === config.properties ===
query.max-memory=50GB                 # Total across all nodes
query.max-memory-per-node=8GB        # Per worker node
query.max-total-memory-per-node=10GB  # Including system memory
memory.heap-headroom-per-node=2GB     # Reserved for JVM internals
query.low-memory-killer.policy=total-reservation-on-blocked-nodes
```

### 2.4 Data Flow — Pipeline Model

```mermaid
sequenceDiagram
    participant C as Client
    participant Co as Coordinator
    participant W1 as Worker 1
    participant W2 as Worker 2
    participant DS as Data Source

    C->>Co: SQL Query
    Co->>Co: Parse → Analyze → Plan → Optimize
    Co->>Co: Create Stages (DAG)
    
    par Stage 0 — Source Stage
        Co->>W1: Execute Split 1
        Co->>W2: Execute Split 2
        W1->>DS: Read data pages (parallel)
        W2->>DS: Read data pages (parallel)
    end

    Note over W1,W2: Pipeline: data streams through operators

    par Stage 1 — Shuffle Stage
        W1->>W2: Exchange data (hash partition)
        W2->>W1: Exchange data (hash partition)
    end

    par Stage 2 — Aggregate Stage
        W1->>Co: Partial results
        W2->>Co: Partial results
    end

    Co->>Co: Final aggregation
    Co->>C: Stream results (page by page)
```

**Key Insight — Pipeline vs Batch:**
- **Trino (pipeline):** Data flows through operators continuously, results start arriving immediately
- **Spark (batch):** Each stage completes fully before next stage starts
- Trino ưu điểm: Low latency cho interactive queries
- Trino nhược điểm: Nếu 1 stage fail, phải restart toàn bộ query (trừ khi bật fault tolerance)

### 2.5 Splits — Unit of Parallelism

```mermaid
graph LR
    subgraph Table[" "]
        Table_title["📊 Table: events"]
        style Table_title fill:none,stroke:none,color:#333,font-weight:bold
        P1[Partition<br/>date=2024-01-01]
        P2[Partition<br/>date=2024-01-02]
        P3[Partition<br/>date=2024-01-03]
    end

    subgraph Splits[" "]
        Splits_title["📦 Splits (parallel units)"]
        style Splits_title fill:none,stroke:none,color:#333,font-weight:bold
        S1[Split 1<br/>file1.parquet]
        S2[Split 2<br/>file2.parquet]
        S3[Split 3<br/>file3.parquet]
        S4[Split 4<br/>file4.parquet]
        S5[Split 5<br/>file5.parquet]
    end

    subgraph Workers[" "]
        Workers_title["⚙️ Workers"]
        style Workers_title fill:none,stroke:none,color:#333,font-weight:bold
        W1[Worker 1<br/>S1 + S4]
        W2[Worker 2<br/>S2 + S5]
        W3[Worker 3<br/>S3]
    end

    P1 --> S1 & S2
    P2 --> S3
    P3 --> S4 & S5
    Splits --> Workers
```

---

## PHẦN 3: QUERY EXECUTION DEEP DIVE

### 3.1 Query Lifecycle

```mermaid
graph LR
    SQL[SQL Text] --> Parse[Parsing<br/>AST]
    Parse --> Analyze[Analysis<br/>Type Check<br/>Resolve Names]
    Analyze --> Plan[Logical Plan<br/>Relational Algebra]
    Plan --> Optimize[Optimizer<br/>Cost-Based +<br/>Rule-Based]
    Optimize --> Fragment[Fragmentation<br/>Split into Stages]
    Fragment --> Schedule[Scheduling<br/>Assign to Workers]
    Schedule --> Execute[Execution<br/>Pipelined<br/>Streaming]
    Execute --> Result[Results<br/>Stream to Client]

    style Optimize fill:#fff3e0
    style Execute fill:#e8f5e9
```

### 3.2 Cost-Based Optimizer (CBO)

Trino's CBO sử dụng table/column statistics để quyết định optimal plan:

```sql
-- Collect statistics for CBO (Hive/Iceberg)
ANALYZE hive.db.events;
ANALYZE iceberg.db.orders;

-- CBO decisions when statistics available:
-- 1. Join ordering (which table to probe/build)
-- 2. Join type (broadcast vs hash-partitioned)
-- 3. Aggregation strategy (partial, final, single)
-- 4. Filter placement (push down where possible)

-- ============================================================
-- CBO Session Settings
-- ============================================================
SET SESSION join_reordering_strategy = 'AUTOMATIC';
SET SESSION join_distribution_type = 'AUTOMATIC';
SET SESSION enable_stats_calculator = true;

-- ============================================================
-- Example: CBO auto-selects broadcast join for small table
-- ============================================================
-- customers: 10K rows (small → broadcast to all workers)
-- orders: 100M rows (large → stays partitioned)
SELECT o.*, c.name
FROM orders o         -- 100M rows → scan stays distributed
JOIN customers c      -- 10K rows → broadcast to every worker!
ON o.customer_id = c.id;

-- ============================================================
-- EXPLAIN shows optimizer decisions
-- ============================================================
EXPLAIN (TYPE DISTRIBUTED)
SELECT o.*, c.name
FROM orders o JOIN customers c ON o.customer_id = c.id;

-- Output shows:
-- Fragment 0: Output → ...
-- Fragment 1: ScanFilterProject (orders)
--   InnerJoin[("customer_id" = "id")]
--     Distribution: REPLICATED  ← means broadcast join!
```

### 3.3 Rule-Based Optimizations

```sql
-- Trino applies many rule-based optimizations automatically:

-- 1. Predicate Pushdown
--    WHERE clause pushed into connector/scan
SELECT * FROM events WHERE event_date = CURRENT_DATE;

-- 2. Projection Pushdown
--    Only needed columns read from storage
SELECT user_id, event_type FROM events;

-- 3. Limit Pushdown
--    LIMIT pushed to source when possible
SELECT * FROM mysql.app.users LIMIT 10;

-- 4. TopN Pushdown
--    ORDER BY + LIMIT pushed to source
SELECT * FROM postgresql.app.users
ORDER BY created_at DESC LIMIT 100;

-- 5. Aggregation Pushdown
--    COUNT/SUM pushed to JDBC sources
SELECT count(*) FROM postgresql.analytics.events;

-- 6. Join Elimination
--    Unnecessary joins removed
SELECT o.* FROM orders o
JOIN customers c ON o.customer_id = c.id;
-- If c.id is unique and no columns from c are used → join eliminated

-- 7. Subquery Decorrelation
--    Correlated subqueries → joins
SELECT * FROM orders WHERE customer_id IN (
    SELECT id FROM customers WHERE tier = 'premium'
);
-- Rewritten to inner join
```

### 3.4 Pushdown Deep Dive

```sql
-- ============================================================
-- Predicate pushdown (filter at source)
-- ============================================================
SELECT * FROM mysql.app.users
WHERE created_at > DATE '2024-01-01';
-- MySQL executes: SELECT * FROM users WHERE created_at > '2024-01-01'

-- ============================================================
-- Projection pushdown (select only needed columns)
-- ============================================================
SELECT name, email FROM hive.datalake.users;
-- Hive connector reads ONLY name + email columns from Parquet
-- Columnar format advantage: skip entire columns

-- ============================================================
-- Aggregation pushdown (aggregate at source)
-- ============================================================
SELECT count(*) FROM postgresql.analytics.events;
-- PostgreSQL executes: SELECT count(*) FROM events
-- Only 1 number transferred instead of all rows

-- ============================================================
-- Limit pushdown
-- ============================================================
SELECT * FROM mysql.app.users LIMIT 10;
-- MySQL: SELECT * FROM users LIMIT 10

-- ============================================================
-- TopN pushdown
-- ============================================================
SELECT * FROM postgresql.app.users
ORDER BY created_at DESC LIMIT 100;
-- PostgreSQL handles ORDER BY + LIMIT

-- ============================================================
-- Check pushdown with EXPLAIN
-- ============================================================
EXPLAIN SELECT * FROM mysql.app.users WHERE status = 'active';
-- Look for: "constraint on status: supported, filterPredicate"
-- If "not supported" → filter happens in Trino (slower)
```

### 3.5 Join Strategies

```mermaid
graph TB
    subgraph Broadcast[" "]
        Broadcast_title["📡 Broadcast Join"]
        style Broadcast_title fill:none,stroke:none,color:#333,font-weight:bold
        direction TB
        BDesc["Small table copied to ALL workers<br/>Good when one side < 100MB"]
        BSmall[Small Table<br/>customers: 10K rows] -->|"Full copy"| BW1[Worker 1]
        BSmall -->|"Full copy"| BW2[Worker 2]
        BSmall -->|"Full copy"| BW3[Worker 3]
    end

    subgraph Partitioned[" "]
        Partitioned_title["🔀 Partitioned / Hash Join"]
        style Partitioned_title fill:none,stroke:none,color:#333,font-weight:bold
        direction TB
        PDesc["Both tables hash-partitioned by join key<br/>Same key → same worker"]
        PLeft[Table A<br/>orders: 100M] -->|"Hash by user_id"| PW1[Worker 1: hash=0]
        PRight[Table B<br/>events: 500M] -->|"Hash by user_id"| PW1
        PLeft -->|"Hash by user_id"| PW2[Worker 2: hash=1]
        PRight -->|"Hash by user_id"| PW2
    end
```

```sql
-- ============================================================
-- Force broadcast join (khi biết 1 table nhỏ)
-- ============================================================
SELECT /*+ BROADCAST(customers) */
    o.order_id, c.name
FROM orders o
JOIN customers c ON o.customer_id = c.id;

-- ============================================================
-- Force partitioned/hash join (cả 2 table lớn)
-- ============================================================
SELECT /*+ REDISTRIBUTE(orders), REDISTRIBUTE(events) */
    o.*, e.*
FROM orders o
JOIN events e ON o.user_id = e.user_id;

-- ============================================================
-- Session-level join control
-- ============================================================
SET SESSION join_distribution_type = 'BROADCAST';
-- or
SET SESSION join_distribution_type = 'PARTITIONED';

-- Size threshold for auto broadcast
SET SESSION join_max_broadcast_table_size = '100MB';
```

### 3.6 Fault-Tolerant Execution (FTE)

```mermaid
graph TD
    subgraph Standard[" "]
        Standard_title["Standard Execution"]
        style Standard_title fill:none,stroke:none,color:#333,font-weight:bold
        S1[Query Start] --> S2[Stage 0 on Workers]
        S2 --> S3[Stage 1 on Workers]
        S3 --> S4[Result]
        S2 -.->|"Worker fails"| SFail[❌ Entire Query Fails]
    end

    subgraph FaultTolerant[" "]
        FaultTolerant_title["Fault-Tolerant Execution"]
        style FaultTolerant_title fill:none,stroke:none,color:#333,font-weight:bold
        F1[Query Start] --> F2[Stage 0 with Checkpoints]
        F2 -->|"Save intermediate"| Spool[(Exchange<br/>Spooling)]
        Spool --> F3[Stage 1 on Workers]
        F3 --> F4[Result]
        F2 -.->|"Worker fails"| FRetry[🔄 Retry failed task<br/>on another worker]
        FRetry --> F3
    end

    style SFail fill:#f44336,color:#fff
    style FRetry fill:#4caf50,color:#fff
```

```properties
# Enable fault tolerance (Trino 400+)
retry-policy=TASK                          # TASK or QUERY
task-retry-attempts=4                      # Max retries per task
retry-initial-delay=10s
retry-max-delay=1m
retry-delay-scale-factor=2.0

# Exchange spooling (intermediate data checkpointing)
exchange.deduplication-buffer-size=32MB

# Spooling to filesystem
exchange-manager.name=filesystem
exchange.base-directories=s3://trino-exchange/spooling/

# When to use FTE:
# ✅ Long-running ETL queries (hours)
# ✅ Large clusters with frequent node failures
# ✅ Batch workloads (dbt models)
# ❌ Interactive/low-latency queries (overhead)
# ❌ Small clusters (< 5 workers)
```

---

## PHẦN 4: CONNECTORS & CATALOGS

### 4.1 Connector Architecture (SPI)

```mermaid
graph TB
    subgraph SPI[" "]
        SPI_title["Trino SPI — Service Provider Interface"]
        style SPI_title fill:none,stroke:none,color:#333,font-weight:bold
        ConnectorFactory[ConnectorFactory<br/>Creates connector instances]
        ConnectorMetadata[Metadata API<br/>schemas, tables, columns, stats]
        ConnectorSplitManager[Split Manager<br/>How to parallelize reads]
        ConnectorPageSource[Page Source<br/>Read data pages]
        ConnectorPageSink[Page Sink<br/>Write data: INSERT/CTAS]
        ConnectorIndex[Index API<br/>Optional: index lookups]
    end

    subgraph Catalogs[" "]
        Catalogs_title["📁 Registered Catalogs"]
        style Catalogs_title fill:none,stroke:none,color:#333,font-weight:bold
        Cat1["hive<br/>(etc/catalog/hive.properties)"]
        Cat2["iceberg<br/>(etc/catalog/iceberg.properties)"]
        Cat3["mysql<br/>(etc/catalog/mysql.properties)"]
        Cat4["kafka<br/>(etc/catalog/kafka.properties)"]
    end

    Catalogs --> SPI
    SPI --> DataSources[(Data Sources)]
```

**Naming Convention:** `catalog.schema.table`
```sql
-- Examples:
SELECT * FROM hive.raw.events;          -- catalog=hive, schema=raw, table=events
SELECT * FROM iceberg.warehouse.orders;  -- catalog=iceberg
SELECT * FROM mysql.app.users;           -- catalog=mysql
```

### 4.2 Data Lake Connectors

```properties
# ================================================================
# Hive Connector (HDFS, S3, GCS, Azure ADLS)
# ================================================================
# etc/catalog/hive.properties
connector.name=hive
hive.metastore.uri=thrift://metastore:9083

# S3 configuration
hive.s3.aws-access-key=AKIAIOSFODNN7EXAMPLE
hive.s3.aws-secret-key=wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY
hive.s3.endpoint=s3.amazonaws.com
hive.s3.path-style-access=false
hive.s3.ssl.enabled=true

# GCS configuration
# hive.gcs.json-key-file-path=/etc/trino/gcs-key.json

# Azure ADLS configuration
# hive.azure.abfs.access-key=<key>

# Performance tuning
hive.max-split-size=64MB
hive.max-initial-splits=200
hive.max-splits-per-second=1000
hive.parquet.use-column-names=true
hive.orc.use-column-names=true
hive.allow-drop-table=true
hive.allow-rename-table=true

# Caching (optional — accelerate repeated queries)
hive.cache.enabled=true
hive.cache.location=/mnt/ssd/trino-cache
hive.cache.ttl=24h
hive.cache.disk-usage-percentage=80


# ================================================================
# Iceberg Connector (RECOMMENDED for new projects)
# ================================================================
# etc/catalog/iceberg.properties
connector.name=iceberg
iceberg.catalog.type=hive_metastore
hive.metastore.uri=thrift://metastore:9083

# Or REST catalog (Nessie, Polaris, Unity)
# iceberg.catalog.type=rest
# iceberg.rest-catalog.uri=http://nessie:19120/api/v2

# Or JDBC catalog (PostgreSQL/MySQL backend)
# iceberg.catalog.type=jdbc
# iceberg.jdbc-catalog.driver-class=org.postgresql.Driver
# iceberg.jdbc-catalog.connection-url=jdbc:postgresql://host:5432/iceberg_catalog
# iceberg.jdbc-catalog.connection-user=iceberg
# iceberg.jdbc-catalog.connection-password=password

# Iceberg-specific settings
iceberg.file-format=PARQUET
iceberg.compression-codec=ZSTD
iceberg.target-max-file-size=512MB

# Iceberg MERGE/DELETE/UPDATE support
iceberg.delete-schema-locations-fallback=true


# ================================================================
# Delta Lake Connector
# ================================================================
# etc/catalog/delta.properties
connector.name=delta_lake
hive.metastore.uri=thrift://metastore:9083
delta.enable-non-concurrent-writes=true
delta.register-table-procedure.enabled=true

# S3 config
hive.s3.aws-access-key=...
hive.s3.aws-secret-key=...


# ================================================================
# Hudi Connector
# ================================================================
# etc/catalog/hudi.properties
connector.name=hudi
hive.metastore.uri=thrift://metastore:9083
```

### 4.3 Database Connectors (JDBC)

```properties
# ================================================================
# PostgreSQL
# ================================================================
connector.name=postgresql
connection-url=jdbc:postgresql://host:5432/database
connection-user=trino_reader
connection-password=${ENV:PG_PASSWORD}

# Performance settings
postgresql.array-mapping=AS_ARRAY
postgresql.include-system-tables=false

# Connection pool
connection-pool.max-total=50
connection-pool.max-idle=10


# ================================================================
# MySQL
# ================================================================
connector.name=mysql
connection-url=jdbc:mysql://host:3306?useSSL=true&requireSSL=true
connection-user=trino_reader
connection-password=${ENV:MYSQL_PASSWORD}


# ================================================================
# SQL Server
# ================================================================
connector.name=sqlserver
connection-url=jdbc:sqlserver://host:1433;database=mydb;encrypt=true
connection-user=trino_reader
connection-password=${ENV:MSSQL_PASSWORD}


# ================================================================
# Oracle
# ================================================================
connector.name=oracle
connection-url=jdbc:oracle:thin:@host:1521:ORCL
connection-user=trino_reader
connection-password=${ENV:ORACLE_PASSWORD}
oracle.synonyms.enabled=true


# ================================================================
# MongoDB
# ================================================================
connector.name=mongodb
mongodb.connection-url=mongodb://user:pass@host:27017/
mongodb.schema-collection=_schema


# ================================================================
# ClickHouse
# ================================================================
connector.name=clickhouse
connection-url=jdbc:clickhouse://host:8123/
connection-user=default
connection-password=${ENV:CH_PASSWORD}
```

### 4.4 Specialized Connectors

```properties
# ================================================================
# Kafka (query topics as SQL tables!)
# ================================================================
connector.name=kafka
kafka.nodes=kafka1:9092,kafka2:9092,kafka3:9092
kafka.table-names=events,clicks,orders
kafka.default-schema=default
kafka.hide-internal-columns=false
kafka.timestamp-upper-bound-force-push-down-enabled=true

# ================================================================
# Elasticsearch / OpenSearch
# ================================================================
connector.name=elasticsearch
elasticsearch.host=elastic-host
elasticsearch.port=9200
elasticsearch.default-schema-name=default
elasticsearch.scroll-size=1000
elasticsearch.scroll-timeout=1m

# ================================================================
# Redis
# ================================================================
connector.name=redis
redis.table-names=sessions,cache_data
redis.nodes=redis:6379
redis.default-schema=default

# ================================================================
# Prometheus (query metrics as SQL!)
# ================================================================
connector.name=prometheus
prometheus.uri=http://prometheus:9090

# ================================================================
# Google Sheets
# ================================================================
connector.name=google_sheets
gsheets.credentials-path=/etc/trino/gsheets-creds.json
gsheets.metadata-sheet-id=<sheet-id>

# ================================================================
# Memory (temp tables / testing)
# ================================================================
connector.name=memory
memory.max-data-per-node=128MB

# ================================================================
# JMX (query JVM metrics)
# ================================================================
connector.name=jmx

# ================================================================
# TPCH / TPCDS (benchmark data generator)
# ================================================================
connector.name=tpch
# or
connector.name=tpcds
```

### 4.5 Cross-Catalog Federated Queries

```sql
-- ============================================================
-- THE KILLER FEATURE: JOIN across ANY data sources in 1 query
-- ============================================================

-- Customer 360 view: PostgreSQL + Iceberg + MongoDB + Kafka
SELECT
    pg.user_id,
    pg.username,
    pg.email,
    lake.total_events,
    lake.last_event_date,
    mongo.preferences,
    realtime.latest_action,
    realtime.action_time
FROM postgresql.app.users pg

-- Join with data lake aggregates (Iceberg on S3)
LEFT JOIN (
    SELECT
        user_id,
        count(*) AS total_events,
        max(event_date) AS last_event_date
    FROM iceberg.datalake.events
    WHERE event_date >= DATE '2024-01-01'
    GROUP BY user_id
) lake ON pg.user_id = lake.user_id

-- Join with MongoDB document store
LEFT JOIN mongodb.profiles.user_preferences mongo
    ON pg.user_id = mongo.user_id

-- Join with real-time Kafka topic
LEFT JOIN kafka.default.user_actions realtime
    ON pg.user_id = realtime.user_id

WHERE pg.status = 'active'
ORDER BY lake.total_events DESC NULLS LAST
LIMIT 100;


-- ============================================================
-- Data migration: Copy from MySQL → Iceberg
-- ============================================================
CREATE TABLE iceberg.warehouse.customers AS
SELECT * FROM mysql.legacy_app.customers;

-- ============================================================
-- CTAS across catalogs
-- ============================================================
CREATE TABLE iceberg.analytics.daily_summary AS
SELECT
    d.department_name,
    COUNT(DISTINCT e.user_id) AS unique_users,
    SUM(e.revenue) AS total_revenue
FROM hive.raw.events e
JOIN postgresql.app.departments d ON e.dept_id = d.id
GROUP BY d.department_name;
```

---

## PHẦN 5: SQL FEATURES

### 5.1 Advanced Window Functions

```sql
-- ============================================================
-- Running totals with frames
-- ============================================================
SELECT
    order_date,
    revenue,
    SUM(revenue) OVER (
        ORDER BY order_date
        ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
    ) AS running_total,
    AVG(revenue) OVER (
        ORDER BY order_date
        ROWS BETWEEN 6 PRECEDING AND CURRENT ROW
    ) AS rolling_7day_avg,
    LAG(revenue, 7) OVER (ORDER BY order_date) AS revenue_7days_ago,
    revenue - LAG(revenue, 7) OVER (ORDER BY order_date) AS wow_change
FROM daily_revenue;

-- ============================================================
-- Percentile and ranking
-- ============================================================
SELECT
    product_id,
    revenue,
    RANK() OVER (ORDER BY revenue DESC) AS rank,
    DENSE_RANK() OVER (ORDER BY revenue DESC) AS dense_rank,
    ROW_NUMBER() OVER (ORDER BY revenue DESC) AS row_num,
    NTILE(10) OVER (ORDER BY revenue DESC) AS decile,
    PERCENT_RANK() OVER (ORDER BY revenue) AS percentile,
    CUME_DIST() OVER (ORDER BY revenue) AS cumulative_dist
FROM product_sales;

-- ============================================================
-- Top-N per group (common interview pattern!)
-- ============================================================
SELECT * FROM (
    SELECT
        category,
        product_name,
        revenue,
        ROW_NUMBER() OVER (
            PARTITION BY category
            ORDER BY revenue DESC
        ) AS rn
    FROM product_sales
) WHERE rn <= 3;

-- ============================================================
-- Session analysis with gap detection
-- ============================================================
WITH session_markers AS (
    SELECT
        user_id,
        event_time,
        event_type,
        CASE WHEN event_time - LAG(event_time) OVER (
            PARTITION BY user_id ORDER BY event_time
        ) > INTERVAL '30' MINUTE
        OR LAG(event_time) OVER (
            PARTITION BY user_id ORDER BY event_time
        ) IS NULL
        THEN 1 ELSE 0 END AS new_session
    FROM events
)
SELECT
    user_id,
    event_time,
    event_type,
    SUM(new_session) OVER (
        PARTITION BY user_id 
        ORDER BY event_time
    ) AS session_id
FROM session_markers;

-- ============================================================
-- FIRST_VALUE / LAST_VALUE
-- ============================================================
SELECT
    user_id,
    event_time,
    event_type,
    FIRST_VALUE(event_type) OVER (
        PARTITION BY user_id
        ORDER BY event_time
    ) AS first_action,
    LAST_VALUE(event_type) OVER (
        PARTITION BY user_id
        ORDER BY event_time
        ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING
    ) AS last_action
FROM events;
```

### 5.2 Array, Map & Row Functions

```sql
-- ============================================================
-- Array operations
-- ============================================================
SELECT
    user_id,
    tags,
    CARDINALITY(tags) AS tag_count,
    CONTAINS(tags, 'premium') AS is_premium,
    ARRAY_JOIN(tags, ', ') AS tags_string,
    ARRAY_SORT(tags) AS sorted_tags,
    ARRAY_DISTINCT(tags) AS unique_tags,
    SLICE(tags, 1, 3) AS first_3_tags,
    CONCAT(tags, ARRAY['new_tag']) AS with_new_tag,
    ARRAY_REMOVE(tags, 'expired') AS without_expired
FROM user_profiles;

-- Lambda functions on arrays
SELECT
    user_id,
    FILTER(tags, t -> t LIKE 'data%') AS data_tags,
    TRANSFORM(tags, t -> UPPER(t)) AS upper_tags,
    ANY_MATCH(tags, t -> t = 'admin') AS is_admin,
    ALL_MATCH(scores, s -> s > 70) AS all_passing,
    REDUCE(scores, 0, (s, x) -> s + x, s -> s) AS total_score
FROM user_profiles;

-- ============================================================
-- Map operations
-- ============================================================
SELECT
    user_id,
    properties,
    MAP_KEYS(properties) AS keys,
    MAP_VALUES(properties) AS values,
    ELEMENT_AT(properties, 'plan') AS plan,
    MAP_FILTER(properties, (k, v) -> k IN ('plan', 'region')) AS filtered,
    MAP_CONCAT(properties, MAP(ARRAY['env'], ARRAY['prod'])) AS extended
FROM user_metadata;

-- ============================================================
-- UNNEST (explode arrays/maps to rows)
-- ============================================================
-- Explode array
SELECT user_id, tag
FROM user_profiles
CROSS JOIN UNNEST(tags) AS t(tag);

-- Explode array with ordinal position
SELECT user_id, tag, pos
FROM user_profiles
CROSS JOIN UNNEST(tags) WITH ORDINALITY AS t(tag, pos);

-- Explode map to key-value rows
SELECT user_id, key, value
FROM user_metadata
CROSS JOIN UNNEST(properties) AS t(key, value);

-- ============================================================
-- Row (Struct) types
-- ============================================================
SELECT
    user_id,
    address.street,
    address.city,
    address.zip
FROM users;

-- Create row
SELECT ROW('John', 30, 'NYC') AS person;

-- Cast to named row
SELECT CAST(ROW('John', 30) AS ROW(name VARCHAR, age INT));
```

### 5.3 JSON Functions

```sql
-- ============================================================
-- JSON parsing and extraction
-- ============================================================
SELECT
    json_extract_scalar(payload, '$.user.id') AS user_id,
    json_extract_scalar(payload, '$.user.name') AS name,
    json_extract(payload, '$.items') AS items_array,
    json_array_length(json_extract(payload, '$.items')) AS item_count,
    CAST(json_extract_scalar(payload, '$.amount') AS DOUBLE) AS amount
FROM raw_events
WHERE json_extract_scalar(payload, '$.event_type') = 'purchase';

-- JSON path with arrays
SELECT
    json_extract_scalar(payload, '$.items[0].product_id') AS first_product,
    json_extract_scalar(payload, '$.items[0].price') AS first_price,
    json_extract_scalar(payload, '$.items[1].product_id') AS second_product
FROM raw_events;

-- ============================================================
-- Build JSON from SQL
-- ============================================================
SELECT JSON_OBJECT(
    KEY 'user_id' VALUE user_id,
    KEY 'metrics' VALUE JSON_OBJECT(
        KEY 'events' VALUE event_count,
        KEY 'revenue' VALUE total_revenue
    )
) AS user_json
FROM user_metrics;

SELECT JSON_ARRAY(1, 2, 'three', true) AS mixed_array;

-- ============================================================
-- JSON to table with UNNEST
-- ============================================================
SELECT item.*
FROM raw_events
CROSS JOIN UNNEST(
    CAST(json_extract(payload, '$.items') AS ARRAY(
        ROW(product_id VARCHAR, quantity INT, price DOUBLE)
    ))
) AS t(item);
```

### 5.4 Time Travel (Iceberg / Delta Lake)

```sql
-- ============================================================
-- Iceberg Time Travel
-- ============================================================

-- Query specific snapshot by ID
SELECT * FROM iceberg.db.orders
FOR VERSION AS OF 7654321098765;

-- Query at a specific timestamp
SELECT * FROM iceberg.db.orders
FOR TIMESTAMP AS OF TIMESTAMP '2024-06-15 10:00:00 UTC';

-- ============================================================
-- Iceberg Metadata Tables (invaluable for debugging!)
-- ============================================================

-- View all snapshots
SELECT snapshot_id, committed_at, operation, summary
FROM iceberg.db."orders$snapshots"
ORDER BY committed_at DESC;

-- View history (parent-child snapshot chain)
SELECT * FROM iceberg.db."orders$history";

-- View manifest files
SELECT * FROM iceberg.db."orders$manifests";

-- View data files (size, record count, partition)
SELECT file_path, record_count, file_size_in_bytes, partition
FROM iceberg.db."orders$files";

-- View partition stats
SELECT * FROM iceberg.db."orders$partitions";

-- ============================================================
-- Iceberg Table Maintenance
-- ============================================================

-- Expire old snapshots (cleanup storage)
ALTER TABLE iceberg.db.orders
    EXECUTE expire_snapshots(retention_threshold => '7d');

-- Remove orphan files
ALTER TABLE iceberg.db.orders
    EXECUTE remove_orphan_files(retention_threshold => '7d');

-- Optimize (compact small files)
ALTER TABLE iceberg.db.orders EXECUTE optimize
    WHERE order_date >= DATE '2024-01-01';

-- ============================================================
-- Delta Lake Time Travel
-- ============================================================
SELECT * FROM delta.db.orders
FOR VERSION AS OF 42;

SELECT * FROM delta.db.orders
FOR TIMESTAMP AS OF TIMESTAMP '2024-06-15 10:00:00 UTC';

-- Delta history
SELECT * FROM delta.db."orders$history";
```

### 5.5 Table Management — CTAS, INSERT, MERGE

```sql
-- ============================================================
-- CREATE TABLE AS SELECT (CTAS)
-- ============================================================
CREATE TABLE iceberg.analytics.daily_summary
WITH (
    format = 'PARQUET',
    partitioning = ARRAY['day(order_date)'],
    sorted_by = ARRAY['customer_id']
) AS
SELECT
    order_date,
    customer_id,
    count(*) AS order_count,
    sum(amount) AS total_amount
FROM hive.raw.orders
GROUP BY 1, 2;

-- ============================================================
-- INSERT INTO (append data)
-- ============================================================
INSERT INTO iceberg.analytics.daily_summary
SELECT
    order_date,
    customer_id,
    count(*) AS order_count,
    sum(amount) AS total_amount
FROM hive.raw.orders
WHERE order_date = CURRENT_DATE
GROUP BY 1, 2;

-- ============================================================
-- MERGE (upsert — Iceberg connector)
-- ============================================================
MERGE INTO iceberg.db.customers AS target
USING staging.new_customers AS source
ON target.customer_id = source.customer_id
WHEN MATCHED AND source.is_deleted THEN
    DELETE
WHEN MATCHED THEN
    UPDATE SET
        name = source.name,
        email = source.email,
        updated_at = current_timestamp
WHEN NOT MATCHED THEN
    INSERT (customer_id, name, email, created_at)
    VALUES (source.customer_id, source.name, source.email, current_timestamp);

-- ============================================================
-- DELETE (GDPR / data cleanup)
-- ============================================================
DELETE FROM iceberg.db.users
WHERE user_id IN (
    SELECT user_id FROM gdpr_deletion_requests
    WHERE requested_at < CURRENT_DATE - INTERVAL '30' DAY
);

-- ============================================================
-- UPDATE (Iceberg)
-- ============================================================
UPDATE iceberg.db.users
SET email = 'redacted@deleted.com',
    name = 'DELETED USER'
WHERE user_id IN (SELECT user_id FROM gdpr_deletion_requests);

-- ============================================================
-- Polymorphic Table Functions (Trino 420+)
-- ============================================================
-- Register external Iceberg table
SELECT * FROM TABLE(
    iceberg.system.register_table(
        schema_name => 'db',
        table_name => 'external_table',
        table_location => 's3://bucket/path/to/table'
    )
);
```

### 5.6 Approximate & Statistical Functions

```sql
-- ============================================================
-- Approximate count distinct (HyperLogLog)
-- ~2% error, 100x faster on billions of rows
-- ============================================================
SELECT approx_distinct(user_id) AS unique_users
FROM events;

-- Compare with exact (much slower)
SELECT count(DISTINCT user_id) AS exact_unique_users
FROM events;

-- ============================================================
-- Approximate percentile (T-Digest)
-- ============================================================
SELECT
    service_name,
    approx_percentile(response_time_ms, 0.50) AS p50,
    approx_percentile(response_time_ms, 0.90) AS p90,
    approx_percentile(response_time_ms, 0.95) AS p95,
    approx_percentile(response_time_ms, 0.99) AS p99
FROM request_logs
GROUP BY service_name;

-- ============================================================
-- Approximate most frequent (TopK / Space-Saving)
-- ============================================================
SELECT approx_most_frequent(100, page_url, 10000) AS top_100_pages
FROM page_views;

-- ============================================================
-- HyperLogLog for sketch-based analytics
-- ============================================================
-- Create HLL sketch (can be stored + merged later)
SELECT
    event_date,
    approx_set(user_id) AS user_hll
FROM events
GROUP BY event_date;

-- Merge HLL sketches across dates
SELECT cardinality(merge(user_hll)) AS unique_users_all_time
FROM daily_sketches;

-- ============================================================
-- Statistical functions
-- ============================================================
SELECT
    corr(ad_spend, revenue) AS correlation,
    regr_slope(revenue, ad_spend) AS slope,
    regr_intercept(revenue, ad_spend) AS intercept,
    regr_r2(revenue, ad_spend) AS r_squared
FROM marketing_data;
```

### 5.7 Common Table Expressions (CTEs) & Recursive

```sql
-- ============================================================
-- Standard CTE (WITH clause)
-- ============================================================
WITH monthly_revenue AS (
    SELECT
        date_trunc('month', order_date) AS month,
        sum(amount) AS revenue
    FROM orders
    GROUP BY 1
),
growth AS (
    SELECT
        month,
        revenue,
        LAG(revenue) OVER (ORDER BY month) AS prev_revenue,
        (revenue - LAG(revenue) OVER (ORDER BY month)) / 
            LAG(revenue) OVER (ORDER BY month) * 100 AS growth_pct
    FROM monthly_revenue
)
SELECT * FROM growth ORDER BY month;

-- ============================================================
-- Recursive CTE (org chart, graph traversal)
-- ============================================================
WITH RECURSIVE org_chart AS (
    -- Base: top-level managers
    SELECT id, name, manager_id, 0 AS level
    FROM employees
    WHERE manager_id IS NULL
    
    UNION ALL
    
    -- Recursive: employees under managers
    SELECT e.id, e.name, e.manager_id, o.level + 1
    FROM employees e
    JOIN org_chart o ON e.manager_id = o.id
)
SELECT * FROM org_chart ORDER BY level, name;
```

---

## PHẦN 6: PERFORMANCE TUNING

### 6.1 Query Optimization Checklist

```mermaid
graph TD
    Q[Slow Query?] --> P1{Partition<br/>Pruning?}
    P1 -->|"No partition filter"| Fix1[✅ Add partition<br/>column to WHERE]
    P1 -->|"Yes"| P2{Column<br/>Pruning?}
    
    P2 -->|"SELECT *"| Fix2[✅ Select only<br/>needed columns]
    P2 -->|"Specific columns"| P3{Join<br/>Strategy?}
    
    P3 -->|"Large x Large<br/>partitioned join"| P4{Data<br/>Skew?}
    P3 -->|"Large x Small<br/>not broadcast"| Fix3[✅ Hint: BROADCAST<br/>small table]
    
    P4 -->|"Skewed keys"| Fix4[✅ Skew join hint<br/>or pre-aggregate]
    P4 -->|"Even distribution"| P5{Memory<br/>Pressure?}
    
    P5 -->|"OOM errors"| Fix5[✅ Enable spill<br/>or increase memory]
    P5 -->|"OK"| P6[Check EXPLAIN ANALYZE<br/>for bottleneck]
```

### 6.2 Optimization Techniques

```sql
-- ============================================================
-- 1. PARTITION PRUNING (most important!)
-- ============================================================

-- ✅ GOOD: Uses partition column directly
SELECT * FROM events
WHERE event_date = DATE '2024-01-15';
-- Reads: 1 partition only

-- ❌ BAD: Function on partition column prevents pruning
SELECT * FROM events
WHERE YEAR(event_date) = 2024 AND MONTH(event_date) = 1;
-- Reads: ALL partitions, then filters

-- ❌ BAD: No partition filter at all
SELECT * FROM events
WHERE event_type = 'purchase';
-- Reads: ALL partitions (full scan)


-- ============================================================
-- 2. COLUMN PRUNING (columnar format advantage)
-- ============================================================

-- ✅ GOOD: Minimal columns
SELECT user_id, event_type, amount
FROM events WHERE event_date = CURRENT_DATE;
-- Reads: 3 columns from Parquet

-- ❌ BAD: SELECT * reads ALL columns
SELECT * FROM events WHERE event_date = CURRENT_DATE;
-- Reads: ALL 50 columns from Parquet (10x more I/O)


-- ============================================================
-- 3. PREDICATE PUSHDOWN
-- ============================================================

-- Check if predicate is pushed down
EXPLAIN SELECT * FROM mysql.app.users WHERE status = 'active';
-- Look for: "filterPredicate" vs "ScanFilterAndProject"


-- ============================================================
-- 4. DYNAMIC FILTERING
-- ============================================================

-- Trino auto-builds bloom filter from small (build) side
SET SESSION enable_dynamic_filtering = true;

SELECT f.*, d.category_name
FROM fact_sales f
JOIN dim_category d ON f.category_id = d.id
WHERE d.department = 'Electronics';
-- Trino pushes category_id filter to fact_sales scan
-- Only reads matching splits from fact_sales!


-- ============================================================
-- 5. AVOID CROSS JOINs
-- ============================================================

-- ❌ Terrible: N x M rows
SELECT * FROM users, events;

-- ✅ Use proper JOIN with condition
SELECT * FROM users u JOIN events e ON u.id = e.user_id;


-- ============================================================
-- 6. USE approx_ FOR EXPLORATION
-- ============================================================

-- Exact (slow on 1B+ rows)
SELECT count(DISTINCT user_id) FROM events;

-- Approximate (fast, ~2% error)
SELECT approx_distinct(user_id) FROM events;
```

### 6.3 Configuration Tuning

```properties
# ================================================================
# Worker Resources
# ================================================================
query.max-memory=200GB                     # Total across cluster
query.max-memory-per-node=20GB            # Per worker
query.max-total-memory-per-node=24GB      # + system overhead

# Low memory query killer
query.low-memory-killer.policy=total-reservation-on-blocked-nodes
query.low-memory-killer.delay=5m

# ================================================================
# Concurrency & Parallelism
# ================================================================
query.max-queued-queries=5000
query.max-concurrent-queries=100
task.concurrency=16                        # CPU cores per worker
task.http-response-threads=100
task.max-worker-threads=100
task.writer-count=4                        # INSERT parallelism

# ================================================================
# Spill to Disk (for memory-intensive queries)
# ================================================================
spill-enabled=true
spiller-spill-path=/mnt/ssd/trino-spill
spiller-max-used-space-threshold=0.9
max-spill-per-node=200GB
spill-compression-enabled=true

# ================================================================
# Network & Exchange
# ================================================================
exchange.http-client.max-connections=250
exchange.http-client.max-connections-per-server=250
exchange.concurrent-request-multiplier=3

# ================================================================
# Query timeout
# ================================================================
query.max-run-time=6h
query.max-execution-time=6h
query.max-cpu-time=24h                     # Total CPU across workers

# ================================================================
# JVM (jvm.config)
# ================================================================
# -Xmx48G                           # 70-80% of node memory
# -XX:+UseG1GC
# -XX:G1HeapRegionSize=32M
# -XX:+ExplicitGCInvokesConcurrent
# -XX:+ExitOnOutOfMemoryError
# -XX:ReservedCodeCacheSize=512M
# -XX:-UseBiasedLocking
# -Djdk.attach.allowAttachSelf=true
```

### 6.4 EXPLAIN & Query Debugging

```sql
-- ============================================================
-- EXPLAIN: View logical plan
-- ============================================================
EXPLAIN
SELECT count(*) FROM events WHERE event_date = CURRENT_DATE;

-- ============================================================
-- EXPLAIN (TYPE DISTRIBUTED): View physical plan
-- ============================================================
EXPLAIN (TYPE DISTRIBUTED)
SELECT o.*, c.name
FROM orders o JOIN customers c ON o.customer_id = c.id;
-- Shows: Fragments, join strategy, exchange type

-- ============================================================
-- EXPLAIN ANALYZE: Execute + show runtime stats
-- ============================================================
EXPLAIN ANALYZE
SELECT event_type, count(*)
FROM events
WHERE event_date >= CURRENT_DATE - INTERVAL '7' DAY
GROUP BY 1;
-- Shows per operator:
--   CPU time, wall time
--   Input/Output rows
--   Memory usage
--   Spill bytes
--   Data read

-- ============================================================
-- EXPLAIN (TYPE IO): Show I/O estimates
-- ============================================================
EXPLAIN (TYPE IO)
SELECT * FROM events WHERE event_date = CURRENT_DATE;
-- Shows: estimated rows, splits, bytes read

-- ============================================================
-- System tables for debugging
-- ============================================================

-- Active queries
SELECT
    query_id,
    state,
    user,
    source,
    substr(query, 1, 100) AS query_preview,
    date_diff('second', created, now()) AS running_seconds,
    total_cpu_time,
    peak_user_memory_bytes / 1048576 AS peak_memory_mb
FROM system.runtime.queries
WHERE state = 'RUNNING'
ORDER BY created;

-- Recent failures
SELECT
    query_id,
    user,
    error_type,
    error_code,
    substr(query, 1, 200) AS query_preview,
    created
FROM system.runtime.queries
WHERE state = 'FAILED'
    AND created > current_timestamp - INTERVAL '1' HOUR
ORDER BY created DESC;

-- Kill a runaway query
CALL system.runtime.kill_query(
    query_id => '20240115_123456_00001_abcde',
    message => 'Query taking too long — killed by admin'
);
```

---

## PHẦN 7: DEPLOYMENT

### 7.1 Docker Compose (Development / Testing)

```yaml
# docker-compose.yml — Trino + Hive Metastore + MinIO (S3-compatible)

services:
  trino-coordinator:
    image: trinodb/trino:460
    container_name: trino
    hostname: trino
    ports:
      - "8080:8080"
    volumes:
      - ./etc/coordinator-config.properties:/etc/trino/config.properties
      - ./etc/jvm.config:/etc/trino/jvm.config
      - ./etc/catalog:/etc/trino/catalog
      - ./etc/node.properties:/etc/trino/node.properties
    depends_on:
      metastore:
        condition: service_healthy
    deploy:
      resources:
        limits:
          memory: 8G
          cpus: "4"
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8080/v1/info"]
      interval: 10s
      timeout: 5s
      retries: 5

  trino-worker:
    image: trinodb/trino:460
    deploy:
      replicas: 2
      resources:
        limits:
          memory: 8G
          cpus: "4"
    volumes:
      - ./etc/worker-config.properties:/etc/trino/config.properties
      - ./etc/jvm.config:/etc/trino/jvm.config
      - ./etc/catalog:/etc/trino/catalog
    depends_on:
      trino-coordinator:
        condition: service_healthy

  metastore:
    image: apache/hive:4.0.0
    container_name: hive-metastore
    environment:
      SERVICE_NAME: metastore
      DB_DRIVER: postgres
      SERVICE_OPTS: >-
        -Djavax.jdo.option.ConnectionDriverName=org.postgresql.Driver
        -Djavax.jdo.option.ConnectionURL=jdbc:postgresql://metastore-db:5432/metastore
        -Djavax.jdo.option.ConnectionUserName=hive
        -Djavax.jdo.option.ConnectionPassword=hive
    ports:
      - "9083:9083"
    depends_on:
      metastore-db:
        condition: service_healthy
    healthcheck:
      test: ["CMD", "bash", "-c", "cat < /dev/null > /dev/tcp/localhost/9083"]
      interval: 10s
      timeout: 5s
      retries: 5

  metastore-db:
    image: postgres:16
    environment:
      POSTGRES_USER: hive
      POSTGRES_PASSWORD: hive
      POSTGRES_DB: metastore
    volumes:
      - metastore_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U hive"]
      interval: 5s
      timeout: 5s
      retries: 5

  minio:
    image: minio/minio:latest
    container_name: minio
    command: server /data --console-address ":9001"
    environment:
      MINIO_ROOT_USER: minioadmin
      MINIO_ROOT_PASSWORD: minioadmin
    ports:
      - "9000:9000"
      - "9001:9001"
    volumes:
      - minio_data:/data
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:9000/minio/health/live"]
      interval: 10s
      timeout: 5s
      retries: 3

volumes:
  metastore_data:
  minio_data:
```

```properties
# etc/coordinator-config.properties
coordinator=true
node-scheduler.include-coordinator=false
http-server.http.port=8080
discovery.uri=http://trino:8080
query.max-memory=16GB
query.max-memory-per-node=4GB

# etc/worker-config.properties
coordinator=false
http-server.http.port=8080
discovery.uri=http://trino:8080
query.max-memory-per-node=4GB
```

### 7.2 Kubernetes (Helm Chart)

```bash
# Add Trino Helm repo
helm repo add trino https://trinodb.github.io/charts
helm repo update

# Install with custom values
helm install trino trino/trino \
    --namespace trino \
    --create-namespace \
    --values trino-values.yaml

# Upgrade
helm upgrade trino trino/trino \
    --namespace trino \
    --values trino-values.yaml
```

```yaml
# trino-values.yaml
image:
  repository: trinodb/trino
  tag: "460"

server:
  workers: 5
  coordinatorExtraConfig: |
    query.max-memory=200GB
    query.max-memory-per-node=20GB
    fault-tolerant-execution-task-memory=8GB
  workerExtraConfig: |
    query.max-memory-per-node=20GB
  autoscaling:
    enabled: true
    minReplicas: 2
    maxReplicas: 20
    targetCPUUtilizationPercentage: 70
    behavior:
      scaleDown:
        stabilizationWindowSeconds: 300
      scaleUp:
        stabilizationWindowSeconds: 60

coordinator:
  jvm:
    maxHeapSize: "12G"
  resources:
    requests:
      memory: "8Gi"
      cpu: "4"
    limits:
      memory: "16Gi"
      cpu: "8"

worker:
  jvm:
    maxHeapSize: "24G"
  resources:
    requests:
      memory: "16Gi"
      cpu: "4"
    limits:
      memory: "32Gi"
      cpu: "8"

additionalCatalogs:
  iceberg: |
    connector.name=iceberg
    iceberg.catalog.type=hive_metastore
    hive.metastore.uri=thrift://hive-metastore:9083
    iceberg.file-format=PARQUET
    iceberg.compression-codec=ZSTD

  postgresql: |
    connector.name=postgresql
    connection-url=jdbc:postgresql://postgres:5432/analytics
    connection-user=trino
    connection-password=${ENV:PG_PASSWORD}

  delta: |
    connector.name=delta_lake
    hive.metastore.uri=thrift://hive-metastore:9083

serviceMonitor:
  enabled: true
  labels:
    release: prometheus

ingress:
  enabled: true
  className: nginx
  hosts:
    - host: trino.internal.company.com
      paths:
        - path: /
          pathType: Prefix
```

### 7.3 Trino Gateway (Load Balancer / Router)

```mermaid
graph TB
    subgraph Clients[" "]
        Clients_title["👥 Clients"]
        style Clients_title fill:none,stroke:none,color:#333,font-weight:bold
        BI[BI Tools]
        CLI2[Trino CLI]
        App[Applications]
    end

    Gateway[🚪 Trino Gateway<br/>trinodb/trino-gateway]

    subgraph Clusters[" "]
        Clusters_title["Multiple Trino Clusters"]
        style Clusters_title fill:none,stroke:none,color:#333,font-weight:bold
        Prod[Production Cluster<br/>Interactive queries<br/>5 workers]
        ETL[ETL Cluster<br/>Long-running jobs<br/>20 workers]
        Adhoc[Ad-hoc Cluster<br/>Analyst exploration<br/>10 workers]
    end

    Clients --> Gateway
    Gateway -->|"BI queries"| Prod
    Gateway -->|"dbt/Airflow"| ETL
    Gateway -->|"Jupyter/CLI"| Adhoc
```

```yaml
# Trino Gateway configuration
# https://github.com/trinodb/trino-gateway
requestRouter:
  port: 8080
  name: trinoRouter
  historySize: 1000

backends:
  - name: production
    proxyTo: http://trino-prod:8080
    active: true
    routingGroup: interactive
  - name: etl
    proxyTo: http://trino-etl:8080
    active: true
    routingGroup: batch
  - name: adhoc
    proxyTo: http://trino-adhoc:8080
    active: true
    routingGroup: adhoc
```

### 7.4 Managed Trino Services

| Service | Based On | Pricing | Best For |
|---------|----------|---------|----------|
| **AWS Athena** | Trino | $5/TB scanned | Serverless S3 queries |
| **Starburst Galaxy** | Trino | SaaS subscription | Enterprise Trino |
| **Starburst Enterprise** | Trino | License per node | Self-hosted enterprise |
| **Google Dataproc** | Trino option | Per-minute cluster | GCP ecosystem |
| **Azure HDInsight** | Trino option | Per-node-hour | Azure ecosystem |

```sql
-- AWS Athena example (Trino-compatible SQL, no infra!)
SELECT
    date_trunc('month', order_date) AS month,
    count(*) AS order_count,
    sum(amount) AS revenue
FROM "s3_catalog"."analytics"."orders"
WHERE order_date >= DATE '2024-01-01'
GROUP BY 1
ORDER BY 1;
-- Cost: ~$5 per TB scanned
-- Tip: Use partitioned + columnar format = 10-100x cheaper
```

---

## PHẦN 8: SECURITY

### 8.1 Authentication Methods

```mermaid
graph LR
    subgraph Auth[" "]
        Auth_title["🔐 Authentication"]
        style Auth_title fill:none,stroke:none,color:#333,font-weight:bold
        PWD[Password<br/>LDAP/File]
        OAuth[OAuth2<br/>Google/Okta/Azure AD]
        Kerberos[Kerberos<br/>Enterprise AD]
        Cert[Certificate<br/>mTLS]
        JWT[JWT Token<br/>Service-to-service]
    end

    Auth --> Trino[Trino Coordinator]
    Trino --> AuthZ[Authorization<br/>Access Control]
```

```properties
# ================================================================
# Password Authentication (LDAP)
# ================================================================
http-server.authentication.type=PASSWORD
password-authenticator.name=ldap
ldap.url=ldaps://ldap.company.com:636
ldap.user-bind-pattern=${USER}@company.com
ldap.group-auth-pattern=(&(objectClass=person)(memberof=cn=trino-users,ou=groups,dc=company,dc=com))

# ================================================================
# OAuth2 / OpenID Connect
# ================================================================
http-server.authentication.type=OAUTH2
http-server.authentication.oauth2.issuer=https://accounts.google.com
http-server.authentication.oauth2.client-id=<client-id>
http-server.authentication.oauth2.client-secret=<secret>
http-server.authentication.oauth2.scopes=openid,email
http-server.authentication.oauth2.principal-field=email

# ================================================================
# Kerberos
# ================================================================
http-server.authentication.type=KERBEROS
http.server.authentication.krb5.config=/etc/krb5.conf
http.server.authentication.krb5.keytab=/etc/trino/trino.keytab
http.server.authentication.krb5.service-name=trino

# ================================================================
# TLS / HTTPS (always enable in production!)
# ================================================================
http-server.https.enabled=true
http-server.https.port=8443
http-server.https.keystore.path=/etc/trino/trino.jks
http-server.https.keystore.key=changeit
```

### 8.2 Authorization — File-Based Access Control

```properties
# etc/access-control.properties
access-control.name=file
security.config-file=/etc/trino/rules.json
security.refresh-period=5s
```

```json
{
  "catalogs": [
    {
      "user": "admin",
      "catalog": ".*",
      "allow": "all"
    },
    {
      "user": "data_engineer",
      "catalog": "(hive|iceberg|delta)",
      "allow": "all"
    },
    {
      "user": "analyst",
      "catalog": "(hive|iceberg)",
      "allow": "read-only"
    },
    {
      "user": ".*",
      "catalog": "system",
      "allow": "read-only"
    }
  ],
  "schemas": [
    {
      "user": "analyst",
      "schema": "raw.*",
      "owner": false
    }
  ],
  "tables": [
    {
      "user": "analyst",
      "table": ".*\\.pii\\..*",
      "privileges": []
    }
  ],
  "queries": [
    {
      "user": "analyst",
      "allow": ["execute", "kill"]
    },
    {
      "user": ".*",
      "allow": ["execute"]
    }
  ]
}
```

### 8.3 Data Masking & Row Filtering

```json
{
  "columnMask": [
    {
      "user": "analyst",
      "catalog": ".*",
      "schema": ".*",
      "table": ".*",
      "column": "email",
      "expression": "regexp_replace(email, '(.).*(@.*)', '$1***$2')"
    },
    {
      "user": "analyst",
      "column": "ssn",
      "expression": "'***-**-' || substr(ssn, 8)"
    },
    {
      "user": "analyst",
      "column": "credit_card",
      "expression": "'****-****-****-' || substr(credit_card, -4)"
    },
    {
      "user": "analyst",
      "column": "phone",
      "expression": "regexp_replace(phone, '(\\d{3})\\d{4}(\\d{3})', '$1****$2')"
    }
  ],
  "rowFilter": [
    {
      "user": "regional_analyst_apac",
      "catalog": "hive",
      "schema": ".*",
      "table": "customers",
      "expression": "region = 'APAC'"
    },
    {
      "user": "regional_analyst_emea",
      "table": "customers",
      "expression": "region = 'EMEA'"
    }
  ]
}
```

### 8.4 OPA (Open Policy Agent) Integration

```properties
# etc/access-control.properties
access-control.name=opa
opa.policy.uri=http://opa-server:8181/v1/data/trino/allow
opa.policy.row-filters-uri=http://opa-server:8181/v1/data/trino/rowFilters
opa.policy.column-masking-uri=http://opa-server:8181/v1/data/trino/columnMask
```

```rego
# Rego policy for OPA
package trino

default allow = false

allow {
    input.context.identity.user == "admin"
}

allow {
    input.action.operation == "SelectFromColumns"
    input.context.identity.groups[_] == "analysts"
    not contains(input.action.resource.table.catalogName, "pii")
}
```

---

## PHẦN 9: MONITORING & OPERATIONS

### 9.1 Trino Web UI

```mermaid
graph LR
    subgraph UI[" "]
        UI_title["Trino Web UI — :8080/ui/"]
        style UI_title fill:none,stroke:none,color:#333,font-weight:bold
        Dashboard[Dashboard<br/>Active queries<br/>Worker status]
        QueryDetail[Query Detail<br/>Stages, tasks<br/>Live plan view]
        History[Query History<br/>Past queries<br/>Error analysis]
        Workers[Worker List<br/>CPU, memory<br/>Network I/O]
    end
```

Key metrics visible in UI:
- **Running/Queued/Blocked** query counts
- **Per-query:** CPU time, wall time, memory, rows processed
- **Stage-level:** Input/output rows, operators, parallelism
- **Worker-level:** CPU utilization, memory, network I/O

### 9.2 JMX Monitoring via SQL

```sql
-- ============================================================
-- Query JMX metrics directly with SQL!
-- ============================================================

-- System memory
SELECT
    node,
    "FreePhysicalMemorySize" / 1048576 AS free_memory_mb,
    "TotalPhysicalMemorySize" / 1048576 AS total_memory_mb,
    "SystemCpuLoad" * 100 AS cpu_percent,
    "AvailableProcessors" AS cpu_cores
FROM jmx.current."java.lang:type=OperatingSystem";

-- GC stats
SELECT
    node,
    "CollectionCount" AS gc_count,
    "CollectionTime" AS gc_time_ms
FROM jmx.current."java.lang:type=GarbageCollector,name=G1 Young Generation";

-- Trino query stats
SELECT *
FROM jmx.current."trino.execution:name=QueryManager";

-- Task executor stats
SELECT *
FROM jmx.current."trino.execution:name=TaskExecutor";
```

### 9.3 Prometheus + Grafana

```yaml
# prometheus.yml
scrape_configs:
  - job_name: trino
    metrics_path: /metrics
    static_configs:
      - targets: ["trino-coordinator:8080"]
    scrape_interval: 15s
```

**Key Prometheus Metrics:**
| Metric | Description | Alert Threshold |
|--------|-------------|-----------------|
| `trino_running_queries` | Active queries | > 100 |
| `trino_queued_queries` | Waiting queries | > 50 |
| `trino_blocked_queries` | Memory-blocked | > 10 |
| `trino_failed_queries_total` | Failed queries (counter) | Rate > 5/min |
| `trino_memory_pool_reserved_bytes` | Memory reservation | > 80% of max |
| `trino_cpu_time_seconds_total` | Total CPU used | - |

### 9.4 Operational Runbook

```sql
-- ============================================================
-- Daily Health Check Queries
-- ============================================================

-- 1. Cluster health
SELECT * FROM system.runtime.nodes;
-- Check: all workers "active", recent "last_response_time"

-- 2. Query success rate (last hour)
SELECT
    state,
    count(*) AS query_count,
    avg(date_diff('second', created, "end")) AS avg_duration_sec
FROM system.runtime.queries
WHERE created > current_timestamp - INTERVAL '1' HOUR
GROUP BY state;

-- 3. Slowest queries (last 24h)
SELECT
    query_id,
    user,
    substr(query, 1, 100) AS query_preview,
    date_diff('second', created, "end") AS duration_sec,
    peak_user_memory_bytes / 1048576 AS peak_memory_mb,
    total_cpu_time
FROM system.runtime.queries
WHERE state = 'FINISHED'
    AND created > current_timestamp - INTERVAL '24' HOUR
ORDER BY date_diff('second', created, "end") DESC
LIMIT 20;

-- 4. Memory hogs
SELECT
    query_id,
    user,
    state,
    peak_user_memory_bytes / 1048576 AS peak_memory_mb,
    substr(query, 1, 100) AS query_preview
FROM system.runtime.queries
WHERE state = 'RUNNING'
ORDER BY peak_user_memory_bytes DESC;

-- 5. Error analysis
SELECT
    error_type,
    error_code,
    count(*) AS error_count
FROM system.runtime.queries
WHERE state = 'FAILED'
    AND created > current_timestamp - INTERVAL '24' HOUR
GROUP BY error_type, error_code
ORDER BY error_count DESC;
```

---

## PHẦN 10: REAL-WORLD USE CASES

### 10.1 Data Lake Analytics Platform

```mermaid
graph LR
    subgraph Ingest[" "]
        Ingest_title["📥 Ingestion"]
        style Ingest_title fill:none,stroke:none,color:#333,font-weight:bold
        Kafka2[Kafka] --> Flink[Flink]
        App[App DBs] --> CDC[Debezium CDC]
        API[APIs] --> Airflow[Airflow ETL]
    end

    subgraph Lake[" "]
        Lake_title["🏞️ Data Lake (S3)"]
        style Lake_title fill:none,stroke:none,color:#333,font-weight:bold
        Bronze[Bronze Layer<br/>Raw data]
        Silver[Silver Layer<br/>Clean, typed]
        Gold[Gold Layer<br/>Aggregated]
    end

    subgraph Query[" "]
        Query_title["🔍 Query Layer"]
        style Query_title fill:none,stroke:none,color:#333,font-weight:bold
        Trino2[Trino Cluster]
    end

    subgraph Consume[" "]
        Consume_title["📊 Consumers"]
        style Consume_title fill:none,stroke:none,color:#333,font-weight:bold
        Superset[Apache Superset<br/>Dashboards]
        Jupyter[Jupyter<br/>Ad-hoc Analysis]
        dbt2[dbt<br/>Transformations]
    end

    Flink & CDC & Airflow --> Bronze
    Bronze --> Silver --> Gold
    Lake --> Trino2
    Trino2 --> Consume
```

### 10.2 Data Federation / Data Mesh

```sql
-- Each team owns their domain data
-- Trino federates queries across all domains

-- Marketing domain (PostgreSQL)
-- Product domain (MongoDB)
-- Finance domain (Iceberg on S3)
-- Events domain (Kafka + Iceberg)

SELECT
    p.product_name,
    p.category,
    m.campaign_name,
    m.ad_spend,
    f.revenue,
    f.revenue - m.ad_spend AS profit,
    e.click_count,
    e.conversion_rate
FROM mongodb.product.products p
JOIN postgresql.marketing.campaigns m ON p.product_id = m.product_id
JOIN iceberg.finance.product_revenue f ON p.product_id = f.product_id
JOIN (
    SELECT 
        product_id,
        count(*) AS click_count,
        sum(CASE WHEN event_type = 'purchase' THEN 1 ELSE 0 END) * 1.0 / count(*) AS conversion_rate
    FROM iceberg.events.product_events
    WHERE event_date >= CURRENT_DATE - INTERVAL '30' DAY
    GROUP BY product_id
) e ON p.product_id = e.product_id
ORDER BY profit DESC;
```

### 10.3 GDPR / Data Privacy Compliance

```sql
-- Process GDPR deletion requests using Trino + Iceberg

-- Step 1: Find all user data across all sources
WITH user_data_locations AS (
    SELECT 'iceberg.warehouse.orders' AS source, count(*) AS records
    FROM iceberg.warehouse.orders WHERE user_id = 'USER_123'
    UNION ALL
    SELECT 'iceberg.warehouse.events', count(*)
    FROM iceberg.warehouse.events WHERE user_id = 'USER_123'
    UNION ALL
    SELECT 'iceberg.warehouse.profiles', count(*)
    FROM iceberg.warehouse.profiles WHERE user_id = 'USER_123'
)
SELECT * FROM user_data_locations WHERE records > 0;

-- Step 2: Delete user data (Iceberg DELETE)
DELETE FROM iceberg.warehouse.orders WHERE user_id = 'USER_123';
DELETE FROM iceberg.warehouse.events WHERE user_id = 'USER_123';
DELETE FROM iceberg.warehouse.profiles WHERE user_id = 'USER_123';

-- Step 3: Compact files (rewrite without deleted rows)
ALTER TABLE iceberg.warehouse.orders EXECUTE optimize;
ALTER TABLE iceberg.warehouse.events EXECUTE optimize;

-- Step 4: Expire old snapshots (remove physical data)
ALTER TABLE iceberg.warehouse.orders EXECUTE expire_snapshots(retention_threshold => '0d');
ALTER TABLE iceberg.warehouse.events EXECUTE expire_snapshots(retention_threshold => '0d');
```

### 10.4 dbt + Trino

```yaml
# dbt profiles.yml
my_project:
  target: prod
  outputs:
    prod:
      type: trino
      method: none  # or ldap, kerberos, oauth
      host: trino-coordinator
      port: 8080
      user: dbt_user
      database: iceberg
      schema: analytics
      catalog: iceberg
      threads: 8
      session_properties:
        query_max_run_time: 2h
        fault_tolerant_execution_task_memory: 8GB
```

```sql
-- models/marts/daily_revenue.sql
{{ config(
    materialized='table',
    properties={
      "format": "'PARQUET'",
      "partitioning": "ARRAY['day(order_date)']"
    }
) }}

SELECT
    order_date,
    product_category,
    count(DISTINCT customer_id) AS unique_customers,
    count(*) AS order_count,
    sum(amount) AS revenue,
    avg(amount) AS avg_order_value
FROM {{ ref('stg_orders') }}
WHERE order_date >= CURRENT_DATE - INTERVAL '365' DAY
GROUP BY 1, 2
```

---

## PHẦN 11: TRINO VS ALTERNATIVES

### 11.1 Comprehensive Comparison

| Feature | Trino | Spark SQL | DuckDB | BigQuery | Athena | Redshift |
|---------|-------|-----------|--------|----------|--------|----------|
| **Type** | MPP Query Engine | Distributed Processing | Embedded OLAP | Serverless DWH | Serverless Query | Cloud DWH |
| **Latency** | Seconds | Minutes | Milliseconds | Seconds | Seconds | Seconds |
| **Max Data** | Petabytes | Petabytes | ~200 GB | Petabytes | Petabytes | Petabytes |
| **Federation** | ✅ Core feature | ⚠️ Limited | ❌ Single | ❌ BQ only | ✅ Federated | ⚠️ Spectrum |
| **Storage** | None (query only) | None (compute) | In-process | Managed | None (S3) | Managed |
| **Concurrency** | High (100s) | Low (10s) | Single user | Very high | Moderate | High |
| **Cost Model** | Self-managed | Self-managed | Free/OSS | Per-query | Per-query | Per-node |
| **ML/AI** | ❌ | ✅ MLlib | ❌ | ✅ BigQuery ML | ❌ | ✅ Redshift ML |
| **Streaming** | ⚠️ Kafka queries | ✅ Structured Streaming | ❌ | ❌ | ❌ | ❌ |
| **Best For** | Interactive federation | Heavy ETL + ML | Local analysis | Cloud BI | S3 ad-hoc | Enterprise DWH |

### 11.2 Decision Tree

```mermaid
graph TD
    Start[Need to Query Data?] --> Size{Data Size?}
    
    Size -->|"< 10 GB"| DuckDB[🦆 DuckDB<br/>Local, instant, free]
    Size -->|"10 GB - 10 TB"| Concurrent{How many users?}
    Size -->|"> 10 TB"| Federation{Need Federation?}
    
    Concurrent -->|"1-5 users"| DuckDB
    Concurrent -->|"5+ users"| Budget{Budget?}
    
    Budget -->|"Self-managed OK"| Trino[🔷 Trino<br/>Interactive MPP]
    Budget -->|"Want managed"| Cloud{Cloud Provider?}
    
    Cloud -->|"AWS"| Athena[☁️ AWS Athena<br/>Serverless Trino]
    Cloud -->|"GCP"| BigQuery[🟦 BigQuery<br/>Serverless DWH]
    Cloud -->|"Azure"| Synapse[🟪 Azure Synapse<br/>Serverless SQL]
    
    Federation -->|"Yes, multi-source"| Trino
    Federation -->|"No, single source"| ETL{Query Type?}
    
    ETL -->|"Interactive BI"| Trino
    ETL -->|"Heavy ETL / ML"| Spark[⚡ Apache Spark]
    ETL -->|"Streaming"| Flink2[🌊 Apache Flink]

    style Trino fill:#4285f4,color:#fff
    style DuckDB fill:#fdd835
    style Spark fill:#e65100,color:#fff
    style Athena fill:#ff9800
    style BigQuery fill:#1565c0,color:#fff
```

---

## PHẦN 12: HANDS-ON LABS

### Lab 1: Local Trino + Iceberg + MinIO

```bash
# Step 1: Create project structure
mkdir -p trino-lab/etc/catalog
cd trino-lab

# Step 2: Create config files (see Section 7.1 for docker-compose.yml)
# Create catalog configs:

# etc/catalog/iceberg.properties
cat > etc/catalog/iceberg.properties << 'EOF'
connector.name=iceberg
iceberg.catalog.type=hive_metastore
hive.metastore.uri=thrift://metastore:9083
iceberg.file-format=PARQUET
hive.s3.endpoint=http://minio:9000
hive.s3.path-style-access=true
hive.s3.aws-access-key=minioadmin
hive.s3.aws-secret-key=minioadmin
EOF

# Step 3: Start cluster
docker compose up -d

# Step 4: Connect
docker exec -it trino trino

# Step 5: Create schema and table
trino> CREATE SCHEMA iceberg.analytics
       WITH (location = 's3a://warehouse/analytics/');

trino> CREATE TABLE iceberg.analytics.events (
           event_id VARCHAR,
           user_id VARCHAR,
           event_type VARCHAR,
           amount DOUBLE,
           event_time TIMESTAMP(6) WITH TIME ZONE
       )
       WITH (
           format = 'PARQUET',
           partitioning = ARRAY['day(event_time)']
       );

# Step 6: Insert and query
trino> INSERT INTO iceberg.analytics.events VALUES
           ('e1', 'u1', 'purchase', 99.99, TIMESTAMP '2024-01-15 10:00:00 UTC'),
           ('e2', 'u2', 'signup', 0.00, TIMESTAMP '2024-01-15 11:00:00 UTC'),
           ('e3', 'u1', 'purchase', 49.99, TIMESTAMP '2024-01-16 09:00:00 UTC');

trino> SELECT event_type, count(*), sum(amount) AS total
       FROM iceberg.analytics.events
       GROUP BY event_type;

# Step 7: Time travel
trino> SELECT * FROM iceberg.analytics."events$snapshots";
```

### Lab 2: Federated Query — PostgreSQL + Iceberg

```bash
# Add PostgreSQL to docker-compose.yml
# Create etc/catalog/postgres.properties:
cat > etc/catalog/postgres.properties << 'EOF'
connector.name=postgresql
connection-url=jdbc:postgresql://postgres-app:5432/myapp
connection-user=reader
connection-password=password
EOF
```

```sql
-- Query across PostgreSQL (operational) + Iceberg (analytics)
SELECT
    u.id AS user_id,
    u.name,
    u.email,
    COALESCE(e.event_count, 0) AS events_last_7d,
    COALESCE(e.total_spent, 0.0) AS spent_last_7d,
    CASE
        WHEN e.total_spent > 100 THEN 'high_value'
        WHEN e.total_spent > 0 THEN 'regular'
        ELSE 'inactive'
    END AS segment
FROM postgresql.myapp.users u
LEFT JOIN (
    SELECT
        user_id,
        count(*) AS event_count,
        sum(amount) AS total_spent
    FROM iceberg.analytics.events
    WHERE event_time >= CURRENT_TIMESTAMP - INTERVAL '7' DAY
        AND event_type = 'purchase'
    GROUP BY user_id
) e ON CAST(u.id AS VARCHAR) = e.user_id
ORDER BY e.total_spent DESC NULLS LAST;
```

### Lab 3: Python Client (trino-python-client)

```python
"""
pip install trino pandas
"""

from trino.dbapi import connect
from trino.auth import BasicAuthentication
import pandas as pd

# Connect to Trino
conn = connect(
    host="localhost",
    port=8080,
    user="analyst",
    catalog="iceberg",
    schema="analytics",
    # auth=BasicAuthentication("user", "pass"),  # if auth enabled
)

# Execute query
cursor = conn.cursor()
cursor.execute("""
    SELECT
        date_trunc('day', event_time) AS day,
        event_type,
        count(*) AS event_count,
        sum(amount) AS total_amount
    FROM events
    WHERE event_time >= CURRENT_TIMESTAMP - INTERVAL '30' DAY
    GROUP BY 1, 2
    ORDER BY 1
""")

# Fetch as pandas DataFrame
columns = [desc[0] for desc in cursor.description]
df = pd.DataFrame(cursor.fetchall(), columns=columns)
print(df)

# Parameterized query
cursor.execute(
    "SELECT * FROM events WHERE user_id = ? AND event_date >= ?",
    params=["user_123", "2024-01-01"]
)

cursor.close()
conn.close()
```

---

## 📦 Verified Resources

| Resource | Link | Note |
|----------|------|------|
| Trino GitHub | [trinodb/trino](https://github.com/trinodb/trino) | 10k⭐ Main repo |
| Trino Docs | [trino.io/docs/current](https://trino.io/docs/current/) | Official documentation |
| Trino Helm Charts | [trinodb/charts](https://github.com/trinodb/charts) | Kubernetes deployment |
| Trino Gateway | [trinodb/trino-gateway](https://github.com/trinodb/trino-gateway) | Load balancer |
| Trino Python Client | [trinodb/trino-python-client](https://github.com/trinodb/trino-python-client) | Python SDK |
| PrestoDB | [prestodb/presto](https://github.com/prestodb/presto) | 16k⭐ Meta's fork |
| Starburst | [starburst.io](https://www.starburst.io/) | Enterprise Trino |
| dbt-trino | [starburstdata/dbt-trino](https://github.com/starburstdata/dbt-trino) | dbt adapter |
| Trino Community | [Trino Slack](https://trino.io/slack.html) | Community support |
| Trino Blog | [trino.io/blog](https://trino.io/blog/) | Articles & talks |

---

## 🔗 Liên Kết Nội Bộ

- [[01_Apache_Iceberg_Complete_Guide|Apache Iceberg]] — Primary table format for Trino
- [[02_Delta_Lake_Complete_Guide|Delta Lake]] — Alternative table format
- [[06_Apache_Spark_Complete_Guide|Apache Spark]] — Heavy ETL & ML
- [[13_DuckDB_Complete_Guide|DuckDB]] — Local OLAP alternative
- [[11_Data_Catalogs_Guide|Data Catalogs]] — Metadata management
- [[15_Fivetran_Airbyte_Guide|Fivetran & Airbyte]] — Data ingestion
- [[../fundamentals/10_Cloud_Platforms|Cloud Platforms]] — AWS Athena, etc.

---

*Last Updated: February 2026*
*Coverage: Architecture, SQL, Connectors, Security, Deployment, Monitoring, Labs*
