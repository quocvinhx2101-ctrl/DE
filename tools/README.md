# 🔧 Data Engineering Tools - SOTA 2025 (21 files)

> Hướng dẫn chi tiết các công cụ State-of-the-Art trong Data Engineering

---

## 📚 Mục Lục

### Overview
| # | File | Topics |
|---|------|--------|
| 00 | [SOTA Overview 2025](00_SOTA_Overview_2025.md) | Tổng quan công nghệ DE hiện đại |

### Table Formats (Lakehouse Foundation)
| # | File | Topics |
|---|------|--------|
| 01 | [Apache Iceberg](01_Apache_Iceberg_Complete_Guide.md) | Netflix's format, đang dẫn đầu adoption |
| 02 | [Delta Lake](02_Delta_Lake_Complete_Guide.md) | Databricks's format, tích hợp Spark tốt |
| 03 | [Apache Hudi](03_Apache_Hudi_Complete_Guide.md) | Uber's format, incremental processing |

### Stream & Batch Processing
| # | File | Topics |
|---|------|--------|
| 04 | [Apache Flink](04_Apache_Flink_Complete_Guide.md) | True streaming, stateful processing |
| 05 | [Apache Kafka](05_Apache_Kafka_Complete_Guide.md) | Event streaming platform |
| 06 | [Apache Spark](06_Apache_Spark_Complete_Guide.md) | Unified analytics engine |

### Transformation & Orchestration
| # | File | Topics |
|---|------|--------|
| 07 | [dbt](07_dbt_Complete_Guide.md) | SQL-first transformation |
| 08 | [Apache Airflow](08_Apache_Airflow_Complete_Guide.md) | Workflow orchestration |
| 09 | [Prefect & Dagster](09_Prefect_Dagster_Complete_Guide.md) | Next-gen orchestrators |

### Quality & Governance
| # | File | Topics |
|---|------|--------|
| 10 | [Data Quality Tools](10_Data_Quality_Tools_Guide.md) | Great Expectations, Soda, dbt tests |
| 11 | [Data Catalogs](11_Data_Catalogs_Guide.md) | DataHub, OpenMetadata, Atlan |

### Modern & Lightweight
| # | File | Topics |
|---|------|--------|
| 12 | [Polars](12_Polars_Complete_Guide.md) | Blazing-fast DataFrame (Rust) |
| 13 | [DuckDB](13_DuckDB_Complete_Guide.md) | In-process OLAP, serverless |
| 14 | [Trino/Presto](14_Trino_Presto_Complete_Guide.md) | Distributed SQL, federated queries |
| 15 | [Fivetran/Airbyte](15_Fivetran_Airbyte_Guide.md) | EL(T) connectors |

### Observability & Alternatives
| # | File | Topics |
|---|------|--------|
| 16 | [Observability Tools](16_Observability_Monitoring_Tools.md) | **NEW** - OpenTelemetry, Monte Carlo |
| 17 | [Modern Alternatives](17_Modern_Alternatives.md) | **NEW** - Dagster, Mage.ai, SQLMesh |

### Infrastructure & AI
| # | File | Topics |
|---|------|--------|
| 18 | [Terraform & IaC](18_Terraform_IaC_for_DE.md) | **NEW** - IaC for data infra, AWS patterns, CI/CD |
| 19 | [GenAI for DE](19_GenAI_for_DE.md) | **NEW** - Text-to-SQL, AI pipelines, PII detection |

---

## 🎯 Cách Sử Dụng

**Beginner:** 00 → 06 (Spark) → 07 (dbt) → 08 (Airflow)

**Intermediate:** 05 (Kafka) → 04 (Flink) → 01-03 (Table Formats) → 12-13 (Polars/DuckDB)

**Advanced:** 09-11 (Modern Orchestration, Quality) → 14-17 (Trino, Observability, Alternatives)

---

## 🔗 Liên Kết

- [Fundamentals](../fundamentals/) - Kiến thức nền tảng
- [Papers](../papers/) - Research papers quan trọng
- [Use Cases](../usecases/) - Real-world implementations

---

*Cập nhật: February 2026*
