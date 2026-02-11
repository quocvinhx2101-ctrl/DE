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

```
papers/
├── README.md                              # File này
├── 01_Distributed_Systems_Papers.md       # MapReduce, GFS, Bigtable, Dynamo, Spanner
├── 02_Stream_Processing_Papers.md         # Kafka, Flink, Dataflow, MillWheel
├── 03_Data_Warehouse_Papers.md            # Kimball, Inmon, C-Store, Dremel
├── 04_Table_Format_Papers.md              # Iceberg, Delta Lake, Hudi
├── 05_Consensus_Papers.md                 # Paxos, Raft, ZooKeeper, Chubby
├── 06_Database_Internals_Papers.md        # LSM-tree, B-tree, MVCC, PostgreSQL
├── 07_Data_Quality_Governance_Papers.md   # Data quality, lineage, governance
├── 08_ML_Data_Papers.md                   # Feature stores, MLOps, ML pipelines
├── 09_Query_Optimization_Papers.md        # System R, Cascades, Calcite, HyPer
└── 10_Serialization_Format_Papers.md      # Avro, Parquet, Arrow, Protobuf
```

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

---

## 🎯 LEARNING PATH

**Recommended Reading Order:**

### Level 1: Foundations
1. **Distributed Systems** - GFS, MapReduce, Bigtable
2. **Consensus** - Paxos, Raft
3. **Database Internals** - LSM-tree, B-tree

### Level 2: Data Processing
4. **Data Warehouse** - Kimball, C-Store
5. **Stream Processing** - Kafka, Dataflow model
6. **Serialization** - Avro, Parquet, Arrow

### Level 3: Modern Data Platform
7. **Table Formats** - Iceberg, Delta Lake
8. **Query Optimization** - Calcite, vectorized execution
9. **ML Data** - Feature stores, MLOps
10. **Data Quality** - Governance, lineage

---

## 🔗 LIÊN KẾT VỚI CÁC FOLDER KHÁC

- `../tools/` - Hướng dẫn sử dụng các tool SOTA
- `../fundamentals/` - Kiến thức nền tảng Data Engineering
- `../usecases/` - Case studies từ các công ty lớn

---

*Tổng hợp: February 2026*
*Total: 10 paper topic files*
