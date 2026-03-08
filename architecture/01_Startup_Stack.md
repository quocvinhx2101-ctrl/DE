# The Startup Stack (0 - 1TB) 🚀

> **Context:** Công ty mới thành lập, Data Team có đúng 1-2 người. Data dưới 1TB. Yêu cầu lớn nhất: "Có số report cho sếp ngay tuần sau".

---

## 📐 Kiến trúc tổng thể

```mermaid
flowchart LR
    subgraph "Sources"
        PG[(Postgres\nApp DB)]
        API[Stripe/Hubspot]
    end

    subgraph "Ingestion (Extract & Load)"
        ELT[Fivetran / Airbyte]
    end

    subgraph "Storage & Compute"
        BQ[(BigQuery /\nSnowflake)]
    end

    subgraph "Transformation"
        DBT[dbt Cloud / Core]
    end

    subgraph "Serving"
        BI[Metabase / Superset]
    end

    PG --\u003e ELT
    API --\u003e ELT
    ELT --\u003e BQ
    BQ \u003c--\u003e DBT
    BQ --\u003e BI
```

## 🛠️ Stack Chi Tiết

| Layer | Tools Khuyên Dùng | Lý Do Dùng | Lý Do KHÔNG Dùng Kẻ Nhỏ Khác |
|-------|-------------------|------------|------------------------------|
| **Ingestion** | Fivetran, Airbyte Cloud | Setup mất 10 phút. Tự lo schema drift. | Khổ cực nếu tự viết Python scripts để kéo API (maintenance nightmare). |
| **Warehouse** | BigQuery, Snowflake | No-ops (không cần config server). Trả tiền theo query. Dữ liệu bé thì query tốn vài cent/tháng. | Đừng dựng Redshift lúc này (phải size node, tốn fix cost). |
| **Transform** | dbt (core hoặc Cloud) | Analytics Engineers tự viết SQL là xong. Tự generate docs + lineage. | Đừng viết Stored Procedures rải rác khó debug. |
| **Orchestration**| Triggers có sẵn / GitHub Actions | Pipeline đơn giản chỉ chạy 1 lần/ngày. | **Tuyệt đối không** tự dựng Airflow lúc này (quá nặng, over-engineer). |
| **BI** | Metabase | Dễ dùng cho business users. | Tableau quá đắt cho startup. |

---

## 💡 Nhận định từ thực tế (Senior Advice)

1. **Mua thời gian (Buy Time):** Ở quy mô này, lương của 1 Data Engineer đắt hơn rất nhiều so với bill của Fivetran + BigQuery. Hãy dùng Managed Services trọn gói. Mục tiêu là delivering business value, không phải khoe tech stack.
2. **Postgres Analytics:** Mở rộng hơn, nếu data chỉ có vài chục GB, bạn **thậm chí không cần Data Warehouse**. Dùng luôn 1 con Read-Replica của Postgres Production chạy Metabase là đủ. 
3. **Data Quality:** Ở giai đoạn này, error reporting qua Slack từ dbt tests (unique, not_null) là quá đủ. Đừng mua thêm tool Data Observability.
