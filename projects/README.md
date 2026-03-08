# 🔨 Hands-on Projects - Data Engineering (8 projects)

> Các project thực hành để build portfolio và học kỹ năng thực tế

---

## 📚 Danh Sách Projects

- [01_ETL_Pipeline.md](01_ETL_Pipeline.md) - End-to-end data pipeline (Beginner)
- [02_Realtime_Dashboard.md](02_Realtime_Dashboard.md) - Real-time analytics với Kafka (Intermediate)
- [03_Data_Warehouse.md](03_Data_Warehouse.md) - Modern DWH với dbt (Intermediate-Advanced)
- [04_Data_Platform.md](04_Data_Platform.md) - Self-service data platform MVP (Advanced)
- [05_ML_Pipeline.md](05_ML_Pipeline.md) - ML feature engineering pipeline (Advanced)
- [06_CDC_Pipeline.md](06_CDC_Pipeline.md) - CDC với Debezium + Iceberg (Advanced)
- [07_Debug_Production_Pipeline.md](07_Debug_Production_Pipeline.md) - **NEW** Debug & fix 6 bugs trong production pipeline (Intermediate-Advanced)
- [08_Legacy_Migration.md](08_Legacy_Migration.md) - **NEW** Migrate cronjob bash → Airflow/dbt zero-downtime (Intermediate-Advanced)

---

## 🗺️ Project Roadmap

| Beginner | 01. ETL Pipeline | Python, SQL, Docker |
|---|---|---|
| Airflow, Basic ETL |  |  |
| Inter- | 02. Real-time Dashboard | Kafka, Streaming |
| mediate | Redis, Flink/Faust |  |
| Inter- | 03. Data Warehouse | dbt, Data Modeling |
| Advanced | Testing, BI |  |
| Advanced | Coming Soon: |  |
| - Data Platform | Full architecture |  |
| - ML Pipeline | Feature store, MLOps |  |
| - CDC Pipeline | Debezium, Iceberg |  |

---

## 🎯 Theo Level

### Beginner Projects

**Project 1: End-to-End ETL Pipeline**
- Difficulty: ⭐⭐
- Time: 2-3 weeks
- Learn: Python, SQL, Docker, Airflow, dbt basics

**Skills practiced:**
- API data extraction
- Database operations
- Basic transformations
- Scheduling với orchestrator
- Containerization

### Intermediate Projects

**Project 2: Real-time Analytics Dashboard**
- Difficulty: ⭐⭐⭐
- Time: 3-4 weeks
- Learn: Kafka, Stream processing, Redis, Real-time viz

**Skills practiced:**
- Message queues
- Stream processing
- Windowed aggregations
- Real-time dashboards
- HyperLogLog for unique counts

**Project 3: Modern Data Warehouse**
- Difficulty: ⭐⭐⭐⭐
- Time: 4-6 weeks
- Learn: dbt, Data modeling, Snowflake/BigQuery, BI

**Skills practiced:**
- Dimensional modeling
- dbt project structure
- Incremental models
- Data quality tests
- Documentation

### Advanced Projects

**Project 4: Data Platform MVP**
- Difficulty: ⭐⭐⭐⭐⭐
- Time: 6-8 weeks
- Learn: DataHub, Superset, Full platform architecture

**Skills practiced:**
- Multi-tool integration (Airflow + dbt + DataHub + Superset)
- Data governance (catalog, lineage)
- Self-service analytics

**Project 5: ML Feature Engineering Pipeline**
- Difficulty: ⭐⭐⭐⭐
- Time: 4-6 weeks
- Learn: Metaflow, Feature Store, ML serving

**Skills practiced:**
- Feature engineering patterns
- Offline/Online feature stores
- Data quality for ML

**Project 6: CDC with Debezium + Iceberg**
- Difficulty: ⭐⭐⭐⭐
- Time: 4-6 weeks
- Learn: Debezium, Kafka Connect, Iceberg, Event-driven architecture

**Skills practiced:**
- Change Data Capture
- Event-driven pipelines
- Data lake ACID transactions

**Project 7: Debug & Fix Production Pipeline** 🔥
- Difficulty: ⭐⭐⭐⭐
- Time: 1-2 weeks
- Learn: Debugging, incident response, root cause analysis

**Skills practiced:**
- 6 planted bugs to find and fix
- Triage and communicate with stakeholders
- Write blameless postmortem
- Add monitoring and prevention

**Project 8: Legacy Migration**
- Difficulty: ⭐⭐⭐⭐
- Time: 3-4 weeks
- Learn: Migration planning, zero-downtime, backward compatibility

**Skills practiced:**
- Understand and document legacy code
- Parallel build and dual-run verification
- Cutover planning with quality gates
- Stakeholder communication

---

## 📋 Project Template

Mỗi project đều follow structure này:

```
project-name/
├── README.md           # Overview và instructions
├── docker-compose.yml  # Infrastructure
├── .env.example        # Environment variables
│
├── src/                # Application code
├── tests/              # Unit tests
├── config/             # Configuration files
│
├── docs/               # Additional documentation
└── scripts/            # Utility scripts
```

