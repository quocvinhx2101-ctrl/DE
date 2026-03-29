# 06. Structured Streaming

## 🎯 1. TL;DR
- **Structured Streaming**: Là engine của Spark cho phép xử lý luồng dữ liệu (Data Stream) gần thời gian thực (Micro-batches).
- **Core API**: Dùng API y hệt như làm Batch trên Spark với cú pháp `readStream` và `writeStream`.
- Trọng tâm đề thi: Câu hỏi về Streaming chiếm lượng RẤT LỚN. Tập trung 100% vào **Trigger modes**, **CheckpointLocation**, và **Watermark**.

## 🧠 2. Bản Chất Sự Khác Biệt (Core Concepts)

- **Micro-batch Architecture**: Spark Stream không xử lý từng `dòng` đơn lẻ (record-at-a-time). Nó gom nhiều records vừa tới thành các "gói nhỏ" (Micro-batches) - VD: Cứ có dòng mới là gom cục 100 dòng để xử lý 1 lần.
- **Checkpoint**: RẤT QUAN TRỌNG. Là một thư mục trên Storage (S3/ADLS). Lưu "Trạng thái / Vị trí / Phiên bản offset" xử lý hiện tại lại. Nhờ Checkpoint, nếu Cluster sập trưa nay, chiều nay khởi động lại nó sẽ ĐỌC TIẾP từ dòng kế tiếp, ĐẢM BẢO **Exactly-Once** processing (Không thừa, Không thiếu dữ liệu).
- **Watermark**: Mức "chịu đựng" độ trễ. VD: Watermark 1 giờ (1h) -> Nhận xử lý data bị đến trễ trong vòng < 1h. Dòng nào đến muộn quá 1h -> "Drop" (bỏ qua).

## ⌨️ 3. Cú Pháp Bắt Buộc Nhớ (Code Patterns)

### Cấu trúc cơ bản chuẩn của Read & Write Stream
```python
# 1. READ: chuyển read thành readStream
df = spark.readStream.table("bronze_events")

# 2. TRANSFORM
clean_df = df.filter("user_id IS NOT NULL")

# 3. WRITE: chuyển write thành writeStream KÈM CHECKPOINT
(clean_df.writeStream
  .option("checkpointLocation", "/path/to/_checkpoints") # Bắt Buộc
  .trigger(availableNow=True)                            # Xác định khi nào lấy batch
  .outputMode("append")                                  # Ghi thêm vào
  .toTable("silver_events")                              # Bảng đích
)
```

## ⚖️ 4. Phân Biệt Các Khái Niệm Dễ Nhầm Lẫn (TRIGGER MODES)

| Trigger Mode (Kích Hoạt) | Ý Nghĩa Chạy | Use Case / Từ Khoá |
| :--- | :--- | :--- |
| **Chưa set (Default)** | Xử lý gói mới ngay lập tức (ASAP) sau khi xong gói cũ. | Lowest latency (Real-time nhất có thể). |
| **`trigger(processingTime="1 minute")`** | Chạy gói mới cách nhau đúng mỗi khoảng chu kỳ (VD: 1 phút). | Định kỳ đều đặn (Periodic). |
| **`trigger(once=True)`** | (Legacy) Load ra **MỘT gói DUY NHẤT** (có thể sẽ không lấy hết lượng dữ liệu mới vào tồn đọng). Xong tự tắt. | Thi hay hỏi bẫy. Rất ít dùng hiện tại. |
| **`trigger(availableNow=True)`** | Load ra **TẤT CẢ** dữ liệu mới còn tồn đọng (chia làm nhiều batch nếu quá nhiều). Chạy tới khi hết sạch hàng rồi tự tắt (STOP). | "Process ALL available data" / Incremental Batch / Từ khóa Vàng. |

## ⚠️ 5. Cạm Bẫy Đề Thi & ExamTopics

**1. Vua của các câu hỏi Streaming (Q67)**
- 🚨 **ExamTopics Q67**: Yêu cầu muốn tiêu thụ SẠCH SẼ toàn bộ các file đang đợi trong queue ("Process ALL available data incrementally and then stop the cluster to save cost").
- **Đáp án**: Chắc chắn là **`trigger(availableNow=True)`**.
- **Tính bẫy**: Đề thường gài `trigger(once=True)`. Tại sao sai? Vì `once=True` chỉ xử lý ĐÚNG MỘT micro-batch rồi tự sát, vì thế CÓ THỂ KHÔNG HẾT BỘ DATA nếu quá lớn. Những đáp án bịa đặt như `trigger(processingTime="once")` hoặc `continuous="once"` là sai syntax.

**2. Quên Checkpoint Location (Q118)**
- 🚨 **Trap**: "Code streaming chạy bị lỗi Exception..." hoặc một đáp án "Checkpoint is optional".
- **Đáp án**: Để đạt *exactly-once* và *fault tolerance*, **Bắt buộc** phải khai báo `.option("checkpointLocation", "dir_path")`. Code ví dụ nào trong đề mà thiếu option này thì phải loại ngay. Checkpoint là danh tính của pipeline. Thay đổi đường dẫn Checkpoint sẽ coi như chạy lại từ đầu.

**3. Tạm dừng một Stream thủ công**
- 🚨 **Trap**: Đề hỏi "Làm sao để stop 1 interactive stream đang chạy mãi trong Notebook?" 
- **Đáp án**: Gọi method `.stop()` trên streaming query object. Cụ thể: `query = df.writeStream... 
 query.stop()`.

**4. Khái niệm Watermark**
- 🚨 **Trap**: Tại sao output của stream stateful không update / bị drop?
- **Khung tư duy**: Watermark không cứu vớt tốc độ, nó là "hợp đồng về độ trễ". Đặt watermark 10 phút nghĩa là data đến trễ quá 10 phút sẽ bị DROP khỏi state. Bạn phải tự trade-off giữa "chi phí RAM lưu state" và "tính đầy đủ của data".

## 🌟 6. Khái Quát Trục Tư Duy (Deep Dives)

- **Streaming reliability không chỉ nằm ở Trigger**: Đừng nghĩ Trigger là thần thánh. Tính ổn định và đúng đắn của Delta là sự kết hợp của: 
  1. Checkpoint lưu Offset.
  2. Idempotent Sinks (Nơi nạp hỗ trợ nạp đè không rác/trùng).
  3. Xử lý logic đúng cách (VD: merge vào Delta table thay vì chỉ append).
- **Quy tắc chọn Trigger đi thi**:
  - Tắt - mở theo lịch -> `availableNow=True`.
  - Muốn pipeline luôn bật 24/7, bắn batch mỗi 30s -> `processingTime="30 seconds"`.
  - Có yếu tố độ trễ thấp cực khủng -> `continuous` (nhưng ít khi hỏi dính vào cái này).

## 🔗 7. Official Docs Tham Khảo
- **Deep Dive:** [[01_Databricks#12. STRUCTURED STREAMING|01_Databricks.md — Section 12: Structured Streaming]]
- **Docs:** [Structured Streaming](https://docs.databricks.com/en/structured-streaming/index.html)
- **Triggers:** [Triggers Settings](https://docs.databricks.com/en/structured-streaming/triggers.html)
