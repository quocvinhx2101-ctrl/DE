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

### Databricks Git Folders (Repos) — Version Control

Databricks Git Folders cho phép **clone, pull, push, commit** trực tiếp trong UI. 
⚠️ **Lưu ý quan trọng:** Khả năng thao tác Git (bao gồm merge/rebase/conflict workflows) có thể khác theo phiên bản workspace và cấu hình tính năng. Với tác vụ collaboration phức tạp, nhiều team vẫn ưu tiên xử lý trên Git provider (GitHub, GitLab, v.v.) để review/approval nhất quán.

### Variable Explorer — Debug Tool

Khi analyst/engineer truyền argument sai kiểu dữ liệu (ví dụ: truyền string thay vì int), notebook có **Variable Explorer** giúp xem:
- Tên biến
- Giá trị hiện tại
- Kiểu dữ liệu (int, str, DataFrame...)

→ Phát hiện bug nhanh mà không cần thêm `print()` statements.

### Interactive Debugging & Logs

Ngoài Variable Explorer, Databricks cung cấp các công cụ debug cấp độ cluster ngay trong UI:
- **Spark UI:** Link trực tiếp từ cell đang chạy. Xem chi tiết Job/Stage, phát hiện data skew hoặc tasks bị kẹt.
- **Driver & Worker Logs:** Xem `stdout/stderr` (các lệnh print, error stacktrace) và `log4j` system logs trực tiếp từ menu Compute -> Logs. Cực kỳ hữu dụng khi code crash do OOM hoặc lỗi thư viện C++ ở mức OS.

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

### Notebook Workflow: %run vs dbutils.notebook.run()

Khi muốn gọi notebook B từ notebook A:
- **`%run ./Notebook_B`**: Chạy notebook B trong CÙNG context với notebook A. (Nghĩa là A có thể xài biến, function do B tạo ra). Thích hợp để load functions dùng chung.
- **`dbutils.notebook.run("./Notebook_B", 60, {"date": "2024-01-01"})`**: Chạy notebook B như một job ĐỘC LẬP (khác context). Mất 60s timeout. Trả về kết quả qua `dbutils.notebook.exit()`.
  → Hỗ trợ truyền tham số (**Widgets**) vào notebook B thông qua dictionary `{"key": "value"}`. Dùng cho modular pipelines.

> 🚨 **ExamTopics Q28:** "Which operation to run SQL query and operate with results in PySpark?" → **`spark.sql`** (đáp án C).
> - `spark.delta.table` → SAI, không tồn tại.
> - `SELECT * FROM sales` → đó là SQL thuần, không phải PySpark operation.
> - `spark.table` → chỉ load table, không chạy query.

---

## Use Case Trong Thực Tế

### Use Case 1: Team QA test data bằng Python
- Mục tiêu: chạy test quality nhanh trên table thật.
- Cách làm: dùng `spark.table("...")` để lấy DataFrame, sau đó assert bằng PySpark.

### Use Case 2: Team analyst viết SQL, team DE kiểm tra bằng code
- Mục tiêu: tái sử dụng query SQL nhưng xử lý hậu kiểm bằng Python.
- Cách làm: dùng `spark.sql("SELECT ...")` để chạy query và tiếp tục transform bằng DataFrame API.

### Use Case 3: Debug bug khó tái hiện trong notebook
- Mục tiêu: dừng theo breakpoint và xem giá trị biến tại từng bước.
- Cách làm: dùng Interactive Debugger + Variable Explorer thay vì chỉ đọc logs.

## Ôn Nhanh 5 Phút

- `spark.sql(...)`: chạy SQL string.
- `spark.table("name")`: đọc table thành DataFrame.
- `%run`: chia sẻ biến/hàm cùng context.
- `dbutils.notebook.run(...)`: chạy notebook độc lập, trả string result.
- Interactive Debugger: dùng khi cần step-by-step.
- Job/Workflow: dùng khi cần lịch chạy định kỳ.

---

## Khung Tư Duy Trước Khi Vào Trap

