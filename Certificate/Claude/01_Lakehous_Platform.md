#databricks/claude 

# 1. Lakehouse Platform & Compute

## 🎯 1. TL;DR
- **Lakehouse**: Kết hợp sự linh hoạt/rẻ của Data Lake (Cloud Object Storage) và tính tin cậy/ACID của Data Warehouse (Delta Lake).
- **Core Architecture**: Tách biệt rõ ràng **Control Plane** (Databricks quản lý backend) và **Data Plane** (Tài nguyên tính toán thực thi trên cloud của khách hàng).
- **Compute Strategy**: Câu hỏi thi luôn xoay quanh việc chọn đúng loại Cluster cho đúng workload để tối ưu chi phí và hiệu năng.

## 🧠 2. Bản Chất Lý Thuyết (Core Concepts)

### Kiến Trúc Control Plane vs Data Plane
- **Control Plane**: Nơi Databricks duy trì các dịch vụ web application, notebook UI, Job Scheduler, Unity Catalog metadata, và quản trị workspace. (Nằm trên tài khoản Cloud của Databricks).
- **Data Plane**: Nơi thực sự xử lý dữ liệu. Gồm các Spark Clusters chạy trên VPC/VNet của bạn (khách hàng) và truy xuất dữ liệu từ Object Storage (S3/ADLS/GCS) của chính bạn. Dữ liệu của bạn KHÔNG bị đưa về Control Plane.

### Cluster Pools & Auto Termination
- **Cluster Pool**: Duy trì sẵn một tập hợp các máy ảo (EC2/VM) ở trạng thái "standby" (idle). Khi một Job / Cluster khởi động, nó lấy luôn máy từ Pool (mất vài giây) thay vì xin cấp phát từ Cloud Provider (mất vài phút). Giảm đáng kể "cluster start time".
- **Auto Termination**: Tự động tắt cluster sau X phút không có hoạt động, giúp tiết kiệm chi phí. (Cực kì quan trọng với All-Purpose xài chung).

## ⌨️ 3. Cú Pháp Bắt Buộc Nhớ (Code Patterns)

*Chương này chủ yếu nghiêng về khái niệm kiến trúc hơn là code. Trọng tâm là việc phân bổ workload:*

- **All-Purpose Cluster**: Giao diện UI, tạo thủ công -> Bật chức năng `Auto Termination` (Vd: 120 phút).
- **Job Cluster**: Tạo ra thông qua Databricks Jobs (Workflow) -> Chạy xong tự hủy (Không cần Auto Termination).
- **SQL Warehouse**: Khởi chạy qua menu SQL -> Có `Serverless` (khởi động tính bằng giây) và `Auto Stop` mặc định thấp (Vd: 10 phút) để tối ưu cost.

## ⚖️ 4. Phân Biệt Các Khái Niệm Dễ Nhầm Lẫn

| Loại Compute | Đặc điểm nhận dạng | Use Case trong Đề thi |
| :--- | :--- | :--- |
| **All-Purpose Cluster** | Đắt hơn (Premium DBU), chạy liên tục, share được. | Phân tích ad-hoc, kĩ sư viết code/debug trên Notebooks. |
| **Job Cluster** | Rẻ hơn (Job DBU), ephemeral (chạy xong hủy ngay). | Chạy ETL pipelines ban đêm, scheduler tự động. |
| **SQL Warehouse** | Tối ưu riêng cho engine SQL (Photon), không chạy PySpark/Scala. | Phân tích BI (Tableau/PowerBI) và chạy Databricks SQL queries. |
| **Serverless Compute** | Không cần quản lý infra, scale tức thì trong giây. | Cần Zero-management, hoặc dashboard BI cần phản hồi ngay (startup cực nhanh). |

## ⚠️ 5. Cạm Bẫy Đề Thi & ExamTopics

**1. Job Cluster vs All-Purpose (Q193)**
- 🚨 **Trap**: Dùng All-Purpose cho Automated Job / Lịch trình (Scheduled).
- **Đáp án**: Chuyển sang **Job Cluster** (rẻ hơn, tự scale, chạy xong tự hủy). Tránh bẫy dùng Serverless SQL cho ETL notebook hoặc All-Purpose cho Pipeline.

**2. Tối Ưu Thời Gian Khởi Động (Q127)**
- 🚨 **Trap/Q127**: "Job có nhiều task, cluster start lâu quá".
- **Đáp án**: Dùng **Cluster Pools** (duy trì sẵn VM idle). Tránh các bẫy: bật Autoscale, đổi sang Serverless (đề đang hỏi Job clusters).

**3. Tối Ưu Chi Phí Idle (Q90)**
- 🚨 **Trap/Q90**: "Minimize running time of SQL endpoint for daily dashboard refresh".
- **Đáp án**: Bật **Auto Stop** (tự tắt khi hết query). Tránh bẫy nhầm với Auto Termination của All-purpose.

**4. Serverless Hỗ Trợ Gì, Khi Nào Dùng? (Q180, Q191, Q192)**
- 🚨 **Q191**: "Cần đáp ứng SLA cao + minimal ops overhead" -> **Serverless** (Databricks tự tối ưu cluster, zero management).
- 🚨 **Q180**: Serverless hỗ trợ ngôn ngữ nào -> **SQL và Python**. Không tối ưu liền khối cho Scala/Java.
- 🚨 **Q192**: Migrate sang Serverless thì ưu tiên loại nào trước cực kì an toàn? -> **Low frequency BI + adhoc SQL** (ít risk).

**5. Single Source of Truth (Q29)**
- 🚨 **Trap**: Analyst và DE ra số khác nhau do kiến trúc silo.
- **Đáp án**: Lakehouse giải quyết bằng **Single Source of Truth** (Dữ liệu quy về một mối duy nhất).

**6. Boundary Dữ Liệu (Control vs Data Plane)**
- 🚨 **Trap**: Đề hỏi mã code thực thi hay dữ liệu lưu ở đâu -> **Data Plane** (trên máy/VPC của bạn). Control Plane chỉ giữ metadata, workspace UI và Job scheduler.

## 🌟 6. Khung Tư Duy Xử Lý Tình Huống

- **Nguyên lý gốc**: (1) Workload nào -> (2) Ưu tiên gì (Start nhanh hay Rẻ) -> (3) Chọn Compute. Đừng chọn compute theo "tên sang chảnh".
- **Không học thuộc lòng con số**: Thời gian start hay giá DBU sẽ thay đổi theo region/cloud, chọn giải pháp dựa trên kiến trúc (VD: Pool *nhanh hơn* cold start, nhưng *tốn* chút tiền standby).
- **Phạm vi Serverless**: Đọc docs tuỳ thuộc là SQL Warehouse Serverless hay Job Serverless vì giới hạn (ngôn ngữ, tính năng) có thể lệch nhau.

## 🔗 7. Official Docs Tham Khảo
- **Deep Dive**: [[01_Databricks#2. KIẾN TRÚC TỔNG THỂ|Kiến Trúc Tổng Thể]] | [[01_Databricks#3. COMPUTE LAYER|Compute Layer]]
- **Docs**: [Getting Started Concepts](https://docs.databricks.com/en/getting-started/concepts.html)
- **Docs**: [Compute Serverless](https://docs.databricks.com/en/compute/serverless.html)
