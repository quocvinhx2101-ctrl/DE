# §2 NOTEBOOKS & DEBUGGING — Dev Tools, Variable Explorer, Databricks Connect

> **Exam Weight:** 30% (shared) | **Difficulty:** Dễ
> **Exam Guide Sub-topics:** Databricks Connect, Notebook features, Built-in debugging tools

---

## TL;DR

**Databricks Notebooks** = interactive coding environment hỗ trợ multi-language (Python, SQL, Scala, R) trong cùng 1 notebook. Có built-in **Variable Explorer** để debug, và **Databricks Connect** cho local IDE development.

---

## Nền Tảng Lý Thuyết

### Notebook là gì?

Notebook = môi trường code interactive, chia thành **cells** (ô code). Mỗi cell chạy độc lập và hiển thị kết quả ngay bên dưới. Khác với script Python truyền thống (chạy từ đầu đến cuối), notebook cho phép **chạy từng bước** — rất tiện cho explore data.

**Databricks Notebook khác Jupyter thế nào?**

| Feature | Jupyter Notebook | Databricks Notebook |
|---------|-----------------|-------------------|
| Multi-language | ❌ 1 kernel = 1 ngôn ngữ | ✅ Mix Python + SQL + Scala + R trong cùng notebook |
| Collaboration | ❌ Phải share file | ✅ Real-time co-editing (như Google Docs) |
| Version Control | ❌ Manual | ✅ Built-in revision history + Git integration |
| Cluster Access | ❌ Local only | ✅ Gắn vào Spark cluster, chạy distributed |
| Variable Explorer | ⚠️ Plugin | ✅ Built-in, xem value + type at a glance |
| Scheduling | ❌ | ✅ Attach to Job Workflow, chạy tự động |

### Magic Commands — Multi-language Cells

Notebook Databricks có 1 ngôn ngữ **default** (Python, SQL, Scala, hoặc R), nhưng bạn có thể chạy ngôn ngữ khác bằng **magic commands**:

```python
# Cell mặc định là Python
df = spark.table("sales")
df.show()
```

```sql
-- Chuyển sang SQL bằng %sql
%sql
SELECT product, SUM(revenue) FROM sales GROUP BY product
```

```scala
// Chuyển sang Scala
%scala
val df = spark.table("sales")
```

```python
# Chạy shell command
%sh
ls /dbfs/mnt/data/
```

### Databricks Connect — Code ở Local, Chạy ở Cloud

**Bài toán:** DE muốn dùng VSCode/PyCharm quen thuộc (autocomplete, debug tốt hơn) nhưng data + compute nằm trên Databricks cluster.

**Giải pháp:** Databricks Connect = "cầu nối". Code viết trên laptop → compile → gửi lên cluster → chạy → trả kết quả về laptop.

```python
# Trên laptop (VSCode/PyCharm)
from databricks.connect import DatabricksSession

spark = DatabricksSession.builder.getOrCreate()
# Từ đây, spark hoạt động y hệt trên Databricks
df = spark.table("prod.silver.events")
df.filter("country = 'VN'").show()
# Code chạy trên local → compute trên remote cluster
```

### Variable Explorer — Debug Tool

Khi analyst/engineer truyền argument sai kiểu dữ liệu (ví dụ: truyền string thay vì int), notebook có **Variable Explorer** giúp xem:
- Tên biến
- Giá trị hiện tại
- Kiểu dữ liệu (int, str, DataFrame...)

→ Phát hiện bug nhanh mà không cần thêm `print()` statements.

---

## So Sánh Với Open Source

| Databricks Feature | OSS Equivalent | Khác biệt |
|-------------------|---------------|-----------|
| Notebooks | Jupyter | Multi-language, collaboration, scheduling |
| Variable Explorer | Jupyter Variable Inspector | Built-in, không cần cài plugin |
| Databricks Connect | spark-submit (remote) | IDE-native, interactive |
| `spark.sql()` | SparkSession.sql() | Chạy SQL query từ Python, trả DataFrame |
| `spark.table()` | SparkSession.table() | Load table thành DataFrame |

---

## Cú Pháp / Keywords Cốt Lõi

### spark.sql() vs spark.table() — PHẢI PHÂN BIỆT

```python
# spark.sql() — chạy BẤT KỲ SQL query, trả về DataFrame
df = spark.sql("SELECT * FROM sales WHERE amount > 100")
# Dùng khi: cần WHERE, JOIN, GROUP BY, hoặc DDL commands

# spark.table() — load ENTIRE table thành DataFrame
df = spark.table("sales")
# Dùng khi: chỉ cần load table, transform bằng PySpark API sau

# Khi nào dùng sql vs table?
# sql → khi đã biết query SQL cần chạy
# table → khi muốn dùng PySpark API (df.filter(), df.groupBy())
```

> 🚨 **ExamTopics Q28:** "Which operation to run SQL query and operate with results in PySpark?" → **`spark.sql`** (đáp án C).
> - `spark.delta.table` → SAI, không tồn tại.
> - `SELECT * FROM sales` → đó là SQL thuần, không phải PySpark operation.
> - `spark.table` → chỉ load table, không chạy query.

---

## Cạm Bẫy Trong Đề Thi (Exam Traps)

### Trap 1: Debugger vs Variable Explorer
- **Đáp án nhiễu:** "Spark UI has a debug tab that contains variables" → **SAI**. Spark UI = job/stage monitoring.
- **Đúng:** **Variable Explorer** (hoặc Debugger's variable explorer) cho phép xem biến at runtime (ExamTopics Q177).
- **Logic:** Spark UI = cluster-level monitoring. Variable Explorer = notebook-level debugging.

### Trap 2: spark.sql vs spark.table
- **Đáp án nhiễu:** `spark.delta.table` → **không tồn tại** trong PySpark API.
- **Đúng:** `spark.sql("SELECT ...")` để chạy bất kỳ SQL → trả DataFrame.
- **Logic:** `sql()` = universal (bất kỳ SQL statement), `table()` = shortcut cho `SELECT *`.

### Trap 3: Notebook cho pipeline scheduling
- **Đáp án nhiễu:** "Real-time streaming support" hay "Collaborative editing" → **SAI** cho ETL scheduling.
- **Đúng:** **Task workflows and job scheduling** (ExamTopics Q135).
- **Logic:** Question hỏi "organizing steps into structured process, run regularly" = cần scheduler, không phải real-time hay collaboration.

---

## 🔗 Tham Khảo

- **Deep Dive:** [[01_Databricks#19. DATABRICKS CLI & SDK|01_Databricks.md — Section 19: CLI & SDK]]
- **Official Docs:** https://docs.databricks.com/en/notebooks/index.html
- **Databricks Connect:** https://docs.databricks.com/en/dev-tools/databricks-connect/index.html
