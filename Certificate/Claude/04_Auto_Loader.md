# 04. Auto Loader (Incremental Ingestion)

## 🎯 1. TL;DR
- **Auto Loader (`cloudFiles`)**: Cơ chế đọc file gia tăng (incremental) liên tục/tự động từ Cloud Storage (S3/ADLS/GCS) vào hệ sinh thái Databricks.
- Phù hợp nhất cho dữ liệu lớn lên tới **hàng triệu file/folder** bằng cách tự động track những file mới đến và chỉ xử lý dữ liệu chưa xử lý.
- Công cụ chủ chốt trong kiến trúc Medallion (thường là đẩy từ source → Bronze layer).

## 🧠 2. Bản Chất Sự Khác Biệt (Core Concepts)

- Thay vì đọc đi đọc lại hay dùng trigger manual (đắt đỏ và chậm với storage lớn), **Auto Loader duy trì State** (nhờ cơ chế Checkpoint + Storage Queue) để biết file nào đã nạp.
- Chỉ cần xác định format đầu vào `cloudFiles.format` (json, csv, avro, parquet...), Spark Structured Streaming sẽ tự động stream thành real-time hoặc batch-trigger (`Trigger.Once`).
- Có khả năng **Auto Schema Inference** đi kèm **Schema Evolution** cực đỉnh: Khi nguồn bị đổi/thêm cột, Auto Loader phát hiện, cập nhật Schema và tiếp tục chạy mà không bị hỏng pipeline.

## ⌨️ 3. Cú Pháp Bắt Buộc Nhớ (Code Patterns)

### Cú pháp cốt lõi nhất (Khai báo `format("cloudFiles")`):
```python
df = (spark.readStream
  .format("cloudFiles")           # PHẢI LÀ cloudFiles, KHÔNG PHẢI csv/json
  .option("cloudFiles.format", "json")  # Định dạng của FILE GỐC (VD: json)
  .option("cloudFiles.schemaLocation", "/path/to/schema_checkpoint") # Nơi lưu schema
  .load("/path/to/source/data")   # Thư mục gốc chứa file
)

(df.writeStream
  .option("checkpointLocation", "/path/to/checkpoint")               # Nơi lưu state (offset)
  .trigger(availableNow=True)     # Trigger dạng batch (tuỳ chọn)
  .toTable("my_bronze_table")     # Đẩy vào bảng Delta
)
```

## ⚖️ 4. Phân Biệt Các Khái Niệm Dễ Nhầm Lẫn

| Khái Niệm | Auto Loader (`cloudFiles`) | Structured Streaming (Bình Thường) | COPY INTO |
| :--- | :--- | :--- | :--- |
| **Bản chất** | Streaming native tối ưu cho Cloud Storage (S3/ADLS) | Streaming tiêu chuẩn của Spark | Lệnh SQL batch ingestion |
| **Tracking file mới** | Dùng Directory Listing tối ưu hoặc Notification (Queue) | Scan thư mục liên tục (rất chậm và đắt nếu có >1 tỷ file) | Track các file đã load trong transaction log của bảng đích |
| **Lựa chọn khi nào?** | Data Volume khổng lồ, schema thay đổi liên tục, Streaming/Batch linh hoạt. | Dữ liệu đẩy từ Kafka/Kinesis (Event bus), không phải file-based. | User thích SQL thuần tuý, Volume file < 10,000 file/batch, cấu trúc tĩnh. |

## ⚠️ 5. Cạm Bẫy Đề Thi & ExamTopics

**1. Syntax Bắt Buộc Nhớ (Q179)**
- 🚨 **Trap**: Đề cho 4 đoạn code PySpark và yêu cầu chọn code đúng cho Auto Loader.
- **Đáp án**: Nhớ 3 keyword quyết định:
  1. Phải là `readStream` (code bẫy viết sai chính tả thành `readstream`).
  2. Phải là `format("cloudFiles")` (Đề hay lừa `format("json")` rồi option `cloudFiles` - SAI). Option con mới là `.option("cloudFiles.format", "json")`.
  3. Option ghi HOA từng chữ cái đúng: `.option("pathGlobFilter", "*.png")`.

**2. Auto Loader vs COPY INTO (Q17)**
- 🚨 **ExamTopics Q17/Trap**: "Identify new files since previous run, only ingest new files from a shared directory"
- **Đáp án**: **Auto Loader**. Nó thiết kế cho incremental streaming, tạo Checkpoint để track file mới. (Bẫy lừa: Unity Catalog - dùng phân quyền).
- **Phân biệt thật nhanh**: 
  - **"Schema Evolution", "Millions of files", "Incremental Streaming"** ➞ Auto Loader.
  - **"Idempotent SQL command", "Thousands of files", "Simple Batch"** ➞ COPY INTO.

**3. Bắt Bệnh Từ Trigger Mode (Q67)**
- 🚨 **ExamTopics Q67**: Vẫn muốn xử lý Incremental streaming nhưng "process all available data in as many batches as required" (Chạy tất cả backlog hiện tại đến khi hết thì thôi và tắt cluster).
- **Đáp án**: Bắt buộc là `.trigger(availableNow=True)`.
- **Bẫy**: `.trigger(once=True)` (Nó chỉ chạy ĐÚNG 1 micro-batch và dừng, dễ gây rớt data do giới hạn maxFilesPerTrigger).

**4. Checkpoint Location / Schema Location (Q125)**
- 🚨 **Trap**: Schema Evolution (tự động nội suy).
- **Quy tắc**: Gần như **BẮT BUỘC PHẢI CÓ** `cloudFiles.schemaLocation`. Không có checkpoint path thì job crash hoặc sẽ load lại data từ đầu gây Duplicate.

**5. Rescued Data Column (Q123)**
- Khi file JSON/CSV ném lên 1 cột có Data Type sai bét so với schema đã định -> Để tránh hụt field/rớt data, bật `.option("cloudFiles.inferColumnTypes", "true")`. Dữ liệu lỗi được gom vào cột `_rescued_data` để QA xem xét sau.

## 🌟 6. Khung Tư Duy Xử Lý Tình Huống

- **Auto Loader không phải "phép màu" mọi lúc**: Cực mạnh để nạp Incremental. Nhưng nếu bài toán chỉ là batch vài nghìn file một lần, thì setup SQL `COPY INTO` nhẹ, dễ vận hành và đỡ tốn tiền streaming cluster hơn.
- **Directory Listing vs File Notification**: 
  - *Directory listing*: Khởi bút nhanh nhất, cực tốt cho bucket vừa.
  - *File notification*: Phải dùng khi scale siêu lớn (nhiều triệu file/ngày) nhằm tránh liệt API do lệnh "List Files" của AWS S3/GCS.
- **Hiểu bản chất Checkpoint**: Mỗi Stream Job phải gắn với 1 checkpoint path CỐ ĐỊNH, coi như "CMND" của Job để biết nó đã đọc file nào. Xóa checkpoint tương đương "Đọc lại từ đầu".

## 🔗 7. Official Docs Tham Khảo
- **Deep Dive:** [[01_Databricks#11. AUTO LOADER|01_Databricks.md — Section 11: Auto Loader]]
- **Docs:** [Databricks: Auto Loader](https://docs.databricks.com/en/ingestion/cloud-object-storage/auto-loader/index.html)
- **Docs:** [Schema Evolution & Rescue](https://docs.databricks.com/en/ingestion/cloud-object-storage/auto-loader/schema.html)
