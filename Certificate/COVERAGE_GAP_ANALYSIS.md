# 🔬 Đánh Giá Chi Tiết Độ Phủ Tài Liệu — Mục Tiêu 45/45

> **Phương pháp:** Cross-reference từng sub-topic trong Exam Guide (Nov 2025) + từng câu trong ExamTopics 60+ questions → kiểm tra xem Claude/ và Hilarious/ cover đến đâu.

---

## Tổng Quan Đánh Giá

| Section | Exam % | Số câu ~45 | Độ phủ Claude/ | Độ phủ Hilarious/ | Độ phủ tổng | Verdict |
|---------|--------|------------|----------------|-------------------|-------------|---------|
| §1 Platform | 10% | ~5 | 🟢 90% | 🟢 95% | **🟢 93%** | Gần đủ |
| §2 Ingestion | 30% | ~14 | 🟢 88% | 🟢 92% | **🟢 90%** | Có lỗ hổng nhỏ |
| §3 Processing | 31% | ~14 | 🟢 85% | 🟢 90% | **🟢 88%** | Có lỗ hổng |
| §4 Production | 18% | ~8 | 🟡 78% | 🟡 82% | **🟡 80%** | Cần bổ sung |
| §5 Governance | 11% | ~5 | 🟢 85% | 🟢 88% | **🟢 87%** | Có lỗ hổng nhỏ |

**Độ phủ trung bình: ~87%** — Rất tốt cho 70% passing, nhưng để đạt **45/45 cần patch các lỗ hổng dưới đây.**

---

## §1 — Databricks Intelligence Platform (10%, ~5 câu)

### ✅ Đã Cover Tốt

| Topic | File cover | ExamTopics Q# | Nhận xét |
|-------|-----------|---------------|----------|
| Lakehouse Architecture (single source of truth) | Claude/01 + Hilarious/§1 | Q29 | ✅ Clear: cả 2 file giải thích tốt |
| Control Plane vs Data Plane | Claude/01 | Q74 | ✅ Covered: UC + Orchestration = Control Plane |
| Compute types (All-Purpose / Job / SQL Warehouse) | Claude/01 + Hilarious/§1,§3 | Q60 | ✅ Excellent coverage |
| Serverless (Python/SQL only) | Claude/01 + Hilarious/§1 | Q180, Q191, Q192 | ✅ Clear |
| Liquid Clustering vs Partitioning vs Z-Order | Claude/02 | Q187, Q188 | ✅ Deep coverage |
| Predictive Optimization | Claude/02 | Q187 | ✅ Covered |

### ⚠️ Lỗ Hổng — Cần Bổ Sung

| Lỗ hổng | Mức nghiêm trọng | ExamTopics Q# | Giải pháp |
|---------|-------------------|---------------|-----------|
| **Cluster Pools** — giảm startup time bằng cách giữ idle VMs sẵn sàng | 🔴 Cao | **Q127** "improve startup time for job clusters" → Answer: **Cluster Pool** | Tài liệu **KHÔNG** mention Cluster Pools ở bất kỳ file nào. Cần thêm vào Claude/01 hoặc Claude/12 |
| **SQL Endpoint Auto Stop** — tự tắt khi idle | 🟡 Trung bình | **Q90** "minimize running time of SQL endpoint" → Answer: **Auto Stop** | Chỉ mention thoáng qua trong Hilarious/§3. Cần ví dụ rõ hơn |
| **SQL Dashboard Scheduling** — refresh schedule với end date | 🟡 Trung bình | **Q55, Q86** schedule query refresh / end after date | Tài liệu thiếu chi tiết về SQL Dashboard scheduling |

---

## §2 — Development & Ingestion (30%, ~14 câu)

### ✅ Đã Cover Tốt

| Topic | File cover | ExamTopics Q# | Nhận xét |
|-------|-----------|---------------|----------|
| Auto Loader (cloudFiles, streaming) | Claude/04 + Hilarious/§2 | Q17 | ✅ Excellent |
| Directory Listing vs File Notification | Claude/04 + Hilarious/§2 | — | ✅ Clear |
| Schema evolution modes + `_rescued_data` | Claude/04 + Hilarious/§2 | — | ✅ Detailed |
| Delta Lake ACID + Transaction Log | Claude/05 | Q52 (VACUUM) | ✅ Deep |
| Time Travel (VERSION AS OF / TIMESTAMP AS OF) | Claude/05 | Q59, Q70 | ✅ Both syntax forms covered |
| VACUUM default 168 hours | Claude/05 | Q52 | ✅ Clear |
| Schema Enforcement vs Evolution | Claude/05 | — | ✅ Good |
| Structured Streaming triggers | Claude/06 | Q67 | ✅ `availableNow` vs `once` |
| Checkpointing + exactly-once | Claude/06 | — | ✅ |
| Notebooks: `%run` vs `dbutils.notebook.run()` | Claude/03 + Hilarious/§2 | — | ✅ Excellent |
| Widgets (text, dropdown, etc.) | Claude/03 + Hilarious/§2 | — | ✅ |
| Databricks Connect v2 | Claude/03 + Hilarious/§2 | — | ✅ |
| Variable Explorer | Claude/03 + Hilarious/§2 | Q177 | ✅ |
| `spark.sql()` vs `spark.table()` | Claude/03, Claude/08 | Q28 | ✅ |

