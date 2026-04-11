# 🚑 Bí Kíp Cai Nghiện AI & Vượt Ải Vòng 1 (HackerRank/CoderPad) Trong 3 Tuần

Bệnh "Teo cơ thuật toán" do dùng AI (Copilot/ChatGPT) quá nhiều là hội chứng chung của đại đa số dân Tech và DE hiện tại. Khi phỏng vấn Vòng 1 bằng máy chấm bị **Cấm Copy-Paste, Tab focus lock, Video record**, cảm giác "ngợp" và quên sạch syntax là chắc chắn xảy ra.

Tuy nhiên, Data Engineer **KHÔNG CẦN cày 700 bài LeetCode** như dân Backend/Competitive Programming. Bạn chỉ cần luyện đúng **Target** (Phạm vi hẹp) để lấy lại cảm giác gõ chay. Dưới đây là chiến lược "Rehab" trong vòng 3 tuần.

---

## 🎯 Phần 1: Tóm Gọn Phạm Vi Cần Học (Scope Reduction)

Máy chấm DE thường cho 3 bài (2 bài SQL Thời lượng 20p + 1 bài Python/DSA Thời lượng 25p). Đừng cày lan man!

### 1. Phạm vi SQL (Tập trung HackerRank Medium/Hard)
Nếu ôn SQL cho vòng 1, bạn chỉ xào đi xào lại đúng 4 trụ cột này (Tuyệt đối bỏ qua dăm ba cái `SELECT JOIN` cơ bản).
1.  **Window Functions Cực Nặng:** `ROW_NUMBER()`, `RANK()`, `DENSE_RANK()`, `LEAD()`, `LAG()`. (80% câu hỏi thi nằm ở đây).
2.  **Date/Time Manipulation:** Hàm trừ ngày `DATEDIFF`, trích xuyết `EXTRACT(MONTH FROM date)`. (Rất hay dùng tính Retention, Moving Average).
3.  **CTE & Recursive CTEs:** Tư duy bảng nháp `WITH tablename AS ()`. 
4.  **Self-Joins / Bẫy Kéo Bảng:** Dùng một bảng nối lại với chính nó (Ví dụ: Tìm User lương cao hơn sếp của mình).

### 2. Phạm vi Python/DSA (Tập trung LeetCode Easy/Medium mảng String & Dict)
1.  **Hash Map / Dictionary (Tần suất 90%):** Bài toán đếm số lần xuất hiện (Word Count), bài toán Two Sum, gom nhóm User theo Category. (Chỉ cần thuộc lòng `collections.defaultdict` và `Counter`).
2.  **String Parsing:** Cắt chuỗi mạn phép Regex (Log Parsing).
3.  **Two Pointers:** Bài kẹp 2 đầu (VD: Nhập 2 mảng Sorted thành 1, Check chuỗi Palindrome).
4.  **Sliding Window:** Giữ cửa sổ độ dài K chạy dọc (VD: Tìm tháng có doanh thu gom 3 ngày liên tiếp cao nhất).

*(Bỏ qua hẳn Graph phức tạp, Trees, Dynamic Programming 2D vì quá tốn thời gian mà DE hiếm khi bị hỏi)*

---

## ⏱️ Phần 2: Timeline "Cai Nghiện AI" (Chiến Lược Tập Trận)

### Tuần 1: Rì sét Não Bộ (Gõ Code "Chay" Mở Mắt)
- **Tắt sạch Copilot, Tabnine** trên IDE nội địa (VS Code / PyCharm).
- **Tuyệt chiêu:** Mở File Text thuần (hoặc mở tool web Leetcode) và giải lại các bài CỰC DỄ. 
- Mụch đích tuần này là để não bạn nhớ lại syntax (Quên mất mở For loop Python cần dấu `:`, quên cách khai báo Dictionary khởi tạo). Bạn sẽ bị ức chế, nhưng phải gõ chay lại cái syntax cơ bắp dăm ba lần.

### Tuần 2: Hack SQL Bằng Muscle Memory (Bộ Nhớ Cơ Bắp)
- Đăng nhập HackerRank. Tìm mục **SQL -> Dấu tick "Medium & Hard"**.
- Giải đúng 10 bài. Bài trọng tâm: 
  - *15 Days of Learning SQL (Khó vờ lờ, giải được là vô đối)*
  - *New Companies*
  - *Weather Observation Station Series* (Tập dượt Logic Toán).
- **Quy tắc luyện:** Gõ ra câu `SELECT FROM JOIN`... Cứ bí là check mạng, nhưng check xong thì **TẮT TAB MẠNG và phải GÕ LẠI BẰNG TAY** từ đầu đến cuối một cách cuồn cuộn.

### Tuần 3: Trận Giả (Mô Phỏng CoderPad)
Sự hoảng loạn hủy diệt khả năng code của bạn nhiều hơn là sự ngu dốt.
- **Tập gỡ Bug Error Text:** Trên máy chấm tự động, code lỗi nó sẽ ra dòng báo C++ / Python Traceback đỏ lòm. Dân quen xài ChatGPT hay ném cái Error đó lên GPT để nó sửa dùm. Do đó kỹ năng tự đọc Stack Trace của mắt bị đui mù.
- **Tập Thử:** Viết bài giải trên `pad.dev` hoặc Mở Leetcode tab ẩn danh. Set đồng hồ đếm ngược 40 phút. Đâm đầu vào giải và Cố tự đọc lỗi Traceback để sửa.

---

## 💡 Phần 3: Mẹo Qua Môn (Hack The Scanner)

Nếu trong phòng thi não quá trắng, không thể gõ ra Logic Toàn Mỹ (Optimal O(n)):
1. **Dùng Brute-Force Nhận Điểm Vớt:** Máy chấm test-case. Giữa việc Mất 30 phút rặn ra cách tối ưu rồi Bug và Việc 5 Phút viết 2 Vòng For lô-gích đè O(N^2) (Brute Force). Hãy **chạy Brute Force trước**. Ăn được 60/100 điểm testcase còn hơn dính 0 Điểm vì cấn lỗi Cú Pháp thuật toán cao siêu. Vòng 1 chỉ Đếm Điểm Qua Môn chứ Không Xét Học Sinh Giỏi.
2. **Comment "Phông Bạt":** Máy không biết đọc, nhưng vòng 1 có thể Senior DE sẽ review lại bài code của bạn. NẾU bạn chạy O(n^2) quá chuối, thì hãy Gõ Vào Code Dòng Comment: 
   `# I know Brute Force O(N^2) is bad. The optimal way is HashMap O(N) but facing time limit here. Logic is... ` (Tỏ ra nguy hiểm, cho thấy não có tư duy nhưng tay chậm).
3. **Python In-built Functions:** Tranh thủ học các hàm cứu sinh: `enumerate`, `zip`, `sorted(dict.items(), key=lambda x: x[1])`. Đỡ phải viết vòng lặp rườm rà.

---
**Kho Tài Liệu Tiếp Theo Bước Lên Live Code:** Khi não đã thông mạch, bạn dùng chính file `08_Vietnam_DE_Interviews.md` luyện nội công cho khâu Tech Review 1:1.
