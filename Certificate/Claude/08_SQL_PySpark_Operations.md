# 08. SQL & PySpark Operations

## 🎯 1. TL;DR
- **Trọng tâm DML**: Đề thi hỏi rất nhiều về `MERGE INTO` (Upsert), các hàm xử lý mảng (Array Functions) khi làm việc với JSON, và cạm bẫy cực lớn ở các hàm đếm (`count`).
- **Data Skipping**: Hiểu được Lazy Evaluation của Spark để nhận biết lúc nào một biến DataFrame chỉ là Plan (kế hoạch) và lúc nào nó thực sự tiêu tốn tính toán (Action/Trigger).

## 🧠 2. Bản Chất Sự Khác Biệt (Core Concepts)

- **Lazy Evaluation**: Các lệnh làm sạch (`.filter`, `.select`) sẽ KHÔNG chạy ngay mà chỉ tạo ra sơ đồ "Execution Plan". Hệ thống đợi đến khi bạn gọi `.show()`, `.count()` hoặc `.write()` (được gọi là Action) thì Data mới thực sự xử lý.
- **MERGE INTO**: "Upsert - Thêm Kèm Sửa" dựa trên khoá (Key). Nếu bạn chèn (Insert) đè data mới xuống Target, bạn sinh ra Duplicate (Trùng lặp). Với Merge -> Nếu Target có khoá đó rồi -> Sửa (Update)/Xóa (Delete), chưa có -> Mới thêm vào (Insert). Cực kì phổ biến ở Silver layer.
- **Array Functions**: Nested Data (Mảng JSON) rất thường xuyên gặp. Trong Databricks, ta không cần code Python mệt mỏi, SQL gốc có thể làm phẳng mảng (`flatten`), phá mảng thành nhiều row (`explode`), hay chạy vòng lặp trên mảng (`TRANSFORM`).

## ⌨️ 3. Cú Pháp Bắt Buộc Nhớ (Code Patterns)

### Vua của các lệnh thao tác mảng (Array)
```sql
-- explode: Tách Array ra nhiều dòng. VD [A, B] -> Dòng 1 có A, Dòng 2 có B
SELECT order_id, explode(items) as item FROM orders;

-- flatten: Biến Mảng của Mảng thành 1 Mảng 1 chiều. VD [[A,B], [C]] -> [A,B,C]
SELECT flatten(nested_arrays_column) FROM table;
```

### Các hàm đếm thần thánh (BẮT BUỘC THUỘC LÒNG)
```sql
SELECT
  -- Đếm TẤT CẢ độ dài của bảng (Kể cả mấy dòng NULL vô giá trị)
  COUNT(*) as total_rows, 
  
  -- Đếm số dòng mà cột name KHÔNG BỊ NULL
  COUNT(name) as valid_name_rows,
  
  -- Đếm số dòng thoả mãn điều kiện (VD: Doanh thu > 100) -> Trả về số lượng (Count), không phải True/False
  COUNT_IF(revenue > 100) as high_value_orders
FROM sales;
```

## ⚖️ 4. Phân Biệt Các Khái Niệm Dễ Nhầm Lẫn

| Khái Niệm | Công Dụng Đặc Trưng |
| :--- | :--- |
| **`COUNT(*)`** | Quét qua Bảng và trả lại tổng số dòng. Bất chấp tất cả. |
| **`COUNT(col)`** | Chỉ đếm các ô KHÁC NULL của cột đó. (Thi hay bẫy lồng Null vào). |
| **`COUNT_IF(condition)`** | Đếm dòng MATCH với điều kiện truyền trong ngoặc. |
| **`UNION`** | Nối 2 bảng, tự động **XÓA trùng lặp (No duplicates)**. Chạy nặng hơn All. |
| **`UNION ALL`** | Nối 2 bảng, **GIỮ LẠI TẤT CẢ**. Chạy rất nhanh. |

## ⚠️ 5. Cạm Bẫy Đề Thi & ExamTopics

- 🚨 **Bẫy Logic Đếm Cột (VỀ CHẮC CHẮN CÓ TRONG ĐỀ - ExamTopics Q8, Q75):** Cho cột `col` có giá trị `[0, 1, 2, NULL, 2, 3]`:
  - Hỏi `COUNT(*)`? Trả lời: **6** (Đếm tất cả các dòng, kể cả dòng có Null).
  - Hỏi `COUNT(col)`? Trả lời: **5** (Chỉ đếm các dòng chứa giá trị khác Null).
  - Hỏi `COUNT_IF(col > 1)`? Trả lời: **3** (Chỉ đếm các số 2, 2, 3).
  - Hỏi đếm số lượng Null? Trả lời: **`count_if(member_id IS NULL)`**.
- 🚨 **Bẫy Khái Niệm "Merge Data" (ExamTopics Q20):** Đề bảo "Có data mới đẩy vào, nếu có ID rồi cập nhật lại (overwrite specific attributes), không có ID thì tống data đó vào (insert)". Chốt luôn Option nào chứa chữ **`MERGE INTO`**. 
  - Đề thi hay hỏi dùng thao tác gì khi bảng đích **không được phép chứa dữ liệu trùng lặp** -> Chọn **`MERGE INTO`**.
  - (Lưu ý: Không dùng `INSERT OVERWRITE` vì sửa mất lịch sử của target. `INSERT INTO` mặc định dễ tạo bản ghi trùng).