### ⚠️ Lỗ Hổng — Cần Bổ Sung

| Lỗ hổng | Mức nghiêm trọng | ExamTopics Q# | Giải pháp |
|---------|-------------------|---------------|-----------|
| **`pathGlobFilter`** — filter file types trong Auto Loader | 🔴 Cao | **Q179** "parse only png files" → Answer: `.option("pathGlobFilter", "*.png")` | Claude/04 và Hilarious/§2 **KHÔNG** mention `pathGlobFilter`. Đây là option quan trọng cần thêm |
| **JDBC format** — đọc từ SQLite/external databases | 🟡 Trung bình | **Q21** "create table from SQLite db" → Answer: `org.apache.spark.sql.jdbc` | Hilarious/§5 mention Lakehouse Federation nhưng **không cover** JDBC reader format cụ thể |
| **COPY INTO vs Auto Loader** — bảng so sánh chi tiết | 🟡 Trung bình | — | Mention ở cả 2 nhưng thiếu bảng comparison trực quan |
| **Unity Catalog Volumes** — lưu trữ file unstructured | 🟡 Trung bình | — | Hilarious/§5 mention ngắn trong phần Managed vs External. Cần section riêng vì exam guide liệt kê rõ |

---

## §3 — Data Processing & Transformations (31%, ~14 câu)

### ✅ Đã Cover Tốt

| Topic | File cover | ExamTopics Q# | Nhận xét |
|-------|-----------|---------------|----------|
| Medallion Architecture (B/S/G) | Claude/07 + Hilarious/§3 | Q50, Q159, Q182 | ✅ Excellent, nhiều Q |
| MERGE INTO (upsert) | Claude/08 | Q20 | ✅ |
| `count_if` vs `count(*)` vs `count(col)` | Claude/08 | Q8, Q75 | ✅ Multiple Q covered |
| Array functions (`explode`, higher-order) | Claude/08 | Q2 | ✅ |
| Lakeflow Expectations (WARN/DROP/FAIL) | Claude/09 + Hilarious/§3 | Q63 | ✅ Deep |
| Streaming Table vs Materialized View | Claude/09 + Hilarious/§3 | Q34 | ✅ |
| STREAM() function | Claude/09 | Q34 | ✅ |
| Multi-notebook pipelines + DAG auto-resolution | Hilarious/§3 | — | ✅ |
| APPLY CHANGES / CDC / SCD Type 1&2 | Hilarious/§3 | — | ✅ |
| DLT mixed Python + SQL notebooks | Claude/09 + Hilarious/§3 | Q26, Q65 | ✅ |
| QUALIFY / ROW_NUMBER() dedup | Hilarious/§3 | — | ✅ |

### ⚠️ Lỗ Hổng — Cần Bổ Sung

| Lỗ hổng | Mức nghiêm trọng | ExamTopics Q# | Giải pháp |
|---------|-------------------|---------------|-----------|
| **UNION vs UNION ALL** — khi nào dùng từng loại | 🔴 Cao | **Q39** "combine tables without duplicates" → Answer: **UNION** (deduplicates). `UNION ALL` keeps all rows | Claude/08 **KHÔNG** cover UNION/UNION ALL/INTERSECT. Cần thêm |
| **PySpark GroupBy aggregation syntax** — `.groupBy().agg()` | 🟡 Trung bình | **Q174** "complex aggregations for product revenue" | Claude/08 covers concepts nhưng thiếu PySpark syntax `.agg(sum(), avg(), count())` |
| **Python control flow** — `==` vs `=` trong if statements | 🟢 Thấp | **Q48** "if day_of_week == 1 and review_period:" | Đây là Python cơ bản, nhưng exam vẫn hỏi. Không cần thêm vào tài liệu |
| **Spark fundamentals** — lazy evaluation, transformations vs actions, DAGs | 🟡 Trung bình | — (Exam guide lists this) | Exam guide liệt kê nhưng Claude files **KHÔNG** có section chuyên về Spark Core concepts. Hilarious/§3 cover cluster types nhưng thiếu Spark execution model |

---

## §4 — Productionizing Data Pipelines (18%, ~8 câu)

### ✅ Đã Cover Tốt

