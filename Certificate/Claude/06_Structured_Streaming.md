# §2 STRUCTURED STREAMING — Triggers, Watermark, Checkpointing

> **Exam Weight:** 30% (shared) | **Difficulty:** Trung bình
> **Exam Guide Sub-topics:** readStream/writeStream, Trigger modes, Checkpointing, Watermarking

---

## TL;DR

**Structured Streaming** = Spark engine xử lý data liên tục dưới dạng micro-batches. Kết hợp với Delta Lake để đạt exactly-once semantics. Keyword quan trọng nhất: **trigger modes** (đề thi hỏi rất nhiều).

---

## Nền Tảng Lý Thuyết

### Batch vs Streaming — Khác Nhau Cơ Bản

**Batch Processing** (truyền thống):
- Đọc data → xử lý → ghi kết quả → DỪNG.
- Ví dụ: ETL chạy 2AM mỗi đêm, xử lý data ngày hôm trước.
- Nhược điểm: Data cũ nhất = 24 giờ (chờ đến run tiếp theo).

**Streaming** (real-time):
- Đọc data liên tục → xử lý → ghi → lặp lại mãi mãi.
- Ví dụ: IoT sensors gửi data mỗi giây, hệ thống fraud detection.
- Ưu điểm: Data fresh (near real-time).

**Spark Structured Streaming = Streaming nhưng viết code như Batch:**

```python
# Batch code:
df = spark.read.format("json").load("/data/")

# Streaming code (gần giống!):
df = spark.readStream.format("json").load("/data/")
#         ^^^^^^^^^^
# Chỉ đổi read → readStream, Spark tự xử lý incremental
```

### Micro-Batch Architecture

Structured Streaming KHÔNG xử lý từng record 1. Thay vào đó, nó gom records thành **micro-batches** và xử lý mỗi batch:

```mermaid
graph LR
    S["📥 Source<br/>(Kafka, S3, Delta)"] -->|"Records"| B1["Batch 1<br/>(100 records)"]
    B1 -->|"Process"| T1["Transform"]
    T1 -->|"Write"| D["📤 Delta Sink"]
    
    S -->|"More records"| B2["Batch 2<br/>(150 records)"]
    B2 -->|"Process"| T2["Transform"]
    T2 -->|"Write"| D
    
    S -->|"More records"| B3["Batch 3<br/>(80 records)"]
    B3 -->|"..."| T3["..."]
```

### Trigger Modes — "Mỗi Batch Kích Hoạt Khi Nào?"

Đây là phần đề thi hỏi **NHIỀU NHẤT** về Streaming:

| Trigger | Hành vi | Ví dụ thực tế |
|---------|---------|--------------|
| `trigger(availableNow=True)` | Process ALL available data → chia nhiều batches nếu cần → **STOP** | Incremental ETL: "xử lý hết data mới rồi tắt" |
| `trigger(once=True)` | Process chỉ **1 micro-batch** → STOP | Legacy, thay thế bởi `availableNow` |
| `trigger(processingTime="30 seconds")` | Chạy mỗi 30 giây, liên tục | Real-time dashboard |
| Không set trigger | Chạy liên tục ASAP (batch xong là batch tiếp) | Lowest latency streaming |

**Khác biệt then chốt: `availableNow` vs `once`**

```text
Data có 10,000 records mới:

trigger(once=True):
  Batch 1: process 5,000 records → STOP
  → Còn 5,000 records CHƯA xử lý!

trigger(availableNow=True):
  Batch 1: process 5,000 records
  Batch 2: process 3,000 records
  Batch 3: process 2,000 records → HẾT data → STOP
  → ALL records đã xử lý!
```

### Checkpoint — "Bookmark Của Stream"

Checkpoint = nơi lưu **progress** (đã đọc đến đâu, offset nào). Như bookmark trong sách — nếu bạn dừng đọc, lần sau mở lại biết đọc từ đâu.

```text
Checkpoint chứa:
├── offsets/          ← Đã đọc đến offset nào
├── commits/          ← Batch nào đã commit thành công
├── state/            ← State cho aggregation/windowing
└── metadata           ← Config của query
```

