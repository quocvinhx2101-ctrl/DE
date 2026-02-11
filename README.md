# Data Engineering Knowledge Base

## Comprehensive Guide to Data Engineering - From Research Papers to Production Systems

---

## 📚 GIỚI THIỆU

Repository này chứa **115 guides** kiến thức toàn diện về Data Engineering:

| Category | Files | Description |
|----------|-------|-------------|
| **papers/** | 11 | Research papers gốc |
| **fundamentals/** | 25 | Kiến thức nền tảng + SWE + Advanced |
| **tools/** | 21 | SOTA tools 2025 + IaC + GenAI |
| **usecases/** | 13 | BigTech + SME case studies |
| **projects/** | 9 | Hands-on projects (incl. debug & migration) |
| **interview/** | 6 | Interview prep + Coding test |
| **roadmap/** | 6 | Career + Certification |
| **platforms/** | 6 | Cloud platforms |
| **mindset/** | 7 | Senior/Staff DE tư duy + operations |
| **business/** | 9 | Business impact + stakeholders |

Tất cả guides được viết với:
- Code examples (Python, SQL, Bash)
- Mermaid diagrams cho architecture
- Best practices và production tips
- Real-world scenarios

---

## 📁 STRUCTURE

```
Fun/
├── README.md                        # File này (Master Index)
├── MY_LEARNING_ROADMAP.md           # Lộ trình học cá nhân
│
├── papers/                          # Research Papers (11 files)
│   ├── 01_Distributed_Systems_Papers.md
│   ├── 02_Stream_Processing_Papers.md
│   ├── 03_Data_Warehouse_Papers.md
│   ├── 04_Table_Format_Papers.md
│   ├── 05_Consensus_Papers.md
│   ├── 06_Database_Internals_Papers.md
│   ├── 07_Data_Quality_Governance_Papers.md
│   ├── 08_ML_Data_Papers.md
│   ├── 09_Query_Optimization_Papers.md
│   └── 10_Serialization_Format_Papers.md
│
├── fundamentals/                    # Core Knowledge (25 files)
│   ├── 01_Data_Modeling_Fundamentals.md
│   ├── 02_SQL_Mastery_Guide.md
│   ├── 03_Data_Warehousing_Concepts.md
│   ├── 04_Data_Lakes_Lakehouses.md
│   ├── 05_Distributed_Systems_Fundamentals.md
│   ├── 06_Data_Formats_Storage.md
│   ├── 07_Batch_vs_Streaming.md
│   ├── 08_Data_Integration_APIs.md
│   ├── 09_Security_Governance.md
│   ├── 10_Cloud_Platforms.md
│   ├── 11_Testing_CICD.md
│   ├── 12_Monitoring_Observability.md
│   ├── 13_Python_Data_Engineering.md
│   ├── 14_Git_Version_Control.md
│   ├── 15_Clean_Code_Data_Engineering.md
│   ├── 16_DE_Environment_Setup.md
│   ├── 17_Cost_Optimization.md
│   ├── 18_OOP_Design_Patterns.md
│   ├── 19_DSA_For_Data_Engineering.md
│   ├── 20_Networking_Protocols.md
│   ├── 21_Debugging_Troubleshooting.md          # NEW
│   ├── 22_Schema_Evolution_Migration.md         # NEW
│   ├── 23_Data_Mesh_Data_Products.md            # NEW
│   ├── 24_Data_Contracts.md                     # NEW
│   └── 25_Reverse_ETL.md                        # NEW
│
├── tools/                           # SOTA Tools (21 files)
│   ├── 00_SOTA_Overview_2025.md
│   ├── 01_Apache_Iceberg_Complete_Guide.md
│   ├── 02_Delta_Lake_Complete_Guide.md
│   ├── 03_Apache_Hudi_Complete_Guide.md
│   ├── 04_Apache_Flink_Complete_Guide.md
│   ├── 05_Apache_Kafka_Complete_Guide.md
│   ├── 06_Apache_Spark_Complete_Guide.md
│   ├── 07_dbt_Complete_Guide.md
│   ├── 08_Apache_Airflow_Complete_Guide.md
│   ├── 09_Prefect_Dagster_Complete_Guide.md
│   ├── 10_Data_Quality_Tools_Guide.md
│   ├── 11_Data_Catalogs_Guide.md
│   ├── 12_Polars_Complete_Guide.md
│   ├── 13_DuckDB_Complete_Guide.md
│   ├── 14_Trino_Presto_Complete_Guide.md
│   ├── 15_Fivetran_Airbyte_Guide.md
│   ├── 16_Observability_Monitoring_Tools.md
│   ├── 17_Modern_Alternatives.md
│   ├── 18_Terraform_IaC_for_DE.md               # NEW
│   └── 19_GenAI_for_DE.md                       # NEW
│
├── usecases/                        # Case Studies (13 files)
│   ├── 01-06: BigTech (Netflix, Uber, Airbnb, LinkedIn, Spotify, Meta)
│   └── 07-12: SME (Startup, Ecommerce, SaaS, Fintech, Healthcare, Manufacturing)
│
├── interview/                       # Interview Prep (6 files)
│   ├── 01_Common_Interview_Questions.md
│   ├── 02_SQL_Deep_Dive.md
│   ├── 03_System_Design.md
│   ├── 04_Behavioral_Questions.md
│   ├── 04B_Behavioral_Questions_Intern.md
│   └── 05_Coding_Test_DE.md
│
├── roadmap/                         # Career Development (6 files)
│   ├── 01_Career_Levels.md
│   ├── 02_Skills_Matrix.md
│   ├── 03_Learning_Resources.md
│   ├── 04_Certification_Guide.md         # NEW
│   └── 05_Job_Search_Strategy.md         # NEW
│
├── projects/                        # Hands-on Projects (9 files)
│   ├── 01_ETL_Pipeline.md
│   ├── 02_Realtime_Dashboard.md
│   ├── 03_Data_Warehouse.md
│   ├── 04_Data_Platform.md
│   ├── 05_ML_Pipeline.md
│   ├── 06_CDC_Pipeline.md
│   ├── 07_Debug_Production_Pipeline.md      # NEW
│   └── 08_Legacy_Migration.md               # NEW
│
├── platforms/                       # Cloud Platforms (6 files)
│   ├── 01_Databricks.md
│   ├── 02_Snowflake.md
│   ├── 03_BigQuery.md
│   ├── 04_Redshift.md
│   └── 05_Azure_Synapse.md
│
├── business/                        # Business Impact (9 files)
│   └── 01-08 + README
│
└── mindset/                         # Senior/Staff DE Mindset (7 files)
    ├── 01_Design_Patterns.md
    ├── 02_Architectural_Thinking.md
    ├── 03_Problem_Solving.md
    ├── 04_Career_Growth.md
    ├── 05_Day2_Operations.md                # NEW
    └── 06_Tech_Leadership.md                # NEW
```

---

## 🎯 LEARNING PATHS

### Path 1: Quick Start (4 tuần)

```
Week 1: SQL + Data Modeling
├── fundamentals/02_SQL_Mastery_Guide.md
└── fundamentals/01_Data_Modeling_Fundamentals.md

Week 2: Python + Modern Tools
├── fundamentals/13_Python_Data_Engineering.md
├── tools/12_Polars_Complete_Guide.md
└── tools/13_DuckDB_Complete_Guide.md

Week 3: Orchestration + Transformation
├── tools/08_Apache_Airflow_Complete_Guide.md
└── tools/07_dbt_Complete_Guide.md

Week 4: Cloud + Practice
├── platforms/ (choose 1)
└── projects/01_ETL_Pipeline.md
```

### Path 2: Comprehensive (6 tháng)

```
Xem chi tiết: MY_LEARNING_ROADMAP.md
```

---

## 📊 QUICK REFERENCE

### Core Skills
| Topic | Primary Resource | Practice |
|-------|-----------------|----------|
| SQL | [02_SQL_Mastery_Guide](fundamentals/02_SQL_Mastery_Guide.md) | [02_SQL_Deep_Dive](interview/02_SQL_Deep_Dive.md) |
| Python | [13_Python_Data_Engineering](fundamentals/13_Python_Data_Engineering.md) | [05_Coding_Test_DE](interview/05_Coding_Test_DE.md) |
| Data Modeling | [01_Data_Modeling](fundamentals/01_Data_Modeling_Fundamentals.md) | Design star schema |
| System Design | [03_System_Design](interview/03_System_Design.md) | [03_BigQuery](platforms/03_BigQuery.md) |

### Modern Data Stack
| Layer | Tool | Guide |
|-------|------|-------|
| Ingestion | Airbyte | [15_Fivetran_Airbyte](tools/15_Fivetran_Airbyte_Guide.md) |
| Transform | dbt | [07_dbt](tools/07_dbt_Complete_Guide.md) |
| Orchestration | Airflow | [08_Airflow](tools/08_Apache_Airflow_Complete_Guide.md) |
| Storage | Iceberg | [01_Iceberg](tools/01_Apache_Iceberg_Complete_Guide.md) |
| Processing | Polars/DuckDB | [12_Polars](tools/12_Polars_Complete_Guide.md), [13_DuckDB](tools/13_DuckDB_Complete_Guide.md) |
| Warehouse | Snowflake/BQ | [platforms/](platforms/) |

---

## 🏢 USE CASES

### BigTech

| Company | Highlight | Guide |
|---------|-----------|-------|
| Netflix | Created Iceberg | [01_Netflix](usecases/01_Netflix_Data_Platform.md) |
| Uber | Created Hudi | [02_Uber](usecases/02_Uber_Data_Platform.md) |
| Airbnb | Created Airflow | [03_Airbnb](usecases/03_Airbnb_Data_Platform.md) |
| LinkedIn | Created Kafka | [04_LinkedIn](usecases/04_LinkedIn_Data_Platform.md) |
| Spotify | GCP-native | [05_Spotify](usecases/05_Spotify_Data_Platform.md) |
| Meta | Created Presto | [06_Meta](usecases/06_Meta_Data_Platform.md) |

### SME

| Type | Budget | Guide |
|------|--------|-------|
| Startup | $0-500/mo | [07_Startup](usecases/07_Startup_Data_Platform.md) |
| E-commerce | $500-3K/mo | [08_Ecommerce](usecases/08_Ecommerce_SME_Platform.md) |
| SaaS | $1K-5K/mo | [09_SaaS](usecases/09_SaaS_Company_Platform.md) |
| Fintech | $2K-10K/mo | [10_Fintech](usecases/10_Fintech_SME_Platform.md) |

---

## 🎤 INTERVIEW PREPARATION

| Type | Resource |
|------|----------|
| Concepts | [01_Common_Interview_Questions](interview/01_Common_Interview_Questions.md) |
| SQL | [02_SQL_Deep_Dive](interview/02_SQL_Deep_Dive.md) |
| System Design | [03_System_Design](interview/03_System_Design.md) |
| Behavioral | [04_Behavioral_Questions](interview/04_Behavioral_Questions.md) |
| Coding Test | [05_Coding_Test_DE](interview/05_Coding_Test_DE.md) |

---

## 🗺️ CAREER DEVELOPMENT

| Goal | Resource |
|------|----------|
| Level up | [01_Career_Levels](roadmap/01_Career_Levels.md) |
| Skill gaps | [02_Skills_Matrix](roadmap/02_Skills_Matrix.md) |
| Learn | [03_Learning_Resources](roadmap/03_Learning_Resources.md) |
| Get certified | [04_Certification_Guide](roadmap/04_Certification_Guide.md) |
| Job search | [05_Job_Search_Strategy](roadmap/05_Job_Search_Strategy.md) |

---

## 📊 REPOSITORY STATS

```
TOTAL CONTENT:

├── papers/          11 files (Research papers + README)
├── fundamentals/    25 files (Core + SWE + Advanced Topics + README)
├── tools/           21 files (SOTA + IaC + GenAI + README)
├── usecases/        13 files (BigTech + SME + README)
├── interview/        6 files (Questions + Coding + Behavioral + README)
├── roadmap/          6 files (Career + Certification + README)
├── projects/         9 files (Hands-on + Debug + Migration + README)
├── platforms/        6 files (Cloud platforms + README)
├── mindset/          7 files (Senior mindset + Operations + Leadership + README)
├── business/         9 files (Business impact + README)
└── Root              2 files (README + MY_LEARNING_ROADMAP)
─────────────────────────────────────
TOTAL:               115 comprehensive guides
```

---

## 📅 VERSION INFO

- **Created:** February 2026
- **Last Updated:** February 2026
- **Total Guides:** 115 files across 10 folders
- **Format:** Markdown with Mermaid diagrams

---

*Happy Learning! 🚀*
