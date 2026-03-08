# 🏗️ Data Architecture Patterns

> "Tool xịn đến mấy mà không biết ráp nối vào kiến trúc tổng thể thì cũng chỉ là đống gạch rải rác."

Phần này cung cấp các **bản thiết kế tổng thể (Blueprints)** để bạn biết cách nhặt các tool từ mục `/tools` và ghép chúng thành một hệ thống dữ liệu hoàn chỉnh, tuỳ thuộc vào quy mô (scale) của công ty.

---

## 📋 Mục Lục Các Kiến Trúc

Tuỳ vào lượng dữ liệu (Data Volume), số lượng Engineer (Team Size), và mức độ phức tạp của Business, kiến trúc Data sẽ tiến hoá qua 3 giai đoạn:

1. **[Giai đoạn 1: The Startup Stack (0 - 1TB)](01_Startup_Stack.md)**
   - **Triết lý:** "Speed to market". Không tự maintain hạ tầng.
   - **Tập trung:** ELT đơn giản, Batch processing, BI Dashboard.
   - **Team:** 1-2 Data Engineers / Analytics Engineers.

2. **[Giai đoạn 2: The Scale-up Stack (1TB - 100TB)](02_Scaleup_Stack.md)**
   - **Triết lý:** "Reliability & Scalability". Tách bạch Compute và Storage.
   - **Tập trung:** Data Lakehouse, Kafka Streaming, Airflow Orchestration, Data Quality.
   - **Team:** 3-10 Data Engineers.

3. **[Giai đoạn 3: The Enterprise Stack (100TB - PB scale)](03_Enterprise_Stack.md)**
   - **Triết lý:** "Decentralization & Governance".
   - **Tập trung:** Data Mesh, Multi-catalog (Iceberg/Nessie), Data Contracts, Khả năng Read/Write cực lớn cực nhanh (Trino).
   - **Team:** Nhiều Domain Teams + 1 Central Platform Team.

---

## 💡 Nhận định từ thực tế (Senior Advice)

- **Đừng Over-engineer:** Đừng cố dựng Kafka cluster và Iceberg Lakehouse nếu công ty bạn mới chỉ có 50GB data/ngày. Dùng Postgres + Metabase là đủ. Build system đi trước business need 2 năm là một dạng lãng phí (waste).
- **Tính toán TCO (Total Cost of Ownership):** Tool Open-source rẻ tiền license nhưng cực đắt tiền maintain. Tool Managed (ví dụ Snowflake, Fivetran) đắt tiền license nhưng tiết kiệm headcount.
- **Modern Data Stack (MDS) đã hạ nhiệt:** Năm 2021-2022 người ta thích "rã" kiến trúc thành 15 tools khác nhau (Fivetran → Snowflake → dbt → Hightouch → MonteCarlo). Hãy cẩn thận, chi phí tích hợp và network egress sẽ giết chết ngân sách của bạn. Xu hướng hiện tại là "Gom lại" (Consolidation).
