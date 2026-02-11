# 🏗️ Project 04: Self-Service Data Platform MVP

> Build một data platform hoàn chỉnh với data catalog, orchestration, và visualization

---

## 📋 Project Overview

**Difficulty:** Advanced
**Time Estimate:** 6-8 weeks
**Skills Learned:** Data Platform Architecture, Data Catalog, Governance, Self-Service Analytics

### Mục Tiêu

Build một self-service data platform cho team 10-50 người, bao gồm ingestion, storage, transformation, catalog, và visualization.

```mermaid
graph TD
    subgraph Sources[" "]
        Sources_title["📡 DATA SOURCES"]
        style Sources_title fill:none,stroke:none,color:#333,font-weight:bold
        S1[("PostgreSQL\nApp DB")]
        S2["REST APIs"]
        S3["CSV/JSON Files"]
    end

    subgraph Ingestion[" "]
        Ingestion_title["📥 INGESTION"]
        style Ingestion_title fill:none,stroke:none,color:#333,font-weight:bold
        AI["Airbyte\nEL(T)"]
    end

    subgraph Orchestration[" "]
        Orchestration_title["⏰ ORCHESTRATION"]
        style Orchestration_title fill:none,stroke:none,color:#333,font-weight:bold
        AF["Apache Airflow\nDAGs & Scheduling"]
    end

    subgraph Storage[" "]
        Storage_title["🗄️ STORAGE"]
        style Storage_title fill:none,stroke:none,color:#333,font-weight:bold
        PG[("PostgreSQL\nWarehouse")]
        MN[("MinIO\nS3-compatible")]
    end

    subgraph Transform[" "]
        Transform_title["✨ TRANSFORM"]
        style Transform_title fill:none,stroke:none,color:#333,font-weight:bold
        DBT["dbt\nSQL Models"]
    end

    subgraph Catalog[" "]
        Catalog_title["📚 CATALOG"]
        style Catalog_title fill:none,stroke:none,color:#333,font-weight:bold
        DH["DataHub\nDiscovery & Lineage"]
    end

    subgraph Viz[" "]
        Viz_title["📊 VISUALIZATION"]
        style Viz_title fill:none,stroke:none,color:#333,font-weight:bold
        SS["Apache Superset\nDashboards"]
    end

    S1 & S2 & S3 --> AI
    AI --> PG & MN
    AF -.->|orchestrate| AI
    AF -.->|orchestrate| DBT
    PG --> DBT --> PG
    PG --> DH
    PG --> SS
    DBT -.->|metadata| DH

    style AF fill:#017cee,color:#fff
    style DH fill:#1890ff,color:#fff
    style SS fill:#20a7c9,color:#fff
    style PG fill:#336791,color:#fff
```

---

## 🛠️ Tech Stack

| Component | Tool | Lý Do Chọn |
|-----------|------|-------------|
| Ingestion | Airbyte | Open-source, 300+ connectors, UI dễ dùng |
| Warehouse | PostgreSQL | Free, reliable, đủ cho MVP |
| Object Storage | MinIO | S3-compatible, self-hosted |
| Transform | dbt | SQL-first, testing, documentation |
| Orchestration | Airflow | Industry standard, mature ecosystem |
| Data Catalog | DataHub | LinkedIn created, rich features, Docker quickstart |
| Visualization | Apache Superset | Airbnb created, powerful, self-hosted |

---

## 📂 Project Structure

```
data-platform-mvp/
├── docker-compose.yml          # Toàn bộ infrastructure
├── .env.example
├── README.md
│
├── airflow/
│   ├── dags/
│   │   ├── ingestion_dag.py
│   │   ├── dbt_dag.py
│   │   └── quality_dag.py
│   └── plugins/
│
├── dbt_project/
│   ├── dbt_project.yml
│   ├── profiles.yml
│   └── models/
│       ├── staging/
│       ├── intermediate/
│       └── marts/
│
├── superset/
│   └── dashboards/
│
├── datahub/
│   └── recipes/              # Ingestion recipes cho DataHub
│
├── scripts/
│   ├── setup.sh
│   └── seed_data.py
│
└── docs/
    └── architecture.md
```

---

## 🚀 Step-by-Step Implementation

### Step 1: Core Infrastructure

**docker-compose.yml:**
```yaml
version: '3.8'

services:
  # ========== DATABASE ==========
  postgres:
    image: postgres:15
    environment:
      POSTGRES_USER: platform
      POSTGRES_PASSWORD: platform123
      POSTGRES_DB: data_warehouse
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./scripts/init.sql:/docker-entrypoint-initdb.d/init.sql
    ports:
      - "5432:5432"

  # ========== OBJECT STORAGE ==========
  minio:
    image: minio/minio
    environment:
      MINIO_ROOT_USER: minioadmin
      MINIO_ROOT_PASSWORD: minioadmin
    command: server /data --console-address ":9001"
    ports:
      - "9000:9000"
      - "9001:9001"
    volumes:
      - minio_data:/data

  # ========== ORCHESTRATION ==========
  airflow:
    image: apache/airflow:2.8.0
    environment:
      AIRFLOW__CORE__EXECUTOR: LocalExecutor
      AIRFLOW__DATABASE__SQL_ALCHEMY_CONN: postgresql+psycopg2://platform:platform123@postgres/airflow_db
    volumes:
      - ./airflow/dags:/opt/airflow/dags
    ports:
      - "8080:8080"
    depends_on:
      - postgres

  # ========== VISUALIZATION ==========
  superset:
    image: apache/superset:latest
    ports:
      - "8088:8088"
    depends_on:
      - postgres

volumes:
  postgres_data:
  minio_data:
```

