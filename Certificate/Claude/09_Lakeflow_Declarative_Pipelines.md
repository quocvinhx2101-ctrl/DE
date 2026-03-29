# 09. Lakeflow / Delta Live Tables (DLT)

## 🎯 1. TL;DR
- **Lakeflow PIPELINES / DLT**: Bạn khai báo BẠN MUỐN GÌ (Declarative), Databricks sẽ lo TẤT CẢ công việc bù đắp lại (Checkpoint, Retry logic, tạo Cluster, vẽ sơ đồ DAG tự động).
- **Expectations**: Bộ quy tắc kiểm soát chất lượng dữ liệu (Data Quality Constraints) được nhúng thẳng vào DLT (DROP ROW, FAIL UPDATE). 

## 🧠 2. Bản Chất Sự Khác Biệt (Core Concepts)

- **Declarative vs Imperative**:
  - *Imperative (Spark truyền thống)*: Viết cách code nó chạy ra sao (tạo `readStream`, cài `trigger`, đặt `checkpointLocation`).
  - *Declarative (DLT)*: Bạn chỉ tập trung vào nghiệp vụ SQL (Tạo luồng từ đầu đến đích), DLT tự render ra luồng xử lý và tự quản lý checkpoint cho bạn.  
- **LIVE vs STREAMING LIVE**:
  - `LIVE Table` (Batch): Materialized View - tính toán lại toàn bộ dữ liệu.
  - `STREAMING LIVE Table`: Chỉ tính toán, nạp xử lý phần dữ liệu mới (Incremental) từ lần chạy trước. Tối ưu cực mạnh mẽ.
- **Constraints / Expectations**: Bộ 3 mức phạt Data "bẩn":
  1. Dữ liệu lỗi vẫn nhét vào bảng (Nhưng văng Warning log).
  2. Vứt dòng lỗi đó đi (Nhưng vẫn chạy tiếp Pipeline).
  3. Dừng luôn toàn bộ Pipeline không chạy nữa.

## ⌨️ 3. Cú Pháp Bắt Buộc Nhớ (Code Patterns)

### Streaming tự động trên DLT
Được kích hoạt bằng hàm `STREAM` lồng bên trong lúc gọi bảng `LIVE` (Bắt buộc phải ghép cả 2 chữ):

```sql
-- Lệnh SQL Khai báo
CREATE STREAMING LIVE TABLE silver_table
AS SELECT * FROM STREAM(LIVE.bronze_table)
```

### Bộ 3 Data Quality (Expectations) của DLT (BẮT BUỘC RÕ RÀNG)
```sql
-- Dòng bẩn vẫn qua, nhưng Warn -> DEFAULT (Chỉ EXPECT)
CONSTRAINT valid_id EXPECT (id IS NOT NULL)

-- Dòng bẩn bị vứt đi -> DROP ROW
CONSTRAINT valid_id EXPECT (id IS NOT NULL) ON VIOLATION DROP ROW

-- 1 Dòng bẩn làm SẬP cả Pipeline -> FAIL UPDATE
CONSTRAINT valid_id EXPECT (id IS NOT NULL) ON VIOLATION FAIL UPDATE
```

## ⚖️ 4. Phân Biệt Các Khái Niệm Dễ Nhầm Lẫn

| Mệnh Lệnh (Expectation) | Tác Động Tới Table Đích | Tác Động Tới Pipeline (Tắt/Bật) |
| :--- | :--- | :--- |
| **`EXPECT` (Warn)** | **Có lưu** dòng bẩn | Pipeline vẫn chạy bình thường |
| **`DROP ROW`** | **Xóa/Bỏ** dòng bẩn | Pipeline vẫn chạy bình thường |
| **`FAIL UPDATE`** | **Không lưu** bất cứ thứ gì | Pipeline **Crash/Dừng lập tức** |

| Tool | Bản Chất Đồng Bộ / Cập Nhật (CDC) | Mức Lưu Lịch Sử Nhớ |
| :--- | :--- | :--- |
| **APPLY CHANGES INTO** | Cơ chế CDC tích hợp sẵn trong DLT để Xử lý UPDATE/DELETE từ Source gắp lên Silver Layer. | SCD Type 1 (Mặc định: Ghi đè dòng mới nhất) / SCD Type 2 (Thêm option: Lưu 100% dòng đời cũ). |

## ⚠️ 5. Cạm Bẫy Đề Thi & ExamTopics