### Khi đề hỏi công cụ notebook, hãy phân loại trước
- Nhóm thực thi SQL/PySpark (`spark.sql`, `spark.table`).
- Nhóm modular notebook (`%run`, `dbutils.notebook.run`).
- Nhóm debug quan sát biến (Debugger, Variable Explorer).

### Cách tránh nhầm nhanh
- Câu hỏi yêu cầu "run SQL string" → ưu tiên `spark.sql`.
- Câu hỏi yêu cầu "đọc table để xử lý tiếp" → ưu tiên `spark.table`.
- Câu hỏi yêu cầu "xem biến theo thời gian thực" → debugger/variable explorer.

## Giải Thích Sâu Các Chỗ Dễ Nhầm (Đối Chiếu Docs Mới)

### 1) Notebook không thay thế hoàn toàn codebase dạng package
- Notebook rất mạnh cho discovery, thử nghiệm, và giải thích logic theo từng bước.
- Nhưng khi đi production quy mô lớn, bạn vẫn nên đưa logic ổn định vào package/module để test và CI tốt hơn.
- Tư duy đúng: notebook cho iteration + orchestration entrypoint; library cho business logic cốt lõi.

### 2) `spark.sql()` vs `spark.table()` — hiểu theo mức độ biểu đạt
- `spark.table()` phù hợp khi mục tiêu chính là lấy table thành DataFrame để xử lý bằng API PySpark.
- `spark.sql()` phù hợp khi câu truy vấn cần biểu đạt SQL trực tiếp (join, window, subquery, CTE).
- Sai lầm hay gặp: dùng `spark.table()` rồi cố ép mọi thứ vào API khiến code dài và khó đọc hơn SQL gốc.

### 3) `%run` và `dbutils.notebook.run()` khác nhau ở boundary
- `%run` chia sẻ context; thuận tiện nhưng dễ gây phụ thuộc ẩn giữa notebook.
- `dbutils.notebook.run()` tách context rõ hơn, phù hợp orchestration theo task và truyền tham số.
- Khi codebase lớn, tách boundary rõ giúp debug và CI ổn định hơn.

### 4) Git Folders/Reops: tránh phát biểu tuyệt đối
- Tính năng Git trong Databricks thay đổi theo phiên bản workspace/feature rollout.
- Vì vậy câu khẳng định "không thể merge" cần viết theo hướng: kiểm tra khả năng cụ thể trong workspace hiện tại.
- Tinh thần học đúng theo docs: xác nhận thao tác Git hỗ trợ ở môi trường bạn đang dùng, không suy luận từ bản cũ.

### 5) Databricks Connect: coi như "remote Spark session" chứ không phải local Spark giả lập
- Code chạy trong IDE local nhưng thực thi phân tán vẫn dựa vào compute ở Databricks.
- Điều này giải thích vì sao behavior/performance phụ thuộc vào runtime remote, không chỉ máy local.
- Khi gặp khác biệt kết quả, ưu tiên kiểm tra runtime version + cluster config trước.

---

## Cạm Bẫy Trong Đề Thi (Exam Traps) — Trích Từ ExamTopics

## Học Sâu Trước Khi Vào Trap

### 1) Mental Model: Notebook = Runtime Context + Collaboration Surface
- Đừng xem notebook chỉ là nơi viết code; nó còn là container cho trạng thái runtime.
- Câu exam thường xoáy vào việc "context có được chia sẻ hay không" giữa các cách gọi notebook.

### 2) Quy trình debug hiệu quả cho người mới
- Bước 1: tái hiện lỗi trên input nhỏ.
- Bước 2: đặt breakpoint ở điểm chuyển đổi dữ liệu quan trọng.
- Bước 3: quan sát biến trung gian trước và sau transform.
- Bước 4: xác nhận kiểu dữ liệu, null pattern, và số lượng records.

### 3) `spark.sql` vs `spark.table` trong workflow thực tế
- `spark.sql` khi bạn cần sức mạnh biểu thức SQL đầy đủ.
- `spark.table` khi muốn lấy table object nhanh và xử lý bằng DataFrame API.
- Không nên dùng sai entrypoint vì dễ dẫn đến code khó đọc, khó maintain.

