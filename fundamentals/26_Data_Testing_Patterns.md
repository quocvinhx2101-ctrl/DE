# 🧪 Data Testing Patterns & CI/CD

> "Pipeline chạy ra log SUCCESS không có nghĩa là data đúng. Bad data tệ hơn là không có data."

Phần này đi sâu vào các pattern test pipeline thực tế ở Production, xa hơn những bài test `not_null` hay `unique` cơ bản.

---

## 📋 Mục Lục

1. [Các Cấp Độ Testing Trong Data](#các-cấp-độ-testing-trong-data)
2. [Unit Testing Data Pipelines](#-unit-testing-data-pipelines-pytest)
3. [Data Diffing (Thay đổi cấp độ dòng)](#-data-diffing-so-sánh-dữ-liệu-khi-merge-pr)
4. [CI/CD cho Data](#-cicd-pipeline-cho-data)

---

## Các Cấp Độ Testing Trong Data

Giống như Software Engineering, Data Engineering cũng cần tháp testing:

1. **Unit Tests (Code level):** Test các UDFs, custom transformations bằng Pytest với giả lập (Mock) Dataframes. Chạy dưới 10 giây ở máy local.
2. **Data Tests (Data level):** Test dữ liệu thực tế (ví dụ `dbt test`). Chạy sau khi pipeline load data. Chạy mất vài phút ở Warehouse.
3. **Integration Tests (System level):** Đẩy batch sample data từ API/Kafka $\to$ Warehouse $\to$ Validate kết quả cuối.
4. **Data Diffing (Regression level):** "Thay đổi logic tính doanh thu này sẽ ảnh hưởng tới bao nhiêu dòng trong bảng Fact hiện tại?". Chạy ở CI lúc tạo Pull Request.

---

## 🕵️ Unit Testing Data Pipelines (Pytest)

> Đừng test pipeline bằng cách "chạy thử với DB prod rồi `SELECT` xem đúng không". Hãy viết Unit Test.

```python
# pipeline/transform.py
import polars as pl

def calculate_customer_ltv(df: pl.DataFrame) -\u003e pl.DataFrame:
    \"\"\"Tính Lifetime Value của khách hàng\"\"\"
    return (
        df.group_by("customer_id")
        .agg(
            pl.sum("revenue").alias("lifetime_value"),
            pl.count("order_id").alias("total_orders")
        )
        .filter(pl.col("lifetime_value") \u003e 0) # Lọc đơn hoàn trả
    )
```

**Unit Test với Pytest:**

```python
# tests/test_transform.py
import polars as pl
from pipeline.transform import calculate_customer_ltv

def test_calculate_customer_ltv():
    # 1. Arrange: Tạo Mock DataFrame siêu nhỏ
    input_data = pl.DataFrame({
        "customer_id": [1, 1, 2, 3],
        "order_id": [101, 102, 103, 104],
        "revenue": [50.0, 150.0, -20.0, 100.0]  # Khách 2 có revenue âm (được hoàn)
    })
    
    expected_output = pl.DataFrame({
        "customer_id": [1, 3],
        "lifetime_value": [200.0, 100.0],
        "total_orders": [2, 1]
    })
    
    # 2. Act: Chạy function
    result = calculate_customer_ltv(input_data)
    
    # 3. Assert: So sánh (Sort để rớt tính random)
    from polars.testing import assert_frame_equal
    assert_frame_equal(result.sort("customer_id"), expected_output.sort("customer_id"))
```
*Lợi ích:* Bắt được lỗi logic ngay lúc gõ code trên VS Code, không cần đợi Airflow hay dbt run tốn tiền cloud.

---

## 🔍 Data Diffing (So sánh dữ liệu khi merge PR)

> "Sếp hỏi: Em vừa sửa logic tính `is_active_user`. Có bao nhiêu khách hàng cũ dính thay đổi này?"

Chạy `dbt test` chỉ nói cho bạn biết code không bị lỗi syntax và data thoả mãn ràng buộc (not null, unique). Nó KHÔNG bào cho bạn biết bạn vừa lỡ xoá nhầm 2 triệu dòng của tháng trước.

**Data Diffing** là kĩ thuật dùng tool mã nguồn mở (như `data-diff`) để compare từng dòng giữa môi trường Prod và môi trường PR nhánh của bạn.

```bash
# Cài đặt data-diff
pip install data-diff

# So sánh bảng prod với bảng bạn đang sửa ở nhánh feature_a
data-diff \
  postgresql://user:pass@host/prod \
  postgresql://user:pass@host/dev \
  prod_schema.fact_orders \
  dev_schema.pr123_fact_orders \
  --key order_id
```

**Kết quả trả về ở Pull Request (qua GitHub Actions):**
```text
Data Diff Summary:
- 120,500 rows unchanged
- 50 rows deleted ❌ (CẨN THẬN: Bạn xoá mất 50 đơn hàng)
- 0 rows added
- 1,200 rows updated ⚠️ (Thay đổi giá trị cột `total_amount`)
```
*Senior Advice:* Cái này cứu mạng team Data rất nhiều lần trước khi merge code lên nhánh Main và đè data sai lên màn hình sếp.

---

## 🚀 CI/CD Pipeline cho Data

Cấu trúc một Github Actions / GitLab CI tiêu chuẩn cho DE Team:

```yaml
# .github/workflows/data_pipeline_ci.yml
name: Data Pipeline CI

on:
  pull_request:
    paths:
      - 'models/**'     # Khi sửa dbt models
      - 'pipeline/**'   # Khi sửa Python ETL

jobs:
  test_and_diff:
    runs-on: ubuntu-latest
    steps:
      # Step 1: Kiểm tra format code (Ruff / SQLFluff)
      - name: Lint Code
        run: |
          ruff check .
          sqlfluff lint models/

      # Step 2: Chạy Unit tests cho Python logic
      - name: Run Pytest
        run: pytest tests/

      # Step 3: Tạo "Slim CI" (Chạy dbt nhưng chỉ build những bảng bị sửa)
      - name: dbt Build Modified Models Only
        run: dbt build --select state:modified+ --defer --state ./prod-run-artifacts

      # Step 4: Chạy Data Diff và post comment vào PR
      - name: Data Diff
        run: |
          data-diff prod.orders dev_pr_${{ github.event.pull_request.number }}.orders \
          > diff_results.txt
          gh pr comment ${{ github.event.pull_request.number }} -F diff_results.txt
```

---

## 💡 Nhận định từ thực tế (Senior Advice)

- **Đừng viết test cho những thứ hiển nhiên:** Test column `id` là NOT NULL bằng dbt test thì tốt. Nhưng test xem hàm `SELECT UPPER(name)` có trả về chữ viết hoa không thì vớ vẩn. Hãy tập trung viết Unit Test cho những **Business Logic** phức tạp (cách tính thuế, logic tính điểm rating, rules phân loại spam).
- **Slim CI ở dbt là bắt buộc:** Khi bảng warehouse có 500 layers, mở 1 PR sửa 1 bảng cỏn con mà CI build lại nguyên cả 500 bảng thì mất 3 tiếng và chục đô tiền Snowflake. Bạn phải implement **dbt state deferral (Slim CI)** để nó chỉ build bảng bị sửa cộng với bảng con bị ảnh hưởng.
- **Tạo Sandbox Environment rẽ nhánh:** Giống AWS có dev/stag/prod, kho data cũng cần chia rẽ nhánh: khi developer A mở nhánh `feature/new_revenue_logic`, kịch bản xịn nhất là dbt tự động tạo 1 schema `dev_userA_pr123` clone từ prod (bằng tính năng Zero-copy clone của Snowflake/Iceberg) để test chạy cực nhanh và không tốn tiền lưu trữ thêm. Đừng bắt tất cả kĩ sư chạy chung một schema `dev`.
