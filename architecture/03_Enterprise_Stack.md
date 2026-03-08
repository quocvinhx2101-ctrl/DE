# The Enterprise Stack (100TB - PB scale) 🏛️

> **Context:** Công ty có 10+ Product Teams. Platform đang nghẽn cổ chai: Data Team có 20 người ngồi gỡ bug cho hàng ngàn pipelines. Data kẹt trong các "Silos" (Team A không biết xài Data Team B). Yêu cầu bây giờ là Governance, Data Contracts, và Phân tán quyền làm chủ (Decentralization).

---

## 📐 Kiến trúc tổng thể (Data Mesh & Federation)

```mermaid
flowchart TB
    subgraph "Domain A (Orders)"
        DB_A[(Prod DB)]
        CDC_A[CDC]
        Lake_A[(Domain Lake)]
        Contract_A(Data\nContracts)
    end

    subgraph "Domain B (Payments)"
        DB_B[(Prod DB)]
        Stream_B[Kafka]
        Lake_B[(Domain Lake)]
        Contract_B(Data\nContracts)
    end

    subgraph "Central Data Platform (Self-serve)"
        Direction TB
        Catalog[Enterprise Catalog\nNessie / DataHub]
        Access[RBAC & Policy\nRanger / Lake Formation]
        Federation((Trino / Presto\nQuery Engine))
    end

    subgraph "Consumers & Data Products"
        ML[ML Models]
        BI[Enterprise BI]
        App[Customer Facing Apps]
    end

    DB_A --\u003e CDC_A --\u003e Lake_A
    Lake_A -.-\u003e Contract_A
    Contract_A ==\u003e Catalog

    DB_B --\u003e Stream_B --\u003e Lake_B
    Lake_B -.-\u003e Contract_B
    Contract_B ==\u003e Catalog

    Catalog --\u003e Access
    Access --\u003e Federation

    Lake_A \u003c..\u003e Federation
    Lake_B \u003c..\u003e Federation

    Federation ==\u003e ML
    Federation ==\u003e BI
    Federation ==\u003e App
```

## 🛠️ Stack Chi Tiết

| Layer | Tools Khuyên Dùng | Lý Do Dùng | Lý Do KHÔNG Dùng Kẻ Nhỏ Khác |
|-------|-------------------|------------|------------------------------|
| **Data Products** | Domain Lakes (Iceberg/Hudi) | Các team tự chủ build & manage data của mình, expose qua "Data Contracts". | Không còn khái niệm "Đổ chung vào 1 kho (Central Data Dumps)". Tắc nghẽn! |
| **Catalog & Governance** | Nessie / DataHub / Polaris | Nessie cho phép "Git-like" branching data (commit/rollback toàn bộ lake). DataHub manage metadata + lineage across domains. | Metadata lúc này cực kì phân mảnh, nếu không có Central Catalog thì không ai tìm thấy data. |
| **Federated Engine** | Trino / Presto | Query trực tiếp Iceberg files từ Domain A và Postgres từ Domain B trong CÙNG 1 CÂU SQL mà không cần move data. | BigQuery/Snowflake tốn kém nếu copy PB data vào để JOIN. Trino (In-memory) giải bài toán này. |
| **Access Control**| Apache Ranger / AWS Lake Formation | Row-level và Column-level PII masking tập trung. | Không thể hardcode permission ở tận Application. |

---

## 💡 Nhận định từ thực tế (Senior Advice)

1. **Văn hóa quan trọng hơn Công nghệ (Tech \u003c Culture):** Đưa Data Mesh vào lúc này là vấn đề con người. Domain teams (SWEs) rất hận việc phải học Spark/Flink. Bạn phải build **Platform SDK** cực dễ (như deploy Vercel) để SWEs tự define metrics bằng dbt mà không cần quan tâm hạ tầng cluster.
2. **"Data Contract" là chốt chặn sinh tử:** Nếu schema ở source đổi màu (add/remove column), Pipeline sập. Bạn CẦN cài Data Contract checks tại gRPC layer hay CI/CD layer của Backend team. Backend đổi schema mà break Contract $\to$ Block PR của Backend team.
3. **Bài toán Multi-region & Compliance:** Enterprise dính luật GDPA/HIPAA. Lúc này kiến trúc Data Mesh toả sáng vì Data ở Germany ở yên tại Germany Lake, Data ở US ở yên US Lake, Trino query trả về report aggregate cho CEO mà ko vi phạm luật di chuyển dữ liệu.
