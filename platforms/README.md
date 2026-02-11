# ☁️ Cloud Data Platforms

> So sánh chi tiết các nền tảng dữ liệu đám mây hàng đầu

---

## 📖 Mục Lục

### Major Platforms
- [01 - Databricks](01_Databricks.md) - Lakehouse platform, Spark-native, Unity Catalog
- [02 - Snowflake](02_Snowflake.md) - Cloud data warehouse, separation of compute & storage
- [03 - BigQuery](03_BigQuery.md) - Google's serverless DWH, slot-based pricing
- [04 - Redshift](04_Redshift.md) - AWS native DWH, RA3 nodes, Spectrum
- [05 - Azure Synapse](05_Azure_Synapse.md) - Microsoft integrated analytics, Spark + SQL

---

## 🎯 Quick Comparison

| Feature | Databricks | Snowflake | BigQuery |
|---------|------------|-----------|----------|
| Architecture | Lakehouse | Cloud DWH | Serverless |
| Engine | Spark | Custom | Dremel |
| Format | Delta Lake | Proprietary | Capacitor |
| Streaming | Structured Str | Snowpipe | Streaming |
| ML | MLflow native | Snowpark | Vertex AI |
| Best for | ML + Lakehouse | SQL Analytics | Serverless |

---

## 📊 Cách Chọn Platform

**Databricks** nếu:
- Team mạnh Spark/Python
- Cần Lakehouse architecture
- ML/AI là ưu tiên
- Multi-cloud strategy

**Snowflake** nếu:
- Team mạnh SQL
- Cần dễ quản lý
- Data sharing quan trọng
- Multi-cloud strategy

**BigQuery** nếu:
- Đã dùng GCP
- Cần serverless hoàn toàn
- Batch analytics lớn
- Budget-conscious (pay per query)

**Redshift** nếu:
- Đã dùng AWS ecosystem
- Cần tight integration (S3, Glue, SageMaker)
- Predictable workloads

**Azure Synapse** nếu:
- Enterprise dùng Microsoft stack
- Cần Power BI integration
- Hybrid on-prem + cloud

---

## 🔗 Liên Kết

- [Fundamentals: Cloud Platforms](../fundamentals/10_Cloud_Platforms.md) - Cloud basics
- [Tools](../tools/) - Công cụ DE
- [Use Cases: BigTech](../usecases/) - Real-world implementations

---

*Cập nhật: February 2026*
