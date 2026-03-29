# 03. Notebooks & Debugging

## 🎯 1. TL;DR
- **Databricks Notebooks**: Môi trường code tương tác đa ngôn ngữ (Python, SQL, Scala, R) trong cùng 1 file. Rất tiện để explore data, visualize trực tiếp và debug.
- **Workflow / Điều phối**: Có thể gọi Notebook khác như một hàm hoặc chuỗi Pipeline.
- **Databricks Connect**: Cầu nối cho phép kĩ sư dùng IDE cài ở máy cá nhân (VSCode, PyCharm) nhưng code chạy và ăn tài nguyên thực tế trên Databricks Cluster.

## 🧠 2. Bản Chất Lý Thuyết (Core Concepts)

- **Đa ngôn ngữ (Magic Commands)**: Mặc định mỗi notebook có 1 ngôn ngữ. Nhưng các Cell có thể chuyển ngôn ngữ khác via `%sql`, `%python`, `%r`, `%md` (cho Markdown).
- **Variable Explorer**: Tích hợp sẵn trong UI Notebook bên phải màn hình. Cho phép xem trạng thái, giá trị, và kiểu dữ liệu của biến môi trường (variables) hiện tại mà không cần `print()`. Gỡ xác định (Debug) rất mạnh.
- **Git Folders (Repos)**: Tích hợp Git, hỗ trợ clone repository từ GitHub/GitLab... thẳng vào UI Databricks để CI/CD cơ bản (push/pull code).

## ⌨️ 3. Cú Pháp Bắt Bắc Nhớ (Code Patterns)

### Trả về PySpark DataFrame từ SQL
```python
# Chạy câu lệnh SQL bất kỳ, kết quả trả thẳng về 1 biến DataFrame trong Python
df = spark.sql("SELECT * FROM silver.users WHERE age > 18")

# Đọc TOÀN BỘ 1 bảng vào DataFrame (ngắn gọn hơn, dùng khi không cần WHERE, GROUP)
df_table = spark.table("silver.users")
```

### Gọi Notebook A từ Notebook B
```python
# Cách 1: Chạy cùng Context (biến sinh ra trong Notebook B sẽ tồn tại ở Notebook A)
%run ./Path/To/Notebook_B

# Cách 2: Chạy độc lập (Isolated) thông qua hàm của Databricks Utilities (dbutils)
# - Không chia sẻ biến (tách biệt Memory).
# - Trả về một kết quả cụ thể dưới dạng chuỗi (String) thông qua dbutils.notebook.exit()
result = dbutils.notebook.run("./Notebook_B", timeout_seconds=60, arguments={"date": "2024"})
```

## ⚖️ 4. Phân Biệt Các Khái Niệm Dễ Nhầm Lẫn

| Lệnh / Công Cụ | Phân Biệt Ngữ Cảnh Dùng |
| :--- | :--- |
| **`spark.sql()`** | Chạy một QUERY SQL (Có SELECT, WHERE...). |
| **`spark.table()`** | CHỈ ĐỂ ĐỌC trọn vẹn 1 Bảng (table) được khai báo trong Unity Catalog lên memory thành PySpark DF. Không thể truyền query DML vào đây. |
| **`%run`** | Bao trùm (Include) code. Hai thể chung biến. Khi nào cần tải chung các hàm/hằng số dùng chung (Library/Config). |
| **`dbutils.notebook.run`** | Chạy như một mắt xích độc lập trong luồng Pipeline. Tránh dính dáng memory rác với nhau. Có thể truyền tham số qua Widget. |

## ⚠️ 5. Cạm Bẫy Đề Thi & ExamTopics

