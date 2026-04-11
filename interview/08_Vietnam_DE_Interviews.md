# 🇻🇳 Tuyển Tập Vàng Live Coding Data Engineer VN (Masterclass)

> Bản Masterclass Tuyệt Mật Dài 1.5k+ Dòng.
> Khác với LeetCode vòng vèo, các vòng thi **Live Coding / CoderPad / HackerRank** của khối ngành DE tại Việt Nam (Zalo, Shopee, VNG, VNPay, Momo, Big Banks) chú trọng cực độ vào khả năng: Bóc tách Data, Tối ưu RAM (Memory footprint), Join 2 tập Data không dùng hàm dựng sẵn, và Tư duy gỡ lỗi API. Dưới đây là tuyển tập **Full Solution Step-by-Step** được đúc kết từ hàng ngàn vòng phỏng vấn thực chiến.

---

## 📋 Mục Lục
### Phần 1: Python Core & Data Structures (Không dùng Pandas)
1.  [Đọc file TXT/CSV 100GB khi chỉ có 500MB RAM (Memory Yielding)](#bai-1-doc-file-100gb-voi-ram-ngheo-nan)
2.  [Merge 2 file Log khổng lồ đã Sort (Two Pointers)](#bai-2-merge-2-file-log-khong-can-load-vao-ram)
3.  [Đập phẳng mạng nhện JSON (Deeply Nested Flatten)](#bai-3-dap-phang-mang-nhen-json-voi-de-quy)
4.  [Xây Dựng Retry Decorator cho Giao Dịch Chập Chờn](#bai-4-decorator-retry-exponential-backoff)
5.  [Parsing Log Apache và đếm Top K IP phá phá nhất (Heap)](#bai-5-top-k-ip-dos-bot-voi-hash-map--min-heap)

### Phần 2: Pandas Data Manipulation Thực Chiến
6.  [Xử lý "Bể Bảng" (Unpivot/Melt) dữ liệu Chấm Công](#bai-6-chuyen-bang-rong-thanh-dai-melt-du-lieu-cham-cong)
7.  [Xử lý Bọt Bẩn (Fill Missing) bằng Trung Bình Cụm (Imputation)](#bai-7-impute-missing-values-thong-minh-theo-nhom)
8.  [Nối Chuỗi String Lịch Sử Hành Trình (Group Concat)](#bai-8-group-concat-gop-lich-su-di-chuyen)

### Phần 3: SQL Live Coding (HackerRank Hard Level)
9.  [Tính Retention Rate (T+1, T+7) Cohort Kinh Điển](#bai-9-sql-cohort-retention-rate-kinh-dien)
10. [Tính Running Total và Reset khi gặp Dấu mốc (Gaps & Islands)](#bai-10-gap-and-islands-tinh-streak-chuoi-thang)
11. [Recursive CTE: Truy vết Cây Gia Phả Cấp Trên](#bai-11-recursive-cte-truy-lo-gia-pha-nhan-su)
12. [Đỉnh cao SCD Type 2: Tra cứu Lịch Sử Khách Hàng Quá Khứ](#bai-12-slowly-changing-dimensions-type-2)

### Phần 4: PySpark Live Coding
13. [Thiết Kế Hàm Salting Chống Data Skew Bằng RDD/DF](#bai-13-salting-logic-tri-tieu-data-skew)
14. [Xử lý Late Data Sessionization Streaming](#bai-14-spark-structured-streaming-watermarking)

---

## 🐍 Phần 1: Python Core & Data Structures (Không dùng Thư viện)

*Quy tắc vòng VNG/Momo: Không cho Import Pandas. Ép xài Python thuần (Data Structures) để đánh giá khả năng hiểu lõi (Low-level memory handling).*

### Bài 1: Đọc file 100GB với RAM nghèo nàn

**Problem:** 
Log web server được dump ra 1 file CSV 100GB. Server chạy code chỉ cấp đúng 500MB RAM. Viết hàm đếm tổng số lượng dòng có `status_code == 200` mà không làm sập OS.

**Tư duy giải quyết (Analytical Thinking):**
- Không thể gọi `f.read()` hay `f.readlines()` vì nó nạp Trọn Toàn Bộ File String vào Heap Memory.
- Phải dùng cơ chế **Iterator / Generator** của Python. Khi chạy vòng for qua file object, Python sẽ thực hiện I/O Read buffer từng dòng 1, xử lí đếm, và vứt dòng đó khỏi RAM lập tức (Garbage Collected).
- Chú ý: Đề thi thường gài bẫy dòng bị lỗi hoặc Header rớt vào. 

**Step-by-step Solution:**
```python
def count_successful_requests(file_path: str) -> int:
    """
    Time Complexity: O(N) đi qua N byte của file.
    Space Complexity: O(1) chỉ tốn vài bytes cho con trỏ bộ nhớ (pointer) hiện hành.
    """
    total_200 = 0
    
    try:
        # Mở file với context manager để luôn đóng cẩn thận ráo trọi File Descriptor
        with open(file_path, 'r', encoding='utf-8') as f:
            # Mẹo: Đề phòng file CSV có header ở dòng đầu tiên, phải bóc nó ra
            header = next(f, None) 
            
            for line_number, line in enumerate(f, start=2):
                # Bẫy 1: Dòng trống lảng xẹt ở cuối file
                if not line.strip():
                    continue
                    
                # Phân tách string cơ bản (Cực kì nhẹ so với Regex)
                columns = line.strip().split(',')
                
                # Bẫy 2: Dòng bị rách nát (thiếu cột). Giả định cột status ở index 3.
                if len(columns) > 3:
                    status_code_str = columns[3].strip()
                    
                    if status_code_str == '200':
                        total_200 += 1
                        
    except FileNotFoundError:
        print("Lỗi I/O: Không tìm thấy đường dẫn log.")
        return 0
        
    return total_200

# Trả lời phụ thêm khi Interviewer chọc gậy bánh xe:
# Q: "Tốc độ đọc của Python quá chậm vì GIL limit. Em tính sao?"
# A: "Em sẽ chia file 100gb bằng Multiprocessing Chunk. Mở OS Seek() nhảy tới File Offset
# byte chunk, bắt các Process Worker xẻ Cày Đồng Thời. Đột phá tốc độ x10 lần."
```

---

### Bài 2: Merge 2 file Log Không Cần Load Vào RAM

**Problem:**
Bạn có 2 file log Text `app_log_A.txt` và `app_log_B.txt`. Cả 2 file ĐÃ ĐƯỢC SORT TĂNG DẦN theo thời gian (Timestamp nằm ở đầu mỗi dòng, cách nhau bằng dấu Tab `\t`). Mỗi file nặng 10GB.
Yêu cầu: Gộp 2 file này thành 1 file `merged_logs.txt` với thứ tự Time Tăng Dần. Không được RAM-Load.

**Tư duy giải quyết (Analytical Thinking):**
- Bắt buộc dùng Pattern **Two Pointers trong External Storage**. Mở 2 tay 2 File Handler cầm chừng.
- Con trỏ nào (File nào) có Timestamp nhỏ hơn thì thả dòng đó xuống Ổ Băng đĩa Ghi. Bóc cục dòng kế của tay đó lên chuẩn bị So Găng tiếp.
- Kỹ xảo: Nếu 1 tay xả hết bài trước, thì tay kia cứ điềm nhiên xúc nốt nguyên phần dư cuối cho nhanh chặn.

**Step-by-step Solution:**
```python
def extract_timestamp(line: str) -> float:
    """Hàm ruột tách lấy con Cọc Mốc Unix-time"""
    if not line:
        return float('inf') # Nếu đứt dây thì quăng Vô Tận Ngăn Cản
    parts = line.split('\t')
    return float(parts[0])

def streaming_merge_sorted_logs(file_a: str, file_b: str, out_file: str):
    """
    Time Complexity: O(N + M) với N M là số dòng 2 file.
    Space Complexity: O(1) Bám dính 2 String hiện tại trên Memory.
    """
    with open(file_a, 'r') as fa, open(file_b, 'r') as fb, open(out_file, 'w') as fout:
        # Bốc mồi dòng 1 của 2 họng
        line_a = fa.readline()
        line_b = fb.readline()
        
        # Vo vòng lặp Lưỡi cày đôi
        while line_a or line_b:
            ts_a = extract_timestamp(line_a)
            ts_b = extract_timestamp(line_b)
            
            # Ai non Nớt Thời Gian (Xảy ra trước) thì nhả Đạn First
            if ts_a <= ts_b:
                fout.write(line_a)
                line_a = fa.readline() # Xúc cục đá ngó mẻ mới
            else:
                fout.write(line_b)
                line_b = fb.readline()

# Interviewer Trick Check:
# - Lỡ 100 File thì sao? 
# -> A: Dạ em đẩy 100 File Handlers vào Min-Heap Priority Queue. 
# Bốc Nét nhả Nét (K-Way Merge Heap Sort). Cực Ngầu!
```

---

### Bài 3: Đập phẳng Mạng Nhện JSON với Đệ Quy

**Problem:**
Data App Mobile đẩy Event lên Kafka ở dạng Deeply Nested JSON với độ sâu vô hạn. Backend yêu cầu bẻ bẹt File về Mảng 1 Chiều.

Đầu vào:
```json
{
  "user": 12,
  "metrics": {
       "clicks": 5,
       "details": {
           "device": "iOS",
           "os_ver": "16.1"
       }
  }
}
```
Khát vọng vươn lòi:
```json
{
  "user": 12,
  "metrics_clicks": 5,
  "metrics_details_device": "iOS",
  "metrics_details_os_ver": "16.1"
}
```

**Tư duy giải quyết (Analytical Thinking):**
Trống gõ **Đệ Quy (Recursion) hoặc Stack-DFS**. Khi vướng phải Dictionary ngầm dưới rốn, ta Tự gọi lại chính ta, Bỏ thêm Dấu Vết nối liền (Mác Tên Tiền Tố Của Thằng Cha) vào cho Thằng con hưởng thụ. Chấm dứt Khi không còn con nào là Type `dict`.

**Step-by-step Solution:**
```python
def flatten_json_recursive(nested_dict: dict, prefix: str = "", separator: str = "_") -> dict:
    """
    Time Complexity: O(K) Quét trọn mọi Tế bào lá Nhánh.
    Space Complexity: O(De) Trong ĐÓ De là cấu trúc Mảnh ghép sâu (Depth). Ngốn Stack Call.
    """
    flat_store = {}
    
    for key, val in nested_dict.items():
        # Lắp Tên Họ Ghép Cha Truyền Con Nối
        new_key = f"{prefix}{separator}{key}" if prefix else key
        
        # Rẽ Nhánh
        if isinstance(val, dict):
            # Cú Ngoặt Đệ Quy Thần Sầu
            # Quăng con Mẻ Cửa Hàng con, đưa cái Tên Cha mới rèn xuống ép làm Cốt Cán
            sub_dict_flat = flatten_json_recursive(val, prefix=new_key, separator=separator)
            flat_store.update(sub_dict_flat)
        else:
             # Lõi Chạm Góc Ngã Tường
             flat_store[new_key] = val
             
    return flat_store
```

---

### Bài 4: Decorator Retry (Exponential Backoff)

**Problem:**
Viết Python xử lí Data lấy từ API KiotViet. Vì API yếu SL, cứ gọi trúng lúc đông là dính lỗi 503 Service Unavailable hoặc 429 Too Many Requests. Đề bắt buộc phải đính `Decorator` lên bất kỳ hàm nào muốn Retry 3 lần, mỗi lần Trễ gấp Đôi thời gian.

**Tư duy giải quyết (Analytical Thinking):**
Một Function bọc lấy Bịch Function Của Người khác là Definition của Decorator Trong Python. Phải xé Vách Phân Giải được Exception Quăng Lên.

**Step-by-step Solution:**
```python
import time
from functools import wraps

# Một Factory sinh Decorator (Nhận Tham Số Đầu Vào Cấu Hình)
def exponential_retry(max_retries=3, base_delay_seconds=2):
    def decorator_wrap(func):
        @wraps(func)
        def robust_wrapper(*args, **kwargs):
            # Tuần hoàn theo nhịp Đập của Retries
            for attempt in range(max_retries):
                try:
                    # Rống hàm Chính Phẩm
                    return func(*args, **kwargs)
                except Exception as critical_err:
                    print(f"Xảy ra thảm hoạ: {critical_err}. Đang dốc sức Gồng Lần {attempt + 1}")
                    if attempt == max_retries - 1:
                        # Hết đát Nguồn Cứu trợ, Chấp Nhận Thả Lỗi Sập Code
                        raise critical_err
                    # Quỷ Kế Nghỉ Giải Lao Tăng Độ Trễ Nguỵ Nhiễm (2s, 4s, 8s)
                    sleep_time = base_delay_seconds * (2 ** attempt)
                    print(f"Ngủ Sâu Tránh Động Tim {sleep_time} giây...")
                    time.sleep(sleep_time)
        return robust_wrapper
    return decorator_wrap

# Live Check:
import requests

@exponential_retry(max_retries=3, base_delay_seconds=1)
def fetch_api_shopee(url):
    response = requests.get(url, timeout=5)
    response.raise_for_status() # Bóp cò Văng Exception nếu Bị Chửi 50X/40X
    return response.json()
```

---

### Bài 5: Top K IP DDoS Bot Với Hash Map & Min-Heap

**Problem:**
Server ngập trong đống file Access Log Apache khổng lồ (IP Request Nằm la liệt). Đề HackerRank đòi Rút Tỉa Top 5 IPs Nằm Vạ Chày Cối Gõ Request Gây Nghẽn (DDos). Phải O(N log K).

**Tư duy giải quyết:** 
Vung đống Cát Lọc Map -> Kẹp Quét Qua Min Heap Size K.

**Step-by-step Solution:**
```python
import heapq
from collections import defaultdict

def top_k_malicious_ips(access_logs: list[str], k: int) -> list[str]:
    # Lược Đếm Thuật Tông O(N)
    freq_map = defaultdict(int)
    for log_line in access_logs:
        # Regex or Tẽ Chuỗi (Ví dụ Log "192.168.1.1 GET / HTTP 200")
        ip = log_line.split(" ")[0]
        freq_map[ip] += 1
        
    # Tạo Mâm Đựng Thúng Heap Size K
    # Heap in Python Mặc định là Min-Heap.
    min_heap = []
    
    for ip_str, freq in freq_map.items():
        # Đút vô Rổ (Đẩy tuple tần số nằm Trước để Heap Compare Bằng Số Đếm Tần Suất)
        heapq.heappush(min_heap, (freq, ip_str))
        
        # Cái Rổ Quá Béo Chật -> Quăng Kẻ Yếu nhất Vực (Lót Đáy Rổ)
        if len(min_heap) > k:
            heapq.heappop(min_heap)
            
    # Lấy chiến Tích ra Xắp Lại (Từ Heap Đang Lộn ngược min-heap -> Top Đỉnh Cao to nạc)
    # Lấy element thứ 1 (Chính là IP String) 
    return [item[1] for item in sorted(min_heap, reverse=True)]
```

---

## 🐼 Phần 2: Pandas Data Manipulation Thực Chiến

*Vòng thi Live Test của KMS Technology, Tiki, hay VNG rất chuộng ném cho ứng viên 1 cái DataFrame cực kỳ hiểm hóc, bắt xào nấu đập nặn móp méo dữ liệu trong 10 phút. Bắt buộc nhớ Cú Pháp Thần Chú đằng sau.*

### Bài 6: Chuyển Dạng Bảng "Bể" Rộng -> Dài (Unpivot / Melt) Dữ Liệu Chấm Công

**Problem:**
Nhân sự HR đưa file tính công Bằng Excel dãn nở ngang cực kì khốn khổ để Đẩy vào CSDL Quan hệ SQL:
Mỗi Column là một Ngày trong Tháng lôi ra Ngang Bè Bè `ID | Name | Day_1 | Day_2 | ... | Day_31`

| ID | Tên | Day_1 | Day_2 | Day_3 |
|---|---|---|---|---|
| 01 | QV | Nghỉ | Đi Làm | Nghỉ |

Chế tác Thành File Schema Dọc (Row-based) Chuẩn OLTP:
| ID | Tên | Ngày | Trạng Thái |
|---|---|---|---|
| 01 | QV | Day_1 | Nghỉ |
| 01 | QV | Day_2 | Đi Làm |

**Tư duy giải quyết:**
Hàm huyền thoại **pd.melt()** dùng để búng đũa bẻ cái Dàn Mảng Cột Ngang Đập Tàu thành Chiều Dọc. Khái niệm này gọi là Unpivoting.

**Step-by-step Solution:**
```python
import pandas as pd

def normalize_hr_timesheet(df: pd.DataFrame) -> pd.DataFrame:
    # Set Cột Bám Tường (Gắn Chết Chặt Cứng Rễ) - Những Cột Này Không Bị Cấn Cuộn Tròn Xuống
    id_vars_cols = ['ID', 'Tên']
    
    # Những Nhánh Lan Ra Sâu - Bị Chém Cúp Đưa Vô Bao Rọc (Cục Ngày)
    val_vars_cols = [col for col in df.columns if col.startswith('Day_')]
    
    # Bẻ Sập Thiết Kế Bằng Phép Melt Kinh Dị
    melt_df = pd.melt(
        df,
        id_vars=id_vars_cols,
        value_vars=val_vars_cols,
        var_name='Ngày',       # Tên Cột Đặt Hàng Mới của Vọng Cột Cũ Bị chặt khúc Đầu Cuộn Vào
        value_name='Trạng Thái'# Lõi Giá Trị Giữa Nằm Tròng Trọc
    )
    
    # Sort Tươi Theo Người Rồi Theo Trục Định Tuyến Khắc Chiều
    clean_df = melt_df.sort_values(by=['ID', 'Ngày']).reset_index(drop=True)
    return clean_df
```

---

### Bài 7: Xử lý Bọt Bẩn Bằng Imputation Trí Tuệ Theo Nhóm (Groupby Transform)

**Problem:**
Bảng dữ liệu Thu nhập bị dính `NaN` khuyết lổ chỗ.
Ông Sếp đòi Lấp Đầy Vùng NaN bằng Mức Lương Trung Bình (Mean) Của NHÓM NGÀNH của Nhân Viên Đó (Chứ không lấy Lương TB Cả Cty Bù bẩy).
VD: Khuyết Lương Kế Toán -> Lấy Lương TB Kế Toán Đắp Vô. Không Chơi Đắp Lương IT.

**Tư duy giải quyết:**
`df['salary'].fillna(df['salary'].mean())` Của Gà Chíp Sắp Die vì là Tính Mean Toàn Cục.
Sức Cuộn Thác `groupby('department')` Lồng hàm `transform` Sẽ Sinh Ra Một Mảng Rọi Vế (Reflection Array) Áp sát độ rộng Đúng Khấc Mọi Con Hươu Chạy Trong Cùng Bảng Gốc Nét Chuẩn Chỉ O(1) Ghép Chồng Lấp Đầy Map.

**Step-by-step Solution:**
```python
def handle_smart_smart_imputation(df: pd.DataFrame) -> pd.DataFrame:
    # Lambda X sẽ đại diện Bóc từng Khối Phòng Ban Ra Tay Gạt Một Cục
    # Điền Missing Value Của Đống Kế Toán Bằng Trị Số TB Kế Toán Nằm Sẵn Trong Lambda Vector
    df['salary_fixed'] = df.groupby('department')['salary'].transform(
        lambda x: x.fillna(x.mean())
    )
    
    # Nếu Mảng String Phân Rã Categorical (Chữ Viết - Thành Phố Chi Nhánh) bị Thiếu Nét Dữ Liệu
    # Áp Dụng Lấy Giá Trị Chễm Chẹo Nhiều Nhất Trồi Lên Sát Nách Gõ Trụ Đầu Tiên (Mode)
    df['branch_boc_phoi'] = df.groupby('department')['branch'].transform(
        lambda x: x.fillna(x.mode()[0])
    )
    
    return df
```

---

### Bài 8: Gom Chuỗi Ráp Nhau Sinh Hành Trình Lịch Sử (Group Concat)

**Problem:**
Cột Event Data là dòng Chảy: Trạng thái Đơn thay đổi. `12h: Đặt Đơn`, `14h: Chờ XN`, `16h: Giao Hàng`. Yêu cầu Gom Đập Cục Theo User Order. Nhồi nhét Đống Status Của Mỗi Mã Đơn Cụm thành Chuỗi Lắt Léo String Nối Nhau bằng Mũi Tên: `"Đặt Đơn -> Chờ XN -> Giao Hàng"`.

**Tư duy giải quyết:**
Dùng `groupby` + `agg()` với Logic Lắp Chuỗi Tự Biên Tự Diễn Bằng Lambda Join. Cực kì quan trọng phải SORT Data theo Thời Gian TRƯỚC KHI Groupby. Chứ không chuỗi Đơn Bay Đảo Lộn Chiều Nghĩa "Trứng nở Cóc Tía".

**Step-by-step Solution:**
```python
def tracking_status_history_compiler(df: pd.DataFrame) -> pd.DataFrame:
    # Nhất Tôn Chỉnh Mệnh: Sắp xếp theo ID và Giây Đồng Mốc Trị.
    sorted_df = df.sort_values(by=['order_id', 'timestamp_event'])
    
    # Nấu Kẹo Nhồi Nhanh
    history_df = sorted_df.groupby('order_id').agg(
        # Bắt Hàm Nhả Mũi Tên Áp dụng Join lên list dồn
        journey_path=('status_string', lambda x: ' -> '.join(x.dropna())),
        # Mở Rộng: Tính độ lớn Hành trình Tốn mấy Giây Cuốn Quét Mâm Đầu Trừ Cuối
        lead_time_duration=('timestamp_event', lambda x: x.max() - x.min())
    ).reset_index()
    
    return history_df
```

---

## 🗄️ Phần 3: SQL Live Coding (HackerRank Hard Level)

*Tại VN, đặc biệt là khối Banking (Techcombank, VPBank, MBBank) hay Ví Điện Tử (MoMo, VNPay), Vòng thi SQL qua HackerRank/CoderPad Thường Cấm Search Google và Ép làm trực tiếp 30 phút rớt Mạng. Bắt buộc nhớ Thuộc lòng.*

### Bài 9: SQL Cohort Retention Rate Kinh Điển

**Problem:**
Tính tỉ lệ giữ chân người dùng (Retention Rate) T+1 (Quay lại vào ngày hôm sau) của Cohort (Nhóm người dùng mới) theo từng ngày.
Cho bảng `user_activity (user_id, activity_date)`. 

**Tư duy giải quyết (Analytical Thinking):**
Bước 1: Tìm ra ngày vỡ lòng (Ngày Khai sinh/First Login) của từng User bằng `MIN()`. Đó gọi là Cohort Date.
Bước 2: Gắn cái rễ Cohort Date đó Ngược Lại vào Lịch Sử Hoạt Động (Join Self hoặc CTE). Tính độ chênh lệch Ngày Mới vs Khai Sinh (`DATEDIFF`).
Bước 3: `COUNT(DISTINCT user_id)` để lôi Tổng Mạng Gốc. Lọc các Cụ có Độ Chênh lệch = 1 để kéo Ra số Retained T1. Chia Tỉ số.

**Step-by-step Solution:**
```sql
WITH CohortOrigin AS (
    -- Bước 1: Tính First Event Date (Ngày cất tiếng khóc chào đời)
    SELECT 
        user_id,
        MIN(activity_date) AS cohort_date
    FROM user_activity
    GROUP BY user_id
),
ActivityWithCohort AS (
    -- Bước 2: Ghép Cohort Date rọi sang từng Sự kiện Click
    SELECT 
        u.user_id,
        u.activity_date,
        c.cohort_date,
        -- Tính Lệch Mốc. Ví dụ: MySQL xài DATEDIFF
        DATEDIFF(u.activity_date, c.cohort_date) AS day_gap
    FROM user_activity u
    JOIN CohortOrigin c ON u.user_id = c.user_id
),
CohortCounts AS (
    -- Bước 3: Gom Quân Đếm Tướng
    SELECT
        cohort_date,
        -- Lực lượng Nòng Cốt: Bao gồm tất cả (Khoảng Cách = 0 cũng được đếm)
        COUNT(DISTINCT user_id) AS total_joined_cohort,
        
        -- Kẻ Trụ Lại Ngày 1 (Gap = 1)
        COUNT(DISTINCT CASE WHEN day_gap = 1 THEN user_id END) AS retained_day_1,
        
        -- Mở Rộng: Kẻ Trụ Lại Ngày 7 (Gap = 7)
        COUNT(DISTINCT CASE WHEN day_gap = 7 THEN user_id END) AS retained_day_7
    FROM ActivityWithCohort
    GROUP BY cohort_date
)
-- Bước Xuất Hàng Tính Tỉ Lệ Tỉ Giá (%)
SELECT 
    cohort_date,
    total_joined_cohort,
    retained_day_1,
    ROUND((retained_day_1 * 100.0) / total_joined_cohort, 2) AS retention_t1_pct,
    ROUND((retained_day_7 * 100.0) / total_joined_cohort, 2) AS retention_t7_pct
FROM CohortCounts
ORDER BY cohort_date ASC;
```

---

### Bài 10: Gap and Islands (Tính Streak Chuỗi Thắng/Đăng Nhập)

**Problem:**
Tìm dải thời gian Cày Cuốc Liền Mạch (Chuỗi Đăng Nhập Liên Tục dài nhất) của 1 Gamer trên App Mobile. 
Bảng `login_log (user_id, login_date)`. Nếu nghỉ 1 ngày là Gãy Chuỗi (Island Bị vỡ bởi Gap).

**Tư duy giải quyết (Analytical Thinking):**
Con ác liệt nhất của Window Function (Tôn Sư Nặng Đô). 
Bởi vì Cột Date Tăng Dần (Mỗi ngày Login 1 lần), Còn Thằng Số Cắt Dòng `ROW_NUMBER()` cũng Tăng Dần (Mỗi Dòng Đếm 1 Bậc). 
Hễ Sự Cố Không Bỏ Lỡ Ngày Nào -> Bọn nó Tịnh Tiến Xong Hành. Khoảng Cách (Hiệu số Toán Trừ) Của Date Trừ Cho Số Row_Number Chắc Chắn Sản Sinh Ra Cùng Một Con Số Ma Thuật Liên Tục (Island Marker ID). Nếu Gãy 1 Ngày, Phép Trừ Văng Ra Kết Quả Nhóm Trừ Mới Tức Khắc. 

**Step-by-step Solution:**
```sql
WITH RawRanks AS (
    -- Tỉa hết Rác Đăng nhập 2 3 lần 1 ngày
    SELECT DISTINCT user_id, login_date
    FROM login_log
),
RankedLogins AS (
    -- Ban Vòng ROW_NUMBER Tịnh Tiến Sát Nách Ngày
    SELECT 
        user_id,
        login_date,
        ROW_NUMBER() OVER (PARTITION BY user_id ORDER BY login_date) as row_num
    FROM RawRanks
),
IslandMarker AS (
    -- Phép Trừ Ma Thuật Lấy Bậc Date Lùi Cho Số Rn_Number
    SELECT 
        user_id,
        login_date,
        -- Nếu SQL Server Cú Pháp Lùi Ngày: DATEADD(day, -row_num, login_date)
        -- Cú Pháp MySQL: DATE_SUB
        DATE_SUB(login_date, INTERVAL row_num DAY) AS island_group_id 
    FROM RankedLogins
)
-- Gom Ván, Thống Tướng Mỗi Đảo 
SELECT 
    user_id,
    MIN(login_date) AS streak_start_date,
    MAX(login_date) AS streak_end_date,
    COUNT(*) AS consecutive_days
FROM IslandMarker
GROUP BY user_id, island_group_id
ORDER BY consecutive_days DESC;
```

---

### Bài 11: Recursive CTE - Truy Lỗ Gia Phả Nhân Sự

**Problem:**
Công ty có Hệ Thống Affiliate Ngàn Cấp (Mô Hình Đa Cấp) hoặc Master Data Nhân Cấp `employees (id, name, manager_id)`. Vị Trí CEO Rễ Trần `manager_id IS NULL`. 
Viết Code MoMo móc nối Đẩy Nguyên Phả Hệ Cây Để Tìm Hết Thằng Cháu Chít Của Ông Trùm ID = 1.

**Tư duy giải quyết (Analytical Thinking):**
Giác ngộ Khái Niệm `WITH RECURSIVE`. Nhan Điện CTE Nó tự Gọi Lại Chính Nó. 
Cấu Trúc Bất Biến 2 Vế: Đầu Là Hạt Giống (Rễ 1). Nối Biển Kết `UNION ALL` Tới Cành Lá Bị Mắc Nợ.

**Step-by-step Solution:**
```sql
WITH RECURSIVE HierarchyCTE AS (
    -- Anchor Member (Khởi Tạo Điểm Xịt Ban Đầu)
    -- Giả sử Tìm Trùm Băng ID = 1
    SELECT 
        id, 
        name, 
        manager_id, 
        1 AS depth_level -- Bước Thang Lần 1
    FROM employees
    WHERE id = 1
    
    UNION ALL
    
    -- Recursive Member (Dây Chuyền Tiếp Tay)
    SELECT 
        child.id, 
        child.name, 
        child.manager_id,
        parent.depth_level + 1 AS depth_level -- Tăng Bậc Thang Cấp
    FROM employees child
    -- Thằng Đứng Sau Tra Móc Vai Thằng Cha Đứng Trống Trên Hàm CTE Ảo
    INNER JOIN HierarchyCTE parent ON child.manager_id = parent.id
)
SELECT * FROM HierarchyCTE
ORDER BY depth_level ASC;
```

---

### Bài 12: SCD Type 2 Query Lõi
**Problem:** Khách hàng thay hạng Thẻ Thành Viên (Bạc -> Bạch Kim). Trong DB chứa hàng Triệu Lịch xử Update dạng Chồng Layer Chặn Trục Thời Gian. 
Bảng `customers (user_id, tier, valid_from, valid_to)`. `valid_to` = '9999-12-31' là Tồn Hiện Tại Cõi đời. Yêu cầu Check Thời Điểm Nặng Bụng quá Khứ 2026-03-01 Khách Mốc đó Có Hạng Thẻ Nào?

**Step-by-step Solution:**
```sql
-- Cực Kì Đơn Giản, Nhưng Bọn Trẻ Hay Lúng Túng Dùng SubQuery Phức Tạp Lòi Rốn
SELECT 
    user_id,
    tier
FROM customers
WHERE user_id = 999 
    -- Nằm lắt léo Giữa 2 Bờ Khê Lãnh Diện
    AND '2026-03-01' >= valid_from 
    AND '2026-03-01' < valid_to;
```

---

## ⚡ Phần 4: PySpark Live Coding

*PySpark Live Coding test mức Staff Data Engineer ở các sàn E-Commerce Việt thường nhắm vào khả năng viết Hàm RDD/DataFrame tối ưu chứ không chuộng câu hỏi lý thuyết suông.*

### Bài 13: Salting Logic Triệt Tiêu Data Skew

**Problem:**
Em có 2 Bảng siêu to: `Transactions` (3 Tỷ Dòng) và `Users_Metadata` (500 Triệu Dòng). 
Cột `country_id` bị lệch cực đoan: 90% Giao dịch ở `VN`. Khi Join 2 bảng bằng `country_id`, Executor ôm Key `VN` bị ngộp thở (OOM), các Executor khác đắp chiếu. Viết Hàm Salting bằng PySpark DataFrame API để tản mác dữ liệu.

**Tư duy giải quyết (Analytical Thinking):**
- **Vấn đề:** Hash Partitioning của Spark quẳng Toàn bộ Data có chung Key `VN` vào thẳng 1 Cục Máu Đông (1 Partition / 1 Task). Executor nhai Cục Máu Đông Này Bị Ban Banh Ram.
- **Giải Pháp Salting:** Đổ Thêm "Muối" (Salt Array 1-10) vào Thượng Tầng.
  - Với Bảng Dịch Vụ Mẹ Bự chà bá (Transactions): Ta Bốc Random từ 1 đến 10 gắn thêm vào sau lưng của Chữ `VN` -> Nó sẽ đẻ ra `VN_1`, `VN_2`... `VN_10`. Spark tự đánh hơi thấy có Tới 10 Keys Lạ Lẫm Nên nó băm Nhỏ Data ra Gửi Cho 10 Executors khác nhau => Triệt Tiêu Cục Máu Đông.
  - Với Bảng Profile Nhỏ Hơn (Users_Metadata): Thằng Mua Phân Thân Làm 10 Mảnh, Thằng Bán Cất Giữ Thông Tin Phải `CŨNG PHÂN THÂN` y hệt 10 Mảnh Để Bảo Đảm Có Hàng Bán. Ta dùng Hàm `F.explode` để rải Đất Nhồi Bảng Users ra x10 Lần.

**Step-by-step Solution:**
```python
from pyspark.sql import SparkSession
import pyspark.sql.functions as F
from pyspark.sql.types import ArrayType, IntegerType

def skew_safe_salting_join(transactions_df, users_df, num_salts=10):
    """
    Kích Thước: Cứu Sống Cluster, nhưng đánh đổi Tốn Thêm Băng Thông Mạng x10 Lần
    cho Mảng Users. Thường dùng Khi Bảng nhỏ Không Thể Cân Nổi Broadcast.
    """
    
    # -------------------------------------------------------------
    # BƯỚC 1: XÁT MUỐI BẢNG LỚN (TRANSACTIONS) BẰNG RANDOM NOISE
    # -------------------------------------------------------------
    # Sinh ngẫu nhiên số từ 0 -> num_salts - 1
    # Thêm cột salt_id random
    t_salted = transactions_df.withColumn(
        "salt_id", 
        (F.rand() * num_salts).cast("integer")
    )
    
    # Chuốt gọt Key Trọng Tâm Bị Lệch 
    # Ví dụ: "VN" + "_" + "5" -> "VN_5"
    t_salted = t_salted.withColumn(
        "salted_country_id", 
        F.concat(F.col("country_id"), F.lit("_"), F.col("salt_id"))
    )

    # -------------------------------------------------------------
    # BƯỚC 2: PHÂN CHI BẢNG NHỎ TRẢI DÀI KHẮP NƠI BẰNG EXPLODE
    # -------------------------------------------------------------
    # Ép Bảng Users đẻ thêm 1 Cột Mảng Array [0, 1, 2, 3.. 9]
    u_array = users_df.withColumn(
        "salt_array", 
        F.array([F.lit(i) for i in range(num_salts)])
    )
    
    # Kéo nổ tung (Explode) Mảng Array -> Bảng Users Bị phình to gấp 10 lần Dòng
    u_exploded = u_array.withColumn("salt_id", F.explode("salt_array"))
    
    # Đúc Dập Key Đồng Dạng Trang Bị Đỡ
    u_exploded = u_exploded.withColumn(
        "salted_country_id", 
        F.concat(F.col("country_id"), F.lit("_"), F.col("salt_id"))
    )

    # -------------------------------------------------------------
    # BƯỚC 3: DỘI JOIN BẰNG CHÌA KHOÁ SALTED RỒI GỌT BỎ RÁC 
    # -------------------------------------------------------------
    joined_df = t_salted.join(
        u_exploded,
        on="salted_country_id",
        how="inner"
    )
    
    # Drop các Cột Trung Gian Ràng Buộc Trọng Thủy Mị Châu
    final_clean = joined_df.drop("salt_id", "salt_array", "salted_country_id")
    
    return final_clean
```

---

### Bài 14: Spark Structured Streaming Watermarking

**Problem:**
Shopee live streaming bão rồng event bắn vào Kafka. Mạng rớt nên Data Click User có thể Lạc Trôi Cập bến Muộn 2 tiếng. 
Sếp kêu: "Tính tổng Click theo cửa sổ 10 phút. Nếu máy của Khách Hàng bị đứt cáp quang, data trễ trong mức Chấp nhận 30 phút thì Đợi Để Cập Nhật. Trễ tận 1 tiếng thì Bỏ Luôn Đừng Tính Toán gây Lặng Nặng Hệ Thống". 
Viết Lệnh Live Struct Streaming.

**Tư duy giải quyết (Analytical Thinking):**
Rút đao **Watermarking** trong Spark Structured Streaming.
Lệnh này Mổ Phẫu Thuật Trên Time Windows:
- `window("timestamp", "10 minutes")`: Nhét Click Thời Điểm X vào Bao Tải X-10
- `withWatermark("timestamp", "30 minutes")`: Thiết Lập Mức Dâng Hồng Thuỷ Khống Chế Điểm Cũ (Late Data Limit). Spark Sẽ Vứt Dữ liệu Rớt Quá Mức Dâng Đi để rác không trích Bộ nhớ Trống State Management Nữa.

**Step-by-step Solution:**
```python
from pyspark.sql.functions import window

def live_aggregate_clicks(streaming_df):
    """
    Spark Vạch Ranh Giới Qua: 
    Max_Event_Time_Seen - Watermark_Threshold
    Nếu Mốc Max = 12h00
    Threshold = 30 mins
    Thì Nước dâng Tới Mức 11h30. Event Lọt Vào Chìa Khóa 11h25 -> Kick Văng (Drop)
    """
    click_aggregations = streaming_df \
        .withWatermark("event_time", "30 minutes") \
        .groupBy(
            window("event_time", "10 minutes"), 
            "user_id"
        ) \
        .count()
        
    return click_aggregations

# Demo Start Viết Xuống Storage (Bắt Buộc Trả Lời Vòng Phỏng Vấn Về Output Mode)
# Mẹo Gắt: Với Watermark, BẮT BUỘC PHẢI DÙNG APPEND HOẶC UPDATE MODE KHI XUẤT RA HỒ
def sink_streaming_pipeline(aggregated_df, output_path):
    query = aggregated_df.writeStream \
        .outputMode("append") \
        .format("parquet") \
        .option("path", output_path) \
        .option("checkpointLocation", f"{output_path}/checkpoint_dir") \
        .start()
        
    # Block Main Thread Bằng Await
    query.awaitTermination()
```

---

---

## 🌐 Phần 5: Data Integration & REST API (Thực Chiến Python Kéo Data)

*Ở Việt Nam, việc kết nối API bên thứ 3 (như Haravan, KiotViet, Sapo, GHTK, GHN, Shopee, Tiki) là cơm bữa. Yêu cầu lớn nhất của vòng Live Coding là: Phải xử lý phân trang (Pagination), chống sập mạng ngang xương (Connection Timeout), và tải dữ liệu siêu bự theo Chunk.*

### Bài 15: Generator Kéo Cạn API Bằng Phân Trang (Pagination Mượt)

**Problem:**
Em cần tải toàn bộ 1 triệu Đơn hàng từ API Haravan. Mỗi API gọi chỉ trả về tối đa 100 đơn (`limit=100`) kèm theo một cờ `has_next` và mã `next_cursor` (String mã hoá) để qua trang. Hãy viết hàm Python kéo cạn data từ API này mà không load cồng kềnh thành 1 Mảng Array 1 triệu phần tử trên RAM.

**Tư duy giải quyết (Analytical Thinking):**
- Sử dụng Parameterized API Requests.
- Vì không biết chính xác có bao nhiêu trang, vòng lặp `while True` là tối ưu nhất.
- Bứt phá Giới Hạn Bộ Nhớ bằng Hàm **Generator (Từ khoá `yield`)**. Ta sẽ trả về (Nhả ra) từng cục Chunk 100 đơn vị chứ không thâu tóm vào biến List `[]`. Điều này giúp tiết kiệm Memory tối đa ở phía ứng dụng gọi hàm. Khi Backend Database cắn đủ 100 đơn, tiến trình sẽ nhả tài nguyên RAM rảnh.

**Step-by-step Solution:**
```python
import requests
import time
from typing import Generator

def fetch_shopee_orders_generator(base_url: str, api_key: str) -> Generator[list, None, None]:
    """
    Kéo API với con trỏ con lăn Cursor-based Pagination.
    Time Complexity: Phụ thuộc vào Băng Thông Mạng API.
    Space Complexity: O(Page_Size) - Tối đa chỉ bế 1 trang trên RAM.
    """
    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json'
    }
    
    current_cursor = "" # Trống là Gọi Trang 1 đầu tiên
    page_count = 1
    
    while True:
        params = {
            'limit': 100,
            'cursor': current_cursor
        }
        
        try:
            # Luôn đặt Timeout để chống Móc Treo Deadlock (Thói quen Cân team Backend)
            print(f"Bắt đầu Vớt Lưới mẻ thứ {page_count}...")
            response = requests.get(base_url, headers=headers, params=params, timeout=10)
            response.raise_for_status() 
            
            data = response.json()
            orders_list = data.get("orders", [])
            
            # Nếu mẻ rỗng thì Ngưng cày lười
            if not orders_list:
                break
                
            # Đùn Đẩy Khạc mẻ lưới cho Vòng lặp Ngoại ăn
            yield orders_list
            
            # Chuyển Động Sang Trang Kế Tiếp
            paging_info = data.get("paging", {})
            has_next = paging_info.get("has_next", False)
            current_cursor = paging_info.get("next_cursor", "")
            
            if not has_next or not current_cursor:
                break
                
            page_count += 1
            
            # Ngủ Chống Cháy Rate Limit Server Shopee/Haravan (Cực kì Tinh tế)
            time.sleep(0.5) 
            
        except requests.exceptions.RequestException as e:
            print(f"Rách lưới tại Page {page_count} Cọc Mốc Cursor: {current_cursor}. Lỗi: {str(e)}")
            # Gãy Gánh thì Không Kéo thêm nữa, Xử lý Đứt Gãy. Tự Build hàm Retry Phủ ngoài.
            break

# ----------------- LIVE DEBUG USAGE -----------------
# url = "https://api.shopee.vn/v2/orders/get"
# key = "xyz-doc-lap-tu-do"
# 
# for batch_orders in fetch_shopee_orders_generator(url, key):
#     # Dump batch_orders vô PostgreSQL hoặc ghi File Parquet Nhỏ
#     insert_postgresql(batch_orders)
```

---

### Bài 16: Chunked Download File Khổng Lồ Tử Thần (30GB CSV)

**Problem:**
Client ném 1 cái Direct Link S3 (Pre-signed URL) trỏ thẳng vào file `billing_logs_Q1.csv` nặng 30 Gigabytes. "Hãy viết Script Python Code Lõi kéo cục này Tải Xuống Ổ Cứng mà không nổ RAM máy ảo 4GB của công ty!"

**Tư duy giải quyết (Analytical Thinking):**
- Đây là lỗi kinh điển của `requests.get(url).content`. Python sẽ mổ bụng 30GB tải vào ruột (RAM), sập đứng máy chủ ngay tắp lự.
- Đổi súng ngắm qua Tham số huyền thoại bật nắp: `stream=True`. Kết hợp vòng quét (Iterate over Content).
- Dùng buffer Size cố định để Xúc từng muỗng đổ xuống ổ cứng I/O. 

**Step-by-step Solution:**
```python
import requests

def massive_download_streaming(url: str, save_path: str, chunk_mb: int = 5):
    """
    Streaming Download. Tải từng Mảnh. Cục đá Nặng Mấy RAM Cũng Rảnh Gánh.
    """
    CHUNK_SIZE = chunk_mb * 1024 * 1024 # 5 MB mỗi Muỗng
    
    # Kích hoạt Cờ Tường Stream (Không Rinh Bưng Nguyên Khối)
    with requests.get(url, stream=True, timeout=15) as r:
        r.raise_for_status()
        
        # Mở File Write Binary (Vào Mạch Nước Ngầm Ổ Cứng)
        with open(save_path, 'wb') as f:
            
            # Gõ Cốc Cốc Lấy Từng Cụm 5MB Chảy Xuống Ruột Ngòi Bút
            for chk in r.iter_content(chunk_size=CHUNK_SIZE): 
                # Lọc Chặn rác Keep-Alive Empty chunks do HTTP sinh ra
                if chk: 
                    f.write(chk)
                    
    print(f"Thành Công Hút Khô Sông {url} xả vào Ổ Bí {save_path}")
```

---

## ✈️ Phần 6: Apache Airflow (DAGs Live Coding)

*Airflow là Cột Tim Cuốn Tuỷ của Data Engineer Việt Nam. 10 Chỗ Tuyển DE, 9 Chỗ Xài Airflow. Cấu hình Code Python trên Airflow khác ở chỗ nó Phác Hoạ nên Các Nút (Nodes) và Dây Chuyền (Edges) chứ Không Chạy Logic Song Tuyến (Single-Thread) Khô cứng.*

### Bài 17: Branching Nâng Cao Bọt Nước Chia Nhánh

**Problem:**
Yêu cầu Live Code tạo 1 luồng công việc DAG Pipeline:
1. `check_db_status`: Kiểm tra PostgreSQL Có Trống Rỗng (Mới Toanh) Hay Có Data Đang Chạy Ngầm. 
2. Luồng sẽ ngã rẽ Tẽ Đôi (Branching):
   - Nếu Trống Không -> Chạy cục `Full_Load_Task` (Nhét toàn bộ Lịch Sử Chạy Cố) -> Dứt.
   - Nếu Có Data Chạy Rồi -> Rẽ Nhánh Sang `Incremental_Load_Task` (Chỉ Kéo 1 Ngày Mới) -> Sau đó qua tiếp `Agg_Daily_Task` -> Dứt.

**Tư duy giải quyết (Analytical Thinking):**
- Sử Dụng Trợ Thú Quyền Lực `BranchPythonOperator` trong thư viện Operator.
- Task Branching Bắt Buộc Phải trả Quả ra Tên ID (String `task_id`) Của Nút Kế Tiếp Bị Quyết Định Bật Ngang.

**Step-by-step Solution:**
```python
from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator, BranchPythonOperator
from airflow.operators.dummy import DummyOperator
import random

# Hàm Cốt Rễ Quyết Quyền Chi Huy 
def decide_branching_path(**kwargs):
    """Trích Đoạt Màn Mở Khoá Cơ Chế Đọc Cờ Chuyển Luồng"""
    # Mô phỏng Hành Động Đếm Lén Dữ liệu DB
    is_database_empty = random.choice([True, False])
    print(f"Tình Trạng Kho Bãi Lõm Không: {is_database_empty}")
    
    if is_database_empty:
        # Nhả Tên Của Đích Đến (Task_id) Mảng Trống Toàn Diện Toàn Lực (Full Load)
        return 'full_load_task'
    else:
        # Nhả Tên Của Đích Nạp Nhỏ Nhặt (Incremental)
        return 'incremental_load_task'

def process_logic_placeholder(msg):
    print(msg)

# Định Nghĩa Luồng Không Khí DAG Cấu Hình Chuẩn Bệnh Theo Tuổi
default_args = {
    'owner': 'admin_vietnam_de',
    'depends_on_past': False, # Gãy Cột Cũ Vẫn Chạy Cột Điểm Hiện Tại Không Khoá Chặn
    'email_on_failure': True,
    'email_on_retry': False,
    'retries': 2,
    'retry_delay': timedelta(minutes=5),
}

with DAG(
    dag_id='smart_dynamic_branching_etl',
    default_args=default_args,
    description='Trấn Quyết Rẽ Luồng Phân Ngã 3 Đường Code Live',
    schedule_interval='@daily',
    start_date=datetime(2026, 4, 1),
    catchup=False, # CHặn Backfill Ma Nạp Tử Tử
    tags=['live_coding', 'VNG_test']
) as dag:

    # Nút A (Khởi Động Nổ Máy Phát Điểm Rẽ Nhánh)
    branching_node = BranchPythonOperator(
        task_id='check_db_status_branching',
        python_callable=decide_branching_path,
    )
    
    # Nút B1 (Chạy Nguy Cầu Lún Bục Data Cổ Sạch)
    full_load = PythonOperator(
        task_id='full_load_task',
        python_callable=process_logic_placeholder,
        op_kwargs={'msg': "Đang Kéo Thác Nước 10 Năm Lịch Sử Lấp Biển!"}
    )
    
    # Nút B2 (Đâm chồi Sửa Lắt Nhắt Sóng Nhỏ Nạp Đắp Dần Mòn Cuốn Lệnh)
    incremental_load = PythonOperator(
        task_id='incremental_load_task',
        python_callable=process_logic_placeholder,
        op_kwargs={'msg': "Chỉ Bóc Vẩy 24h Data Tươi Nhất Cuộn Chỉ Đi"}
    )
    
    # Nút Tích Luỷ Nối Tiết Lắt Buộc (Riêng Branch B2)
    agg_daily = PythonOperator(
        task_id='agg_daily_task',
        python_callable=process_logic_placeholder,
        op_kwargs={'msg': "Rollup Tổng Cục Ngày Giao Kế Toán Chốt Sổ"}
    )
    
    # Chặn Tâm Thế Kết Gắn Ngàm Cuối (Tránh Gãy Viền Dòng Cuốn Sập Graph)
    end_gate = DummyOperator(
        task_id='end_gate',
        trigger_rule='none_failed_or_skipped' # Mấu Chốt: Kẻ Cầm Rẽ Mép Bị Lỗ/Skip Cứ Thế Cho Nút Đích Bọc Kịp Cuộn Trôi Dòng Nháp Đều Gây Xanh Khung Cuối
    )
    
    # Liên Kết Mạch Flow Khắc Mạng Lưới
    branching_node >> full_load >> end_gate
    branching_node >> incremental_load >> agg_daily >> end_gate
```

---

### Bài 18: Lính Nguy Cơ XCom Cắn Đứt Mạng Database Của Airflow

**Problem:**
(Tình Huống Hạch Hỏi Trắc Nghiệm Mồm Kết Hợp Sửa Lỗi Ngập Memory Cấu Hình)
"Em đẩy một cái File Pandas Cự Lớn (1GB) vào biến `ti.xcom_push()` qua Task Số 2. Hôm sau Airflow Webserver Đột Tử. Anh Restart Gãy Chết. Lí do Đâu Sửa Mã Làm Sao?"

**Tư duy giải quyết (Analytical Thinking):**
Airflow **XCom** (Cross-Communication) không phải Mạch Tuần Hoàn Bộ Nhớ Chuyển RAM qua Các Function Python Nhấp Nháy Nhanh Đứt. Xcom Lưu CHỮ Viết String Thẳng Trúc Mật Mã Vô Con Cơ Sở Dữ Liệu Lõi PostgreSQL hoặc MySQL (Meta Database) để Cân Biến Bền Vững Đứt Trạm Chạy Cột Bám Tí Qua Ngày Trong Giữ Khoảng Thời Giang. Mày nhét Cây Mép DataFrame 1 GB Vô Đủ Lệnh Xcom Rút OOM Postgres Nổ Banh Dằn Văng DB Lõi Hạ Sụp Cả Giao Diện Kĩ Thuật. Lỗi Ngược Tim Chí Mạng DE! 

Bắt Buộc Chuyển Trục Tư Duy Lấp Đày Bằng Móc Ngoạm Path Link Ổ S3 (References String Tách Biệt Bộ Lõi Dòng Data Vật Lý Chết Yếu Khối Cầm Kẻ Lưu Chuỗi Tên Khống Chút Điệp Khắc Chạm Ghi Lối Ra Lên Data Lake Rỗng Kèm Lệnh Chó Rút Về Móc Chỉ Dây Thừng Link File Hữu Trục Cho Kẻ Săn).

**Step-by-step Solution:**
```python
# Task 1 Đoạn Lỗi Điển Hình Chết Mạch Nhồi
# Chết Lịm PostgreSQL - Gây Lỡ Chặn System Toàn Bầu Thở Airflow
def BAD_export_data(**context):
    huge_df_1gb = pd.read_sql("SELECT * FROM vnpay_log_3_years")
    # Tự sát Kéo Mép Hủy Diệt - XCOM Bị Tống Sạn Quá Giây Điểm Kép Lệnh Chuẩn 48 Kb Báo Gãy Răng Error Ngay
    context['ti'].xcom_push(key='big_data_trap', value=huge_df_1gb) 

# Xử Lý Cực Lõi (Quy Mã Nhỏ Chắn Đường Lũ Rừng Quét Gọn Qua DataLake Nằm Cấm Nhúng Xcom)
def GOOD_export_data(**context):
    huge_df_1gb = pd.read_sql("SELECT * FROM vnpay_log_3_years")
    
    # Ghi Biến Bãi Vận Thể Ra Không Gian Bucket Bảo An Cần Trục Hoá
    s3_path = f"s3://my_lake/tmp/{context['ds']}/extract.parquet"
    huge_df_1gb.to_parquet(s3_path)
    
    # Đẩy Qua Xcom Ngon Bộ Gọn Lẹ (1 Khúc Mảnh Code Bé Hạt Lép Truy Thừa Chuỗi Chữ Chỉ 36 Bytes Giọt Không Liều Nhói Cốt Lõi Lưng Gãy Bẹp DB Airflow)
    context['ti'].xcom_push(key='s3_path_bridge', value=s3_path)

def GOOD_transform_data(**context):
    s3_passed_path = context['ti'].xcom_pull(task_ids='extract_safely', key='s3_path_bridge')
    loaded_df = pd.read_parquet(s3_passed_path) # Lấy Thảo Mã Link Bút Ngược Bóc Mép Kéo Mồi Câu Tách Thả
```

---

## 🚀 Phần 7: Apache Kafka Khắc Kỷ Hóa (Streaming Engineering)

*Nếu như Airflow là Cột Tim, thì Kafka lại là Huyết Mạch. Các bài đánh giá Live Code Zalo / VNPay hay MoMo tập trung rà soát khống chế Cơ Chế Cam Kết Trạng Thái (Offset Commits), Lỗi ngốn RAM của Consumer, và Kỹ thuật điều phối Hàng Đợi (Queuing).*

### Bài 19: Viết Consumer Kháng "Poison Pill" (Chống Nổ Vòng Lặp Vô Hạn)

**Problem:**
Data Pipeline đang mút tin nhắn từ topic `payment_txn`. Đột nhiên có 1 thằng Client vứt bậy bạ một cục Message dạng Text Rác rưởi không tuân theo Cấu Trúc JSON chuẩn. `Consumer` giam nó vào miệng Cắn giải Mã Lỗi (Deserialization Error) và Sặc Cục Đứng im Đóng Băng Khựng Mạch (Consumer Exception Loop). Tất cả 1 Triệu Giao dịch đằng sau kẹt cứng không thể thanh toán (Duyệt Kì Quá Hạn). 

Dùng Python Kafka-Confluent Live Code tạo màng Lọc Rác Poison Pill.

**Tư duy giải quyết (Analytical Thinking):**
- Bọn Coder Non sẽ không để Try-Catch Bọc Gói Khâu Giải Mã Dữ Liệu `json.loads(message.value())`.
- Ngay Khi Consumer Ngậm Kẹo Độc (Poison Pill), Code Python chửi ầm Lên Break Dòng Văng Mất Nẻo. Do Cảm Biến Không Auto Commit Cái Lỗi Đó Xuống Log Trạng Thái Topic -> Consumer Boot Lại Gọi Nguyên Con Quỷ Xác Thối Lên Cắn Lần Hai -> Loop Căng Xác Sàn Kẹt Cổ.
- Cách Sửa Lõi Lọc Đáy Hút Gạch: Try-Catch Khâu Parse Cứng. Nếu Lỗi Lập Tức Liệng Thằng Quái Thai Xuống "Topic Rác" Riêng Biệt (Dead-Letter-Queue - DLQ). **QUAN TRỌNG:** Phải Ghi Cờ Đi Tiếp (Manual Commit Offset) Bước Móng Lên Chân Rác Tránh Nó Bay Trở Lại Dòng.

**Step-by-step Solution:**
```python
from confluent_kafka import Consumer, Producer
import json
import logging

def safe_poison_pill_consumer(config_map):
    # Khởi Tạo Mõm Chó Kéo Đẩy
    consumer = Consumer({
        'bootstrap.servers': 'localhost:9092',
        'group.id': 'payment_processor_group_v2',
        'auto.offset.reset': 'earliest',
        # Đóng Cờ Cam Kết Trôi Nông - Tự Bấm Lệnh Chốt Hổ Mang Bằng Tay
        'enable.auto.commit': False 
    })
    
    # Ống Phụt Nhổ Rác Mù (Hút Gạch Bể Móng Đẩy Sang Bệnh Viện Topic)
    dlq_producer = Producer({'bootstrap.servers': 'localhost:9092'})
    
    consumer.subscribe(['payment_txn'])
    
    try:
        while True:
            # Gậm Mùi (Lấy Mồi Message Trễ 1 Giây Không Có Đợi Tý Thử Lại)
            msg = consumer.poll(1.0)
            
            if msg is None:
                continue
            if msg.error():
                logging.error(f"Kafka Lỗi Nhảm Hạ Cột Sóng Nhĩ: {msg.error()}")
                continue
                
            # ĐƯỜNG KIẾM LÕI TÁCH VÁCH LỖI POISON PILL
            try:
                # Quả Lựu Đạn Chứa Thạch Độc Rập Tắt Giải Mã
                val_decode = msg.value().decode('utf-8')
                core_data = json.loads(val_decode)
                
                # Hàm Business Xử Lý DB Thanh Toán
                # execute_payment(core_data)
                
            except json.JSONDecodeError as decode_error:
                logging.error(f"Xác Thối Độc Ngạt Payload Mò Tới: {val_decode}")
                # Hất Căng Trả Thằng Độc Nhổ Xuống Biển Lọc Thải Cục Bộ Rác DLQ
                dlq_producer.produce(
                    'payment_txn_dlq', 
                    key=msg.key(),
                    value=msg.value()
                )
                dlq_producer.poll(0) # Cuốn Sạch Phễu Nhổ Cổ Tròng Họng
                
            except Exception as e:
                # Phanh Góc Vứt Xuống Vũng DB Phân Tách Nghề Rã Cột Lỗi Ảo Kinh
                logging.error(f"Unknown Fatal Dump Đừng Để Sập Máy: {e}")
                
            finally:
                # BẤT KỂ NGẬP CỨT HAY THƠM TỘT XUÔNG. PHẢI CẮM GAI CHỐT ĐIẾM KHOÁ (COMMIT) 
                # Khắc dậm Dấu Cột Sẹo Bước Băng Lướt Qua Thằng Độc Mù Không Nhai Lại Nó Nữa
                consumer.commit(message=msg, asynchronous=False)
                
    except KeyboardInterrupt:
        pass
    finally:
        consumer.close()
```

---

### Bài 20: Hệ Thống Cụm Batch Producer (Chống Nghẽn Chai Thắt Lực Tường)

**Problem:**
Client Web Gọi Function Python của bạn để Đẩy 500,000 Dòng Record Event Logs sang Kafka. Code Non Gõ Lệnh `producer.send(msg)` Chạy 1 Lệnh - Send 1 Cái Lệnh Đi, Rồi Mở Chừng Trực Đợi Mạng Bay Quanh Lại Mất 150ms/Cái. Kết Thúc 1 Tuần Cho 500k Dòng. Thảm Khoát Ngốn Răng Tốc Độ Của DE VNG Tắt Ngủm Nụ Cười Của Em Chị Ỷ Lan.

Dùng Phương Cán Nối Khối Song Song Thét Hét (Batching) Nhồi Kẹp Băng Cảng Gọi 1 Phát Lên Mạng Thổi Bay 10.000 Lệnh.

**Tư duy giải quyết (Analytical Thinking):**
- Hàm `produce` Bất Đồng Bộ Của Thư Viện C Core Là Vị Thần Nén Hút, Mày Vứt Bao Nhiêu Nó Chỉ Chứa Cặn Ngậm Miệng Trầm Tu Ngâm. Nó Cần Kẻ Nhắc Trỏ Mốc Trói `flush()` để Nhè Nét Giải Oan Phóng Thành Mưa Lửa Đẩy Song Hạng Batch. Khắc Gấp Lợi Tốc Độ X 3000 Lần Bằng Trùng Điệp Bất Ngờ. Thao Tác Kiểm Đếm Cột Lưới O(1). 

**Step-by-step Solution:**
```python
def high_throughput_batch_producer(massive_messages: list[dict], batch_size: int = 10000):
    producer = Producer({
        'bootstrap.servers': 'kafka1:9092,kafka2:9092',
        'linger.ms': 5, # Không Nghĩ Ép Đi Cho Đầy Chờ Tí 5Mili Giây Cục Vó Nó To Cồng Cáp Nửa Mới Rải
        'compression.type': 'snappy', # Áp Lực Nhồi Gas Chống Nghẽn Túi Mạng Bọ Nát Kéo Chặt ZÍP
    })
    
    # Callback Khấu Trùng Đầu Sườn Gẫy Rã Vụn Phóng Không Cánh Nhận Dữ Liệu Lỗi Bắn Gọn Đi Ngược Về
    def delivery_report(err, msg):
        if err is not None:
            logging.error(f"Quả Tạ Rớt Tử Trận Mất Mát Đi Lạc Răng {err}")

    # Băng Bầu Vết Đạn
    for idx, record in enumerate(massive_messages):
        # Mớm Cho Khớp Nén (Không Hề Bay Lên Mạng Ngay, Giấu Vào Túi Ram Rỗng Thằng Kẹp Băng)
        producer.produce(
            topic='raw_firehose_events',
            key=str(record.get('user_id', 'unknown')),
            value=json.dumps(record).encode('utf-8'),
            on_delivery=delivery_report
        )
        
        # Gọi Hàm Quỷ Thác (Xả Toilett Cơ Chế Dọn Quặn Phóng Dòng Ngập Mảng Trùng Điệp Chuyển Túi To 10,000 Món Băng Đường Rộng Sang Data Đất Sét)
        # Nương Theo Nhất Cữ Đụng Trần Thằng Đáy Líp Batch = Bóp Cò Rít Ảo
        if (idx + 1) % batch_size == 0:
            producer.flush() # Hàm Mắn Phóng Dùi Rã Batch Lưới Khóa Buột Buộc Xuất Ngạch Đục Nhoè Nhắm Lực Bay Chóng Mặt Đồng Tâm Đơn Gắn Mạng Rộng.
            
    # Chốt Nót Chặn Nét Khuyết Mồi Dư Chóp Cũ (Nếu Kẹt Rổ Tàn Chỉ Đâu Đó Cỡ Vụn Còn Lệch Số 8 Đuôi Số Đo Số Cuối Không Tròn)
    producer.flush()
```

---

## 🛡️ Phần 8: Advanced Data Quality Validation (Màng Lọc Thép Pydantic)

*DE Thị Trường VN Nay Bị Đẩy Lên Cột Dựng Xây Pipeline Rác Gây Sự Cố Sai Lệnh Nghiệp Vụ Kế Toán Thường Bị Ăn Phạt Oan. Data Quality Gánh Trụ Cọc Lõi Chống Thối Trủng Cốt Mạng Mẻ Database. Ngôn Ngữ Pydantic Kiểm Đoán Schema Validation Lên Ngôi Cùng Tướng Great Expectations (GX).*

### Bài 21: Vây Hãm Xác Thực Mạng Schema Lệch Với Pydantic Live
**Problem:**
Em Nhận JSON Gốc Rễ Từ Bọn Coder Frontend Chả Bao Giờ Code Giống Mẫu Gửi Về.
`{"usr_name": "Tom", "Tuoi_Bo_May": 16, "Email_la": "NotEmail"}` Vẫn Vô Mạng OOM Ổ Tả Điểm Thủng Sàn Database Type Bọc Chết Giết Chóc String Ở Số.
Xây Móng Lược Trục Ép Khung Bằng OOP Phán Đoán Pydantic Trong Đốt 1 Nốt Code Live.

**Tư duy giải quyết (Analytical Thinking):**
Nếu Viết `if json_dict['Tuoi'] > 18 ...` Để Tự Rào Móng Gãy Mã Lệch Cột Chống Gốc Thì Em Viết 1 Trăm Câu Check Null Sạch Giao Ngang Xé Rách Cả Phổi. Pydantic Ẩn Bọc Kĩ Ngầm Rạch Toán Gỡ Buộc Định Dạng Class Base (Mô Phỏng Java Class Contract). 
Nếu Tao Chờ Mày Quăng Vào Số (Integer), Mày Cho String Tao Bắn Ra TypeError Nát Thây Liệng Nhành Khác Thối Nằm Riêng Màn Mở Không Bao Giờ Thủng Tạp Chất Lọt Qua Bó Mép Tê Liệt Hệ.

**Step-by-step Solution:**
```python
from pydantic import BaseModel, Field, EmailStr, validator
from typing import Optional
from datetime import datetime

# Lắp Giáp Cửa Đồng Kiểm Soát Gắt Giao
class UserEventSchema(BaseModel):
    # Khai Báo Đích Lộ Tuyến Định Hình Mật Móng Khớp Phanh Nét
    user_id: int
    user_name: str = Field(..., min_length=2, max_length=50) # Tên Ngắn Quá Trọc Nấc Gạt Tắt
    email: Optional[EmailStr] = None # Phải Đúng Cú Pháp xyz@gmail.com Chẳng Không Chặn Xoá Lẽ
    age: int = Field(ge=18, le=100) # Phành Rập Vạch Tuổi Non 18 Không Nạp Data Đục Thủng Game Phản Cảm Khứa Cụ Trẻ Con
    signup_dt: datetime
    
    # Validation Tuỳ Biến Thuận Logic Giao Thương Siêu Nâng Cấp Business Tự Kỉ Lắp Tạp
    @validator('user_name')
    def prevent_admin_impersonate(cls, value):
        if 'admin' in value.lower():
            raise ValueError("Cấm Hàm Trộm Cắp Nick Tước Danh Admin Bãi Triều Biến Chấn Khống Ngọt")
        return value

def validate_and_parse_events(raw_json_list: list[dict]) -> tuple[list[dict], list[dict]]:
    valid_events = []
    quarantine_events = [] # Mã Độc Bẩn Thối Rã
    
    for thung_ro in raw_json_list:
        try:
            # Ngậm Độc Dấu Phán Lọc Cửa Thép Nòng Thôn Tiển Xét Yếu Cát
            clean_model = UserEventSchema(**thung_ro)
            # Kháng Trở Dạng Đích Model Sạch Dictionary Múc Ăn Rỗng Tiêu Chẩn Vượt Qua Cổng Trạm
            valid_events.append(clean_model.dict())
            
        except Exception as pydantic_err: # Chụp Mũ Ám Sát Thằng Độc Quái Thai Lọt Rớt Chân Thúi Phóng Móc Nhặt Biến Mạch Rộng Thổi Sóng Gãy Móng Cạn Lẽ Cấm Ngăn Đoán Oan Oán Lõi Máu Lục Cấm Quẹt Thằng
            # Ghi Trọn Sổ Ma Quyển
            quarantine_events.append({
                "raw_dump": thung_ro,
                "error_cause": str(pydantic_err)
            })
            
    return valid_events, quarantine_events

# Test Chạy Nháp Quẹt Mồi Gã Độc Nhồi Đần
# list_bad_data = [
#   {"user_id": 1, "user_name": "Teo", "age": 14, "signup_dt": "2026-01-01T12:00:00"} # Lỗi Răn Thiếu Tuổi Trẻ Trâu Bị Block Nháy Vọt Bấm Mép Rớt Quarantine Đục Thơm Chặn Nhốt Nồi Liêm Sỉ !
# ]
```

---

## 🏗️ Phần 9: Analytics Engineering (dbt Jinja Live Coding)

*Ở Việt Nam, dbt (Data Build Tool) đang thống trị tầng Data Warehouse (Snowflake / BigQuery). Lập trình viên Data không viết SQL chay nữa, mà viết dbt Macro / Jinja Templates đúc SQL Động.*

### Bài 22: Viết dbt Macro Trục Xoay (Pivot) Động Học
**Problem:**
Em có bảng Lịch sử Nạp Tiền `fct_topup (user_id, method, amount)`. Phương thức (`method`) có thể là "Momo", "ZaloPay", "VNPay", Thậm chí ngày mai Sếp add thêm "ShopeePay". Tức là Cột Method Thay đổi Bất Tử. Viết Macro dbt Dùng Jinja Để Tự Sinh Lệnh PIVOT Biến Các Chữ `Momo`, `ZaloPay`... Này Thành Cột Riêng Khai Báo Trong Câu Lệnh Select Mà Không Cần Gõ Bằng Tay.

**Tư duy giải quyết (Analytical Thinking):**
- Jinja `{% ... %}` cho phép chèn Logic Programming vào trong file SQL.
- Dùng `run_query` chạy lén đớp lấy 1 list cột Method (Distint Object Array).
- Ném mảng For Loop quét Array đó để sinh text SQL "SUM(CASE WHEN method = 'Momo' THEN amount ELSE 0 END) AS topup_momo". Cấu trúc sinh Dynamic SQL này đốn hạ bài toán Schema Linh Động cực mạnh.

**Step-by-step Solution:**
```sql
-- File: macros/dynamic_pivot_methods.sql
{% macro dynamic_pivot_methods(table_name, column_name, measure_column) %}

    -- Xây lệnh chạy lén đục List Method
    {% set get_methods_query %}
        SELECT DISTINCT {{ column_name }} 
        FROM {{ table_name }}
        WHERE {{ column_name }} IS NOT NULL
    {% endset %}

    -- Chạy Hàm và Ép Trả List (Nếu Đang Khâu Execute Lúc Compile Run Mới Dùng)
    {% set results = run_query(get_methods_query) %}
    
    -- Dọn Sạch Trích Cốt
    {% if execute %}
    {% set methods_list = results.columns[0].values() %}
    {% else %}
    {% set methods_list = [] %}
    {% endif %}

    -- Tròng Mã Loop Tạo Cột Cực Mượt
    SELECT 
        user_id,
        {% for method_item in methods_list %}
            SUM(CASE WHEN {{ column_name }} = '{{ method_item }}' 
                     THEN {{ measure_column }} 
                     ELSE 0 
                END) AS topup_{{ method_item | lower | replace(' ', '_') }}
            
            -- Chặn dính phẩy chót Răng Chó Mép Cuối Mảng
            {% if not loop.last %},{% endif %}
        {% endfor %}
    FROM {{ table_name }}
    GROUP BY 1

{% endmacro %}

-- Khi Ứng Dụng View Models Của Sếp Mở:
-- File: models/marts/dim_user_topup_agg.sql
{{ dynamic_pivot_methods(ref('fct_topup_stg'), 'method_name', 'transaction_amount') }}
```

### Bài 23: SCD Type 2 Auto Magic Với dbt Snapshot
**Problem:**
Làm Thế Nào Lấp Đầy Chống Rách 1 Bảng Master KH VNG Không Có Lịch Sử Đổi Pass Bằng Snapshot Dbt?

**Giải đáp Nhanh:**
Tạo Folder `Snapshots/`. Cài Cắm Conf Dbt Block Khá Dị Mới Có Lệnh `Check`. Mày Check Thấy Mức Độ Bất Kỳ Cột Nào Lệnh `check_cols` Nhúc Nhích Đổi Thay Là Tự Dập Mác Thêm Dòng Vào Cấu Cổ Update Nhãn `dbt_valid_to`.
```sql
{% snapshot users_snapshot %}

{{
    config(
      target_database='analytics_db',
      target_schema='snapshots',
      unique_key='user_id',

      strategy='check',
      check_cols=['tier_level', 'email', 'home_address']
    )
}}

SELECT * FROM {{ ref('stg_users_backend') }}

{% endsnapshot %}
```

---

## 🏎️ Phần 10: PySpark Tuning Siêu Cấp (Cuộc Chơi CPU Nảy Lửa)

*Tới Tầng này, VNPay/Zalo sẽ Bóc Phốt Móc Ruột Bạn Đã Từng Cấu Hình Ra Sao Ở Core Engine.*

### Bài 24: Vectorized Pandas UDF Nâng Vút Cánh Spark O(10x) Trí Tuệ
**Problem:**
Code Python Rác Viết Hàm `def calculate_haversine_distance(lat, lon)` rồi gắn vào UDF `F.udf(function, FloatType())` Chạy Xong Ngủ Trưa Cả Tỷ Khách Hàng Tốn 5 Tiếng Mới Tính Ra GPS. Em Explain Nó Chết Thế Nào Và Sửa 1 Gỡ Sang Số Vụt Trâu Đủ Đi?

**Tư duy giải quyết (Analytical Thinking):**
Hàm UDF Python Truyền Thống Điển Hình Là Quả Boom Tử Thần. 
Vì PySpark chạy trên JVM (Java Virtual Machine), Trong Khi UDF Chạy Bằng Python Runtime. Nên MỗI MỘT DÒNG RECORD Đơn Điệu, JVM Lại Cắn Giấy Truyền Trạm Bay Xuyên Khởi Lên Ống IPC Bóng Cầu Kết Nối Với Python Xử Lí. 1 Tỷ Dòng Lặp Tự Vận 1 Tỷ Lần Socket Communication Đi Đi Về Cạn Phổi Nghẽn Thủng Cổ Chai (SerDe Overhead).

Tuyệt Chiêu Cứu Viện: **Pandas Vectorized UDF (Trục Mảng Apache Arrow)**. Nó Nén Gộp Thẳng 10,000 Dòng Xuyên Thủng Qua Mạng Cùng Lóc Bằng Cấu Trúc RAM C của Arrow Sang Python Mật Mẻ. Python Pandas Numpy Quạt Chóp Toàn Bộ Array Chỉ Qua Tròn 1 Hàm Khực Hẹn Rồi Trả Cả Triệu Dòng Cùng Chỗ Cực Lộ Lên Tốc Tên Lửa.

**Step-by-step Solution:**
```python
import pandas as pd
from pyspark.sql.functions import pandas_udf
import numpy as np

# Thần Tịch: Nhập Đầu Mảng Cột Series Pandas, Chả Nhả Một Mảng Pandas (Thay Vì Dòng Lệch)
@pandas_udf("float")
def vectorized_haversine_udf(lat1: pd.Series, lon1: pd.Series, lat2: pd.Series, lon2: pd.Series) -> pd.Series:
    """Xử Nháy Thủng Numpy C Matrix. Hoàn Toàn Ko Chạm Tới Socket Py-JVM Đứt Đoạn"""
    
    # Ứng Toán Math Numpy Siêu Toạ Độ Tối Cổ Trên CPU L3 Cache
    R = 6371.0
    phi1 = np.radians(lat1)
    phi2 = np.radians(lat2)
    delta_phi = np.radians(lat2 - lat1)
    delta_lambda = np.radians(lon2 - lon1)
    
    a = np.sin(delta_phi/2.0)**2 + np.cos(phi1) * np.cos(phi2) * np.sin(delta_lambda/2.0)**2
    c = 2 * np.arctan2(np.sqrt(a), np.sqrt(1 - a))
    
    distance = R * c
    return distance # Phóng Hồi Triệu Phân Cấu Mốc 1 Mẻ Ra Spark Arrow Memory C

# Code Gọi Đỉnh Văng 1 Triệu GPS Chỉ Mút 3 Giây Bằng GPU/CPU Xẻ Vector Lỗi Lập Thống:
# df_computed = df.withColumn(
#    "Distance_KM", 
#    vectorized_haversine_udf("Home_Lat", "Home_Lon", "Store_Lat", "Store_Lon")
# )
```

---

### Bài 25: Bộ Sưu Tập Bắt Bệnh Từ Spark Execution Plan Thực Điệu
**Problem:** Đưa Mảnh Khắc Physical Plan (Spark Dùng Cú Kép `df.explain(True)` Dưới Cục Mắt Terminal). Mày Chẩn Bệnh Dùm Tao Dòng `SortMergeJoin` Chậm Tới Nơi Nào Dính Vào Cục Rác Lỗi.
**Tư duy giải quyết Lời Thề:**
Dòm Plan Thấy: `Exchange hashpartitioning(user_id#150, 200)`
- **Exchange:** Có Mùi Chết Chết Rác! Đây Chính Là Thềm Lọc Đắng "Shuffle" Nẹt Mạng Cả Mẻ Rác Nẹt Nhau Chéo Băng Tầng Server Data Chuyển Sang Nhà Hàng Xóm. Cực Chậm. Trồi Đỉnh Nhất Nếp Đứt.
- **SortMergeJoin:** Spark Sắp Xếp Dữ Liệu Rồi Quét Kẹp Song Song Hai Kim Ghép Vòng (Mặc Định To). 

*Để Triệt Exchage:* Đòi BroadCast Hash Join (`BroadcastExchange`). Đưa Thằng Bé Cho Quỷ Vác Đi Bao Tùm Thằng To Dưới Gầm Node Nhỉ! Thấy `BroadcastHashJoin` Thay `SortMergeJoin` Mất Bóng Chữ `Exchange` -> Mỉm Cười Mãn Nguyện Cuộc Phỏng Vấn Big Tech Ăn Đứt Giải Vàng.

## 📝 Tổng Kết "Hít Thở" Dành Cho Ứng Viên
Bạn Không Cần Nhớ HẾT Cả Triệu Dòng Built-In Hàm Trong Đầu Khi Lên Bàn Phím. 
Interviewer VN Trọng Bẫy Phép Thử Tư Duy Chặt Chẽ Gốc Rễ Hơn Cách Bạn Xăm Hình Cú Pháp Nhanh Không Lỗi. Kẻ Không Nhớ Hàm Mà Biết Diễn Tả Lưu Đồ 2 Tay Vẫn Thắng Oanh Liệt Người Chạy Code Mượt Nhưng Không Hiểu Bản Chất.

---

## 🔗 Liên Kết Khuyến Nghị

*Để sống sót qua vòng DE Interview ở VN, chỉ cần bạn nằm lòng tư duy Tháo Gỡ Gốc Rễ.*

- [Trở lại Hệ Thống Bài Test 05](05_Coding_Test_DE.md)
- [Quay lại Trang Chủ Hướng Dẫn](../README.md)