### 4) Modular hóa notebook mà vẫn giữ dễ kiểm soát
- `%run` phù hợp chia sẻ hàm dùng chung trong cùng context.
- `dbutils.notebook.run` phù hợp workflow tách biệt theo nhiệm vụ rõ ràng.
- Khi pipeline lớn, tách notebook theo layer/business domain để dễ debug.

### 5) Checklist tự kiểm
- Bạn có giải thích được vì sao cùng gọi notebook nhưng `%run` và `dbutils.notebook.run` cho kết quả khác nhau không?
- Bạn có workflow debug nhất quán khi output sai không?
- Bạn có phân biệt được lỗi logic data với lỗi hạ tầng run không?


### Trap 1: Debugging Code Trong Notebook (Q177)
- **Tình huống:** Một function thỉnh thoảng báo lỗi do analyst vô tình truyền sai data type. Làm sao phát hiện lỗi biến số nhanh nhất?
- **Đáp án đúng:** Dùng **Variable Explorer** (trình khám phá biến số) để theo dõi ngay tại runtime (Đáp án C).
- **Đáp án nhiễu:** "Dùng Spark UI debug tab" → SAI. Spark UI theo dõi Jobs/Stages ở mức cluster data, không có tab nào quản lý trực tiếp python variables của notebook session. Thêm `print()` thì thủ công và tốn công.

### Trap 2: spark.sql vs spark.table (Q28)
- **Tình huống:** Cần chạy một câu SQL string rồi tiếp tục xử lý kết quả bằng PySpark.
- **Đáp án đúng:** `spark.sql(...)`.
- **Cách nhớ 1 dòng:** `sql` để **chạy query**, `table` để **đọc table nguyên bản**.

### Trap 3: Notebook Lifecycle / Lập Lịch (Q135)
- **Tình huống:** Có nhiều bước SQL + Python, muốn chạy định kỳ thành pipeline chuẩn.
- **Đáp án đúng:** **Task workflows and job scheduling**.
- **Bẫy:** Collaborative editing hoặc version control không thay thế scheduler.


### Trap 4: Debug Python Notebook Theo Thời Gian Thực (Q185 - PDF bổ sung)
- **Tình huống:** Output sai, muốn đi từng bước (step-by-step) và xem giá trị biến ngay lúc chạy.
- **Đáp án đúng:** **Python Notebook Interactive Debugger**.
- **Giải thích dễ nhớ:**
  - `Cluster Logs` = nhật ký hạ tầng/job chạy xong, không phải công cụ bước từng dòng code Python.
  - `Job Dashboard` = quan sát trạng thái run, không soi biến cục bộ chi tiết.
  - `Interactive Debugger` mới là công cụ có breakpoint + variable inspection.
### Trap 5: Truy Cập Table Từ PySpark Test Flow (Q105)
- **Tình huống:** Team test bằng Python muốn đọc table `sales` để kiểm tra chất lượng.
- **Đáp án đúng:** `spark.table("sales")`.
- **Phân biệt nhanh:**
  - `spark.table("sales")` = đọc table thành DataFrame.
  - `SELECT * FROM sales` = SQL thuần, không phải lệnh PySpark trực tiếp.

### Trap 6: Python Cơ Bản Trong Notebook (Q114)
- Đề có thể cài câu syntax căn bản: function đúng phải theo form `def func(x, y): return ...`.
- Mục tiêu câu kiểu này là loại nhiễu cú pháp (`function`, thiếu `:`, dùng `print` thay `return`).

## Checklist Trước Khi Sang Chương Khác

- Phân biệt rõ `spark.sql` và `spark.table`.
- Nhớ khi nào dùng `%run` vs `dbutils.notebook.run`.
- Thuộc công cụ debug phù hợp với notebook.
- Nắm một ví dụ workflow scheduling cơ bản.

---

## 🔗 Tham Khảo

- **Deep Dive:** [[01_Databricks#19. DATABRICKS CLI & SDK|01_Databricks.md — Section 19: CLI & SDK]]
- **Official Docs:** https://docs.databricks.com/en/notebooks/index.html
- **Databricks Connect:** https://docs.databricks.com/en/dev-tools/databricks-connect/index.html