---

## 🚀 Getting Started

### Prerequisites

**Tất cả projects cần:**
- Docker và Docker Compose
- Git
- Code editor (VS Code recommended)
- Terminal/Command line

**Optional:**
- Cloud account (AWS/GCP free tier)
- Python 3.9+
- SQL client

### How to Use

1. **Chọn project** phù hợp với level
2. **Clone repo** hoặc create từ scratch
3. **Follow step-by-step** trong mỗi file
4. **Complete checklist** để track progress
5. **Add to portfolio** khi hoàn thành

---

## 🏆 Portfolio Tips

### Khi Hoàn Thành Project

**GitHub Repo:**
- Clear README với architecture diagram
- Setup instructions
- Screenshots/demos
- Lessons learned section

**Write Blog Post:**
- Problem statement
- Solution approach
- Technical decisions
- Challenges và solutions
- Code snippets

**LinkedIn Post:**
- Brief summary
- Key learnings
- Link to repo/blog

---

## 📈 Skill Matrix

Skills learned qua mỗi project:

| Skill | Proj 1 | Proj 2 | Proj 3 | Proj 4 | Proj 5 | Proj 6 |
|---|---|---|---|---|---|---|
| Python | ███ | ███ | ██ | ██ | ████ | ███ |
| SQL | ██ | █ | ████ | ███ | ██ | ██ |
| Docker | ███ | ███ | ███ | ████ | ███ | ████ |
| ETL Concepts | ████ | ██ | ████ | ███ | ██ | ████ |
| Streaming | █ | ████ | █ | █ | █ | ████ |
| Data Modeling | ██ | █ | ████ | ███ | ███ | ██ |
| Orchestration | ███ | ██ | ███ | ████ | ███ | ██ |
| Data Quality | ██ | ██ | ████ | ███ | ████ | ███ |
| Cloud | ██ | ██ | ███ | ████ | ██ | ███ |
| Governance | █ | █ | ██ | ████ | ██ | ██ |
| ML/Features | █ | █ | █ | █ | ████ | █ |
| CDC | █ | █ | █ | █ | █ | ████ |

---

## 🔗 Liên Kết

### Trong Knowledge Base

- [Fundamentals](../fundamentals/) - Kiến thức nền
- [Tools](../tools/) - Chi tiết về tools
- [Interview](../interview/) - Chuẩn bị phỏng vấn
- [Roadmap](../roadmap/) - Career path

### External Resources

**🎓 Khóa Học Miễn Phí (có labs Docker):**
- [DataTalksClub/data-engineering-zoomcamp](https://github.com/DataTalksClub/data-engineering-zoomcamp) ⭐38k — Khóa 9 tuần: Docker, Terraform, Airflow, Spark, Kafka, dbt, BigQuery. Dùng NYC Taxi data.

**🗄️ Datasets Thật (Free):**

| Dataset | Mô Tả | Link |
|---------|--------|------|
| NYC TLC Trip Data | Dữ liệu taxi NYC, Parquet, hàng GB/năm | [nyc.gov/tlc](https://www.nyc.gov/site/tlc/about/tlc-trip-record-data.page) |
| TPC-H / TPC-DS | Benchmark datasets, generate via `dbgen`/`dsdgen` | [tpc.org](https://www.tpc.org/tpch/) |
| dbt jaffle-shop | Dataset demo chính thức của dbt | [github.com/dbt-labs/jaffle-shop](https://github.com/dbt-labs/jaffle-shop) |
| GitHub Archive | Events từ GitHub, JSON, ~50GB/tháng | [gharchive.org](https://www.gharchive.org/) |
| Stack Overflow Survey | Survey hàng năm, CSV, ~100MB | [insights.stackoverflow.com/survey](https://insights.stackoverflow.com/survey) |

**🐳 Docker Images Dùng Trong Projects:**

| Image | Version | Dùng Cho |
|-------|---------|----------|
| `postgres:15` | Stable | Database cho Project 01, 03 |
| `apache/airflow:2.8.0` | LTS | Orchestration |
| `confluentinc/cp-kafka:7.5.0` | Stable | Kafka cho Project 02 |
| `confluentinc/cp-zookeeper:7.5.0` | Stable | Kafka dependency |
| `redis:7` | Stable | Hot storage Project 02 |
| `minio/minio` | Latest | S3-compatible storage |
| `grafana/grafana:latest` | Latest | Visualization |
| `debezium/connect:2.4` | Stable | CDC cho Project 06 |

**📺 YouTube Channels (Verified):**
- [Seattle Data Guy](https://www.youtube.com/@SeattleDataGuy) — DE tutorials thực tế
- [DataTalksClub](https://www.youtube.com/@DataTalksClub) — Workshops, interviews, zoomcamp recordings
- [Confluent](https://www.youtube.com/@Confluent) — Kafka deep dives chính thức
- [Databricks](https://www.youtube.com/@Databricks) — Spark, Delta Lake, Lakehouse

---

*Cập nhật: February 2026*
