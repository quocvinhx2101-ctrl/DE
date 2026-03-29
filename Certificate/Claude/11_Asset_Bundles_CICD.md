# 11. Asset Bundles & CI/CD (Databricks)

## 🎯 1. TL;DR
- **Databricks Asset Bundles (DABs)**: Công cụ IaC (Infrastructure as Code) gốc (native) của Databricks. Dùng để triển khai Pipelines, Jobs dựa trên định dạng YAML từ môi trường Dev lên Prod một cách bài bản thay vì click tay trên UI.
- **Git Repos**: Tích hợp Git ngay trên giao diện Workspace. Hỗ trợ Pull, Clone, Commit, Push nhưng **KHÔNG HỖ TRỢ MERGE**.

## 🧠 2. Bản Chất Sự Khác Biệt (Core Concepts)

- **DABs (Deployment Contract)**:
  - Cho phép định nghĩa một dự án lập trình với file trung tâm là `databricks.yml`.
  - Hỗ trợ thiết lập chia đa môi trường thông qua block `targets: dev, staging, prod`.
  - Có thể tự động đóng gói ứng dụng (Build Python Wheels/Artifacts) và ném lên cụm.
- **Git Repos trong Workspace**:
  - Nó là một công cụ "Lightweight client", cực kì hữu dụng để DE code và lưu Version Control cơ bản.
  - Tuy nhiên, Databricks KHÔNG PHẢI là một nhà cung cấp Git Host (như GitHub, GitLab). Mọi thao tác cần giải quyết xung đột mã nguồn (Merge Conflict), hay Review PR bắt buộc phải mở ứng dụng Github/Gitlab bên ngoài lên làm.

## ⌨️ 3. Cú Pháp Bắt Buộc Nhớ (Code Patterns)

### Cấu trúc cơ bản databricks.yml
```yaml
bundle:
  name: awesome_pipeline
  
targets:
  dev:
    default: true
    workspace:
      host: https://adb-dev.azuredatabricks.net
  prod:
    workspace:
      host: https://adb-prod.azuredatabricks.net
```

### Các CLI Lifecycle kinh điển
```bash
# 1. Kiểm tra cấu hình có lỗi cú pháp không (rất quan trọng trước khi push)
databricks bundle validate -t dev

# 2. Bắt đầu đẩy toàn bộ code và setup lên Workspace đích
databricks bundle deploy -t prod

# 3. Kích hoạt chạy nóng Job luôn từ máy trạm
databricks bundle run daily_etl_job
```

## ⚖️ 4. Phân Biệt Các Khái Niệm Dễ Nhầm Lẫn

| Tính Năng Git | Tác Vụ CÓ THỂ làm trực tiếp trên Databricks Repos UI | Tác Vụ BẮT BUỘC lên Github/Gitlab ngoài web làm |
| :--- | :--- | :--- |
| **Sử dụng Cơ Bản** | Clone (Kéo repo về), Push (Đẩy lên), Commit (Lưu điểm thời gian), Pull (Kéo mới), Switch branch (Đổi nhánh). | Tạo một Repository mới toanh từ đầu. |
| **Xung Đột Code** | Hiển thị cảnh báo conflict khi kéo về. | Giải quyết dòng nào đúng, dòng nào sai (Resolve Merge Conflicts), tạo Merge Request (MR). |

## ⚠️ 5. Cạm Bẫy Đề Thi & ExamTopics

- 🚨 **Bẫy Triển Khai Production Bài Bản (ExamTopics Q190):** Đề hỏi "Cách tiếp cận nào được khuyên dùng để tạo tự động Data Pipelines production nhất quán?". Hoặc: "Kỹ sư lưu mã ETL trên GitHub và cần triển khai workflow production theo best practice."
  - Đáp án chuẩn là: **Databricks Asset Bundles (DAB)** (hoặc dùng kết hợp GitHub Integration).
  - Bẫy: Đừng chọn "Databricks config API", "Làm tay qua UI" (khó scale), hoặc Terraform (chỉ chuyên về setup hạ tầng ban đầu, còn DAB thiết kế riêng cho deploy cụm data pipeline asset).
- 🚨 **Bẫy File Cấu Trúc Bắt Buộc Của DAB:** Để định nghĩa cho DAB hiểu cần triển khai đi đâu, khai báo cái gì, file duy nhất bạn CẦN THIẾT NHẤT LÀ **`databricks.yml`**. Bẫy hay hỏi "File nào đóng vai trò chính" -> Chọn file yaml này.
- 🚨 **Bẫy Thao Tác Git Ngoài UI Databricks:** Keyword "Which git operation MUST be performed OUTSIDE Databricks Repos / Git Folders?".
  - Đáp án là **Merge / Resolve merge conflicts** (Thao tác này bắt buộc phải thực hiện trên chính nền tảng Git remote như GitHub/GitLab).
  - Mọi thứ cơ bản còn lại: Commit, Push, Pull, Create Branch, Revert đều CÓ THỂ click trực tiếp từ giao diện Git Folders Databricks.

## 🌟 6. Khung Tư Duy (Deep Dives)

### Databricks Asset Bundles (DAB) Hoạt Động Ra Sao?
- **Triết lý (Declarative):** Thay vì tạo Job bằng tay, thao tác Pipeline trên UI lặp đi lặp lại (dễ bị lệch môi trường, human error), thì mọi thứ được khai báo bằng Code (Infrastructure/Data as Code - viết trong file `databricks.yml`).
- DAB đóng vai trò như một **contract (hợp đồng)**: Nó gom toàn bộ file mã nguồn script (`.py`, `.sql`) cộng với cụm file cấu hình tạo nên 1 Bundle. Hệ thống CI/CD/Dev sẽ bê nguyên cái Bundle đó quăng lên môi trường (Dev/Staging/Prod) cực kì chuẩn xác và tái lập cao.
- **Nguyên tắc CI/CD chuẩn cho Bundles:** Validate -> Deploy -> Run. (Đừng bao giờ bỏ qua bước validate, luôn check file yaml config hợp lệ trước khi đẩy đi).
- *(Lưu ý: Bạn có thể gặp cái tên cũ "Databricks Bundles" hoặc tên hiện tại "Databricks Asset Bundles", chúng là một).*

### Git Repos (Databricks Git Folders)
- Là công cụ đồng bộ hóa Workspace cục bộ ở Databricks với repo Git thông thường.
- Mọi người thường dùng workflow: Code trực tiếp trong workspace vào branch cá nhân -> Chạy kiểm tra local -> Khi xong thì push lên Git remote (GitHub/GitLab) -> Tạo Pull Request. GitHub Actions lúc này có thể gọi `databricks bundle deploy` đẩy qua môi trường Staging.

## 🔗 7. Official Docs Tham Khảo

- **Databricks Asset Bundles:** [What are Databricks Asset Bundles?](https://docs.databricks.com/en/dev-tools/bundles/index.html)
- **Git Folders:** [Databricks Git folders (Repos)](https://docs.databricks.com/en/repos/index.html)
