# Real-World Data Platform Use Cases

## Case Studies Từ BigTech và SME Companies

---

## 📚 GIỚI THIỆU

Folder này chứa case studies chi tiết về kiến trúc data platform từ:
- **BigTech Companies** (6 files): Kiến trúc scale lớn từ các công ty hàng đầu
- **SME Companies** (6 files): Giải pháp thực tế cho doanh nghiệp vừa và nhỏ

**Format cho mỗi Use Case:**
- WHAT: Mục tiêu/vấn đề cần giải quyết
- HOW: Chi tiết implementation, tech stack, code samples
- WHY: Lý do lựa chọn, business impact, ROI

---

## 📁 STRUCTURE

```
usecases/
├── README.md                          # File này
│
├── === BIGTECH COMPANIES ===
├── 01_Netflix_Data_Platform.md        # Streaming, recommendations, Iceberg
├── 02_Uber_Data_Platform.md           # Real-time, Hudi, H3 geospatial
├── 03_Airbnb_Data_Platform.md         # Airflow, Superset, Minerva
├── 04_LinkedIn_Data_Platform.md       # Kafka origin, Pinot, Datahub
├── 05_Spotify_Data_Platform.md        # GCP, Scio, Backstage
├── 06_Meta_Data_Platform.md           # Presto, TAO, PyTorch, scale
│
├── === SME COMPANIES ===
├── 07_Startup_Data_Platform.md        # MVP to scale (5-50 employees)
├── 08_Ecommerce_SME_Platform.md       # E-commerce ($1M-$50M revenue)
├── 09_SaaS_Company_Platform.md        # SaaS ($500K-$20M ARR)
├── 10_Fintech_SME_Platform.md         # Fintech SME ($1M-$50M)
├── 11_Healthcare_SME_Platform.md      # Clinics, Telehealth, MedTech
└── 12_Manufacturing_SME_Platform.md   # Production, Factory ($5M-$100M)
```

---

## 🏢 BIGTECH COMPANIES (01-06)

### 01. Netflix
- **Scale:** 230M+ subscribers, petabytes/day
- **Highlight:** Created Apache Iceberg
- **Key Stack:** Kafka, Iceberg, Flink, Druid, Presto
- **Data Products:** Recommendations, A/B Testing, QoE monitoring

### 02. Uber
- **Scale:** 130M+ users, trillions of events/week
- **Highlight:** Created Apache Hudi
- **Key Stack:** Kafka, Hudi, Pinot, Flink, Michelangelo (ML)
- **Data Products:** Dynamic pricing, ETA, Driver matching

### 03. Airbnb
- **Scale:** 150M+ users, 7M+ listings
- **Highlight:** Created Apache Airflow & Superset
- **Key Stack:** Airflow, Superset, Minerva, Zipline (features)
- **Data Products:** Search ranking, Smart pricing, Trust platform

### 04. LinkedIn
- **Scale:** 900M+ members, 7+ trillion messages/day
- **Highlight:** Created Apache Kafka
- **Key Stack:** Kafka, Samza, Pinot, Venice, Datahub
- **Data Products:** Feed ranking, PYMK, Job matching

### 05. Spotify
- **Scale:** 600M+ users, billions of streams/day
- **Highlight:** Created Luigi, Backstage
- **Key Stack:** GCP, BigQuery, Dataflow/Scio, Bigtable
- **Data Products:** Discover Weekly, Wrapped, Radio

### 06. Meta/Facebook
- **Scale:** 3B+ users, exabytes of data
- **Highlight:** Created Presto, PyTorch, RocksDB
- **Key Stack:** Presto, Spark, TAO, Scuba, PyTorch
- **Data Products:** News Feed, Ads, Integrity

---

## 🏪 SME COMPANIES (07-12)

### 07. Startup Data Platform
- **Scale:** 5-50 employees, pre-seed to Series A
- **Focus:** MVP → Scale journey
- **Key Stack:** PostgreSQL, dbt Cloud, Fivetran, Metabase
- **Use Cases:** Product analytics, Funnel tracking, Customer 360

### 08. E-commerce SME
- **Scale:** $1M-$50M revenue, online retail
- **Focus:** Sales và customer analytics
- **Key Stack:** Snowflake/BigQuery, dbt, Segment, Looker
- **Use Cases:** Inventory management, Customer segmentation, Revenue analytics

### 09. SaaS Company
- **Scale:** $500K-$20M ARR, B2B/B2C SaaS
- **Focus:** Subscription metrics, PLG analytics
- **Key Stack:** Snowflake, dbt, Segment, Amplitude
- **Use Cases:** MRR/Churn analysis, Product analytics, Customer health

