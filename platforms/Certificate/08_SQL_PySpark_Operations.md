# §3 SQL & PySpark OPERATIONS — MERGE, Aggregations, Functions

> **Exam Weight:** 31% (shared) | **Difficulty:** Trung bình
> **Exam Guide Sub-topics:** DDL/DML, Aggregations, Array functions, count_if, MERGE INTO

---

## TL;DR

Đề thi kiểm tra khả năng viết SQL/PySpark thao tác data: **MERGE INTO** (upsert), **aggregations** (groupBy + agg), **UNION**, và các hàm đặc biệt như `count_if()`, `count()`, array functions. Phải phân biệt rõ DDL (schema) vs DML (data).

---

## Nền Tảng Lý Thuyết

### DDL vs DML — 2 Loại SQL Commands

**DDL (Data Definition Language)** = thay đổi **cấu trúc** (schema):
```sql
CREATE TABLE ...    -- Tạo bảng
ALTER TABLE ...     -- Đổi schema
DROP TABLE ...      -- Xóa bảng
```

**DML (Data Manipulation Language)** = thay đổi **dữ liệu**:
```sql
INSERT INTO ...     -- Thêm rows
UPDATE ... SET ...  -- Sửa rows
DELETE FROM ...     -- Xóa rows
MERGE INTO ...      -- Upsert (Insert + Update + Delete)
SELECT ...          -- Đọc data (technically DQL)
```

### MERGE INTO — "Upsert Thông Minh"

**Bài toán:** Bạn có bảng `customers` (target) và nhận batch data mới `new_data` (source). Trong batch mới:
- Có customer đã tồn tại → cần **UPDATE** info mới.
- Có customer chưa tồn tại → cần **INSERT**.
- Có customer bị đánh dấu xóa → cần **DELETE**.

**Nếu chỉ có INSERT INTO:** Tất cả records đều INSERT → bảng có **DUPLICATE**.

**MERGE INTO giải quyết cả 3 trường hợp trong 1 câu SQL:**

```sql
MERGE INTO customers AS target
USING new_data AS source
ON target.customer_id = source.customer_id
WHEN MATCHED AND source.is_deleted = true
    THEN DELETE
WHEN MATCHED
    THEN UPDATE SET target.name = source.name, target.email = source.email
WHEN NOT MATCHED
    THEN INSERT (customer_id, name, email) VALUES (source.customer_id, source.name, source.email);
```

**Cách nhớ:** MERGE = smart merge 2 tables. INSERT = blind append.

### count(*) vs count(column) vs count_if() — PHẢI HIỂU RÕ

Đây là phần đề thi hay đánh lừa:

```text
Bảng random_values:
| col1 |
|------|
| 0    |
| 1    |
| 2    |
| NULL |
| 2    |
| 3    |
```

```sql
SELECT
    count_if(col1 > 1) AS count_a,  -- Đếm rows thỏa điều kiện
    count(*) AS count_b,             -- Đếm TẤT CẢ rows (kể cả NULL)
    count(col1) AS count_c           -- Đếm rows NON-NULL
FROM random_values;
```

**Phân tích từng hàm:**

| Hàm | Logic | Đếm rows nào | Kết quả |
|-----|-------|--------------|---------|
| `count_if(col1 > 1)` | Đếm rows có col1 > 1 | 2, 2, 3 (3 rows) | **3** |
| `count(*)` | Đếm TẤT CẢ rows | 0, 1, 2, NULL, 2, 3 (6 rows) | **6** |
| `count(col1)` | Đếm rows có col1 NOT NULL | 0, 1, 2, 2, 3 (5 rows, bỏ NULL) | **5** |

→ **Kết quả: 3, 6, 5** (ExamTopics Q75, đáp án A).

### Array Functions — Cho Nested JSON

Khi ingest JSON files, data thường chứa arrays:
```json
{"order_id": 1, "items": ["apple", "banana", "cherry"]}
{"order_id": 2, "items": ["date", "elderberry"]}
```

**Spark Array Functions** giúp thao tác arrays:

