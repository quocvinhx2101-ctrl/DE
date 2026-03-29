# 05. Delta Lake Core

## 🎯 1. TL;DR
- **Delta Lake**: Là open-source storage layer xây dựng trên nền **Parquet files**. Nó khắc phục điểm yếu của Data Lake nhờ việc đem lại ACID transactions, Time Travel, VACUUM và Schema Enforcement.
- Trái tim của Delta Lake là thư mục `_delta_log/` (Transaction Log), lưu trữ mọi lịch sử thay đổi (version) dưới định dạng JSON (mỗi khi commit tạo 1 file).

## 🧠 2. Bản Chất Sự Khác Biệt (Core Concepts)

- **Transaction Log (`_delta_log/`)**: Lưu cấu trúc "Thêm file Parquet A, Xóa tham chiếu file Parquet B". File bị xóa sẽ bị ẩn đi (tạo ra version mới), KHÔNG bị xóa vật lý ngay lập tức -> Nhờ vậy mà có Time Travel (quay ngược phiên bản cũ).
- **Time Travel**: Tính năng cho phép bạn truy vấn hoặc khôi phục (RESTORE) lại dữ liệu từ một Version hoặc Timestamp cụ thể trong quá khứ kể từ khi bảng được tạo (hoạt động dựa trên state trong transaction log và các file vật lý chưa bị xóa).
- **Schema Enforcement vs Evolution**:
  - *Enforcement (Mặc định)*: Ném ra lỗi (Reject) nếu bạn chèn dữ liệu thừa/thiếu cột hoặc khác kiểu dữ liệu với Schema đang có.
  - *Evolution*: Cho phép bảng Delta tự động mở rộng (thêm cột mới) bằng tuỳ chọn `.option("mergeSchema", "true")`.

## ⌨️ 3. Cú Pháp Bắt Buộc Nhớ (Code Patterns)

### Truy vấn quá khứ (Time Travel)
```sql
-- Dùng Version number (Thường gặp trong đề)
SELECT * FROM my_table VERSION AS OF 3;

-- Dùng Timestamp
SELECT * FROM my_table TIMESTAMP AS OF '2024-04-22T14:32:00';

-- Lấy lại vĩnh viễn (Rollback) toàn bộ bảng về Version 3
RESTORE TABLE my_table TO VERSION AS OF 3;
```

### Xóa dọn file (VACUUM)
```sql
-- Xóa các data files KHÔNG CÒN thuộc về version hiện tại VÀ đã già hơn 168 giờ (7 ngày) mặc định.
VACUUM my_table;

-- Tự thiết lập số giờ giữ lại:
VACUUM my_table RETAIN 168 HOURS;
```

## ⚖️ 4. Phân Biệt Các Khái Niệm Dễ Nhầm Lẫn

| Khái Niệm | Mục Đích Chính | Lưu Ý |
| :--- | :--- | :--- |
| **`CREATE OR REPLACE TABLE` (CRAS)** | Thay thế TOÀN BỘ (Drop & Recreate). | Ghi đè cả Data lẫn Schema. |
| **`INSERT OVERWRITE`** | Chỉ ghi đè Dữ liệu. | Từ chối ghi đè nếu Schema mới khác cũ (Failed) (trừ khi bật chạy evolution). |
| **`CREATE TEMP VIEW`** | Chỉ tạo view tạm thời trên Cluster. | KHÔNG lưu vào Unity Catalog. Reset cluster là mất. |
| **Managed vs External Table** | Managed (Databricks tự quản lí nơi lưu): `DROP TABLE` mất cả Meta lẫn files vật lý. | External (Chỉ meta): `DROP TABLE` chỉ xoá Meta, file Gốc ở S3/ADLS VẪN Y NGUYÊN. |

## ⚠️ 5. Cạm Bẫy Đề Thi & ExamTopics

**1. Hậu quả của VACUUM đối với Time Travel (Q52)**
- 🚨 **ExamTopics Q52/Trap**: Kỹ sư dùng Time Travel quay về bản snapshot 3 ngày trước nhưng báo lỗi "data files have been deleted". Yếu tố nào gây ra nguyên nhân này?
- **Đáp án**: Bảng đó đã chạy lệnh **VACUUM**. Lệnh này dọn sạch các file cũ (tombstones). Bẫy này rất hay gài đáp án nhiễu là "do chạy OPTIMIZE" (Tuyệt đối KHÔNG chọn, OPTIMIZE chỉ gộp file chứ Không xóa lịch sử).

**2. Lấy Đúng Version Khôi Phục (Q59)**
- 🚨 **ExamTopics Q59**: Sếp lỡ tay gõ `UPDATE` sai lè lên bảng `VERSION 5`. Bạn muốn lấy lại trạng thái "ngay trước lúc UPDATE".
- **Đáp án**: Dùng truy vấn `VERSION AS OF 4` (Version liền trước số 5).

**3. RESTORE vs VERSION AS OF (Q70)**
- 🚨 **ExamTopics Q70**: Ngân hàng muốn Data Analyst XEM lại / PHÂN TÍCH dựa trên snapshot dữ liệu của 2 tuần trước. DE phải làm gì?
- **Đáp án**: Xem lịch sử trong `transaction logic`, thấy version X ứng với 2 tuần trước. Gửi cho Data Analyst số đó để họ tự query bằng `VERSION AS OF`.
- **Trap chí mạng**: Chọn đáp án chạy `RESTORE TABLE`. Lý do sai: RESTORE quay ngược thời gian toàn bộ BẢNG GỐC, làm bốc hơi toàn bộ dữ liệu pipeline mới ghi vào trong 2 tuần qua. Chỉ dùng RESTORE để vá thảm họa hỏng data.

**4. Schema Evolution**
- 🚨 **Trap**: Khi có "Automatically add new columns / schema changes", bắt buộc là **Schema Evolution** (tùy chọn `mergeSchema`).

**5. Cú Pháp Cơ Bản (Q100)**
- 🚨 **ExamTopics Q100**: Syntax chèn nhanh một dòng. Chú ý bẫy `UPDATE...VALUES` hay `APPEND...`. Câu đúng chỉ là `INSERT INTO table_name VALUES (...)`.

## 🌟 6. Khung Tư Duy (Deep Dives)

- **Delta theo 3 Lớp**: Nhìn Delta = Dữ liệu Parquet + Metadata `_delta_log` + Tập lệnh vận hành (Optimize/Vacuum). Thi hiểu bản chất này là qua 100%.
- **Deletions không phải Xóa Ngay**: Lệnh `DELETE` hay `UPDATE` chỉ thêm dòng mới hoặc sinh Parquet ảo, Data cũ vẫn ở đó (logic delete). Nó chỉ thực sự biến mất khi chạy `VACUUM` quá thời gian giữ lại (retention limit mặc định 7 ngày).
- **Mã Nguồn Quản Lý (Managed vs External)**: 
  - DROP bảng Managed -> Mất luôn cả File Data. 
  - DROP bảng External -> Chỉ mất Metadata, Data vẫn giữ trên gốc S3/ADLS.

## 🔗 7. Official Docs Tham Khảo
- **Deep Dive:** [[01_Databricks#5. DELTA LAKE 3.x ECOSYSTEM|01_Databricks.md — Section 5: Delta Lake 3.x]]
- **Docs:** [Delta Lake](https://docs.databricks.com/en/delta/index.html)
- **Time Travel:** [Databricks Time Travel](https://docs.databricks.com/en/delta/history.html)
- **VACUUM:** [Databricks VACUUM](https://docs.databricks.com/en/sql/language-manual/delta-vacuum.html)