> 💡 **DataHub** có Docker Compose riêng — follow [DataHub Docker Quickstart](https://datahubproject.io/docs/quickstart) để chạy song song.

### Step 2: Data Ingestion với Airbyte

```python
# scripts/seed_data.py
"""Generate sample e-commerce data into PostgreSQL."""
import psycopg2
import random
from datetime import datetime, timedelta
from faker import Faker

fake = Faker()

def generate_customers(cursor, n=1000):
    for _ in range(n):
        cursor.execute("""
            INSERT INTO raw.customers (name, email, country, created_at)
            VALUES (%s, %s, %s, %s)
        """, (
            fake.name(),
            fake.email(),
            fake.country_code(),
            fake.date_time_between(start_date='-2y')
        ))

def generate_orders(cursor, n=5000):
    for _ in range(n):
        cursor.execute("""
            INSERT INTO raw.orders (customer_id, amount, status, order_date)
            VALUES (%s, %s, %s, %s)
        """, (
            random.randint(1, 1000),
            round(random.uniform(10, 500), 2),
            random.choice(['pending', 'paid', 'shipped', 'delivered']),
            fake.date_time_between(start_date='-1y')
        ))
```

### Step 3: Transformation với dbt

**dbt_project/models/marts/revenue_summary.sql:**
```sql
WITH orders AS (
    SELECT * FROM {{ ref('stg_orders') }}
    WHERE status != 'cancelled'
),

daily_revenue AS (
    SELECT
        DATE_TRUNC('day', order_date) AS revenue_date,
        COUNT(*) AS total_orders,
        SUM(amount) AS total_revenue,
        AVG(amount) AS avg_order_value,
        COUNT(DISTINCT customer_id) AS unique_customers
    FROM orders
    GROUP BY 1
)

SELECT * FROM daily_revenue
```

### Step 4: Data Catalog với DataHub

```yaml
# datahub/recipes/postgres_recipe.yml
source:
  type: postgres
  config:
    host_port: "localhost:5432"
    database: data_warehouse
    username: platform
    password: platform123
    include_tables: true
    include_views: true
    profiling:
      enabled: true

sink:
  type: datahub-rest
  config:
    server: "http://localhost:8080"
```

### Step 5: Dashboards với Superset

Setup Superset và tạo dashboards cho:
1. **Revenue Overview** — daily/weekly/monthly trends
2. **Customer Analytics** — LTV segments, geography
3. **Operations** — pipeline health, data freshness

---

## ✅ Completion Checklist

### Phase 1: Infrastructure (Week 1-2)
- [ ] Docker Compose running (Postgres, MinIO, Airflow)
- [ ] Seed data loaded
- [ ] Airflow UI accessible at :8080

### Phase 2: Data Pipeline (Week 3-4)
- [ ] dbt project initialized
- [ ] Staging → Intermediate → Marts models
- [ ] Airflow DAG orchestrating dbt runs
- [ ] Tests passing

### Phase 3: Data Catalog (Week 5-6)
- [ ] DataHub running (Docker quickstart)
- [ ] PostgreSQL metadata ingested
- [ ] Lineage visible in DataHub UI
- [ ] Documentation added

### Phase 4: Self-Service (Week 7-8)
- [ ] Superset connected to warehouse
- [ ] 3+ dashboards created
- [ ] Team members can self-serve queries
- [ ] Data dictionary published

---

## 🎯 Learning Outcomes

**After completing:**
- Data platform architecture decisions
- Multi-tool integration (Airflow + dbt + DataHub + Superset)
- Data governance basics (catalog, lineage, documentation)
- Self-service analytics setup
- Docker multi-service orchestration

---

## 📦 Verified Resources

**GitHub Repos (tất cả có Docker support):**
- [datahub-project/datahub](https://github.com/datahub-project/datahub) — 11.5k⭐, có Docker quickstart
- [apache/airflow](https://github.com/apache/airflow) — 44k⭐, có Docker Compose chính thức
- [apache/superset](https://github.com/apache/superset) — 70k⭐, có docker-compose.yml
- [airbytehq/airbyte](https://github.com/airbytehq/airbyte) — Open-source EL(T)
- [dbt-labs/dbt-core](https://github.com/dbt-labs/dbt-core) — dbt framework

**Docker Images (verified):**
- `postgres:15` — [Docker Hub](https://hub.docker.com/_/postgres)
- `apache/airflow:2.8.0` — [Docker Hub](https://hub.docker.com/r/apache/airflow)
- `apache/superset:latest` — [Docker Hub](https://hub.docker.com/r/apache/superset)
- `minio/minio` — [Docker Hub](https://hub.docker.com/r/minio/minio)

**Datasets:**
- [dbt-labs/jaffle-shop](https://github.com/dbt-labs/jaffle-shop) — Canonical dbt demo
- [NYC TLC Trip Data](https://www.nyc.gov/site/tlc/about/tlc-trip-record-data.page) — Large-scale data

**Tham khảo:**
- [DataTalksClub/data-engineering-zoomcamp](https://github.com/DataTalksClub/data-engineering-zoomcamp) — Full DE course

---

## 🔗 Liên Kết

- [Previous: Data Warehouse](03_Data_Warehouse.md)
- [Next: ML Pipeline](05_ML_Pipeline.md)
- [Use Cases](../usecases/) — Xem architecture từ BigTech

---

*Cập nhật: February 2026*
