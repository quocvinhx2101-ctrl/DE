# 14. Delta Sharing, Lineage & Federation

## 🎯 1. TL;DR
- **Delta Sharing**: Không cần chuyển file (CSV/Parquet) thủ công qua đường thư mệt mỏi! Đây là quy chuẩn cho phép ta cấp quyền để Đối tác (Partner) đọc thẳng Data trực tiếp qua API an toàn.
- **Lakehouse Federation**: Giải quyết bài toán rác dữ liệu. Databricks có thể kết nối thẳng DBs (Postgres, Synapse) và xử lý Query tại chỗ mà KHÔNG CẦN ETL sao chép data vào Databricks.
- **Data Lineage**: Bản đồ "phả hệ" gốc gác của Data. Giúp điều tra nguồn gốc nếu Dashboard ra số sai.

## 🧠 2. Bản Chất Sự Khác Biệt (Core Concepts)

- **Delta Sharing 2 Mô hình**:
  - *Databricks 2 Databricks (D2D)*: Nội bộ công ty cùng nền tảng. Chìa khóa kết nối là dựa trên đoạn UUID có tên là "Sharing identifier" của cái Metastore.
  - *Databricks 2 External*: Bạn Share cho 1 cty xài Tableau/PowerBI (không xài Databricks). Chìa khóa kết nối qua 1 File tên là "Activation Token"
- **Lakehouse Federation / Query Pushdown**: Khi gọi `SELECT count (*) FROM pg_table`, Databricks thông minh không kéo nguyên cái bảng 1 tỷ dòng từ Postgres về. Bộ Optimizer sẽ "đẩy ngược" logic count xuống hẳn cho Postgres đếm, Postgres đếm xong gửi trả đúng 1 con số kết quả cho Databricks.
- **Data Lineage**: Lineage của Unity Catalog siêu mạnh, nó không chỉ track (theo dõi) xem Table này sinh ra từ Notebook nào, mà còn track dài đến tận cuối đường ở các Report/Dashboard luôn.

## ⌨️ 3. Cú Pháp Bắt Buộc Nhớ (Code Patterns)

*Chương này chủ yếu nghiêng về Cấu hình và Flow kết nối, code thi ít xuất hiện cụ thể ngoài việc KHAI RIÊNG 1 RECIPIENT.*

```sql
-- Khởi tạo Share data cho đối tác dùng Databricks (Setup D2D)
CREATE RECIPIENT cty_doi_tac 
USING ID 'aws:us-west-2:1234xxxx-5678-metastore-id';

-- Thêm quyền lấy data
GRANT SELECT ON SHARE my_share TO RECIPIENT cty_doi_tac;
```

## ⚖️ 4. Phân Biệt Các Khái Niệm Dễ Nhầm Lẫn

| Tính Năng Chia Sẻ | Đặc Điểm (Use Case Đi Thi) |
| :--- | :--- |
| **Delta Sharing** | Sinh ra từ Databricks -> Cấp Cho Đối Tác. Read-only (Chỉ đọc). Đặc biệt phù hợp cho các bên không chung nền tảng đám mây. |
| **Lakehouse Federation** | Databricks tọc ngoáy lấy hệ thống Khác "Làm của riêng" (PostgreSQL, SQL Server). Không cần nhân bản data. Tiết kiệm băng thông. |
| **Data Lineage (Phả Hệ)** | Giúp kiểm tra "Tầm ảnh hưởng" (Impact analysis).VD: Cty muốn sửa xoá một Bảng ở cột Silver, nhưng sợ Dashboard bên phòng Sales chết -> Dùng Lineage soi. |

## ⚠️ 5. Cạm Bẫy Đề Thi & ExamTopics

- 🚨 **Bẫy Thông Tin Khởi Tạo D2D Sharing (ExamTopics Q171):** Cần chia sẻ Delta Sharing giữa 2 công ty đều đang xài Databricks (Databricks-to-Databricks). Kỹ sư cần xin thông tin gì ĐẦU TIÊN từ đối tác để làm cầu nối?
  - Đáp án chuẩn: Phải xin **Sharing identifier của Unity Catalog metastore** bên đối tác (Sharing ID bản chất là 1 đoạn mã string định danh).
  - Bẫy: Các đáp án liên quan đến IP Address, URL, hay Share mật khẩu (Password).
- 🚨 **Bẫy Chia Sẻ Tập Lệnh & Asset (ExamTopics Q199):** Có share được Notebook qua giao thức Delta Sharing cùng với Data được không?
  - Đáp án đúng: **Có thể**. Dễ dàng share tập dữ liệu VÀ notebook cho đối tác. Cứ dùng quyền qua Unity Catalog.
  - Bẫy: Chọn cách chắp vá nông dân như "Gửi code qua Email" hay "Đẩy codebase qua Github".