**1. `spark.sql` vs `spark.table` (Q28, Q105)**
- 🚨 **ExamTopics Q28**: Lệnh nào dùng để thực thi **chuỗi truy vấn SQL** và nhận về **PySpark DataFrame**? -> Đáp án là `spark.sql()`. Các lệnh bịa đặt thường thấy trong đề: `spark.delta.table`, `spark.run_sql`.
- 🚨 **ExamTopics Q105**: Team test bằng Python muốn **chỉ load table** `sales` để kiểm tra chất lượng (không cần viết truy vấn phức tạp) -> Đáp án `spark.table("sales")`.

**2. Trả Kết Quả Giữa Các Notebook (`dbutils.notebook.exit`)**
- 🚨 **Trap**: Dùng `return "Giá_trị"` ở cuối Notebook để trả kết quả cho parent pipeline/notebook.
- **Đáp án**: Hành động `return` chỉ áp dụng bên trong function Python. Để Notebook A trả kết quả về cho Notebook B (được gọi qua `dbutils.notebook.run`), cách duy nhất là gọi hàm **`dbutils.notebook.exit("Giá_trị_trả_về")`** ở cuối file.

**3. Làm Việc Từ IDE Cục Bộ (Databricks Connect)**
- 🚨 **Trap**: Đề hỏi làm sao để "Leverage local IDE" (Sử dụng IDE ở local như VSCode/IntelliJ) mà vẫn "execute on Databricks clusters" (tính toán bằng sức mạnh của cluster đám mây).
- **Đáp án**: Bắt buộc là ** Databricks Connect**. Lưu ý nó hoạt động như "remote Spark session", code gõ ở máy bạn nhưng máy trên cloud mới là nơi thực sự tính toán.

**4. Gỡ Lỗi (Debugging / Variable Explorer) (Q177)**
- 🚨 **ExamTopics Q177**: Đề hỏi cách "view the values and types of variables without running additional code" (xem tham số mà không lặp lại lệnh `print`) hoặc một analyst truyền sai type cần track tức thì.
- **Đáp án**: Dùng **Variable Explorer** ở thanh bên phải của Notebook. (Không dùng Spark UI debug tab vì Spark UI quản lý Data/Cluster Jobs, không hiển thị biến Python local trong Notebook).

**5. Scheduling Notebooks (Q135)**
- 🚨 **ExamTopics Q135**: Có nhiều bước SQL + Python rải rác, muốn tự động chạy định kỳ.
- **Đáp án**: Nhét vào Databricks Jobs (Task workflows and job scheduling). Tránh các đáp án gài bẫy như bật version control/co-editing.

**6. Python Căn Bản (Q114)**
- 🚨 **ExamTopics Q114**: Đề cho câu hỏi về hàm, kiểm tra xem bạn có bị hổng syntax Python không. Nhớ lại chuẩn Python là `def func(x, y): return x + y`. (Đề thường gài viết thiếu dấu `:`, ghi chữ `function` thay vì `def`).

## 🌟 6. Khung Tư Duy (Deep Dives)

- **Biên giới của `%run` vs `dbutils.notebook.run()`**: 
  - `%run` gộp chung Context. Mọi biến/hàm khai báo trong notebook gốc đều xài được ở notebook hiện tại mà không cần pass argument -> Thuận tiện nhưng dễ bị shadow biến.
  - `dbutils.notebook.run()` tạo Context cô lập riêng. Cần biến gì thì phải truyền qua argument (kiểu dictionary) -> Dễ kiểm soát, phù hợp cho Production pipeline chia theo Task.
  - Tư duy đi thi: Nếu đề bài nhắc tới `parameter`/`argument` hay chạy độc lập -> `dbutils.notebook.run()`.

## 🔗 7. Official Docs Tham Khảo
- **Deep Dive:** [[01_Databricks#19. DATABRICKS CLI & SDK|01_Databricks.md — Section 19: CLI & SDK]]
- **Notebooks:** [Databricks Docs](https://docs.databricks.com/en/notebooks/index.html)
- **Databricks Connect:** [Databricks Connect](https://docs.databricks.com/en/dev-tools/databricks-connect/index.html)
