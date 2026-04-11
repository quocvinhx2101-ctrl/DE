
## 1. Data Layout & Query Performance Optimization

1. Kiến trúc của databrick chia thành 2 group là Control Plane và Data Plane (Storage & Compute). Ở lớp Data còn chia thành 2 dạng và dùng severless workspace (databricks) hoặc sử dụng classic workspace (Cloud).

2. Severlesss cũng có những lưu ý nhất định là mặc dù active rất nhanh và linh hoạt thời gian không sử dụng là nó tắt nhưng
	- Severless cho Job/Notebook . Nó hoàn toàn **Zero-config (Không cấu hình)**. Bạn **KHÔNG THỂ** chọn Size (Small/Medium), cũng **KHÔNG THỂ** cấu hình số lượng Worker (`min_workers` / `max_workers`) hay Scaling Range.
	- Serverless SQL Warehouse. Nó sinh ra để cắm vào BI tool để viết query nên để tránh viết những câu sai tốn quá nhiều tài nguyên
		- **"Size áo" (Cluster Size - Small, Medium, Large):** Đây là sức mạnh của **MỘT CỤM MÁY**. Nhưng Databricks giấu nhẹm đi việc bên trong cụm Small đó có bao nhiêu Worker Nodes hay bao nhiêu RAM. Bạn chỉ biết Small là yếu, Large là mạnh.
		- **Scaling Range (Min/Max):** Đây là **SỐ LƯỢNG CỤM MÁY**, chứ KHÔNG PHẢI số lượng Worker Nodes trong một máy.

3. The key features in intelligence platform is **Liquid Clustering, Predictive Optimization, data skipping**, and **file compaction**. 

4. kiến trúc Lakehouse thực tế ở dạng serverless hay cả classic compute 
```
   S3 Bucket (Physical Storage)
└── hila/section1_1/sales/
    ├── part-00000.parquet  ← File vật lý
    ├── part-00001.parquet  ← File vật lý
    ├── part-00002.parquet  ← File vật lý
    └── _delta_log/
        ├── 00000.json      ← Transaction log
        └── 00001.json
```

**TRONG MỖI file part-00000.parquet:**
```
[File Header: Schema metadata]
[Row Group 1]
  - Column Chunk: sale_id (compressed, encoded)
  - Column Chunk: sale_date (compressed, encoded)
  - Column Chunk: region (compressed, encoded)
  - Column Chunk: product_id (compressed, encoded)
  - Column Chunk: amount (compressed, encoded)
[Row Group 2]
  - Column Chunk: sale_id
  - Column Chunk: sale_date
  ...
[File Footer: Column statistics, offsets]
```

**Bạn có thể nghĩ như này:**

```
Layer 1: SQL Table (hila.Section1_1.sales) ← Metadata layer
         ↓
Layer 2: Delta Lake Format ← Transaction log + ACID
         ↓
Layer 3: Parquet Files (part-*.parquet) ← File format với columnar layout
         ↓
Layer 4: S3/ADLS/GCS ← Physical storage (bytes on disk)
         ↓
Layer 5: EBS/HDD/SSD ← Hardware disk
```

**"Columnar storage" ở Layer 3** - cách tổ chức data BÊNTRONG file Parquet, KHÔNG phải layer vật lý riêng biệt.

5. **Các điểm chính**
- Liquid Clustering là giải pháp thay thế được khuyến nghị cho partitioning và Z-ordering. Hãy sử dụng CLUSTER BY khi tạo hoặc thay đổi bảng. Bạn có thể thay đổi các clustering key sau này mà không cần ghi lại toàn bộ bảng.
- Predictive Optimization tự động chạy OPTIMIZE và VACUUM trên các bảng được quản lý bởi Unity Catalog. Kích hoạt tính năng này ở mức catalog hoặc schema để loại bỏ các công việc bảo trì thủ công. 
- Data skipping sử dụng thống kê min/max được lưu trong Delta transaction log để bỏ qua các file không liên quan khi thực hiện truy vấn. Nó hoạt động tự động nhưng đạt hiệu quả cao nhất khi dữ liệu được clustered. Deletion vectors tăng tốc DELETE, UPDATE và MERGE bằng cách đánh dấu các hàng đã xóa thay vì ghi lại toàn bộ file. Chúng được bật mặc định. 
- Thông điệp tổng thể cho kỳ thi: Databricks tự động hoá việc bố trí dữ liệu và tối ưu hoá hiệu năng, giúp các kỹ sư tập trung vào xây dựng pipeline thay vì tinh chỉnh lưu trữ.