- 🚨 **Bẫy Tạo Pipeline (ExamTopics Q42):** Đề hỏi "Thứ DUY NHẤT bắt buộc phải có khi cấu hình ở UI để chạy một Pipeline DLT là cái gì?". 
  - Đáp án ĐÚNG LÀ **"Source Code (At least one Notebook/Library)"**. 
  - Đừng bị lừa chọn Storage Path hay Target Database (Vì Databricks có thể tự cấp managed location/DB mặc định).
- 🚨 **Bẫy Lệnh SQL DLT (ExamTopics Q34):** Để DLT biết được nó phải đọc gia tăng luồng dữ liệu liên tục thay vì Full-scan, cú pháp CẦN KIẾM là TỪ KHÓA **`STREAM()`** kết hợp **`LIVE`** (như `FROM STREAM(LIVE.my_table)`). 
  - Khai báo `STREAM()` giúp DLT hiểu phải chạy nó dưới dạng luồng xử lý incremental (chỉ nhặt dòng mới vi mô) thay vì scan chạy lại batch toàn bộ bảng.
  - Đừng để bị lừa thành `STREAM.table` hoặc `LIVE.STREAM`.
- 🚨 **Bẫy Data Quality Level / Expectations (ExamTopics Q63, Q116, Q117, Q126):** Rất hay thi vào các từ khóa xử lý vi phạm Data Quality:
  - Gặp *"Monitor data quality / No action taken"* (Chỉ ghi nhận thống kê lỗi, vẫn cho qua) -> **`EXPECT ...`**.
  - Gặp *"Filter out records"* (Lọc bỏ các bản ghi hư không cho vào target) / *"Continue processing"* (Vẫn xử lý tiếp các record khác bình thường) -> **`EXPECT ... ON VIOLATION DROP ROW`**.
  - Gặp *"Stop execution"* (Sập job, ngắt pipeline) / *"Must strictly meet"* -> **`EXPECT ... ON VIOLATION FAIL UPDATE`**.
  - **Lưu ý:** Nếu muốn biết table nào đang drop records do quality rules -> Nơi xem là **chọn trực tiếp vào dataset đó trên DLT Pipeline UI để xem data quality statistics** (Q117).
  - Tình huống code lỗi null: Dùng chuẩn SQL `location IS NOT NULL` thay vì `!= NULL`. Chọn đáp án có đủ cụm `FAIL UPDATE` thay vì chỉ có `FAIL`.

## 🌟 6. Khung Tư Duy (Deep Dives)

### Cách Hiểu Lakeflow Declarative Pipelines / DLT
- Phân biệt với mô hình truyền thống (Jobs bằng tay nối các Notebook):
  - DLT mang tính **Declarative (Khai báo)**: Bạn chỉ định "Bạn muốn Dataset B được tạo ra từ Dataset A như thế nào", DLT tự động sắp xếp sơ đồ thực thi (Dependency Graph), lên lịch, theo dõi và quản lý checkpoint giùm bạn.
  - Bạn **KHÔNG** tự orchestration chi tiết từng task retry hay quản lý checkpoint đường dẫn.

### Streaming Table vs Materialized View
- **Streaming Table (`CREATE OR REFRESH STREAMING TABLE`):**
  - Thiên về xử lý **Incremental** (nhặt dòng mới, Append-only).
  - Phù hợp nhất cho lớp Bronze/Silver Ingestion. 
  - Đọc event vào liên tục không dứt.
- **Materialized View (`CREATE OR REFRESH MATERIALIZED VIEW` - trước đây gọi là Live Table):**
  - Kết quả được tính lại theo logic khai báo, phù hợp với các thao tác cần quan sát toàn bộ dữ liệu (như Group By, Window). 
  - Phục vụ truy vấn downstream lớp Gold.

### Expectations (Data Contracts)
- `warn` (mặc định), `drop`, `fail` không chỉ là kỹ thuật xử lý rác, mà là quyết định về SLA chất lượng dữ liệu.
- Viết Data Quality rule như một phần của định nghĩa bảng, gắn chặt vào lô dữ liệu, không phải test case chạy rời bên ngoài.

## 🔗 7. Official Docs Tham Khảo

- **Khái niệm Lakeflow Pipelines:** [Delta Live Tables / Lakeflow](https://docs.databricks.com/en/lakeflow/declarative-pipelines/index.html)
- **Data Quality (Expectations):** [Manage data quality with Expectations](https://docs.databricks.com/en/lakeflow/declarative-pipelines/expectations.html)