- 🚨 **Bẫy Nested Data (ExamTopics Q2):** Hỏi "Array functions provide..." -> Đáp án là **"ability to work with complex, nested data ingested from JSON files"**.
- 🚨 **Bẫy nối Data (ExamTopics Q39):** Câu hỏi nối dữ liệu từ tháng 3 và tháng 4, "ensure no duplicate records between tables" -> Chỉ định đáp án CÓ TỪ KHOÁ **`UNION`** (Tránh xa đáp án JOIN hoặc UNION ALL, INNER JOIN là kết nối rows chứ không gộp).
- 🚨 **Bẫy Thực Thi Câu Lệnh Cụ Thể (ExamTopics Q28):** "Run SQL query and operate on results in PySpark?" -> Chọn **`spark.sql`**. Lệnh `spark.table` chỉ để đọc bảng, không chạy câu truy vấn SQL phức tạp được.
- 🚨 **Bẫy Đọc JDBC/SQLite (ExamTopics Q21):** Format của JDBC connection format là **`org.apache.spark.sql.jdbc`** (đáp án A) (Viết chuẩn canonical name thay vì format string nếu có nhiều tuỳ chọn).
- 🚨 **Bẫy Cú Pháp Python (ExamTopics Q48):** Viết code Python sao cho luồng đi vào IF khi `day_of_week` bằng 1 VÀ biến `review_period` (boolean) bằng True.
  - Chọn: `if day_of_week == 1 and review_period:`
  - Bẫy: `day_of_week = 1` (gán chứ không phải so sánh). `review_period == "True"` (vô tình biến nó thành so sánh chuỗi).
- 🚨 **Bẫy Pattern Dữ Liệu Khác (ExamTopics Q100, Q110, Q111):** Nắm rõ `INSERT INTO` để append nhanh, `PIVOT` để đổi dòng thành cột (long to wide).
- 🚨 **Bẫy SQL Khác (ExamTopics Q10, Q68, Q53, Q1):** 
  - Lưu tạm data phân tích không sinh physical -> **Temporary View**.
  - `LEFT JOIN` -> Giữ mọi dòng bảng trái, bảng phải không có thì để `NULL`.
  - Phân tích cú pháp UDF -> Theo format `CREATE FUNCTION ... RETURNS ... RETURN ...`.

## 🌟 6. Khung Tư Duy (Deep Dives)

### Trình Tự Suy Nghĩ Khi Gặp Câu SQL/PySpark:
- Đề đang hỏi thao tác tác động dữ liệu (DML), cấu trúc bảng (DDL), hay biểu thức hàm (Functions)?
- Đề yêu cầu Set Semantics (`UNION`, `INTERSECT` - gộp hàng) hay Join Semantics (`JOIN` - gộp cột)?
- Đề yêu cầu API Entrypoint nào: Truyền qua chuỗi (`spark.sql("SELECT...")`) hay gọi DataFrame API trên object (`spark.table("...").groupBy(...)`)?

### Mẹo Tránh Sai Nhanh:
- Thấy từ "without duplicate" khi gộp dòng: Nghĩ đến `UNION`.
- Thấy từ "upsert" hoặc tránh duplicate theo key: Nghĩ đến `MERGE INTO`.
- Thấy nested array JSON: Nghĩ đến array/higher-order functions (`explode`, `transform`, `filter`).

### Giải Thích Sâu (Deep Dives) Các Chỗ Dễ Nhầm:
1. **SQL vs DataFrame API:** Không phải cái nào hơn, mà là ngữ cảnh.
   - Thích tính Business rõ ràng + logic có cấu trúc quan hệ -> Dùng SQL.
   - Các pipeline có nhiều thao tác lập trình động, đóng gói function tái sử dụng -> DataFrame API sạch hơn.
   - Kỹ năng quan trọng là chuyển đổi mượt 2 API này với cùng 1 execution semantics.
2. **Deterministic `MERGE INTO`:** Nếu khóa match của SOURCE không Unique (có nhiều key trùng trên nhánh merge kiện kết) thì thao tác MERGE rất nguy hiểm và có thể gây lỗi. Luôn Clean up SOURCE trước khi MERGE với schema/nghiệp vụ khóa.
3. **Array/Higher-Order Functions:** Giúp tránh `explode` (tung mảng ra nhiều dòng) quá sớm.
   - Nếu `explode` sớm, số lượng dòng (cardinality) sẽ bung mạnh, kéo thao tác groupby đằng sau chậm lại. `transform/filter` trên list array ngay trên cùng 1 row thường nhẹ nhàng hơn.

## 🔗 7. Official Docs Tham Khảo

- **MERGE:** [Delta Merge Into](https://docs.databricks.com/en/sql/language-manual/delta-merge-into.html)
- **SQL Functions:** [Databricks SQL Built-in Functions](https://docs.databricks.com/en/sql/language-manual/functions/index.html)
