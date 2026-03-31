# READ FIRST — Official Databricks Docs (Before Claude/Hilarious/ExamTopics)

Mục tiêu file này: cho bạn một đường đọc chuẩn từ nguồn chính thức trước khi vào tài liệu luyện đề.

## Cách dùng file này

1. Đọc theo thứ tự Section 1 → 5 (đúng exam guide).
2. Mỗi link chỉ đọc đúng ý chính (không cần đọc toàn bộ docs sâu ngay lần đầu).
3. Sau khi đọc xong từng section, quay lại file `Certificate/Claude/*` cùng section để luyện trap.

---

## Section 1 — Databricks Intelligence Platform

- Lakehouse overview: https://docs.databricks.com/en/lakehouse/index.html
- Databricks compute overview: https://docs.databricks.com/en/compute/index.html
- Serverless compute: https://docs.databricks.com/en/compute/serverless/index.html
- SQL Warehouse: https://docs.databricks.com/en/compute/sql-warehouse/index.html
- Cluster pools: https://docs.databricks.com/en/compute/pools.html
- Liquid clustering: https://docs.databricks.com/en/delta/clustering.html
- Predictive optimization: https://docs.databricks.com/en/optimizations/predictive-optimization.html

**Đọc xong phải trả lời được:**
- Chọn compute theo workload như thế nào?
- Liquid clustering và predictive optimization giải bài toán gì?

---

## Section 2 — Development and Ingestion

- Databricks Connect: https://docs.databricks.com/en/dev-tools/databricks-connect/index.html
- Notebooks: https://docs.databricks.com/en/notebooks/index.html
- Notebook debugger: https://docs.databricks.com/en/notebooks/debugger.html
- Auto Loader overview: https://docs.databricks.com/en/ingestion/cloud-object-storage/auto-loader/index.html
- Auto Loader options: https://docs.databricks.com/en/ingestion/cloud-object-storage/auto-loader/options.html
- Structured Streaming triggers: https://docs.databricks.com/en/structured-streaming/triggers.html
- Lakeflow Connect: https://docs.databricks.com/en/ingestion/lakeflow-connect/index.html

**Đọc xong phải trả lời được:**
- Khi nào dùng Auto Loader, khi nào dùng Lakeflow Connect?
- `availableNow` khác gì các trigger khác?

---

## Section 3 — Data Processing & Transformations

- Medallion architecture: https://docs.databricks.com/en/lakehouse/medallion.html
- Lakeflow Declarative Pipelines (overview): https://docs.databricks.com/en/ldp/index.html
- LDP expectations: https://docs.databricks.com/en/ldp/expectations.html
- LDP SQL development: https://docs.databricks.com/en/ldp/developer/sql-dev.html
- Delta MERGE INTO: https://docs.databricks.com/en/sql/language-manual/delta-merge-into.html
- `count_if` function: https://docs.databricks.com/en/sql/language-manual/functions/count_if.html
- Spark SQL functions: https://docs.databricks.com/en/sql/language-manual/functions/index.html

**Đọc xong phải trả lời được:**
- Bronze/Silver/Gold khác nhau ở mục tiêu nào?
- Khi nào dùng `MERGE`, khi nào dùng set operations (`UNION`, `UNION ALL`)?

---

## Section 4 — Productionizing Data Pipelines

- Jobs overview: https://docs.databricks.com/en/jobs/index.html
- Repair job runs: https://docs.databricks.com/en/jobs/repair-job-failures.html
- Task values: https://docs.databricks.com/en/jobs/task-values.html
- Bundles overview: https://docs.databricks.com/en/dev-tools/bundles/index.html
- Bundles settings: https://docs.databricks.com/en/dev-tools/bundles/settings.html
- CI/CD guidance: https://docs.databricks.com/en/dev-tools/ci-cd/index.html
- Spark UI guide: https://docs.databricks.com/en/optimizations/spark-ui-guide.html

**Đọc xong phải trả lời được:**
- Khi nào dùng Repair thay vì rerun toàn bộ?
- Khi nào tăng warehouse size vs scaling range?

---

## Section 5 — Data Governance & Quality

- Unity Catalog overview: https://docs.databricks.com/en/data-governance/unity-catalog/index.html
- UC privileges: https://docs.databricks.com/en/data-governance/unity-catalog/manage-privileges/privileges.html
- Manage privileges: https://docs.databricks.com/en/data-governance/unity-catalog/manage-privileges/index.html
- Managed tables: https://docs.databricks.com/en/tables/managed.html
- External tables: https://docs.databricks.com/en/tables/external.html
- Unity Catalog lineage: https://docs.databricks.com/en/data-governance/unity-catalog/data-lineage.html
- Delta Sharing overview: https://docs.databricks.com/en/delta-sharing/index.html
- Create recipient (sharing): https://docs.databricks.com/en/delta-sharing/create-recipient.html
- Lakehouse Federation: https://docs.databricks.com/en/query-federation/index.html
- System tables overview: https://docs.databricks.com/en/admin/system-tables/index.html

**Đọc xong phải trả lời được:**
- Quyền tối thiểu trong UC đi theo tầng như thế nào?
- Delta Sharing, Lineage, Federation khác nhau ở bài toán nào?

---

## Guardrails chống học sai

- Ưu tiên nguồn: Official docs/exam guide > Claude/Hilarious > ExamTopics.
- Không học theo con số cố định (giá, retention, startup time) nếu docs không khóa cứng.
- Mọi kết luận về feature availability phải kiểm tra theo cloud/region/workspace.
- ExamTopics dùng để luyện bẫy câu chữ, không thay thế product truth từ docs.

---

## Lộ trình đọc nhanh (90 phút)

- 15 phút: Section 1 docs cốt lõi
- 20 phút: Section 2 docs cốt lõi
- 20 phút: Section 3 docs cốt lõi
- 20 phút: Section 4 docs cốt lõi
- 15 phút: Section 5 docs cốt lõi

Sau đó mới quay lại `Certificate/Claude/` để làm trap drill.