### 10. Fintech SME
- **Scale:** $1M-$50M revenue, financial services
- **Focus:** Compliance, risk, transaction analytics
- **Key Stack:** Snowflake, dbt, Great Expectations, Sigma
- **Use Cases:** Fraud detection, Compliance reporting, Risk scoring

### 11. Healthcare SME
- **Scale:** Clinics, Telehealth, MedTech startups
- **Focus:** HIPAA compliance, patient analytics
- **Key Stack:** Snowflake, dbt, Fivetran, Tableau
- **Use Cases:** Patient outcomes, Operational efficiency, Quality measures

### 12. Manufacturing SME
- **Scale:** $5M-$100M revenue, factories/production
- **Focus:** OEE, quality, supply chain
- **Key Stack:** TimescaleDB, Snowflake, Grafana, dbt
- **Use Cases:** Production analytics, Predictive maintenance, Quality control

---

## 🔧 TECH STACK COMPARISON

```
INGESTION & STREAMING:

Company     | Messaging      | Stream Processing
------------|----------------|-------------------
Netflix     | Kafka          | Flink, Mantis
Uber        | Kafka          | Flink, Samza
Airbnb      | Kafka          | Spark Streaming
LinkedIn    | Kafka          | Samza, Flink
Spotify     | Pub/Sub        | Dataflow (Beam)
Meta        | Scribe         | Custom streaming


STORAGE:

Company     | Data Lake        | Table Format    | Real-time OLAP
------------|------------------|-----------------|---------------
Netflix     | S3               | Iceberg         | Druid
Uber        | HDFS             | Hudi            | Pinot
Airbnb      | S3               | Hive            | N/A
LinkedIn    | HDFS             | Hive            | Pinot
Spotify     | GCS              | Parquet         | BigQuery
Meta        | HDFS             | Custom          | Scuba


QUERY ENGINES:

Company     | Interactive      | Batch ETL
------------|------------------|------------------
Netflix     | Presto/Trino     | Spark
Uber        | Presto           | Spark
Airbnb      | Presto           | Spark
LinkedIn    | Presto           | Spark
Spotify     | BigQuery         | Dataflow/Spark
Meta        | Presto           | Spark


ORCHESTRATION:

Company     | Workflow         | ML Platform
------------|------------------|------------------
Netflix     | Custom + Meson   | Metaflow
Uber        | Cadence          | Michelangelo
Airbnb      | Airflow          | Bighead
LinkedIn    | Azkaban/Custom   | Pro-ML
Spotify     | Cloud Composer   | Vertex AI/Custom
Meta        | Custom           | FBLearner Flow
```

---

## 🎯 OSS CONTRIBUTIONS BY COMPANY

```
COMPANY         | MAJOR CONTRIBUTIONS
----------------|----------------------------------------------------
Netflix         | Iceberg, Mantis, Metacat, Metaflow, Eureka
Uber            | Hudi, AresDB, Cadence, H3, Horovod, Ludwig
Airbnb          | Airflow, Superset, Knowledge Repo
LinkedIn        | Kafka, Samza, Pinot, Gobblin, Venice, Datahub
Spotify         | Luigi, Scio, Backstage, ANNOY
Meta            | Presto, RocksDB, Velox, PyTorch, FAISS, React


APACHE PROJECTS CREATED:

Company      | Project      | Purpose
-------------|--------------|--------------------------------
LinkedIn     | Kafka        | Distributed streaming
Airbnb       | Airflow      | Workflow orchestration
Airbnb       | Superset     | Data visualization
Netflix      | Iceberg      | Table format
Uber         | Hudi         | Incremental processing
LinkedIn     | Samza        | Stream processing
LinkedIn     | Pinot        | Real-time OLAP
LinkedIn     | Gobblin      | Data ingestion
```

---

## 📊 SCALE COMPARISON

```
DAILY DATA VOLUME:

Company      | Messages/Events     | Data Processed
-------------|---------------------|-------------------
Netflix      | 700B+ events/day    | Petabytes/day
Uber         | Trillions/week      | Petabytes/day
Airbnb       | Billions/day        | Terabytes/day
LinkedIn     | 7+ trillion/day     | 7+ PB/day
Spotify      | Billions/day        | Petabytes/day
Meta         | 100+ trillion/day   | Exabytes


WAREHOUSE SIZE:

Company      | Data Lake Size      | Active Users
-------------|---------------------|-------------------
Netflix      | 100+ PB             | 230M
Uber         | 100+ PB             | 130M
Airbnb       | 50+ PB              | 150M
LinkedIn     | Exabytes            | 900M
Spotify      | Petabytes           | 600M
Meta         | Exabytes            | 3B+
```

---

## 🔑 COMMON PATTERNS

### 1. Lambda/Kappa Architecture
- Streaming + Batch from same source
- Real-time for serving, batch for analytics
- Netflix, Uber, LinkedIn all use variations