| Topic | File cover | ExamTopics Q# | Nhận xét |
|-------|-----------|---------------|----------|
| Jobs DAG / task dependencies | Claude/10 + Hilarious/§4 | Q41, Q128 | ✅ |
| Repair & Rerun | Claude/10 + Hilarious/§4 | Q175 | ✅ |
| Cron syntax | Claude/10 | Q27 | ✅ |
| Task Values (`dbutils.jobs.taskValues`) | Hilarious/§4 | — | ✅ |
| Job Cluster vs All-Purpose | Claude/10 + Hilarious/§3 | — | ✅ |
| DABs (validate/deploy/run, targets) | Claude/11 + Hilarious/§4 | Q190 | ✅ |
| Git Repos (merge outside only) | Claude/11 + Hilarious/§4 | Q35 | ✅ |
| Spark UI stages & troubleshooting | Claude/12 + Hilarious/§2 | Q181 | ✅ |

### ⚠️ Lỗ Hổng — Cần Bổ Sung

| Lỗ hổng | Mức nghiêm trọng | ExamTopics Q# | Giải pháp |
|---------|-------------------|---------------|-----------|
| **SQL Alerts** — webhook/email alerts khi query result đạt threshold | 🔴 Cao | **Q131** "notify team via webhook when NULL values reach 100" → Answer: **Alert with webhook destination** | Tài liệu **KHÔNG** cover SQL Alerts in detail. Claude/12 mentions alerts thoáng qua nhưng thiếu: alert types, destinations (email/webhook), template |
| **SQL Dashboard scheduling** — end date, refresh frequency | 🔴 Cao | **Q55, Q86, Q90** scheduling queries with end dates, Auto Stop | Tài liệu thiếu hoàn toàn phần SQL Dashboard scheduling lifecycle |
| **SQL Warehouse scaling** — size vs scaling range (concurrency) | 🟡 Trung bình | **Q130** "many users running small queries simultaneously" → Answer: **Increase scaling range** (not size) | Claude/12 mentions nhưng cần ví dụ rõ hơn: size = vertical (bigger queries), scaling range = horizontal (more concurrent users) |
| **Spark UI CPU time vs Task time** interpretation | 🟡 Trung bình | **Q178** "high CPU time vs Task time" → CPU over-utilization | Claude/12 covers OOM nhưng thiếu CPU utilization metrics cụ thể |
| **Jobs UI navigation** — Runs tab vs Tasks tab | 🟢 Thấp | **Q129** "review processing notebook in active run" → Runs tab → click active run | Đây là UI knowledge, khó cover trong docs. Nên biết qua practice |
| **Serverless Compute migration strategy** — first workload to migrate | 🟡 Trung bình | **Q192** "first step migrating to Serverless" → Answer: **Low frequency BI/SQL workloads** | Tài liệu mention Serverless benefits nhưng thiếu migration path/strategy |

---

## §5 — Data Governance & Quality (11%, ~5 câu)

### ✅ Đã Cover Tốt

| Topic | File cover | ExamTopics Q# | Nhận xét |
|-------|-----------|---------------|----------|
| Three-level namespace (catalog.schema.table) | Claude/13 + Hilarious/§5 | — | ✅ |
| Managed vs External tables (DROP behavior) | Claude/13 + Hilarious/§5 | Q64 | ✅ |
| GRANT / REVOKE / USE CATALOG + USE SCHEMA + SELECT | Claude/13 + Hilarious/§5 | Q61, Q85, Q89, Q197 | ✅ Excellent, nhiều Q |
| Delta Sharing (D2D/D2O, read-only) | Claude/14 + Hilarious/§5 | Q171, Q196, Q199 | ✅ |
| Lineage (upstream/downstream, auto-capture) | Claude/14 + Hilarious/§5 | Q198 | ✅ |
| Lakehouse Federation (Connection → Foreign Catalog) | Claude/14 + Hilarious/§5 | Q184 | ✅ |
| Audit Logs (`system.access.audit`) | Hilarious/§5 | — | ✅ |
| Data Explorer — find table owner | — | Q22 | Partially covered |

### ⚠️ Lỗ Hổng — Cần Bổ Sung

