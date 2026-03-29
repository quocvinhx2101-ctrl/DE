# 12. Performance & Spark UI (Troubleshooting)

## 🎯 1. TL;DR
- **Spark UI**: Trọng tâm là phân tích được tab `Stages` xem biểu đồ thời gian báo Skew, và đọc `SQL/DataFrame` để biết có `Shuffle` hay không.
- **OOM (Out Of Memory)**: Lỗi vua khi sập Pipeline, học thuộc cách tối ưu bằng Narrow Filter và Scale CPU.
- **SQL Warehouse**: Nắm rõ cách scale Ngang (Scaling Range) vs Dọc (Cluster Size) cực kì quan trọng. Chọn sai = đi tong bài thi.

## 🧠 2. Bản Chất Sự Khác Biệt (Core Concepts)

- **OOM Error (`Java Heap Space`)**: Báo bạn hết RAM. Lý do: 
  - Query lấy lên 1 cục Data mảng bự quá làm tràn bộ nhớ Driver (`collect()`). 
  - Hoặc Node xử lý Join 2 bảng gây Shuffle quá mức.
  - SỬA LỖI: Thu hẹp Data Filter (đọc ít đi), upsize Worker Node, KHÔNG bao giờ có chuyện sửa OOM bằng việc cho Cache Data (Vì bản chất Cache vào Ram lại càng làm Ram tốn thêm).
- **CPU Time vs Task Time**: 
  - `CPU Time cao ≈ Task Time`: Nghĩa là Cluster đang dồn nén toàn bộ thời gian vào tính toán. Xử lý bằng cách mua Cluster mạnh hơn (Upsize core).
  - `CPU Time cực thấp mà Task time cao`: Máy có RAM/CPU nhưng chỉ ngồi CHỜ, do dính nghẽn Mạng, Lỗi Skew data dập vào 1 cục.
- **Data Skew**: Hiện tượng dữ liệu đổ sạch vào một Partition (VD: Doanh thu tỉnh lẻ rất ít, nhưng TP.HCM quá nhiều). Làm toàn bộ Node nghẽn ngồi chờ đúng cái thằng có Data to nhất chạy xong. 
- **Auto Stop & SQL Alerts**: SQL Endpoint tự tắt khi rảnh. Alert giúp tạo quy tắc giám sát truy vấn (Ví dụ: Số đơn > 100 gửi email/Webhook vào Slack/PagerDuty).

## ⌨️ 3. Cú Pháp Bắt Buộc Nhớ (Code Patterns)

*Chương này chủ yếu cấu hình giao diện thay vì Code SQL.*

```sql
-- Khi bị Shuffle vì join bảng To với bảng NHỎ -> Ép Spark dùng Broadcast Hash Join (Nhét bảng nhỏ qua Ram Node khác mất mẹ Skew)
SELECT /*+ BROADCAST(small_table) */ * FROM large_table t1 JOIN small_table t2 ...
```

## ⚖️ 4. Phân Biệt Các Khái Niệm Dễ Nhầm Lẫn

**TỐI ƯU CẤU HÌNH SQL WAREHOUSE (CHẮC CHẮN CÓ TRONG ĐỀ THI VÀ PHẢI DO ĐÚNG USECASE)**

| Loại Bệnh | Phương Án Tối Ưu Phù Hợp (SQL Warehouse) | Giải Thích |
| :--- | :--- | :--- |
| Query siêu nặng phức tạp, 1 người chạy | **Tăng Cluster Size** (XS -> XL) | Scale "DỌC". Đưa máy khoẻ hơn, mạnh hơn xử lý các lệnh Scan siêu khổng lồ. |
| Query đơn giản nhe, nhưng **Nhiều Người Cùng Chạy** | **Tăng Scaling Range (VD: Tăng `Max number of clusters`)** | Scale "NGANG". Xếp thêm nhiều máy y chang nhau đứng vào chầu trực gồng gánh nhiều ông User cùng thao tác để k ai chờ. |

## ⚠️ 5. Cạm Bẫy Đề Thi & ExamTopics

- 🚨 **Bẫy Lỗi OutOfMemory (OOM) - (ExamTopics Q181):** Đề hỏi "Bạn dính lỗi OutOfMemoryError, làm sao khắc phục?".
  - Đáp án đúng: **Narrow the filters** (Thu hẹp điều kiện lọc dữ liệu giảm tải) hoặc **Upsize worker nodes** (Nâng kích cỡ máy để có thêm RAM xử lý RAM driver/executor).
  - Bẫy: "Cache the DataFrame". ĐÂY LÀ ĐÁP ÁN SAI VÀ LỪA ĐẢO. Cache lại một dataframe quá to đang bị OOM thì chỉ làm nó OOM nặng hơn hoặc tràn ngập đĩa xuống HDD (spill).