**Tại sao checkpoint BẮT BUỘC?**
- Không có checkpoint → restart = đọc lại từ đầu = **duplicate data**.
- Có checkpoint → restart = đọc tiếp từ chỗ dừng = **exactly-once**.

### Watermark — "Chấp Nhận Trễ Bao Lâu"

Trong streaming, data có thể đến **trễ** (ví dụ: event lúc 10:00 nhưng đến hệ thống lúc 10:15).

**Watermark = ngưỡng chấp nhận late data.** Data trễ hơn watermark bị bỏ qua.

```python
# Watermark 1 giờ: chấp nhận data trễ tối đa 1 tiếng
stream_df = (spark.readStream.table("events")
    .withWatermark("event_time", "1 hour")
    .groupBy(window("event_time", "10 minutes"), "region")
    .count()
)

# event_time = 10:00, arrive at 10:30 → ✅ accepted (trễ 30 min < 1 hour)
# event_time = 10:00, arrive at 11:30 → ❌ dropped (trễ 1.5 hours > 1 hour)
```

---

## So Sánh Với Open Source

| Databricks Feature | OSS Equivalent | Khác biệt |
|-------------------|---------------|-----------|
| Structured Streaming | Apache Spark Structured Streaming | Tương tự, Databricks thêm optimizations |
| `trigger(availableNow=True)` | ❌ Không có | Databricks-specific, process all → stop |
| Delta as Sink | Parquet sink | Delta + checkpoint = exactly-once |
| Auto Loader source | Custom file source | `cloudFiles` format, file tracking |

---

## Cú Pháp / Keywords Cốt Lõi

### Complete Streaming Pattern

```python
# 1. READ streaming source
stream_df = (spark.readStream
    .format("delta")                    # Source format
    .table("bronze.events")             # Source table
)

# 2. TRANSFORM (giống hệt batch!)
clean_df = (stream_df
    .filter("user_id IS NOT NULL")
    .withColumn("event_date", to_date("event_time"))
)

# 3. WRITE to sink
query = (clean_df.writeStream
    .format("delta")                                        # Sink format
    .option("checkpointLocation", "/checkpoints/silver")    # BẮT BUỘC
    .trigger(availableNow=True)                             # Trigger mode
    .outputMode("append")                                   # Output mode
    .toTable("silver.events")                               # Target table
)
```

> 🚨 **ExamTopics Q67:** "Process ALL available data in as many batches as required" → **`trigger(availableNow=True)`** (đáp án A).
> - `trigger(once=True)` = chỉ 1 batch → CÓ THỂ KHÔNG HẾT data.
> - `trigger(processingTime="once")` → **SAI syntax** (processingTime nhận interval như "30 seconds").
> - `trigger(continuous="once")` → **SAI syntax**.

---

## Cạm Bẫy Trong Đề Thi (Exam Traps)

### Trap 1: `availableNow=True` vs `once=True`
- **Đáp án nhiễu:** `trigger(once=True)` khi hỏi "process ALL available data" → **SAI**.
- **Đúng:** `trigger(availableNow=True)` = process TẤT CẢ, chia nhiều batches.
- **Cách nhớ:** `once` = 1 batch ONLY. `availableNow` = MANY batches until done.

### Trap 2: Syntax sai cho trigger
- ❌ `trigger(processingTime="once")` → processingTime cần interval: "30 seconds", "1 minute".
- ❌ `trigger(continuous="once")` → continuous cần interval: "1 second".
- ✅ `trigger(availableNow=True)` hoặc `trigger(processingTime="30 seconds")`.

### Trap 3: Checkpoint = optional?
- **Đáp án nhiễu:** "Checkpoint is optional for streaming" → **SAI** cho production.
- **Đúng:** Checkpoint **BẮT BUỘC** cho fault tolerance + exactly-once.
- **Logic:** No checkpoint = restart from beginning = duplicate data in sink.

---

## 🔗 Tham Khảo

- **Deep Dive:** [[01_Databricks#12. STRUCTURED STREAMING|01_Databricks.md — Section 12: Structured Streaming]]
- **Official Docs:** https://docs.databricks.com/en/structured-streaming/index.html
- **Triggers:** https://docs.databricks.com/en/structured-streaming/triggers.html
