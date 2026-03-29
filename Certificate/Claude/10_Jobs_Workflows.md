# 10. Jobs & Workflows (Lakeflow orchestration)

## 🎯 1. TL;DR
- **Databricks Jobs**: Hệ thống lập lịch và điều phối (Orchestration) gốc, dùng để sâu chuỗi các Task (Notebook, Python scripts, SQL, DLT...) lại với nhau tạo thành **DAG** (Task phụ thuộc lẫn nhau).
- Ghi điểm cực kì dễ với khái niệm: **Cron Scheduler**, **Repair failed tasks**, và Khái niệm **Job Cluster**.

## 🧠 2. Bản Chất Sự Khác Biệt (Core Concepts)

- **DAG / Task Dependencies**: Chỉ định "Task B CHỈ CHẠY khi Task A xong" (Depends On). Cho phép Databricks tự phân luồng nhánh nếu có Task chạy song song tiết kiệm tời gian.
- **Job Cluster**: Mỗi một luồng Job nên sử dụng Compute loại `Job Cluster` (Trừ khi nó cần giao tiếp nhanh). Lý do giá Compute cực rẻ và nó "chạy xong rồi tự tắt hoàn toàn ngay lập tức".
- **Task Values**: Databricks không support truyền Dataframe qua lại bằng RAM trực tiếp giữa các Task vì mỗi Task chạy trong một Isolation Node khác. Nhưng nó có thể pass "các biến nhỏ" dạng `Strings/Int` như (Trạng thái Status, Tổng số dòng đếm được `count`) xuống cho Task phía sau thông qua tính năng Task Values.

## ⌨️ 3. Cú Pháp Bắt Buộc Nhớ (Code Patterns)

### Cron Syntax Thường Gặp (Hiểu Cấu Trúc Cơ Bản)
Bộ máy đặt lịch chạy Workflow trên Databricks dùng chuẩn CRON: `Phút - Giờ - Ngày/Tháng - Tháng - Ngày/Tuần`:

```text
Từ trái qua phải (5 tham số):
* * * * *   : (Mỗi Phút chạy một lần)
0 6 * * *   : (6 giờ 00 phút sáng mỗi ngày)
0 0 1 * *   : (Ngày 1 đầu tháng, lúc 00:00 midnight)
```

## ⚖️ 4. Phân Biệt Các Khái Niệm Dễ Nhầm Lẫn

| Khái Niệm Phục Hồi | Hành Vi Cách Chạy Lại | Best Practice Nào Tốt Cho Prod? |
| :--- | :--- | :--- |
| **`Run Now` / Rerun** | Chạy bạo lực lại TỪ ZERO toàn bộ Pipeline bất chấp trước đó đã chạy xong hay chưa. Dài dẵng và cực kì Tốn Tiền. | Không nên dùng khi luồng dài. |
| **`Repair Run`** | Thần thánh. "Lúc nãy Lỗi ở Task nào, Sửa code rồi chỉ CHẠY TIẾP ĐÚNG TỪ ĐIỂM FAIL TASK ĐÓ" hoặc các task chưa chạy. | Là tính năng bắt buộc phải nắm khi Failed. Giảm thiểu chi phí kinh khủng. |

## ⚠️ 5. Cạm Bẫy Đề Thi & ExamTopics

- 🚨 **Bẫy Scheduling (ExamTopics Q27):** Đề hỏi *"How to schedule a pipeline programmatically?* -> Đáp án là dùng **Cron syntax** (đáp án D). Đừng để bị lừa chọn DateType hay TimestampType.
  - Nếu đề hỏi làm sao thiết lập chạy 2AM mỗi ngày qua giao diện -> Chọn dùng tool **Jobs/Workflows UI**.
