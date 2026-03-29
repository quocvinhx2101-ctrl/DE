# 02. Optimization & Data Layout

## 🎯 1. TL;DR
- **Data Skipping**: Databricks tự động đọc metadata (min/max của cột) ở mức file để bỏ qua các file không chứa dữ liệu thoả mãn mệnh đề `WHERE`.
- **Liquid Clustering**: Công nghệ thế hệ mới ĐÁNH BẠI hoàn toàn Partitioning và Z-Ordering. Phân cụm dữ liệu tự động, thay đổi key bất cứ lúc nào, giải quyết bài toán "small files" của high cardinality.
- **Predictive Optimization**: AI của Databricks tự động phân tích và chạy `OPTIMIZE` / `VACUUM` dưới nền.

## 🧠 2. Bản Chất Lý Thuyết (Core Concepts)

- **Căn bệnh "Small Files"**: Lưu trữ hàng triệu file nhỏ (ví dụ vài KB) khiến Engine tốn thời gian đọc metadata hơn là đọc dữ liệu. `OPTIMIZE` sinh ra để gom (compact) file nhỏ thành các file to (~1GB) -> Đẩy tốc độ đọc lên tối đa.
- **Liquid Clustering vs Partitioning (Cũ)**:
  - *Partition (Hive-style)*: Chia file vật lý theo thư mục (Vd: `year=2023/month=12/`). NẾU chia theo cột có quá nhiều giá trị duy nhất (High-cardinality như `user_id` hay `timestamp`) -> Tạo ra hàng triệu thư mục & nhỏ file -> Hệ thống sập (OOM). Đã chia partition thì KHÔNG THỂ thay đổi mà không phải ghi lại toàn bộ bảng.
  - *Liquid Clustering*: Lưu dữ liệu linh hoạt, không tạo thư mục cứng. Chạy tốt với High-cardinality. Bạn có thể thay đổi cột Cluster bất kì lúc nào (Vd: tháng này phân cụm theo `user_id`, năm sau phân theo `event_name`) mà KHÔNG cần ghi lại dữ liệu cũ.
- **Deletion Vectors**: Cơ chế đánh dấu dòng bị xóa (logical delete) bằng một tệp nhỏ. Giúp các thao tác `DELETE`, `UPDATE`, `MERGE` chạy cực nhanh vì không cần ghi lại (rewrite) toàn bộ file Parquet vật lý chứa dòng bị xóa đó ngay lập tức (sẽ tự gộp lại sau khi chạy `OPTIMIZE`).

## ⌨️ 3. Cú Pháp Bắt Buộc Nhớ (Code Patterns)

### Khai báo và đổi Key cho Liquid Clustering
```sql
-- Lúc tạo bảng mới
CREATE TABLE events (
  user_id INT,
  event_time TIMESTAMP,
  country STRING
) CLUSTER BY (user_id, event_time);

-- Đổi key động (điểm mạnh nhất của Liquid)
ALTER TABLE events CLUSTER BY (country);

-- Trigger tiến trình sắp xếp thực tế (Incremental)
OPTIMIZE events;
```

### Chạy Tối Ưu Thủ Công (Nếu không bật Predictive)
```sql
-- Gộp file nhỏ thành file lớn (Compact files)
OPTIMIZE events;

-- Xóa các file rác (data files không còn được tham chiếu trong log) có tuổi thọ > 7 ngày (mặc định)
VACUUM events;
```

## ⚖️ 4. Phân Biệt Các Khái Niệm Dễ Nhầm Lẫn

| Khái Niệm | Giải Thích | Tác Động Trong Đề Thi |
| :--- | :--- | :--- |
| **Z-Ordering (Cũ)** | Sắp xếp dữ liệu theo nhiều chiều (multidimensional). | Đề thi mới sẽ coi nó là Legacy. Nếu đáp án có Liquid Clustering cho một workload mới hoặc đa chiều -> Chọn Liquid. |
| **Partitioning** | Chia thư mục cứng vật lý. | Tốt cho các cột low-cardinality (như `year`, `month`). CẤM dùng cho high-cardinality. |
| **OPTIMIZE** | Gom file nhỏ (Compaction) + sắp xếp lại theo Cluster Key. | Tối ưu hóa đọc (Read-optimized). |
| **VACUUM** | Xóa hẳn file vật lý cũ (đã bị overwrite/delete) ra khỏi Storage. | Tiết kiệm chi phí lưu trữ Storage (đừng nhầm là nó giúp tăng tốc độ query). |

