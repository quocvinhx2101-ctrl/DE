# 13. Unity Catalog

## 🎯 1. TL;DR
- **Unity Catalog (UC)**: Giải pháp quản lý vòng đời và quyền hạn truy cập (Governance) cho TẤT CẢ các đối tượng trong Lakehouse (Tables, Views, Volumes, Models) CHUNG ở MỘT NƠI.
- **Three-Level Namespace**: Phải gọi tên đối tượng rõ ràng 3 cấp `catalog.schema.table` thay vì dùng kiểu `schema.table` như Hive xưa.
- **Kiểm soát Truy cập**: Lệnh `GRANT / REVOKE` là vua.

## 🧠 2. Bản Chất Sự Khác Biệt (Core Concepts)

- **Managed vs External Tables**:
  - *Managed Table*: Nằm kẹp trong vùng Storage mặc định của Databricks quản lý. Nhẹ đầu không phải setup Path rườm rà. NÊU `DROP TABLE`, rụng mất cả Dữ liệu vật lí lẫn Tên Bảng (Metadata).
  - *External Table*: Nằm ở Storage S3/ADLS do cty bạn làm chủ hoàn toàn, và định danh lại vào Unity Catalog qua từ khoá `LOCATION 's3://...'`. NẾU `DROP TABLE`, Data Vật lí Ở LẠI, chỉ có Metadata ở Catalog biến mất.
- **Metadata Fallback Hierarchy (Luật tìm chỗ chứa Managed)**: Khi bạn `CREATE TABLE` Managed mà không gán Storage, Databricks Unity Catalog sẽ tìm chỗ ghi Data lùi từ: `Schema -> Catalog -> Metastore`. Chỗ nào cắm Storage rồi thì ghi nhét vào. Thằng chót (Metastore) mà KHÔNG có Storage -> Bắt buộc 1 trong 2 thằng trên đầu phải có.
- **System Tables**: Trong Databricks luôn có sẵn một catalog ẩn tên là `system`. Gồm các bảng như: `system.access.audit` (lưu lại lịch sử ai đăng nhập, ai chạy query, ai xoá bảng), và `system.access.table_lineage` (dùng cho luồng di chuyển từ Bảng A tới Bảng B).

## ⌨️ 3. Cú Pháp Bắt Buộc Nhớ (Code Patterns)

### Cấp Quyền Tối Thiểu (Principle of least privilege)
```sql
-- Cấp quyền XEM CATALOG và VIEW SCHEMA (Bắt buộc dùng USAGE dọn đường)
GRANT USAGE ON CATALOG prod TO data_analysts;
GRANT USAGE ON SCHEMA prod.silver TO data_analysts;

-- Sau đó mới thả quyền Truy vấn Đọc Bảng vào (Nếu thiếu USAGE, SELECT vô dụng)
GRANT SELECT ON TABLE prod.silver.orders TO data_analysts;
```

### Cách gọi Namespace
```sql
SELECT * FROM <tên_catalog>.<tên_schema>.<tên_table>
-- VD: prod.silver.cleaned_users
```

## ⚖️ 4. Phân Biệt Các Khái Niệm Dễ Nhầm Lẫn

| Dạng Quyền | Ý Nghĩa Thực Sử (Quan Trọng để hiểu đề bài thi) |
| :--- | :--- |
| **`USAGE`** | Cấp cho đối tượng Catalog/Schema. Là vé "Thông cửa" đi qua cổng, chưa thể truy vấn được Tên bảng nếu k có nó. |
| **`SELECT`** | Được phép thực hiện "Read" và "Query". |
| **`MODIFY`** | Được phép UPDATE/DELETE/INSERT/MERGE xuống dòng dữ liệu của Bảng. (Không thể Drop Table vì hỏng Schema). |
| **`ALL PRIVILEGES`** | Overkill (Chúa tể). Đi thi hiếm khi nào xài đáp án này do bị Lợi dụng phân quyền quá mức. |

## ⚠️ 5. Cạm Bẫy Đề Thi & ExamTopics

- 🚨 **Bẫy Nhận Diện Chủ Sở Hữu (ExamTopics Q22):** Đề bảo bị cấm truy cập vào Bảng `prod.abc.xyz`. Làm sao kiếm ai là chủ để request access?
  - Chọn: Mở giao diện Data Explorer (Catalog Explorer), xem **Review Owner field** trực tiếp ở chỗ info của đối tượng đó.
  - Bẫy: Tab "Permissions" (chỉ liệt kê người đã được cấp, không phải ai cũng là Owner).
