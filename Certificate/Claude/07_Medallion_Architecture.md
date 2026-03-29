# 07. Medallion Architecture

## 🎯 1. TL;DR
- **Medallion Architecture**: Là mô hình tư duy chia tầng dữ liệu (Data Layers) tiêu chuẩn của Databricks nhằm biến dữ liệu "bẩn" (Raw) thành Dữ liệu "Vàng" (Insight) qua 3 giai đoạn: **Bronze 🥉 -> Silver 🥈 -> Gold 🥇**.
- Mỗi tầng có trách nhiệm lưu trữ và mức độ làm sạch riêng biệt. Đề thi tập trung check xem bạn có hiểu thao tác nào thuộc về layer nào không.

## 🧠 2. Bản Chất Sự Khác Biệt (Core Concepts)

- **Bronze (Kho Nguyên Liệu)**: Tiếp nhận dữ liệu nguyên gốc thô (Raw) từ Source, "coppy-paste" Y XÌ ĐÚC (As-is) mọi thứ vào Data Lake.
  - Mục tiêu: Lưu vết lịch sử không bao giờ mất, tái tạo lại pipeline (Audit/Reprocessing) nếu Silver/Gold bị lỗi hỏng.
  - Quy luật: **Append-only** (Chỉ ghi thêm), **No Transform** (Không biến đổi, không xóa, không gộp).
- **Silver (Bảng Master Sạch)**: Nơi dòng đời dữ liệu bắt đầu sạch sẽ. Mỗi dòng định danh rõ ràng một thực thể (1 giao dịch, 1 khách hàng).
  - Mục tiêu: Chuẩn hóa Schema, lọc rác (Nulls), Đổi kiểu Type, và đặc biệt là **Deduplicate** (Tẩy trùng dòng lặp).
  - Quy luật: Filter, Clean, Join với reference data, Upsert (Merge).
- **Gold (Dashboard Ready / Aggregated)**: Kết tinh dành riêng cho Analytics và Business.
  - Mục tiêu: Tổng hợp (SUM, AVG, COUNT...) đáp ứng 1 KPIs, 1 Báo cáo của riêng lẻ một phòng ban nào đó.
  - Quy luật: Mọi Group by, Aggregate, tính toán Rule Business đều nằm ở đây.

## ⌨️ 3. Cú Pháp Bắt Buộc Nhớ (Code Patterns)

*Chương này chủ đề Architecture nên không có code cụ thể. Cần nhớ cách map nghiệp vụ vào các câu SQL tương ứng:*

```sql
-- Dấu hiệu của Bronze (RAW - JSON)
CREATE TABLE bronze_logs AS SELECT * FROM raw_json_path;

-- Dấu hiệu của Silver (DEDUPLICATE, CLEAN, CAST TYPES)
CREATE TABLE silver_logs AS 
SELECT DISTINCT CAST(id AS INT), UPPER(name) FROM bronze_logs;

-- Dấu hiệu của Gold (GROUP BY, SUM, KPIs)
CREATE TABLE gold_daily_metrics AS 
SELECT region, COUNT(*), SUM(sales) FROM silver_logs GROUP BY region;
```

## ⚖️ 4. Phân Biệt Các Khái Niệm Dễ Nhầm Lẫn

| Hành Động | Layer Phù Hợp Nào? | Tại Sao? |
| :--- | :--- | :--- |
| **"Raw data, nested json, unprocessed"** | 🥉 Bronze | Giữ nguyên gốc, chưa rạch/làm phẳng. |
| **"Filtered, Type-casted, Cleansed master data"** | 🥈 Silver | Dữ liệu chính dùng chung cho toàn bộ công ty sau khi đã sạch. |
| **"Deduplicated events" / Lọc trùng** | 🥈 Silver | Bẫy: Cứ nghĩ tẩy trùng là cao cấp nên tống vào Gold. Sai, Tẩy trùng là làm sạch -> Silver. |
| **"Summary, Aggregated, KPI, Dashboard"** | 🥇 Gold | Business Metric chỉ sinh ra từ việc Group by. |

## ⚠️ 5. Cạm Bẫy Đề Thi & ExamTopics

**1. Layer Matching / Bắt Cặp Chính Xác (Q159)**
- Đề bài yêu cầu bạn Map 3 Use-case vào 3 Layer. Hãy nhớ nằm lòng:
  - 🚨 **Bronze** ➞ **"Raw, As-is", "without transformations", "with a schema applied"**.
  - 🚨 **Silver** ➞ **"Clean, Queryable", "Master Customer Data", "Deduplicate"**.
  - 🚨 **Gold**   ➞ **"Summary, Aggregate", "Department report", "Business metric"**.

**2. Điểm Mù Về Dữ Liệu Bronze (Q182, Q50)**
- 🚨 **Trap**: Đề bẫy rằng Bronze "có ít dữ liệu hơn Raw do được lọc" hoặc "chứa clean data loại bỏ null values".
- **Đáp án**: Chắc chắn SAI. Bronze phải chứa BẰNG với dữ liệu gốc, chỉ là nó được tổ chức lại (có schema applied, có metadata load time). Tuyệt đối **không làm sạch (Cleaning)** tại lớp này, đó là việc của Silver.

**3. Quan Hệ Khối Lượng Bronze vs Silver (Q124)**
- 🚨 **Trap**: Hỏi về record count giữa các bảng.
- **Quy tắc**: Silver áp dụng quality filters/dedup nên thường có **record count ít hơn hoặc bằng Bronze**. Mọi câu khẳng định "Silver > Bronze" đều sai logic luồng chảy.

**4. Bẫy Tính Chất (Design Pattern vs Feature)**
- Medallion Architecture là một "Thiết kế khái niệm" (Design Pattern). Nó KHÔNG phải là một "Feature bật tắt" (Toggle) trong Databricks. Data Engineer tự tuân thủ bằng cách code và đẩy vào các Schema riêng biệt.

**5. Single Source of Truth cho Dashboard**
- 🚨 **Trap**: Marketing và Sales cãi nhau do Dashboard BI lệch số - giải pháp?
- **Khắc phục**: Trỏ tất cả Dashboard của tất cả phòng ban vào truy vấn cùng một bộ bảng duy nhất tại **Gold Layer**.

## 🌟 6. Khung Tư Duy (Deep Dives)

- **Tại sao cần Bronze nguyên bản?** Để "Time Travel / Replay" khi logic ở Silver hay Gold bị code sai dẫn đến hỏng table. Nếu drop mất Raw -> không có cái gốc để làm lại.
- **Silver là Mỏ neo**: Silver không chỉ là "bảng sạch". Nó là data contract cho cả doanh nghiệp. Nhiều Team khác nhau (BI, DS, ML) sẽ cùng lấy nguồn từ Silver để build các bảng Gold riêng.
- **Gold không luôn là Aggregation**: Mọi người hay nghĩ Gold = `GROUP BY`. Nhưng thực tế Gold có thể là Output phục vụ Inference ML (Features Table) hoặc bảng lọc theo miền (ví dụ: nguyên đống log Customer của Silver, tạo bảng Gold chỉ lấy các khách hàng ở vùng ASIA). 

## 🔗 7. Official Docs Tham Khảo
- **Deep Dive:** [[01_Databricks#8. LAKEFLOW DECLARATIVE PIPELINES|01_Databricks.md — Section 8]]
- **Docs:** [Medallion Architecture](https://docs.databricks.com/en/lakehouse/medallion.html)