| Lỗ hổng | Mức nghiêm trọng | ExamTopics Q# | Giải pháp |
|---------|-------------------|---------------|-----------|
| **VIEW permissions** — SELECT on VIEW **and** underlying TABLE | 🔴 Cao | **Q61** "access view, what minimum permissions?" → Answer: **SELECT on VIEW + SELECT on underlying TABLE** | Claude/13 cover GRANT/REVOKE nhưng **KHÔNG** đề cập rõ rằng VIEW cần cả SELECT trên TABLE gốc |
| **Metastore location hierarchy** — nếu metastore không có location, catalog PHẢI có | 🟡 Trung bình | **Q89** "governance conditions in UC" → If metastore has no location, catalog must have managed location | Claude/13 mention metastore nhưng thiếu location inheritance/fallback logic |
| **R2 storage for egress cost reduction** | 🟡 Trung bình | **Q196** "reduce cross-cloud egress costs" → Answer: **Cloudflare R2** | Claude/14 mentions R2 briefly. Cần hiểu rõ tại sao R2 (zero egress fees) |
| **Delta Sharing — sharing identifier** | 🟢 Thấp | **Q171** "first info to request from partner for D2D sharing" → **Sharing identifier of UC metastore** | Claude/14 covers D2D nhưng thiếu chi tiết setup step "sharing identifier" |

---

## 🎯 Tổng Hợp: 12 Lỗ Hổng Cần Patch Cho 45/45

### 🔴 Critical (Có thể mất 3–4 câu nếu không fix)

| # | Topic | Câu exam liên quan | File cần update |
|---|-------|--------------------|----|
| 1 | **Cluster Pools** — giữ idle VMs, giảm startup time | Q127 | Thêm vào `Claude/01` hoặc `Claude/12` |
| 2 | **`pathGlobFilter`** — filter file types trong Auto Loader | Q179 | Thêm vào `Claude/04` |
| 3 | **UNION / UNION ALL / INTERSECT** — set operations SQL | Q39 | Thêm vào `Claude/08` |
| 4 | **SQL Alerts** — webhook/email destinations, thresholds | Q131 | Thêm vào `Claude/12` |
| 5 | **VIEW permissions** — cần SELECT trên cả VIEW + underlying TABLE | Q61 | Thêm vào `Claude/13` |

### 🟡 Important (Có thể mất 2–3 câu)

| # | Topic | Câu exam liên quan | File cần update |
|---|-------|--------------------|----|
| 6 | **SQL Dashboard scheduling** (refresh + end date + Auto Stop) | Q55, Q86, Q90 | Thêm vào `Claude/12` |
| 7 | **JDBC reader format** (`org.apache.spark.sql.jdbc`) | Q21 | Thêm vào `Claude/04` hoặc `Claude/08` |
| 8 | **Metastore → Catalog → Schema location hierarchy** | Q89 | Thêm vào `Claude/13` |
| 9 | **Spark Core concepts** (lazy eval, transformations vs actions) | Exam guide | Thêm mini-section vào `Claude/08` |
| 10 | **PySpark `.groupBy().agg()` syntax** | Q174 | Thêm vào `Claude/08` |
| 11 | **Serverless migration strategy** (first workload: SQL/BI) | Q192 | Thêm vào `Claude/01` |
| 12 | **SQL Warehouse size vs scaling range** (chi tiết hơn) | Q130 | Thêm example vào `Claude/12` |

---

## 📊 Projected Score Without Fixes vs With Fixes

```
Không patch lỗ hổng:
├── §1 Platform (5 câu): 4-5 đúng    → ~4.5/5
├── §2 Ingestion (14 câu): 12-13 đúng → ~12.5/14
├── §3 Processing (14 câu): 12-13 đúng → ~12.5/14
├── §4 Production (8 câu): 5-6 đúng   → ~5.5/8   ← WEAKEST
├── §5 Governance (5 câu): 4 đúng     → ~4/5
└── TỔNG: ~39/45 (87%) ← Pass nhưng không perfect

Sau khi patch 12 lỗ hổng:
├── §1 Platform: 5/5
├── §2 Ingestion: 13-14/14
├── §3 Processing: 13-14/14
├── §4 Production: 7-8/8     ← Cải thiện đáng kể
├── §5 Governance: 5/5
└── TỔNG: 43-45/45 (96-100%) ← TARGET
```

---

## 🚀 Action Plan: Patch 12 Lỗ Hổng

> [!IMPORTANT]
> Nếu bạn muốn, tôi có thể **trực tiếp cập nhật** các file Claude/ để thêm các section bị thiếu vào đúng vị trí. Chỉ cần confirm, tôi sẽ patch từng file một.

**Ưu tiên patch theo đúng trọng số exam:**
1. **§4 Production** (yếu nhất — 80% coverage): Fix SQL Alerts, Dashboard Scheduling, Cluster Pools → +3 câu
2. **§3 Processing**: Fix UNION/UNION ALL, PySpark agg syntax → +1-2 câu
3. **§2 Ingestion**: Fix pathGlobFilter, JDBC → +1-2 câu
4. **§5 Governance**: Fix VIEW permissions, metastore hierarchy → +1 câu
5. **§1 Platform**: Fix Serverless migration → +0-1 câu

**Thời gian cần: ~30 phút** để patch tất cả 12 lỗ hổng vào các file hiện có.