- 🚨 **Bẫy Tiền Mạng Cross-Cloud (Data Egress Cost) - (ExamTopics Q196):** Quá trình Share data to từ AWS Workspace sang cho Azure Workspace của đối tác phát sinh **Phí đẩy Data dời khỏi AWS (Egress cost) khổng lồ**. Làm sao cắt giảm nó (minimize data transfer costs)?
  - Đáp án luôn là chuyển Dataset lên kho trung gian: **Migrate to Cloudflare R2 object storage before sharing**. Databricks hợp tác với R2 Cloudflare cho phép miễn hoặc giảm cực mạnh chi phí egress.
- 🚨 **Bẫy Lakehouse Federation (ExamTopics Q184):** Câu hỏi làm sao trộn 2 nguồn cơ sở dữ liệu `Combine PostgreSQL + Azure Synapse without data duplication` (Tích hợp truy vấn mà không phải copy ETL data về Databricks tốn chỗ). 
  - Chọn **Lakehouse Federation**.
- 🚨 **Bẫy Tầm Quét Data Lineage (ExamTopics Q198):** Đề hỏi "Lineage vẽ được những cái phụ thuộc (dependencies) nào?".
  - Vui lòng chọn cái đáp án dài và tham lam nhất: **ALL dependencies: notebooks, tables, AND reports (Dashboards)**.
  - Cấm chọn mấy thứ có gắn keyword giới hạn như "Only tables" hoặc "Only notebooks".
- 🚨 **Bẫy Quyền External Client:** Team đối tác (External Partners) khi được Share qua giao thức Delta Sharing thì MẶC ĐỊNH luôn là **Read-only**. Nếu muốn sửa hoặc insert thêm data, bên nhận phải nhờ bên cung cấp (Provider) viết vào thông qua Reverse Sharing hoặc cơ chế cấp quyền nâng cao, về cơ bản Delta Sharing truyền thống là luồng đọc.

## 🌟 6. Khung Tư Duy (Deep Dives)

### Trình Tự Tư Duy Về Delta Sharing:
Khi gặp bài toán chia sẻ dữ liệu ra ngoài, cần quan tâm 3 khái niệm:
1. **Provider (Người Cung Cấp):** Gom data vào 1 Cụm tên là Share (`CREATE SHARE hr_share`). Thêm bảng vào cụm Share đó. Trong kiến trúc nó đóng vai trò nhà xuất bản.
2. **Recipient (Người Nhận):** Quản trị 1 danh tính (`CREATE RECIPIENT xyz_partner`). 
3. Databricks sinh ra một **Activation Link / Token** (Với External) hoặc qua **Sharing Identifier** (Với hệ sinh thái D2D). Bên Provider `GRANT SELECT ON SHARE hr_share TO RECIPIENT xyz_partner`.

### Data Lineage Của Unity Catalog
- Không chỉ là cái "Giao diện đồ thị nối mũi tên trên UI", Lineage cực kì quan trọng khi muốn làm **Impact Analysis** (Gốc mà đổi lược đồ thì ngọn đi đời nhà ma không?), hoặc tracing ngược truy tìm gốc rễ lỗi (Root-cause analysis).
- Lineage của Databricks phủ sóng rộng từ mức bảng tới Row-level, Column-level cho đến File, Table, Workflow và Dashboard.

### Lakehouse Federation 
- Giải quyết bài toán không muốn làm Data Ingestion/ETL rườm rà. Bạn có một database PostgreSQL ở Server ngoài dùng nội bộ, thi thoảng Data Analyst muốn query lấy một view báo cáo.
- Federation tạo ra một "Bảng Ảo (Foreign Table)" ngay trong Unity Catalog trỏ thẳng qua PostgreSQL. Bạn gõ lệnh `SELECT` ở Databricks, nó chui qua PostgreSQL mượn bộ máy bên kia chạy, đem cục kết quả trả về Databricks hiển thị. KHÔNG CẦN CHÉP CẢ BẢNG VỀ! (Không Data Duplication).

## 🔗 7. Official Docs Tham Khảo

- **Delta Sharing:** [Delta Sharing Databricks](https://docs.databricks.com/en/delta-sharing/index.html)
- **Data Lineage:** [Data lineage with Unity Catalog](https://docs.databricks.com/en/data-governance/unity-catalog/data-lineage.html)
- **Lakehouse Federation:** [Lakehouse Federation](https://docs.databricks.com/en/query-federation/index.html)
