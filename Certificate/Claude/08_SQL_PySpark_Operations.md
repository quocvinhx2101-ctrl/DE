# §3 SQL & PySpark OPERATIONS — MERGE, Aggregations, Functions

> **Exam Weight:** 31% (shared) | **Difficulty:** Trung bình
> **Exam Guide Sub-topics:** DDL/DML, Aggregations, Array functions, count_if, MERGE INTO

---

## TL;DR

Đề thi kiểm tra khả năng viết SQL/PySpark thao tác data: **MERGE INTO** (upsert), **aggregations** (groupBy + agg), **UNION**, và các hàm đặc biệt như `count_if()`, `count()`, array functions. Phải phân biệt rõ DDL (schema) vs DML (data).

---

## Spark Core Concepts (Exam Guide Topic)

### Lazy Evaluation + Transformations vs Actions

Spark dùng **lazy evaluation**: transformations (map, filter, select, join, groupBy) KHÔNG execute ngay, chỉ build plan. Chỉ khi gọi **action** (count, collect, show, write, save) Spark mới thực sự chạy.

```text
Transformations (lazy): .filter() → .select() → .groupBy() → xây execution plan
Action (trigger):       .count() → Spark chạy toàn bộ plan ↑ cùng lúc
```

**Tại sao?** Lazy evaluation cho phép Spark optimize toàn bộ pipeline trước khi chạy (predicate pushdown, column pruning, join reordering).

### spark.sql() vs spark.table()

```python
# spark.sql() — chạy arbitrary SQL, trả về DataFrame
df = spark.sql("SELECT * FROM customers WHERE age > 25")

# spark.table() — đọc table thành DataFrame, KHÔNG chạy SQL
df = spark.table("customers")
```

> 🚨 **ExamTopics Q28:** "Run SQL query and operate on results in PySpark?" → **`spark.sql`** (đáp án C). `spark.table` chỉ đọc table, không chạy query phức tạp.

### Higher-Order Functions (Arrays without explode)

```sql
-- TRANSFORM: áp function lên mỗi element trong array
SELECT TRANSFORM(items, x -> UPPER(x)) FROM orders;
-- ["apple","banana"] → ["APPLE","BANANA"]

-- FILTER: lọc elements trong array
SELECT FILTER(scores, x -> x > 80) FROM students;
-- [90, 70, 85] → [90, 85]

-- EXISTS: check nếu BẤT KỲ element thỏa điều kiện
SELECT EXISTS(items, x -> x = 'apple') FROM orders;
-- true/false
```

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

### Advanced Aggregations: Window, Pivot, Cube, Rollup

- **Window Functions**: Tính toán trên một "cửa sổ" dữ liệu (các dòng liên quan) mà KHÔNG gộp (collapse) số lượng rows như `groupBy`. Chuyên trị: `rank()`, `dense_rank()`, `row_number()`, `lead()`, `lag()`.
  ```python
  from pyspark.sql.window import Window
  from pyspark.sql.functions import rank, col
  
  windowSpec = Window.partitionBy("department").orderBy(col("salary").desc())
  df.withColumn("rank", rank().over(windowSpec))
  ```
- **Pivot**: Chuyển đổi dữ liệu từ dạng dọc (hàng) sang ngang (cột). Biến các giá trị của 1 column thành các columns mới. Thường đi kèm `groupBy`.
  ```python
  df.groupBy("store").pivot("product_category").sum("revenue")
  ```
- **Cube & Rollup**: Mở rộng của `groupBy` để tính Subtotals (Tổng phụ).
  - `rollup("Year", "Month")`: Tính subtotals có tính phân cấp: (Year, Month) → (Year) → Grand Total.
  - `cube("Year", "Month")`: Tính MỌI tổ hợp phụ: (Year, Month) → (Year) → (Month) → Grand Total. Tính toán nặng hơn rollup.

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
    .format("jdbc") \
    # hoặc dùng class name đầy đủ nếu cần theo connector/runtime
    .option("url", "jdbc:sqlite:/path/to/db") \
    .option("dbtable", "customers") \
    .load()
