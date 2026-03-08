# The Scale-up Stack (1TB - 100TB) 🏗️

> **Context:** Công ty có Product-Market Fit. Cần xử lý real-time event từ app, database production đã to lền không DUMP nguyên con mỗi đêm được nữa. Data Team có 3-10 Data Engineers. Đã đến lúc phải nghiêm túc với "Tách biệt Compute & Storage".

---

## 📐 Kiến trúc tổng thể (Data Lakehouse)

```mermaid
flowchart TB
    subgraph "Sources"
        PG[(Prod DB)]
        Events[Kafka/Clickstream]
        3rd[SaaS / 3rd Party]
    end

    subgraph "Ingestion"
        Debezium[Debezium CDC]
        SparkStr[Spark / Flink Streaming]
        Airbyte[Airbyte / Fivetran]
    end

    subgraph "Data Lakehouse (Storage + Formats)"
        direction TB
        Raw[Raw Layer\nS3/GCS]
        Iceberg[Iceberg / Delta Lake\nBronze -\u003e Silver -\u003e Gold]
    end

    subgraph "Compute & Orchestration"
        SparkCompute[Spark / EMR Compute]
        DBT[dbt]
        Airflow((Airflow))
    end

    subgraph "Serving"
        Superset[Superset / Tableau]
        RevETL[Reverse ETL (Census)]
    end

    PG --\u003e Debezium --\u003e Raw
    Events --\u003e SparkStr --\u003e Raw
    3rd --\u003e Airbyte --\u003e Raw

    Raw --\u003e Iceberg
    Iceberg \u003c--\u003e SparkCompute
    Iceberg \u003c--\u003e DBT

    Airflow .-.\u003e SparkCompute
    Airflow .-.\u003e DBT
    Airflow .-.\u003e Airbyte

    Iceberg --\u003e Superset
    Iceberg --\u003e RevETL
```

## 🛠️ Stack Chi Tiết

| Layer | Tools Khuyên Dùng | Lý Do Dùng | Lý Do KHÔNG Dùng Kẻ Nhỏ Khác |
|-------|-------------------|------------|------------------------------|
| **Streaming & CDC** | Debezium + Kafka | Scan wal-logs của Database không gây tải (zero performance hit). Bắt buộc ở scale này. | Đừng query `SELECT * FROM prod WHERE updated_at` mỗi đêm nữa. Sẽ làm tạch DB. |
| **Storage Layer** | S3 / GCS | Rẻ, high durability. | Đừng chứa raw data trong Data Warehouse, giá storage sẽ cắt cổ. |
| **Table Formats** | Apache Iceberg / Delta Lake | ACID transactions trên file S3 rẻ tiền. Mang tính năng của Data Warehouse xuống Lake. | Parquet thường không có ACID, cập nhật 1 dòng phải ghi lại toàn file. |
| **Compute Engine**| Spark (EMR/Dataproc) | Handle được logic ETL tỷ dòng mà Warehouse bó tay. | Đừng chạy Pandas ở đoạn này nữa. |
| **Transform** | dbt | Trở thành standard industry layer. Governance + Docs. | |
| **Orchestration** | Apache Airflow | Scale 100+ DAGs dễ dàng. Dependency graph cực mạnh. | |

---

## 💡 Nhận định từ thực tế (Senior Advice)

1. **Khủng hoảng Cost:** Chuyển từ Startup lên Scale-up, bill cloud sẽ tăng dựng đứng. Đây là lúc Technical Debt quay lại cắn bạn. Phải lập tức áp dụng **Partitioning** chuẩn trên Iceberg/Delta (part theo date + business_id) và setup **Lifecycle policies** cho S3.
2. **Streaming vs Batch:** Chỉ làm Streaming/CDC với những table thực sự business cần real-time (ví dụ: Fraud detection, Live Dashboard). Gặp 90% còn lại, vẫn hãy chạy Batch. Đừng Streaming "cho sang", cost maintain Kafka broker và Flink chát hơn bạn tưởng.
3. **Data Quality bắt đầu vỡ:** Schema từ source sẽ thay đổi liên tục làm dbt run lỗi mỗi sáng. Lúc này phải đưa Schema Registry vào ingest layer và áp dụng CI/CD cho data pipelines.
