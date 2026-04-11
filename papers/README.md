# Foundational Papers in Data Engineering

## Những Paper Nghiên Cứu Nền Tảng Tạo Nên Các Công Nghệ Data Engineering Hiện Đại

---

## 📚 GIỚI THIỆU

Folder này chứa tổng hợp các paper nghiên cứu gốc - nền tảng lý thuyết cho các công nghệ Data Engineering hiện đại. Mỗi file bao gồm:
- Link paper gốc
- Tóm tắt nội dung chính
- Ảnh hưởng đến các tools hiện tại
- Key concepts cần nắm

---

## 📁 STRUCTURE

|Layer|Files|Coverage|
|---|---|---|
|**Storage**|06 (DB Internals), 10 (Serialization), 04 (Table Formats)|✅ B-Tree, LSM, MVCC, Parquet, Arrow, Iceberg/Delta/Hudi|
|**Coordination**|01 (Distributed Systems), 05 (Consensus)|✅ Paxos, Raft, Zookeeper, GFS, Dynamo|
|**Execution/Compute**|12 (Execution Engines), 02 (Stream), 09 (Query Optimization)|✅ Spark, Flink, Presto, DuckDB, Catalyst, Calcite|
|**Orchestration**|11 (Orchestration & Ingestion)|✅ Airflow, Dryad, FlumeJava, CDC|
|**Data Modeling**|03 (Data Warehouse)|✅ Kimball, Data Vault, Medallion|
|**Quality & Governance**|07 (Data Quality)|✅ Great Expectations, data contracts|
|**Metadata & Discovery**|13 (Metadata Discovery)|✅ DataHub, Amundsen, OpenLineage, Unity Catalog|
|**Network & Data Transfer**|14 (Networking & RPC)|✅ gRPC, Thrift, Arrow Flight, RDMA, NCCL|
|**ML/AI Data**|08 (ML Data)|✅ Feature stores, training data|
|**Industry Analysis**|15 (Kings & Crown Princes)|✅ Tech verdicts 2025-2039, hype analysis|

---

## 📖 CHI TIẾT TỪNG CHỦNG LOẠI

### 01. Distributed Systems (Hệ Phân Tán)
- Google File System (GFS) - 2003
- MapReduce - 2004
- Bigtable - 2006
- Dynamo (Amazon) - 2007
- Spanner - 2012

### 02. Stream Processing (Xử Lý Dòng)
- Apache Kafka - 2011
- MillWheel - 2013
- Dataflow Model - 2015
- Apache Flink
- Spark Streaming

### 03. Data Warehouse (Kho Dữ Liệu)
- Kimball Dimensional Modeling
- C-Store - 2005
- Dremel - 2010
- Hive, Presto

### 04. Table Formats (Định Dạng Bảng)
- Apache Iceberg - Netflix
- Delta Lake - Databricks
- Apache Hudi - Uber

### 05. Consensus (Đồng Thuận)
- Paxos - 1998
- Raft - 2014
- ZooKeeper - 2010
- Chubby - 2006

### 06. Database Internals (Nội Tại Database)
- LSM-Tree - 1996
- B-Tree - 1970
- MVCC - 1981
- PostgreSQL internals

### 07. Data Quality & Governance
- Data quality frameworks
- Data lineage
- GDPR compliance
- Metadata management

### 08. ML Data & Feature Stores
- Hidden Technical Debt in ML - 2015
- Feast Feature Store
- TFX/TFDV
- MLflow, Kubeflow

### 09. Query Optimization (Tối Ưu Truy Vấn)
- System R Optimizer - 1979
- Volcano/Cascades - 1995
- Apache Calcite - 2018
- HyPer/Umbra - Vectorized & Compiled

### 10. Serialization Formats (Định Dạng Dữ Liệu)
- Apache Avro - Schema evolution
- Protocol Buffers - Binary encoding
- Apache Parquet - Columnar storage
- Apache Arrow - In-memory columnar

### 11. Orchestration & Ingestion (Điều Phối & Data Ingestion)
- Dryad & FlumeJava - Lazy evaluation
- Apache Airflow - Workflow scheduler
- Debezium / CDC - Log-based ingestion

### 12. Execution Engines (Execution Models)
- Batch: MapReduce, Tez, Spark
- Interactive SQL: Dremel, Impala, Presto/Trino
- Streaming & ML: Flink, Ray
- Vectorized & Native: DuckDB, ClickHouse, Photon, DataFusion

### 13. Metadata & Data Discovery (Hệ Thần Kinh)
- Goods (Google), Ground (Berkeley)
- Hive Metastore
- DataHub, Amundsen
- OpenLineage, Marquez
- Unity Catalog, OpenMetadata, Polaris

### 14. Networking, RPC & RDMA (Hệ Tim Mạch)
- Apache Thrift 
- gRPC & Protocol Buffers
- Apache Arrow Flight (Zero-copy RPC)
- RDMA in Data Systems (FaRM/HERD)
- NCCL & UCX (GPU-to-GPU AI Networking)

### 15. Kings & Crown Princes (2025–2039)
- Kings: Iceberg, Delta, Parquet, Arrow, Spark, Flink, Kafka, Airflow, dbt
- Crown Princes: DuckDB, Polars, DataFusion, Velox, Ray, Dagster, Redpanda
- Hype analysis: MDS, standalone Vector DBs, blockchain for governance
- Sources: SIGMOD 2025, VLDB 2025, Databricks/Snowflake Summits
---

## 🎯 LEARNING PATH

**Recommended Reading Order:**

### Level 1: Foundations
1. **Distributed Systems** - GFS, MapReduce, Bigtable
2. **Consensus** - Paxos, Raft
3. **Database Internals** - LSM-tree, B-tree
4. **Networking & RPC** - gRPC, Arrow Flight, RDMA

### Level 2: Data Processing
5. **Data Warehouse** - Kimball, C-Store
6. **Stream Processing** - Kafka, Dataflow model
7. **Serialization** - Avro, Parquet, Arrow

### Level 3: Modern Data Platform
8. **Table Formats** - Iceberg, Delta Lake
9. **Execution Engines** - Spark, DuckDB, Presto, DataFusion
10. **Orchestration** - Airflow, FlumeJava
11. **Query Optimization** - Calcite, vectorized execution

### Level 4: Governance & AI (The Capstone)
12. **Metadata & Discovery** - DataHub, Catalog versioning
13. **Data Quality** - Governance, contracts
14. **ML Data** - Feature stores, MLOps

---

## 🔗 LIÊN KẾT VỚI CÁC FOLDER KHÁC

- `../tools/` - Hướng dẫn sử dụng các tool SOTA
- `../fundamentals/` - Kiến thức nền tảng Data Engineering
- `../usecases/` - Case studies từ các công ty lớn

---

*Tổng hợp: April 2026*
*Total: 15 paper topic files*