```sql
-- explode: biến mỗi element trong array thành 1 row riêng
SELECT order_id, explode(items) AS item FROM orders;
-- Output:
-- 1, apple
-- 1, banana
-- 1, cherry
-- 2, date
-- 2, elderberry

-- array_contains: check element tồn tại
SELECT * FROM orders WHERE array_contains(items, 'apple');

-- flatten: biến nested array thành flat array
-- [["a","b"],["c"]] → ["a","b","c"]
SELECT flatten(nested_array) FROM my_table;
```

> 🚨 **ExamTopics Q2:** "Array functions provide..." → **"ability to work with complex, nested data ingested from JSON files"** (đáp án D). Không phải partitions/windows hay time intervals.

---

## Cú Pháp / Keywords Cốt Lõi

### UNION vs INTERSECT vs JOIN

```sql
-- UNION: gộp 2 tables, LOẠI duplicate (set union)
SELECT * FROM march_transactions
UNION
SELECT * FROM april_transactions;
-- Giữ rows duy nhất từ CẢ HAI tables

-- UNION ALL: gộp 2 tables, GIỮ duplicate
SELECT * FROM march_transactions
UNION ALL
SELECT * FROM april_transactions;

-- INTERSECT: chỉ rows xuất hiện ở CẢ HAI tables
-- INNER JOIN: combine rows dựa trên key match
```

> 🚨 **ExamTopics Q39:** Gộp 2 tables "no duplicate records between tables" → **UNION** (đáp án B). INNER JOIN = kết nối rows, không gộp.

### PySpark Aggregation

```python
from pyspark.sql.functions import sum, avg, count, countDistinct

result = (df.groupBy("product")
    .agg(
        sum("revenue").alias("total_revenue"),
        avg("revenue").alias("avg_revenue"),
        count("*").alias("transaction_count"),
        countDistinct("customer_id").alias("unique_customers")
    ))
```

### count_if for NULL Detection

```sql
-- Đếm số NULL trong column
SELECT count_if(member_id IS NULL) FROM my_table;
-- count_if = count rows WHERE condition = true
```

> 🚨 **ExamTopics Q8:** "Count null values" → **`count_if(member_id IS NULL)`** (đáp án C).
> - `count(member_id)` = đếm NON-NULL → SAI.

### JDBC for External Databases

```python
# Read from SQLite/PostgreSQL/MySQL via JDBC
df = spark.read \
    .format("jdbc") \    # ← hoặc "org.apache.spark.sql.jdbc"
    .option("url", "jdbc:sqlite:/path/to/db") \
    .option("dbtable", "customers") \
    .load()
```

> 🚨 **ExamTopics Q21:** Format cho SQLite → **`org.apache.spark.sql.jdbc`** (đáp án A).

---

## Cạm Bẫy Trong Đề Thi (Exam Traps)

### Trap 1: MERGE vs INSERT — khi nào dùng gì
- **Đáp án nhiễu:** "MERGE khi source is not Delta" → **SAI**. MERGE works on any source.
- **Đúng:** MERGE = khi cần **no duplicate records** (ExamTopics Q20, đáp án D).
- **Logic:** INSERT = blind append (duplicates possible). MERGE = check existence first.

### Trap 2: count(*) bao gồm NULL
- **Đáp án nhiễu:** `count(*) = count(col)` → **SAI** khi có NULL.
- **Đúng:** `count(*)` đếm ALL rows (kể cả NULL). `count(col)` bỏ NULL.
- **Cách nhớ:** `*` = everything. `col` = non-null values of that specific column.

### Trap 3: UNION vs UNION ALL
- Đề hỏi "without duplicate records" → **UNION** (automatically deduplicates).
- **UNION ALL** = giữ tất cả, kể cả duplicates.

---

## 🔗 Tham Khảo

- **Deep Dive:** [[01_Databricks#APPENDIX C: INTERVIEW QUESTIONS|01_Databricks.md — Appendix C]]
- **MERGE:** https://docs.databricks.com/en/sql/language-manual/delta-merge-into.html
- **SQL Functions:** https://docs.databricks.com/en/sql/language-manual/functions/index.html