- 🚨 **Bẫy Tìm Hiểu Notebook Đang Chạy Chậm Mở Chi Tiết Đâu? (ExamTopics Q129):** Đề hỏi "Tại sao chạy Notebook cực kì chậm, coi ở đâu?".
  - Đáp án đúng: Vào **Runs tab -> click active run**. Đoạn này chứa Live execution log có thể soi thực tế mức độ chạy đang tắc ở cell nào.
  - Bẫy: Chọn "Tasks tab". Chỗ đó chỉ view định nghĩa (Task configs/definitions), không phải đồ Live.
- 🚨 **Bẫy Lên Lịch Query Databricks SQL (ExamTopics Q55, Q86):** Đề hỏi "Cứ định kì mỗi ngày Query này ở Databricks SQL cần tự động Refresh một lần xong tắt". Chỉnh thế nào?
  - Đáp án đúng: Nhấn vào trang của chính cái query đó rồi setup schedule (**From the query's page in Databricks SQL**). 
  - Đề hỏi "Dừng job sau 1 tuần": Khai báo **"Set refresh schedule to end on a certain date"**.
  - Bẫy: Đừng lao vào "SQL endpoint page" (Warehouse) mà cài đặt.
- 🚨 **Bẫy Setup Warehouse Size vs Scaling Range (ExamTopics Q130):** 
  - Câu hỏi "Many users running small queries simultaneously, queries slow" (Nhiều user chạy truy vấn NHỎ cùng LÚC -> Tắc nghẽn về mặt luồng/số lượng job đợi). 
  - Giải pháp: **Increase scaling range** (Nâng min/max clusters để đẻ thêm kho máy giải đều tải mạng).
  - Bẫy: Nâng `Warehouse size`. Tăng Warehouse size chỉ giúp MỘT single query siêu to khổng lồ chạy bớt ngộp, không giải quyết vấn đề nghẽn cổ chai hàng đợi do nhiều user song song.
- 🚨 **Bẫy Alerts Notification (ExamTopics Q131):** Yêu cầu "Notify a generic webhook or team channel when count is > 100".
  - Đáp án: Cấu hình **Create an alert with a new webhook destination**.
  - Bẫy: Đừng chọn "Custom template" (chỉ để định dạng giao diện email), hay "Email destination" (gửi vào hòm tư nhân 1 người chứ mất tác dụng tới team channel).

## 🌟 6. Khung Tư Duy (Deep Dives)

### Quy Trình Tune & Fix Spark / SQL Warehouse Nhanh Nên Nắm
1. **Xác định nghẽn nằm ở đâu?** Bottleneck bộ nhớ (OOM)? Do Disk (I/O spill)? Hay do tính toán (Compute - CPU cao vs Task list)? Spark UI sẽ trả lời một nửa chuyện đó.
2. **Nếu Sập do OOM (Out Of Memory):**
   - Rà soát Code: Tránh các hàm `toPandas()`, `collect()` kéo đống dữ liệu cực kì khủng về 1 cục Driver.
   - Check Data Skew: Một partition to gấp trăm lần partition kia.
   - Mọi thủ thuật thất bại -> Tăng Size thiết bị, nâng RAM. (TUYỆT ĐỐI không spam CACHE khi xử lý OOM).
3. **Phân Biệt Size vs Auto-scaling Range của Serverless SQL Warehouse:**
   - **Size (T-Shirt size từ XS đến XX-Large):** Tượng trưng sức kéo của máy. Dùng để xử lý các câu SQL query khổng lồ (Nặng đô). Nút cổ chai là *độ lớn* tác vụ.
   - **Scaling Range (Ví dụ bật scale từ 1 máy lên 4 máy):** Tượng trưng khả năng chia bài. Dùng khi cả 100 team mở BI dashboard chung 8h sáng thứ Hai để lấy report nhỏ, query ngắn nhưng lượng người dùng xếp hàng (Concurrency) quá lớn. Do đó Scale range khắc phục *độ tắc nghẽn luồng chờ*.

## 🔗 7. Official Docs Tham Khảo

- **SQL Warehouses (Size vs Scale):** [Serverless SQL Warehouses](https://docs.databricks.com/en/compute/sql-warehouse/index.html)
- **Spark OOM & Skew Tuning:** [Diagnosing Performance Issues](https://docs.databricks.com/en/optimizations/index.html)