- 🚨 **Bẫy Cấu Trúc Metastore / Catalog Location (ExamTopics Q89):** Mệnh đề nào đúng về Metastore? (Chọn 2)
  - ✅ "1 metastore per account per **region**" (Đúng - Mỗi region có 1 Metastore).
  - ✅ "If metastore has no location, **catalog MUST have managed location**" (Đúng - Nếu cha không có thư mục lưu trữ thì con bắt buộc phải có để chứa data).
- 🚨 **Bẫy Cấp Quyền Đọc View vs Underlying Table (ExamTopics Q61):** 
  - Tình huống cấp quyền đọc View che số điện thoại nhưng CẤM đọc bảng gốc (Bảng chứa thông tin nhạy cảm).
  - Trong Data Explorer / Câu thi chuẩn: Bạn cấp quyền **SELECT on VIEW**. Phía Databricks Unity Catalog tự động xử lý quyền mà không cần ép cấp quyền `SELECT` lên bảng gốc.
- 🚨 **Bẫy Quyền Tối Thiểu - Least Privilege (ExamTopics Q197):** Data Analyst muốn "query tables but not modify data". Chọn quyền nào?
  - Chọn **SELECT** (Quyền đọc tối thiểu).
  - Bẫy: Đừng chọn ALL PRIVILEGES, hay MODIFY.
- 🚨 **Bẫy Quản Lý External Storage Bảo Mật (ExamTopics Q195):** Làm sao quản lý an toàn, gọn nhất cho ti tỉ cái external tables khác nhau?
  - Chốt ngay: **Use Unity Catalog to manage access controls** (Tạo external location/Table trên UC rồi phân quyền trực tiếp ở mức Table).
  - Bẫy: Đừng chọn ACLs của AWS/Azure (Cấp mây quá rộng) hoặc Identity Access gắn cứng vào Workspace (không tập trung).
- 🚨 **Bẫy DROP TABLE - Managed vs External (ExamTopics Q106, Q107):** 
  - `DROP TABLE` mà bay màu LUÔN cả FIle Dữ Liệu ở bộ nhớ mây -> Đó là bảng **Managed**. 
  - External table rớt bảng thì chỉ mất Metadata, data trên mây vẫn còn nguyên.

## 🌟 6. Khung Tư Duy (Deep Dives)

### Kiến Trúc Unity Catalog 3 Tầng Khuôn Mẫu (3-Level Namespace)
- Kể từ UC, truy vấn bảng luôn gọi theo định dạng: `[catalog].[schema].[table]` (Ví dụ: `SELECT * FROM prod.sales.customers`).
- **Catalog:** Thường chia theo Environment (dev, staging, prod) hoặc theo Business Unit (Finance, HR).
- **Schema (Database):** Cấp chia module chức năng nghiệp vụ (ví dụ: `sales`, `marketing`).
- (Tuyệt đối quan trọng khi thi: Nếu bạn không có quyền `USE CATALOG` hoặc `USE SCHEMA`, bạn sẽ không thể với tay được tới Table bên trong dù cho bạn có quyền SELECT trên Table đó).

### Managed Table vs External Table
- **Managed Table:** Databricks tự quản lý tuốt luốt đường dẫn lưu trữ. Phù hợp cho đa số nhu cầu, vì nó sinh, sát, dọn rác dính liền nền tảng.
- **External Table:** Data nằm ngoài khu quy hoạch của Databricks (VD: Data team khác đẩy về bucket AWS S3 riêng). Databricks tạo Storage Credential và External Location để "ngó" sang và bọc lại bằng 1 lớp vỏ Table. Khi xóa vỏ Table của Databricks, Data gốc nhà người ta không bị gì.

### Quản Trị Quyền 
- Áp dụng nguyên tắc **Least Privilege:** Cho nhiêu xài nhiêu.
- View-based Access: Kỹ thuật tốt nhất để che cột (Redact data) -> Tạo View mới `SELECT id, name, "****" as phone FROM users` -> Cấp quyền SELECT trên view đó.

## 🔗 7. Official Docs Tham Khảo

- **Unity Catalog Docs:** [What is Unity Catalog?](https://docs.databricks.com/en/data-governance/unity-catalog/index.html)
- **Manage Privileges (Tạo quyền):** [Unity Catalog privileges](https://docs.databricks.com/en/data-governance/unity-catalog/manage-privileges/index.html)