- 🚨 **Bẫy Restart / Repair Lỗi Mạng (ExamTopics Q175):** Job chạy 3 tiếng, Task cuối bị gãy do rớt mạng hoặc sai code. Kỹ sư đã fix code xong. 
  - Đề hỏi: "Làm sao hạn chế tối đa tốn Time, Cost và tính toán lại? (Minimize redundant computation)".
  - Đáp án chắc chắn là click nút: **Repair the task** (Repair run). Lệnh này cho phép chạy lại đúng node/task bị lỗi (và các task downstream của nó) thay vì chạy full toàn bộ pipeline từ đầu (Full rerun).
- 🚨 **Bẫy Dependency (ExamTopics Q128):** Đề cho 1 task `ThườngLệ` đang chạy. Giờ yêu cầu phải chạy task `DữLiệuMới` **TRƯỚC** task `ThườngLệ` đó.
  - Cần chỉnh cấu hình như nào? -> Mở setting của task `ThườngLệ` cũ lên, **THÊM `DữLiệuMới` vào trường "Depends on" của nó**.
  - (Dịch ngược: `ThườngLệ` *phụ thuộc vào* `DữLiệuMới`, tức là đợi DữLiệuMới xong mới chạy).
- 🚨 **Bẫy Chọn Cluster Cho Jobs (ExamTopics Q193):** Đề hỏi "Daily ETL resource-intensive, workload thay đổi, cần auto scale và tiết kiệm chi phí".
  - Đáp án là **Job Cluster** (Hay Automated Cluster). 
  - Lý do: Compute được tạo riêng rẽ cho mỗi Run, chạy xong tắt ngay (Ephemeral) -> Tối ưu chi phí nhất cho batch theo lịch. Quanh năm không tốn tiền nuôi cluster 24/7 (All-purpose cluster). 
- 🚨 **Bẫy Continuous vs Scheduled (ExamTopics Q60):** 
  - **Scheduled (Theo lịch):** Cluster chỉ bật khi đến giờ chạy, chạy xong sẽ tắt -> Tiết kiệm, dùng cho Batch.
  - **Continuous (Liên tục):** Workflows sẽ giữ Cluster "SỐNG" liên tục 24/7, hễ sập là tự bật lại -> Tốn tiền, chỉ dùng cho độ trễ siêu thấp (Low Ops Streaming). Đi thi ưu tiên chi phí thì tuyệt đối né Continuous trừ khi đề bảo "realtime / ms latency".

## 🌟 6. Khung Tư Duy (Deep Dives)

### Trình Tự Tư Duy Về Databricks Jobs
- **Bài toán:** Databricks Job/Workflow không chỉ là "Hẹn giờ chạy code", nó là hệ thống quản lý Đồ thị luồng công việc (DAG - Directed Acyclic Graph) cực kỳ mạnh mẽ.
- Đề thi thường xoay vòng quanh 3 trục chính của Workflow:
  1. **Dependency Logic:** Task nào chạy trước, task nào chạy sau (`Depends On`).
  2. **Scheduling / Compute:** Chạy bằng Cluster loại gì cho rẻ? (Job cluster luôn thắng All-purpose) Chạy bằng trigger nào? (Cron / Continuous / File arrival).
  3. **Vận hành & Recovery:** Khi sập thì nút `Repair` thần thánh hoạt động ra sao để tiết kiệm tiền (chỉ chạy lại những chỗ chưa thành công).

### Task Values (Chia sẻ tham số giữa các Task)
- Trong một Workflow, nếu Task 1 muốn truyền 1 cái Flag, một biến số đếm nhỏ (ví dụ số dòng đã xử lý) xuống cho Task 2, thì dùng tính năng **Task Values**.
- **Chống chỉ định:** Đừng dùng Task Values để truyền cả một file dung lượng lớn hoặc bảng dữ liệu qua lại (Data Transport). Hãy lưu bảng xuống bộ nhớ (Delta Table) rồi truyền đường link hoặc name sang.

## 🔗 7. Official Docs Tham Khảo

- **Khái niệm chung Workflows:** [Databricks Workflows](https://docs.databricks.com/en/jobs/index.html)
- **Truyền Task Values:** [Communicate between tasks](https://docs.databricks.com/en/jobs/task-values.html)