```

> 🚨 **ExamTopics Q21:** Format cho SQLite → **`org.apache.spark.sql.jdbc`** (đáp án A).

---

## Khung Tư Duy Trước Khi Vào Trap

### Trình tự suy nghĩ khi gặp câu SQL/PySpark
- Đề đang hỏi thao tác dữ liệu (DML), cấu trúc (DDL), hay biểu thức hàm?
- Đề yêu cầu set semantics (`UNION`, `INTERSECT`) hay join semantics?
- Đề yêu cầu API entrypoint nào: SQL string (`spark.sql`) hay DataFrame object (`spark.table`, `groupBy/agg`)?

### Mẹo tránh sai nhanh
- Thấy từ "without duplicate" khi gộp dòng: nghĩ đến `UNION`.
- Thấy từ "upsert" hoặc tránh duplicate theo key: nghĩ đến `MERGE`.
- Thấy nested array JSON: nghĩ đến array/higher-order functions.

## Giải Thích Sâu Các Chỗ Dễ Nhầm (Đối Chiếu Docs Mới)

### 1) SQL vs DataFrame API: không phải hơn-thua, mà là đúng ngữ cảnh
- Với logic quan hệ rõ ràng, SQL giúp biểu đạt ngắn và gần business semantics.
- Với pipeline có nhiều thao tác lập trình (hàm, điều kiện động, tái sử dụng module), DataFrame API linh hoạt hơn.
- Kỹ năng quan trọng là chuyển đổi mượt giữa hai cách biểu đạt mà vẫn giữ cùng semantics.

### 2) `MERGE INTO` cần tư duy deterministic theo key
- Nếu khóa match không ổn định hoặc source có duplicate keys chưa xử lý, kết quả MERGE dễ khó đoán.
- Vì vậy, trước MERGE nên đảm bảo dữ liệu nguồn đã được chuẩn hóa khóa nghiệp vụ.
- Đây là điểm production-critical mà câu hỏi exam thường chỉ nhắc ngắn gọn.

### 3) `count_if`, `count(*)`, `count(col)` là bài kiểm tra NULL semantics
- Nắm chắc khác biệt này giúp bạn tránh sai trong cả báo cáo KPI lẫn quality checks.
- Sai lệch phổ biến là tưởng mọi `count` đều bỏ NULL, trong khi `count(*)` thì không.

### 4) Array/higher-order functions giúp tránh explode quá sớm
- Khi dùng `explode` sớm, cardinality tăng nhanh, làm join/aggregate phía sau nặng hơn.
- Với nhiều bài toán, `transform/filter/exists` trên array giữ dữ liệu gọn hơn trước khi cần flatten.

### 5) JDBC format nên viết theo cú pháp canonical trong docs
- Thực hành an toàn là dùng form canonical được docs hiện tại mô tả, và chỉ dùng alias/class-name khi chắc runtime hỗ trợ.
- Tránh học mẹo rời rạc từ blog cũ vì dễ lệch phiên bản.

---

## Cạm Bẫy Trong Đề Thi (Exam Traps) — Trích Từ ExamTopics

## Học Sâu Trước Khi Vào Trap

### 1) Mental Model: SQL/PySpark Questions thường kiểm tra semantics
- Không chỉ hỏi "viết được syntax" mà hỏi bạn hiểu semantics của câu lệnh hay không.
- Ví dụ: `UNION` vs `JOIN`, `count(*)` vs `count(col)`, `MERGE` vs `INSERT`.

### 2) Tư duy giải câu SQL nhanh
- Đọc kỹ từ khóa nghiệp vụ: "without duplicates", "upsert", "nested array", "session-only".
- Map từ khóa sang nhóm lệnh phù hợp trước, rồi mới chọn syntax cụ thể.

### 3) Null semantics là điểm hay mất điểm
- `count(*)` tính cả NULL rows.
- `count(col)` bỏ NULL.
- `count_if(condition)` đếm theo predicate.
- Chỉ cần nhầm một chi tiết NULL là sai cả câu.

### 4) SQL và PySpark nên đi cùng nhau
- Dùng SQL cho biểu thức dữ liệu rõ ràng.
- Dùng DataFrame API cho flow lập trình và tái sử dụng.
- Biết khi nào chuyển giữa hai kiểu giúp code vừa nhanh vừa dễ bảo trì.

### 5) Checklist tự kiểm
- Bạn phân biệt set operation và join operation chưa?
- Bạn nắm null/count semantics chưa?
- Bạn có template groupBy/agg chuẩn để không sai cú pháp khi thi không?


### Trap 1: MERGE INTO Xử Lý Trùng Lặp (Q20)
- **Tình huống:** Khi nào ta nên ưu tiên dùng thẻ `MERGE INTO` thay vì `INSERT INTO` mặc định?
- **Đáp án đúng:** Khi bảng đích (target table) **không được phép chứa dữ liệu trùng lặp (duplicate records)** (Đáp án D). 
- **Giải thích:** `INSERT` là append trực tiếp nên dễ tạo bản ghi trùng khi dữ liệu đã tồn tại. `MERGE` cho phép đối chiếu theo key rồi `UPDATE/INSERT` có kiểm soát (upsert).
- **Bẫy nhiễu:** Đừng chọn "Khi nguồn không phải là bảng Delta" vì nguồn của logic MERGE có thể là bất kỳ format nào được load vào View/DataFrame (CSV, Parquet...).

### Trap 2: Hợp Nhất Bảng Không Trùng Nhau (Q39)
- **Tình huống:** Kế toán có hai bảng `march_transactions` và `april_transactions`. Giám đốc cần tạo bảng mới gộp cả 2 tháng mà "without duplicate records" (không có dòng trùng lặp). Dùng câu lệnh SQL nào?
- **Đáp án chuẩn xác (Đáp án B):** Dùng từ khóa **UNION** (`SELECT * FROM march UNION SELECT * FROM april`).
- **Phân biệt:** `UNION` mặc định sẽ lọc bỏ dòng trùng. Bọn nhiễu (Inner Join, Outer Join) dùng để ghép các CỘT từ các bảng khác nhau có chung join key, không phải là ghép DÒNG toàn thư mục.

### Trap 3: Sự Khác Biệt Giữa Các Loại COUNT (Q75)
- Ví dụ cột `col`: `0, 1, 2, NULL, 2, 3`.
- `count_if(col>1)=3`, `count(*)=6`, `count(col)=5`.
- → **Đáp án A: 3 6 5**.

### Trap 4: Đặc Quyền Của Array Functions (Q2)
- **Tình huống:** Đề hỏi lợi ích lớn nhất của các hàm xử lý mảng (Array functions) trong Spark SQL là gì?
- **Đúng (Đáp án D):** **An ability to work with complex, nested data ingested from JSON files**. (Khả năng xử lý trực tiếp cấu trúc lồng nhau phức tạp sinh ra từ file JSON thay vì phải bung nén/flatten toàn bộ bảng).

### Trap 5: Cú Pháp Điều Kiện Boolean Trong Python (Q48)
- **Tình huống:** Viết code Python sao cho luồng đi vào IF khi `day_of_week` bằng 1 VÀ biến `review_period` mang giá trị `True`.
- **Đúng (Đáp án D):** `if day_of_week == 1 and review_period:`
- **Bẫy:** Không chọn `day_of_week = 1` (đây là gán giá trị, không phải so sánh). Đừng viết dư thừa `review_period == "True"` (string) hoặc `review_period == True`. Trong Python, chỉ cần `and review_period` là đủ ép kiểu boolean.

### Trap 6: Tổng Hợp Bằng DataFrame Aggregations (Q174)
- **Tình huống:** Code block đan xen các hàm sum, avg, count để tổng hợp cho 1 cột `product` từ df có sẵn. 
- **Đúng:** Bắt đầu bằng `df.groupBy("product").agg(...)`, bên trong dùng `sum/avg/count` kèm `.alias()`.

### Trap 7: INSERT / PIVOT / spark.sql f-string (Q100, Q110, Q111)
- Gói nhớ nhanh: `INSERT INTO` để append bản ghi, `PIVOT` để long → wide, `spark.sql(...)` để chạy SQL string từ Python.

### Trap 8: LEFT JOIN Output và Higher-order FILTER (Q112, Q113)
- `LEFT JOIN` giữ toàn bộ rows bảng trái; không match bên phải thì ra `NULL`.
- Higher-order đúng: `FILTER(employees, x -> x.years_exp > 5)`; thiếu lambda (`x ->`) là sai.

### Trap 9: Temporary View, LEFT JOIN Pattern, SQL UDF (Q10, Q68, Q53, Q1 - PDF bổ sung)
- **Q10:** Nếu relational object chỉ dùng tạm trong session và muốn tránh lưu physical data → chọn **Temporary View**.
- **Q68/Q1:** Với `LEFT JOIN`, luôn giữ mọi row ở bảng trái; dòng không match bên phải sẽ có `NULL` ở cột bảng phải.
- **Q53:** Tạo SQL UDF chuẩn thường theo mẫu `CREATE FUNCTION ... RETURNS ... RETURN CASE ... END`.
- **Cách nhớ nhanh:** Temporary = theo session, LEFT = giữ bên trái, FUNCTION = tái sử dụng logic.

### Trap 10: Table vs View và CREATE TABLE CSV (Q102, Q104, Q108)
- **Q102:** Nếu object phải dùng xuyên session và có lưu vật lý, chọn **Table** (không chọn temporary view).
- **Q104:** Muốn ghi vào Delta mà tránh duplicate theo key logic, chọn **`MERGE`** (upsert), không phải append mù.
- **Q108:** Tạo table từ file CSV phải chỉ rõ **`USING CSV`** trước khi khai báo options/location.
- **Cách nhớ 1 dòng:** Table = có storage, Merge = chống trùng, Using CSV = khai báo format nguồn.

---

## 🔗 Tham Khảo

- **Deep Dive:** [[01_Databricks#APPENDIX C: INTERVIEW QUESTIONS|01_Databricks.md — Appendix C]]
- **MERGE:** https://docs.databricks.com/en/sql/language-manual/delta-merge-into.html
- **SQL Functions:** https://docs.databricks.com/en/sql/language-manual/functions/index.html