### 2. Feature Stores
- Critical for ML at scale
- Netflix (Vector), Uber (Michelangelo), Airbnb (Zipline)
- LinkedIn (Feathr), Spotify (custom)

### 3. Metrics Layer
- Single source of truth for metrics
- Airbnb (Minerva), LinkedIn (UMP)
- Reduces dashboard inconsistencies

### 4. Real-time OLAP
- Sub-second analytics
- Druid (Netflix), Pinot (Uber, LinkedIn)
- Scuba (Meta), BigQuery (Spotify)

### 5. Unified Query Layer
- SQL for everyone
- Presto/Trino (Netflix, Uber, LinkedIn, Meta)
- BigQuery (Spotify)

---

## 📈 EVOLUTION PATTERNS

```
TYPICAL EVOLUTION:

Stage 1: Startup
- PostgreSQL/MySQL
- Basic analytics
- Python scripts

Stage 2: Growth
- Hadoop/Spark
- Airflow for orchestration
- First data warehouse

Stage 3: Scale
- Kafka for streaming
- Real-time processing
- ML platform basics

Stage 4: Maturity
- Table formats (Iceberg/Hudi)
- Feature stores
- Metrics layer
- Self-service analytics

Stage 5: Innovation
- Open source contributions
- Custom optimizations
- Industry leadership
```

---

## 🎓 LEARNING PATH

```
BIGTECH LEARNING ORDER:

1. AIRBNB (Fundamentals)
   - Airflow - understand workflow orchestration
   - Superset - understand visualization
   - Minerva - understand metrics layer

2. LINKEDIN (Streaming Foundation)
   - Kafka - understand distributed streaming
   - Understand event-driven architecture
   - Pinot - understand real-time OLAP

3. NETFLIX (Modern Data Lake)
   - Iceberg - understand table formats
   - Understand lakehouse architecture
   - Recommendations at scale

4. UBER (Real-time + Batch)
   - Hudi - understand incremental processing
   - Understand Lambda architecture in practice
   - Geospatial data (H3)

5. SPOTIFY (Cloud-Native)
   - GCP-based architecture
   - Scio/Beam - unified batch+streaming
   - Backstage - developer experience

6. META (Massive Scale)
   - Understand extreme scale challenges
   - Presto internals
   - ML at billion-user scale


SME LEARNING ORDER (theo quy mô công ty):

1. STARTUP (07) - Bắt đầu từ đây
   - PostgreSQL basics
   - First dbt project
   - Simple dashboards

2. ECOMMERCE (08) - Retail focus
   - Multi-source integration
   - Customer segmentation
   - Inventory analytics

3. SAAS (09) - Subscription metrics
   - MRR/ARR tracking
   - Cohort analysis
   - Product analytics

4. FINTECH (10) - Compliance focus
   - Data quality critical
   - Fraud detection basics
   - Regulatory reporting

5. HEALTHCARE (11) - HIPAA compliance
   - PHI data handling
   - Clinical analytics
   - Quality measures

6. MANUFACTURING (12) - IoT + Analytics
   - Time-series data
   - OEE calculation
   - Predictive maintenance
```

---

## 💰 BUDGET COMPARISON

```
COMPANY TYPE          | MONTHLY DATA PLATFORM COST
----------------------|---------------------------
Startup (07)          | $0 - $500/month
E-commerce SME (08)   | $500 - $3,000/month
SaaS SME (09)         | $1,000 - $5,000/month
Fintech SME (10)      | $2,000 - $10,000/month
Healthcare SME (11)   | $2,000 - $8,000/month
Manufacturing SME (12)| $1,000 - $5,000/month

vs BigTech            | $1M - $100M+/month
```

---

## 🔗 LIÊN KẾT VỚI CÁC FOLDER KHÁC

- `../papers/` - Papers nghiên cứu gốc
- `../fundamentals/` - Kiến thức nền tảng
- `../tools/` - Hướng dẫn các tool SOTA

---

## 📚 ADDITIONAL RESOURCES

**Engineering Blogs:**
- Netflix Tech Blog: https://netflixtechblog.com/
- Uber Engineering: https://www.uber.com/blog/engineering/
- Airbnb Tech Blog: https://medium.com/airbnb-engineering
- LinkedIn Engineering: https://engineering.linkedin.com/
- Spotify Engineering: https://engineering.atspotify.com/
- Meta Engineering: https://engineering.fb.com/

**Conferences:**
- Data Council
- DataEngBytes
- Data+AI Summit (Databricks)
- Kafka Summit
- Flink Forward

---

*Document Version: 2.0*
*Last Updated: February 2026*
*Total: 12 case studies (6 BigTech + 6 SME)*