## ⚠️ 5. Cạm Bẫy Đề Thi & ExamTopics

**1. Vấn đề "Small Files" & Over-partitioning**
- 🚨 **Trap**: Đề đưa ra một bảng được partitioned theo một cột có High Cardinality (chứa hàng triệu giá trị như `timestamp`, `customer_id` hoặc mã vùng).
- **Đáp án**: Dẫn tới "Small files issue". Cách fix chuẩn theo Delta Lake là đổi qua **Liquid Clustering** hoặc gỡ partition/dùng Z-Order.

**2. Chiến Lược Đổi Query Pattern (Q187, Q188)**
- 🚨 **ExamTopics Q188**: Bảng partitioned by `purchase_date`, query lại filter ở `customer_id` bị chậm. Bẫy Z-Order nhưng đáp án tốt nhất và hiện đại nhất trên Delta 3.x là **ALTER TABLE ... CLUSTER BY (customer_id, purchase_date)** (Liquid Clustering thay thế cả partition lẫn Z-Order).
- 🚨 **ExamTopics Q187**: Bảng đã có Partition + Z-Order + Predictive Optimization nhưng **logic filter thay đổi liên tục** (tháng này group bằng vùng, tháng sau group theo User) -> **Switch to Automatic Liquid Clustering**.

**3. Tự Động Hóa Dọn Dẹp (Predictive Optimization)**
- 🚨 **Trap**: "eliminates the need to manually manage maintenance operations" (loại bỏ hoàn toàn công việc tối ưu hóa thủ công).
- **Đáp án**: Nhắm thẳng vào **Predictive Optimization**. Tuy nhiên hệ thống chỉ tự động chạy (OPTIMIZE/VACUUM/ANALYZE) dựa trên cấu hình, không thay thế việc bạn phải chọn layout đúng ban đầu.

**4. DELETE FROM vs VACUUM**
- 🚨 **Trap**: Giảm chi phí lưu trữ S3/ADLS bằng cách chạy lệnh `DELETE FROM`.
- **Sự thật**: `DELETE FROM` chỉ xóa logic (đánh dấu tombstone trong History file). Quá khứ vẫn còn đó để Time Travel. Phải chạy `VACUUM` (sau thời gian `retention`) thì file rác mới trực tiếp bị xóa khỏi thùng chứa phần cứng.

**5. Caching vs Data Layout**
- 🚨 **Trap**: Kích hoạt "Delta caching" để giải quyết việc full table scan/truy vấn layout sai. 
- **Giải pháp**: Caching chỉ giải quyết truy xuất phần cứng lặp lại (đọc RAM/Disk thay cho mạng). Còn **File Skipping** (bỏ qua file không chứa dữ liệu cần tìm) thì bắt buộc phải dựa vào Data Layout. Layout sai mà cache thì "vẫn rất mượt mà đọc cả đống file rác".

## 🌟 6. Khung Tư Duy Layout (Deep Dives)

- **Layout/Thiết kế tốt** là điều kiện tiên quyết (Pha 1: Pruning/Skipping tránh việc đọc thừa data). Gói Compute lớn/Caching là tối ưu ngọn (Pha 2).
- **Liquid Clustering đang là Meta**: Được Databricks khuyến nghị dùng cho đa số mọi bảng Delta mới. Tốt hơn Partitioning do tự động cân bằng file size, và tốt hơn Z-Order khi pattern truy vấn thay đổi liên tục.
- **3 Câu tự hỏi khi thiết kế**: Cột filter/group là gì? Cardinality thấp hay cao? Có biến đổi theo thời gian không?

## 🔗 7. Official Docs Tham Khảo
- **Deep Dive:** [[01_Databricks#5. DELTA LAKE 3.x ECOSYSTEM|01_Databricks.md — Section 5: Delta Lake 3.x]]
- **Deep Dive:** [[01_Databricks#14. PREDICTIVE OPTIMIZATION|01_Databricks.md — Section 14]]
- **Liquid Clustering:** [Databricks Docs: Clustering](https://docs.databricks.com/en/delta/clustering.html)
- **Predictive Optimization:** [Databricks Docs: Predictive Opt](https://docs.databricks.com/en/optimizations/predictive-optimization.html)
