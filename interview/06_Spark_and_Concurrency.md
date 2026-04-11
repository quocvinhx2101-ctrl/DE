# ⚡ Spark & Concurrency Deep Dive (Extended Masterclass)

> Bộ cẩm nang tối thượng (1.5k+ dòng) dành cho phỏng vấn Data Engineer chuyên sâu. Focus vào xử lý Big Data, Spark Optimization, Memory Management, và Python Concurrency cực hạn với các bài toán thực tế quy mô hàng chục Terabytes.

---

## 📚 Mục Lục Toàn Tập

### Phần 1: Distributed Computing & PySpark Optimization
1. [Xử lý Data Skew bằng Salting (Tránh OOM)](#task-1-xử-lý-data-skew-lệch-dữ-liệu-bằng-kỹ-thuật-salting)
2. [Broadcast Join vs Shuffle Hash Join deep dive](#task-2-khi-nào-sử-dụng-broadcast-join-so-sánh-với-shuffle-hash-join)
3. [Window Functions trong Môi trường Phân Tán (Sessionization)](#task-7-pyspark-window-functions-trong-môi-trường-phân-tán)
4. [Repartition vs Coalesce & Sizing Memory](#task-8-quản-trị-phân-mảnh-repartition-vs-coalesce)
5. [Tối ưu Write Amplification (S3 Small Files Problem)](#task-9-write-amplification-và-chiến-lược-compaction-s3)
6. [Vectorized Pandas UDFs vs Pure Python UDFs](#task-10-tối-ưu-udfs-đoạt-mạng-vectorized-pandas-udfs)
7. [Accumulators và Broadcast Variables (Biến trạng thái tàng hình)](#task-11-accumulators-và-broadcast-variables)
8. [Xử lý Late Data với Watermarking (Structured Streaming)](#task-12-xử-lý-late-data-với-watermarking-trong-structured-streaming)

### Phần 2: Concurrency & Parallelism trong Python
9. [Đa luồng Thread-Pool Kéo API Rate-Limited](#task-3-kéo-api-siêu-lớn-bằng-đa-luồng-threadpoolexecutor)
10. [Asyncio & Aiohttp - Non-blocking I/O tối cực](#task-4-asyncio---tối-đa-hóa-non-blocking-io)
11. [Bypass GIL bằng Multiprocessing Băm Log 100GB](#task-5-băm-nhỏ-đọc-log-100gb-bypass-gil-hạn-chế)
12. [Hàng Đợi An Toàn Luồng (Thread-safe Producer/Consumer)](#task-13-hàng-đợi-an-toàn-luồng-thread-safe-queue-pattern)
13. [Thuật Toán Giới Hạn Tốc Độ (Token Bucket Rate Limiting)](#task-14-rate-limiting-thuật-toán-token-bucket)
14. [Ngăn chặn Deadlock trong Lock Đồng Thời](#task-15-ngăn-chặn-deadlock-trong-concurrency)
15. [Thiết kế Checkpointing Resilient cho Batch Jobs](#task-16-checkpointing-resilient-cho-long-running-jobs)

### Phần 3: Low-level File Processing
16. [Tối ưu bộ nhớ với Lazy Loading CSV Generator](#task-6-tối-ưu-bộ-nhớ-với-lazy-loading-csv-generator)
17. [Streaming XML/DOM Parsing không sập RAM](#task-17-streaming-xml-parsing-không-sập-ram)

---

## 🔥 Phần 1: Distributed Computing & PySpark Optimization

### Task 1: Xử lý Data Skew (Lệch dữ liệu) bằng kỹ thuật Salting

**Problem:**
Trong hệ thống phân tán, dữ liệu được chia thành các partition dựa trên giá trị băm (Hash) của khóa (Key). Tuy nhiên, thực tế dữ liệu rất hay luẩn quẩn định luật Pareto (80/20). Chẳng hạn, khi `.join()` bảng `fact_clicks` (hàng chục tỷ dòng) với `dim_users`, rất nhiều clicks từ các bots ẩn danh mang `user_id = null` hoặc `user_id = 'UNKNOWN'`.
Hậu quả là Executor xui xẻo nhận partition chứa key `null` sẽ phải buffer hàng chục GB dữ liệu vào RAM, gây ra lỗi **Out of Memory (OOM)**. Cùng lúc đó, các Executor khác lại rảnh rỗi.

**Bài toán:** Viết logic join chống sập (skew-resistant join) sử dụng kỹ thuật "Thêm Muối" (Salting).

**Analytical Thinking (Tư duy giải pháp):**
- Làm sao để ép key `null` phân tán đều ra 100 executors khác thay vì dồn cục vào 1?
- -> Nối vào key `null` một con số ngẫu nhiên từ 0 đến 99 (Thêm Muối). Key `null` sẽ trở thành `null_0, null_1, ..., null_99`. Việc Shuffle giờ đây băm dải hash ra thành 100 mảnh rải đều.
- Để bảng kia (nhỏ) join không trượt phát nào, ta phải nhân bản toàn bộ data của nó thành 100 dòng tương ứng (`null_0` đến `null_99`).

**Solution:**
```python
from pyspark.sql import SparkSession
import pyspark.sql.functions as F
from pyspark.sql.types import IntegerType

# Khởi tạo Spark Session với tuning mặc định tham số Join
spark = SparkSession.builder \
    .appName("SkewJoinHandlingMasterclass") \
    .config("spark.sql.shuffle.partitions", "200") \
    .getOrCreate()

def join_with_salting_advanced(fact_df, dim_df, skew_column="user_id", num_salts=100):
    """
    Xử lý Data Skew với kỹ thuật Salting tối ưu nhất.
    Lưu ý quan trọng: Chỉ nên áp dụng khi Dim Table nhỏ gọn, vì việc Explode 
    dim_df lên 100 lần (nếu bảng có 10 triệu dòng -> 1 tỷ dòng) sẽ lập tức phá nát Cluster.
    
    Time Complexity: Tương đương Shuffle Hash/Sort Merge join + O(N) hàm explode.
    Space Complexity: Đòi hỏi vùng nhớ phình to x100 lần cho Dim Table trên Memory.
    """
    
    # 1. Bảo vệ dữ liệu gốc, cast tránh lỗi kiểu (Schema validation)
    if skew_column not in fact_df.columns or skew_column not in dim_df.columns:
        raise ValueError(f"Cột {skew_column} không tồn tại ở một trong hai bảng.")

    # 2. Add Salt vào Bảng Lớn (Fact Table)
    # Hàm rand() trả về [0.0, 1.0) cực kỳ đồng đều đặn (Uniform Distribution)
    salt_fact_df = fact_df.withColumn(
        "salt_id", 
        F.floor(F.rand() * num_salts).cast(IntegerType())
    ).withColumn(
        "salted_key",
        F.concat_ws("_", F.col(skew_column), F.col("salt_id"))
    )
    
    # 3. Nhân bản (Explode) bảng Nhỏ (Dim Table)
    # Khởi tạo một mảng thuần tĩnh (static array) từ 0 đến num_salts - 1
    salt_array_lit = F.array([F.lit(i) for i in range(num_salts)])
    
    salt_dim_df = dim_df.withColumn(
        "salt_array", salt_array_lit
    ).withColumn(
        # Hàm explode là hàm biến bảng dẹt thành dài (wide to long) cực kỳ đắt đỏ
        "salt_id", F.explode(F.col("salt_array"))
    ).withColumn(
        "salted_key",
        F.concat_ws("_", F.col(skew_column), F.col("salt_id"))
    )
    
    # 4. Thực thi Join
    # Tại bước này, Shuffle mechanism chốt hạ sẽ rải đều mảng "salted_key"
    joined_df = salt_fact_df.join(
        salt_dim_df,
        on="salted_key",
        how="inner"
    )
    
    # 5. Dọn dẹp metadata chừa lại bảng nguyên trạng cho business
    clean_df = joined_df.drop("salt_id", "salt_array", "salted_key")
    
    return clean_df

# Ghi chú cho Interviewer (Edge Cases Triggering):
# - Hỏi Candidate: "Thế Spark 3.0 Adaptive Query Execution (AQE) có tự xử lý Skew không?"
# - Trả lời: Có. Spark AQE có tính năng `spark.sql.adaptive.skewJoin.enabled = true`. AQE tự 
# phát hiện partition phình to lúc runtime và chẻ tách nó (Split skewed partitions). 
# Tuy nhiên, kỹ thuật Salting thủ công vẫn là bí quyết bắt buộc phải thuộc lòng khi 
# độ nặng của data vỡ nát ngay cả khi dùng AQE, hoặc khi dùng GroupBy/Window Functions 
# thay vì Join (AQE ít support Skew GroupBy hơn Join).
```

---

### Task 2: Khi nào sử dụng Broadcast Join? So sánh với Shuffle Hash Join

**Problem:**
Trong hệ thống e-commerce, bảng `fact_sales` có kích cỡ 500 Terabytes trải khắp 100 nodes. Bảng `dim_country` chỉ có 200 dòng (xấp xỉ 10KB).
Mặc định, join qua `country_id`, Spark thực hiện cơ chế Shuffle Sort-Merge Join dẫn đến việc 500TB của `fact_sales` phải vần chuyển qua mạng vô cùng tốn thời gian I/O, tạo tình trạng kẹt cổ chai Switch Mạng (Network Switch Bottleneck). Bằng kinh nghiệm Senior, hãy lập tức giải quyết điều này.

**Analytical Thinking (Tư duy giải pháp):**
Giống như bạn đun nước pha mì, thay vì đun 500 bồn nước khổng lồ và bốc nguyên xe mì chạy tới lui, hãy copy nhỏ giọt 200 vắt mì (dim_country) gửi thẳng xuống cục bộ cắm sẵn ở bếp của 500 bồn nước đó. Quá trình đó gọi là Broadcast (Phát thanh).

**Solution:**
Sử dụng `broadcast()` hint trong Pyspark.

```python
from pyspark.sql.functions import broadcast

def optimal_broadcast_join_edge_cases(large_df, small_df, join_col="country_id"):
    """
    Ứng dụng Broadcast Hash Join (BHJ) cho hiện tượng lệch pha kích cỡ cực lớn.
    
    Lưu ý cho việc Tuning Spark Memory:
    - Bảng small_df sẽ được kéo ngược về Driver node bằng action đằng sau (collect()).
    - Sau đấy Driver đẩy cho TẤT CẢ các Executors qua giao thức BitTorrent-style mạng nội bộ.
    - Cẩn thận: Nếu bảng nhỏ vượt qua tham số spark.sql.autoBroadcastJoinThreshold (default 10MB)
    nhưng bạn mắm môi ép dùng Hint broadcast(), mà driver memory spark.driver.memory không đủ
    => Sẽ gây lỗi Driver OOM (Java.Lang.OutOfMemoryError). Sập toàn bộ application.
    """
    try:
        # Cơ chế hint sẽ bỏ phiếu ưu tiên ép Spark theo lệnh ta muốn bất chấp DAG Optimizer
        final_df = large_df.join(
            broadcast(small_df),
            on=join_col,
            how="inner" 
            # Dù là Left hay Right, bảng BROADCAST bắt buộc phải đóng vai trò Right ở Left Join 
            # hoặc đóng vai trò Left ở Right Join.
        )
        return final_df
    except Exception as network_oom_err:
        print(f"Network Overload / Driver OOM Detected: {network_oom_err}")
        # Phương án dự phòng (Fallback): Gỡ bỏ broadcast và chấp nhận shuffle
        # Tắt AQE để kiểm soát manual nếu cần
        return large_df.join(small_df, on=join_col, how="inner")

"""
🔎 Góc nhìn Phân Tích Kỹ Thuật (So sánh BHJ vs SHJ/SMJ):

1. Chi phí Mạng (Network & Serialization):
   - Bản thân Broadcast: Tốn băng thông kéo data từ Cụm Data về Driver (1 chiều mũi tên), sau đó từ Driver phủ sóng rải xuống Cluster (N chiều mũi tên xuống). Network cost = Size_Nhỏ + N*Size_Nhỏ. Cực thấp nếu Size_Nhỏ là 10MB.
   - Shuffle Hash/Sort Merge: Tát mương bắt cá. Toàn bộ 500TB của Bảng lớn bị băm nhỏ, hash keys, đổ ra đĩa (spill), nén sấy (compression), truyền qua mạng (network fetch phase). Chi phí O(Size_Lớn + Size_Nhỏ). 

2. Ram Tiêu Thụ trên Host:
   - BHJ: Ở tại mỗi Executor node, bộ nhớ JVM phải nhét trọn bảng Nhỏ thành một object HashTable. Kém linh động nếu bộ nhớ bị phân mảnh. Cú build HashTable O(N) rất nhanh.
   - SHJ: Map-side shuffle cần Disk đệm. Không bắt buộc phải tải cả data vô RAM cùng lúc (Graceful degradation).
"""
```

---

### Task 7: PySpark Window Functions trong Môi trường Phân Tán

**Problem:**
Sessionization là kỹ thuật chia sự kiện clickstream (hành vi người dùng lướt web vô định) thành từng "phiên" (session) nếu giữa các lần click có khoảng chết (inactivity gap) lớn hơn 30 phút. 
Bài toán phỏng vấn: Bảng `web_clicks` với cột `user_id`, `timestamp`. Hãy gán nhãn `session_id` duy nhất vào trong dữ liệu hàng tỷ click này để Data Analyst có thể vẽ chart phân tích phễu.

**Analytical Thinking (Tư duy giải pháp):**
Các bài toán SQL cơ bản dùng CTE là không đủ tinh tế, ta phải thể hiện cách Spark tổ chức Window Frame qua RAM phân tán. 
Spark chia `Window.partitionBy()` ra sao? Dữ liệu của 1 `user_id` sẽ được Shuffled dồn trọn vẹn vào 1 Node. Do đó, nếu 1 con bot ddos click 1 tỷ lần, Node gánh `user_id` của con bot đó sẽ sập! (Lại là Data Skew).

**Solution:**
```python
from pyspark.sql.window import Window
import pyspark.sql.functions as F

def generate_session_ids_streaming_batch(events_df, gap_minutes=30):
    """
    Sử dụng Window Functions cao cấp phân tích session.
    Cách hoạt động:
    1. Đưa các event của 1 user nằm liền kề bên nhau trên 1 physical node.
    2. Dùng hàm LAG kéo timestamp của dòng đi trước để so sánh (delta time).
    3. Đóng đinh cờ (Bool) nếu delta > gap_minutes.
    4. Gom dồn (Cumulative Sum) cờ boolean để sinh ra ID tịnh tiến.
    """
    
    # Bắt buộc cung cấp order_by trong Window nếu không hàm LAG sẽ nhặt random dòng
    w_lag = Window.partitionBy("user_id").orderBy("timestamp")
    
    # 1. Tính toán khoảng hụt hẫng (Gap Time)
    events_with_lag = events_df.withColumn(
        "prev_timestamp", 
        F.lag("timestamp", count=1).over(w_lag)
    )
    
    # 2. Quy đổi gap ra số giây và kiểm tra xem có vượt 30 phút (1800 giây)
    is_new_session_col = (
        F.col("timestamp").cast("long") - F.col("prev_timestamp").cast("long")
    ) > (gap_minutes * 60)
    
    # Xử lý edge case: dòng đầu tiên của mỗi User thì prev_timestamp = null, đương nhiên là 1 session mới
    events_flagged = events_with_lag.withColumn(
        "is_new_session",
        F.when(F.col("prev_timestamp").isNull(), 1)
         .when(is_new_session_col, 1)
         .otherwise(0)
    )
    
    # 3. Kỹ thuật mấu chốt: Running Total (Cumulative Sum) của các lá cờ để tạo khối liên minh ID
    # Frame mỏ neo: Chạy từ tận cùng tiền sử (UNBOUNDED) kéo đến điểm chốt hiện tại (CURRENT ROW)
    w_cumsum = Window.partitionBy("user_id").orderBy("timestamp") \
                     .rowsBetween(Window.unboundedPreceding, Window.currentRow)
                     
    sessionized_df = events_flagged.withColumn(
        "session_increment",
        F.sum("is_new_session").over(w_cumsum)
    )
    
    # 4. Gắn mác kết hợp siêu duy nhất Globally (Bằng user_id ghép với increment tag)
    result_df = sessionized_df.withColumn(
        "session_id",
        F.concat_ws("_", F.col("user_id"), F.col("session_increment"))
    ).drop("prev_timestamp", "is_new_session", "session_increment")
    
    return result_df

"""
🔥 Điểm cộng khi Phỏng Vấn (Bonus Points):
Nếu Interviewer bẻ cong câu hỏi: "Nhưng user này là Bot, nó spam 1 tỷ dòng, 
Window sẽ xới bung RAM của mảng chứa buffer cho Window partition."
-> Trả lời: Ta không thể né Window partitionBy gánh lượng data khủng. Ta phải 
thiết lập chốt chặn Bot ở bước Culling. Viết 1 filter agg đếm số lượng click trước 
khi sessionize, nếu >= Threshold, ta gán cờ `is_bot=True` và đẩy ra file rác phân tích sau.
Hoặc áp dụng Approximate sessionization (Sessionization tĩnh dựa vào mốc giờ lưới Grid Hash).
"""
```

### Task 8: Quản trị Phân mảnh (Repartition vs Coalesce)

**Problem:**
Sau khi thực hiện một loạt phép biến đổi (Transformations) như lọc (Filter) bỏ 90% dòng dữ liệu không cần thiết, Data trên các partitions vô tình rơi vào tình trạng "phân mảnh" lởm chởm. 
Bạn muốn dump dataframe cuối cùng này xuống AWS S3 dưới dạng Parquet để ngày mai cho Athena truy vấn. Bạn nên ghi thẳng, hay gọi `.repartition()` hay gọi `.coalesce()` trước? Lệnh nào sẽ đâm thủng túi tiền AWS của Công ty nhất?

**Analytical Thinking (Tư duy giải pháp):**
Giữa `.repartition(N)` và `.coalesce(N)` đều là hành động định khuôn lại tủ kệ chứa data, nhưng cái giá phải trả hoàn toàn khác nhau.
- `repartition` sẽ làm xáo trộn toàn bộ mạng (Full Shuffle), data bứt gốc, gom lại thảy khắp cụm. Bù lại dữ liệu sẽ phẳng lì, dung lượng chia mâm rất mịn.
- `coalesce` chống lại quy luật Shuffle, nó tuyệt đối không di chuyển data khác Executor hiện hành. Nếu bạn báo `coalesce(5)`, nó sáp nhập các cọc kế bên nhau trên 1 host lại. Cực kì nhẹ máy, nhưng hệ luỵ là khối hầm tủ có thể bị lồi lõm (Skew size partitions).

**Solution & Khuyên Dùng Thực Tế:**
```python
def optimize_output_for_s3(filtered_df, target_file_size_mb=128):
    """
    Kích cỡ 128MB là Golden Rule (Tiêu chuẩn vàng) cho HDFS/S3 storage.
    Lớn quá thì query Athena trượt RAM. Nhỏ quá thì S3 sập API requests GET (Small Files Problem).
    """
    # Không thể đoán bừa partition, hãy ước tính size của dataframe trên bộ nhớ để đắp chăn
    sample_size = filtered_df.sample(0.01) # Mồi để lấy 1% data, hoặc ước tính metadata

    # GIẢ DỤ ta biết total volume là 10.000 MB ~ 10GB Data ươm Parquet.
    total_volume_mb = 10000 
    
    # Số Partitions cần thiết để mỗi file nén xuống chuẩn 128MB
    optimal_partitions = total_volume_mb // target_file_size_mb
    
    # NẾU TĂNG LÊN: Giả sử ban đầu đang df đang chia ở 10 partitions. Muốn bung ra 78 cục (128MB).
    # Chắc chắn phải dùng Repartition vì Coalesce KHÔNG THỂ BUNG RA TO HƠN HIỆN TẠI ĐƯỢC.
    # NẾU GIẢM XUỐNG: Ban đầu df 2000 partitions, filter xong muốn tụ lại chừa 78 cục.
    # PHẢI cẩn trọng. Dùng Coalesce nhanh nhưng rủi ro Skew 78 cục có cục nặng 1GB cục nhẹ 0mb.
    
    # 🌟 Mẫu chốt chấn động:
    # Người ta xài Repartition trước khi WRITE để file rớt ra sàn đều chằn chặn tăm tắp. Đừng tham rẻ Coalesce.
    final_df = filtered_df.repartition(optimal_partitions)
    
    return final_df

"""
🔎 Góc nhìn Phân Tích (S3 Small Files Problem):
Năm 2026, câu chuyện kinh dị là "Write Amplification S3".
Nếu bạn cứ ngây thơ viết `.write.partitionBy("date", "country").parquet("s3://logs/")` 
trên độ rộng 2000 partitions. AWS S3 rớt ra 200,000 files có dung lượng 50 KB/file !!!
Lúc Spark nạp lại đống file 50KB này đứt gãy 200,000 calls HTTP GET. Khóc thét đường mạng. 
=> Repartition theo tên Cột trước khi Ghi: `.repartition(10, "date", "country")`
"""
```

---

### Task 9: Write Amplification và Chiến lược Compaction S3

**Problem:**
Tiếp nối tác hại của Small Files. Bạn có một luồng Spark Structured Streaming đẻ file JSON liên lỉ vào Data Lake mỗi 2 phút đặng đạt yêu cầu real-time báo cáo. Sau 1 tháng, bucket S3 phình lên 21,600 files siêu rác lụn vụn mỗi ngày. Bị bill tính tiền Call API Request ngập lụt tài khoản.

**Analytical Thinking (Tư duy giải pháp):**
Ta không thể ngăn chặn Streaming nhả file (Trừ phi bóp Trigger interval lớn hơn).
Giải pháp vàng trong kiến trúc Lakehouse (Databricks Iceberg / Hudi) là kiến trúc chạy song song một tiến trình **Compaction** (Quét nhặt rác dập mành nén lại file Mập). Đọc nhiều file rác -> Nén làm 1 file to -> Xoá file rác.

**Solution:**
```python
def compaction_iceberg_table(spark_session, table_name):
    """
    Ngay nay, Apache Iceberg hay Delta Lake cung cấp cơ chế gộp file tự động.
    Nếu table của bạn có cấu hình tốt, bạn có thể trigger thủ công hoặc ngầm.
    """
    query = f"""
        CALL system.rewrite_data_files(
            table => '{table_name}',
            strategy => 'binpack',
            options => map('target-file-size-bytes','134217728') -- 128 MB
        )
    """
    # Tiến hành hút bụi
    spark_session.sql(query)
    
    # Hút bụi xong thì các file nhỏ bị đánh dấu thùng rác thành cặn bã Orphan files 
    # chứ chưa bốc hơi hoàn toàn, tốn tiền AWS.
    # Dọn kho dứt điểm:
    spark_session.sql(f"CALL system.expire_snapshots('{table_name}', timestamp '2026-04-01 00:00:00.000')")
```

---

### Task 10: Tối ưu UDFs đoạt mạng (Vectorized Pandas UDFs)

**Problem:**
Bạn có logic tính thuế độc quyền tự biên bằng Code Python mà SQL không cung cấp sẵn. Bắt buộc viết hàm UDF. Lập tức query chạy lết rùa chậm x100 lần. Tại sao dính UDF thuần lại mạt rệp đến thế?

**Analytical Thinking (Tư duy giải pháp):**
UDF Python tiêu chuẩn sẽ bắt Spark trượt từng Object của ngôn ngữ JVM (Scala lõi Spark) quăng sang cấp phát cho Interpreter của Python 1 con (Tốn phí Deserialization/Serialization ròng rã cả tỉ ROWS dữ liệu). 
- Kéo Vectorized UDFs (Dưới lớp bọc nó xài cấu trúc Apache Arrow memory in-memory format) để Spark có thể chuyển bưu kiện số lượng lớn Array thẳng nhét vô lõi Pandas numpy xử lý ma trận 1 phát xong hàng loạt khối batch.

**Solution:**
```python
import pandas as pd
from pyspark.sql.functions import pandas_udf
from pyspark.sql.types import DoubleType

# Annotation quyền lực bậc nhất: Pandas UDF Vectorized Batch Array.
@pandas_udf(DoubleType())
def calculate_complex_tax_udf(price_series: pd.Series, discount_series: pd.Series) -> pd.Series:
    """
    Hãy tưởng tượng price_series quăng cho bạn một lúc 10.000 dòng.
    Lúc này mọi thuật toán numpy C++ cắm mặt tính toán trong tích tắc.
    Hoàn toàn không có Serialize vật lý nào vì Spark Arrow và Pandas chung mâm structure.
    """
    # Logic có thể mài sâu học thuật Machine Learning hay Stats library
    net_price = price_series * (1 - discount_series)
    dynamic_tax_rate = net_price.apply(lambda x: 0.1 if x > 1000 else 0)
    
    return net_price * dynamic_tax_rate

"""
So sánh cực độ khi phỏng vấn:
Interviewer: Python UDF và Spark SQL Built-in functions cái nào ngon hơn?
Trả lời: Spark SQL Built-ins NGON NHẤT VÌ Catalyst Optimizer tối ưu hoàn thiện bằng Java/C++ native tận răng. Tránh xài UDF nếu tìm được hàm Pyspark thay thế. Chỉ xài Pandas UDF (chấp nhận rủi ro tốn RAM convert) nếu bài là ML inference hoặc cực kỳ tinh vi do bên thứ 3 (Thư viện tính tiền lãi suất chuyên môn).
"""
```

---

### Task 11: Accumulators và Broadcast Variables (Biến trạng thái tàng hình)

**Problem:**
Trong quá trình Spark càn quét qua 5 tỷ dòng raw string logs, bạn cần báo cáo có bao nhiêu dòng bị hư thối cấu trúc JSON để quăng log ra Telegram Alert. Nếu đẻ ra một action `.filter().count()` thì tốn một lần chà nhám toàn cluster. Bạn có thể dùng biến nguyên thủy Python `counter = 0` không?

**Solution:**
KHÔNG BAO GIỜ xài biến nguyên thủy toàn cục (Global Python counter = 0). Biến đó vô nghĩa, bị đóng hộp Ship lên Executor. Executor đếm cho đã rồi xoá, đách phản xạ lại Driver. Giải pháp là `Accumulator`.

```python
def count_corrupted_lines_zero_cost(spark, rdd_logs):
    """
    Accumulator là write-only reference. Các worker chỉ được nhét số, KHÔNG được đọc (ko thấy xài).
    Và phải bảo lãnh 1 rủi ro cực gắt: Accumulator sẽ đếm lặp HỚ nếu Job thất bại bốc đầu 
    recompute (mất tích task, Spark tự kích Task retry).
    """
    # 1. Khai báo ngay tại bộ nhông lái (Driver)
    bad_record_accumulator = spark.sparkContext.accumulator(0)
    
    def json_robust_parser(line):
        import json
        try:
            return json.loads(line)
        except json.JSONDecodeError:
            # 2. Add dấu hụt. Hoạt động y chang Metrics Counters của Prometheus
            bad_record_accumulator.add(1)
            return None

    # Tái hiện hành động: 
    clean_rdd = rdd_logs.map(json_robust_parser).filter(lambda x: x is not None)
    
    # 💥 BẪY CHẾT NGƯỜI: Chưa Action, Accumulator = 0
    clean_df = spark.createDataFrame(clean_rdd)
    
    # Action nhả đạn
    clean_df.write.parquet("s3://safebox/clean_db/")
    
    # Ở lại vùng hậu chiến kiểm lại số liệu
    print(f"Cảnh báo: Dựng được {bad_record_accumulator.value} dòng nát ngói trong hệ thống.")
    return bad_record_accumulator.value
```

---

### Task 12: Xử lý Late Data với Watermarking trong Structured Streaming

**Problem:**
Log mua bán đẩy vào Flink / Spark Streaming có cột `event_time`. Đương nhiên là 1 vài user mua hàng khi vô hầm cắm trại không có điện thoại sóng mạng. Nửa tiếng sau họ ngoi lên có wifi, luồng app mới dồn dập tống các log cũ 30 phút mốc lên hệ thống. Gói vào window như nào để tính điểm thưởng Doanh Thu cuối ngày mà không làm RAM trào bồn phì nổ? Ngưỡng trễ tối đa bao nhiêu?

**Solution:**
Dùng kỹ thuật `Watermarking`. Spark Streaming sẽ dọn (cắt vứt - flush drop state) cái Mốc Cửa Sổ (Window State Box) ra khỏi Memory kể từ sự kiện trễ tối tân nhất đếm chừa lại Watermark ngạch.

```python
import pyspark.sql.functions as F

def real_time_window_aggregation_with_late_grace(streaming_events_df):
    """
    Luôn bắt buộc Watermarking > Threshold = DROP.
    Nếu window từ 12:00 -> 12:10 
    Watermark là 15 phút. Khi đồng hồ internal Event System ghi nhận thấy 
    sự kiện mới nhất là của 12:40, Mức biên nước dâng (Watermark) dâng cày lên cọc 12:25.
    Lúc này tất cả Window Memory State Box có trước 12:25 bị chốt hạ tống quăng vô ổ sọt xoá RAM.
    Bất kì kiện data muộn nào đến trễ của khung 12:00-12:10 rớt thẳng cẳng ko thèm tiếp nữa.
    """
    
    # Giới hạn lòng nhân đạo chờ đợi Late data là 15 Phút lạm phát trễ
    with_watermark_df = streaming_events_df \
        .withWatermark("event_time", "15 minutes") \
        .groupBy(
            F.window("event_time", "5 minutes", "5 minutes"), # Cửa Tumbling 5p túc chu kỳ cố định
            "product_category"
        ) \
        .sum("sales_amount")
        
    return with_watermark_df
```

---

## ⚡ Phần 2: Concurrency & Parallelism trong Python

### Task 3: Kéo API siêu lớn bằng Đa luồng (ThreadPoolExecutor)

**Problem:**
Lấy profile JSON cho 10,000 Users bị phân trang từ REST API. Yêu cầu: Không chạy tuple `for` tuần tự (sẽ phải chờ timeout nhiều giờ đồng hồ liên tiếp). Cẩn trọng cơ chế Rate Limit `HTTP 429`.

**Solution:**
Sử dụng `ThreadPoolExecutor`. Tuy giới hạn bởi Global Interpreter Lock (GIL) của Python, nhưng vì đây là bài toán đợi Mạng (I/O Bound) -> Multi-threading vẫn giải quyết gọn gàng do thread đang block chờ I/O sẽ tự nhường CPU lại cho OS.

```python
import concurrent.futures
import requests
import time

def fetch_user_profile(user_id: int) -> dict:
    url = f"https://api.example.com/users/{user_id}"
    max_retries = 3
    
    for attempt in range(max_retries):
        try:
            # Timeout cực kì quan trọng để tránh chặn (block) socket luồng chết trôi vô thời hạn
            resp = requests.get(url, timeout=5) 
            
            if resp.status_code == 200:
                return resp.json()
            elif resp.status_code == 429: 
                # Nhận đòn Rate Limit -> Lùi bước Back-off Exponential theo Header
                retry_after = int(resp.headers.get("Retry-After", 2 ** attempt))
                time.sleep(retry_after) 
            else:
                resp.raise_for_status()
        except requests.RequestException as e:
            if attempt == max_retries - 1:
                return {"user_id": user_id, "error": str(e)}
            # Trễ tuyến tính nếu dính lỗi connection
            time.sleep(2 ** attempt)

def parallel_fetch_api(user_ids: list, max_workers: int = 50):
    """
    Sử dụng ThreadPoolExecutor để gọi API đa luồng.
    - Time Complexity: ~ O(N / max_workers) của thời gian trung bình API.
    - Context Switch: Tránh set max_workers dư dả quá lớn (như 1000) OS sẽ lãng phí OS threads swap.
    """
    results = []
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        # Submit tasks ngay lập tức vào Queue Pool
        future_to_uid = {executor.submit(fetch_user_profile, uid): uid for uid in user_ids}
        
        # Generator trả lại task hoàn thành sớm nhất (bất chấp thứ tự submit)
        for future in concurrent.futures.as_completed(future_to_uid):
            try:
                data = future.result()
                results.append(data)
            except Exception as e:
                # Catch catch-all lỗi ngầm không làm đứt dở công sức của entire process
                print(f"Crash không nằm trong dự tính cấu hình tại: {str(e)}")
                
    return results
```

---

### Task 4: Asyncio - Tối đa hóa non-blocking I/O

**Problem:**
Tương tự Task 3 nhưng hệ thống phải đẩy scale lên mức hardcore: Hàng trăm nghìn request cùng lúc (I/O bound mút chỉ). Thiết kế `ThreadPoolExecutor` sẽ bung sập RAM máy do giới hạn File Descriptors và Linux Kernel Threads.

**Solution:**
Tương tác mô hình `Asyncio` kết hợp `aiohttp`. Async là đơn luồng (Single Thread) nhưng với vòng lặp Event Loop non-blocking siêu hạng. Task nào bị nghẽn ngã chờ I/O, Event Loop ngay lập tức gắp Task khác lên chạy đan xen trong cùng 1 Thread OS. Tính mở rộng lên tới 10,000+ connections đồng thời.

```python
import asyncio
import aiohttp

async def fetch_endpoint_async(session: aiohttp.ClientSession, url: str) -> dict:
    try:
        # Khái niệm await - báo hiệu event loop nghỉ tay chuyển context
        async with session.get(url, timeout=10) as resp:
            if resp.status == 200:
                data = await resp.json()
                return {"url": url, "data": data}
            else:
                return {"url": url, "error": resp.status}
    except Exception as e:
        return {"url": url, "error": str(e)}

async def run_massive_async_fetch(urls: list, concurrency_limit: int = 500):
    """
    Dùng Semaphore để chặn cửa luồng thác lũ ồ ạt xé tan Connection Pool mỏng manh.
    """
    semaphore = asyncio.Semaphore(concurrency_limit)
    
    async def sem_bound_fetch(session, url):
        async with semaphore:
            return await fetch_endpoint_async(session, url)

    # Chìa khóa vàng: Dùng chung 1 ClientSession cho TCP Connection Reuse.
    async with aiohttp.ClientSession() as session:
        tasks = [asyncio.create_task(sem_bound_fetch(session, url)) for url in urls]
        # Gom hoạch toán
        return await asyncio.gather(*tasks, return_exceptions=True)
```

---

### Task 5: Băm nhỏ đọc Log 100GB (Bypass GIL hạn chế)

**Problem:**
Parse file text 100GB từ web server. Dùng regex trích xuất data. Logic parsing này là công việc cực kỳ ngốn nhân xử lí (CPU-bound) do Engine Python phải rà rọt Regex. Giao cho Single Core hay Threading đều tắc tịt tốc độ do còng số tám Python GIL (Global Interpreter Lock).

**Solution:**
Sử dụng `multiprocessing`. Chia file mẹ thành N đoạn byte offset (Chunks) và phân phát xuống cho `CPUs count` process con độc lập xử lí.

```python
import multiprocessing as mp
import os

def parse_log_chunk(start_offset: int, end_offset: int, file_path: str):
    """
    Worker can thiệp File con trỏ dựa dẫm vào bytes offset cực kỳ cẩn trọng.
    """
    success_count = 0
    with open(file_path, 'rb') as f:
        # Nhảy sào tới chốt offset
        f.seek(start_offset)
        
        # Sửa chửa tàn dư: Nếu offset đâm toạc nửa cụm từ của dòng, ta vứt dòng mẻ đó
        # Điểm mẻ này đã thuộc quyền sở hữu của Node đi trước.
        if start_offset != 0:
            f.readline()
            
        while f.tell() < end_offset:
            line = f.readline()
            if not line:
                break
                
            # TODO: Add logic Regex matching parsing siêu nặng
            success_count += 1
                
    return success_count

def launch_parallel_parser(file_path: str, cpus: int = mp.cpu_count()):
    """
    Process Controller chia mâm.
    Chia ổ bánh tỷ lệ đồng thuận: File_size // CPU_Cores.
    """
    file_bytes_size = os.path.getsize(file_path)
    chunk_size = file_bytes_size // cpus
    
    chunks = []
    for i in range(cpus):
        s = i * chunk_size
        e = (i + 1) * chunk_size if i < cpus - 1 else file_bytes_size
        chunks.append((s, e, file_path))
        
    with mp.Pool(processes=cpus) as pool:
        results = pool.starmap(parse_log_chunk, chunks)
        
    return sum(results)
```

---

### Task 13: Hàng Đợi An Toàn Luồng (Thread-safe Queue Pattern)

**Problem:**
Bạn đang thiết kế một kiến trúc Ingestion nội bộ. Có 5 Theads đóng vai trò Đọc dữ liệu từ Kafka (Producers), và 10 Threads phụ trách Ghi dữ liệu vào Database (Consumers). Nếu dùng mảng `list[]` thông thường của Python để chèn trung chuyển, Thread này đọc sẽ đâm sầm (Race Condition) làm mất mát phần tử của Thread kia. Nêu hình mẫu ứng dụng.

**Solution:**
```python
from queue import Queue
import threading
import time

def kafka_producer_worker(shared_queue: Queue, producer_id: int):
    # Data flow vào từ Kafka
    for data_item in range(5):
        item = f"Msg_{producer_id}_{data_item}"
        # Hàm put() được bảo kê an toàn bởi OS lock mutex, không bao giờ bị dẫm đạp
        shared_queue.put(item)
        print(f"Producer {producer_id} nhét: {item}")
        time.sleep(0.1)

def database_consumer_worker(shared_queue: Queue, consumer_id: int):
    while True:
        # Lấy đồ ra ăn. Block luồng nếu mâm còn trống.
        item = shared_queue.get()
        if item is None:
            # Poison Pill (Viên thuốc độc báo hiệu kết thúc vòng đời)
            break
            
        # Push to DB...
        print(f"Consumer {consumer_id} nhai: {item}")
        
        # Báo hiệu queue là tôi đã tiêu hoá xong dĩa này
        shared_queue.task_done()

# Khởi hành
job_queue = Queue(maxsize=100) # Đặt Max để Backpressure (áp suất ngược) không làm tràn RAM

# Spawn 5 Producers
producers = []
for i in range(5):
    th = threading.Thread(target=kafka_producer_worker, args=(job_queue, i))
    th.start()
    producers.append(th)
    
# Spawn 10 Consumers
consumers = []
for i in range(10):
    th = threading.Thread(target=database_consumer_worker, args=(job_queue, i))
    th.start()
    consumers.append(th)

# Đợi mỏi gối cho Kafka Producers nôn hết code
for p in producers:
    p.join()

# Bón viên thuốc độc (Poison pills) để kết liễu lũ Consumers
for _ in range(10):
    job_queue.put(None)

for c in consumers:
    c.join()
```

---

### Task 14: Rate Limiting (Thuật Toán Token Bucket)

**Problem:**
Đối tác cung cấp (3rd Party Data Vendor) gửi chát: "Ông chỉ được gọi API của tôi tối đa 50 requests mỗi giây. Phá lệ tôi block IP Cty Ông".
Hãy thiết kế lớp `TokenBucketRateLimiter` thread-safe.

**Solution:**
```python
import threading
import time

class TokenBucketRateLimiter:
    """
    Thuật toán kinh điển (Token Bucket) được Nginx/AWS API Gateway sử dụng đằng sau cánh gà.
    Mỗi dây sẽ nhỏ tọt 50 giọt nước (tokens) vào Xô (Bucket).
    Thread muốn ăn kẹo phải thò tay lấy được giọt nước trong xô mới cho đi qua cổng.
    """
    def __init__(self, capacity: int, fill_rate_per_sec: float):
        self.capacity = capacity
        self.tokens = capacity
        self.fill_rate_per_sec = fill_rate_per_sec
        self.last_fill_timestamp = time.monotonic()
        
        # Cảnh khuyển (Lock) cắn ai giành dật tài nguyên
        self.lock = threading.Lock()
        
    def _add_water_drops(self):
        # Tính khoảng trống từ lần cuối hứng nước ngầm
        now = time.monotonic()
        delta_time = now - self.last_fill_timestamp
        
        new_tokens = delta_time * self.fill_rate_per_sec
        
        self.tokens = min(self.capacity, self.tokens + new_tokens)
        self.last_fill_timestamp = now
        
    def acquire(self, tokens_needed: int = 1) -> bool:
        with self.lock:
            self._add_water_drops()
            if self.tokens >= tokens_needed:
                self.tokens -= tokens_needed
                return True
            return False

# Lúc dùng:
# rate_limiter = TokenBucketRateLimiter(50, 50.0)
# while True:
#     if rate_limiter.acquire():
#         thực_hiện_api_call()
#     else:
#         time.sleep(0.01) # Ngủ chợp mắt xin nước
```

---

### Task 15: Ngăn chặn Deadlock trong Concurrency

**Problem:**
Kho dữ liệu A (Redis) và B (Postgres) cọc tiền nạp cùng lốc. 
Thread X lấy chìa khoá (Lock) A, đang với tay xin chìa B.
Thread Y thộp được chìa B, đang với tay xin chìa A.
Kết quả: 2 Thread đực mặt nhau tới thiên thu. Hậu thuẫn sập (Deadlock).
Khắc phục thế nào?

**Solution:**
**Quy tắc vàng của Deadlock Prevention:** "Always acquire multiple locks in a global strict ordering". Tất cả các chủ phòng Thread phải bốc chìa khoá theo 1 chiều tuân thủ định luật từ điển (Alphabetical Order).
```python
import threading

lock_A = threading.Lock()
lock_B = threading.Lock()

def safe_transfer_lock_acquire(acq_target_1, acq_target_2):
    """
    Bắt buộc xếp chồng Lock theo ID địa chỉ bộ nhớ hoặc tên (VD: id(obj)).
    """
    # Ép ID của thằng nào nhỏ hơn sẽ luôn bị rờ vào lấy túi trước.
    first_lock = acq_target_1 if id(acq_target_1) < id(acq_target_2) else acq_target_2
    second_lock = acq_target_2 if id(acq_target_1) < id(acq_target_2) else acq_target_1
    
    with first_lock:
        with second_lock:
            # Giao dịch an toàn vạn kiếp không bế tắc
            print("Chuyển cục máu data thông suốt...")

# Safe: Thread X gọi safe_transfer_lock_acquire(lock_A, lock_B)
# Safe: Thread Y gọi safe_transfer_lock_acquire(lock_B, lock_A)
# Thread Y cũng bắt buộc đè lock_A ra lấy trước => Xếp hàng chờ Thread X buông tha lock_A. Hoà bình.
```

---

### Phần 3: Low-level File Processing

### Task 6: Tối ưu bộ nhớ với Lazy Loading CSV Generator 
**Problem:** Đọc file vỡ bờ 20GB bằng Python raw memory 500MB giới hạn mà không chết OOM.

**Solution:**
```python
def process_gigantic_csv_lazy(file_path: str, chunk_size=5000):
    """
    Bí kíp của DE lão làng: Data Streaming Yield Generator.
    "Dùng ít ăn ít nhả từng cục - không bao bọc mâm cỗ sình trương bụng".
    """
    def iter_csv_generator(path):
        with open(path, 'r', encoding='utf-8') as f:
            headers = f.readline().strip().split(",")
            for line in f:
                if line.strip():
                    values = line.strip().split(",")
                    # Chỉ trả 1 nháp dict cho người vòi vĩnh (Caller)
                    yield dict(zip(headers, values))
                    
    batch = []
    
    for row in iter_csv_generator(file_path):
        if not row.get("id") or row.get("status") == "FAIL":
            continue
        batch.append(row)
        
        # Sạt nước: Gửi lô lên DB gầm cao.
        if len(batch) >= chunk_size:
            yield batch
            # Cho object gom rác hệ thống (Garbage collector) liếm bay mảng chật hẹp
            batch = [] 
            
    if batch:
        yield batch
```

---

### Task 16: Checkpointing Resilient cho Long-Running Batch Jobs

**Problem:**
Script Python tổng hợp data chạy batch kéo suốt từ 1AM đến 5AM (4 tiếng). Đen đủi lúc 4:55 AM, Database đứt kết nối -> script `raise Exception` văng ra ngủm. Ngày mai bạn phải chạy lại tốn đúng 4 tiếng đồng hồ từ đầu vì không biết hôm qua chạy tới đâu rồi. Viết logic chống nhiễu đoạn (Resilient Checkpointing) cho Jobs dài hạn.

**Solution:**
Lưu lại HWM (High Water Mark - Vạch mực nước cao nhất) xuống ổ đĩa vật lý sau mỗi mẻ batch hoàn thành. Nếu đoạn nào chết, đọc lại cái file Watermark để resume nhảy vọt qua đống đã xử lý.

```python
import json
from pathlib import Path

class ResilientBatchJob:
    def __init__(self, checkpoint_path: str = "/tmp/batch_hwm.json"):
        self.checkpoint_path = Path(checkpoint_path)
        self.current_hwm = self._load_checkpoint()
        
    def _load_checkpoint(self) -> int:
        if self.checkpoint_path.exists():
            with open(self.checkpoint_path, 'r') as f:
                return json.load(f).get("last_processed_id", 0)
        return 0
        
    def _save_checkpoint(self, last_id: int):
        # High Water Mark chốt sổ
        with open(self.checkpoint_path, 'w') as f:
            json.dump({"last_processed_id": last_id}, f)
            
    def process_records(self, max_records=1000000, batch_size=10000):
        # Database giả lập
        records_generator = ({"id": i, "data": f"Data_{i}"} for i in range(1, max_records + 1))
        
        current_batch = []
        for row in records_generator:
            # Skip các đoạn data đã ăn nát râu hôm qua
            if row["id"] <= self.current_hwm:
                continue
                
            current_batch.append(row)
            
            if len(current_batch) >= batch_size:
                try:
                    # Giao hoán nạp đạn vào Data Warehouse (Biên độ Transaction)
                    # flush_to_dwh(current_batch) 
                    
                    # Thành công thì lưu HWM lại
                    last_successful_id = current_batch[-1]["id"]
                    self._save_checkpoint(last_successful_id)
                    current_batch = [] # clear đạn
                    
                except Exception as e:
                    print(f"Sập hầm ngang xương ở ID: {row['id']}. Mai chạy lại tiếp từ đây.")
                    raise e
```

---

### Task 17: Streaming XML Parsing Phân Tích Big Data không sập RAM

**Problem:**
Quên CSV đi, đối tác ngân hàng toàn gửi định dạng XML. Một file XML bọc thẻ `<Transactions>` bự 50GB. Hàm `xml.dom.minidom.parse()` của Python sẽ Load thẳng nguyên CÂY ĐỒ THỊ DOM 50GB vào RAM -> Nổ server. Làm sao để bóc tách node XML?

**Solution:**
Sử dụng IterParse (`xml.etree.ElementTree.iterparse`). Nó đi theo kiểu "Event-driven" (Lướt dòng xuôi tựa con chỏ). Khi đóng tag thẻ, xử lí Data Data rồi DỌN SẠCH bộ nhớ Cây tại rễ rụng, không bao giờ gom lại đống rác DOM Root.

```python
import xml.etree.ElementTree as ET

def parse_massive_xml_memory_safe(xml_file_path: str):
    """
    Sử dụng iterparse thay vì Load Tree. Node nào lấy xong là clear() rễ node đó lập tức.
    Memory sẽ chỉ tốn khoảng 5MB cho dù file có 500GB.
    """
    # Chỉ track các sự kiện khi tag đóng (end)
    context = ET.iterparse(xml_file_path, events=('end',))
    
    # Ép kiểu iterator để có thể nắm rễ đầu tiên trước
    _, root = next(context)
    
    counter = 0
    for event, element in context:
        if element.tag == 'Transaction':  # Tag đích mấu chốt
            # Bóc tách Data
            trans_id = element.find('ID').text
            amount = element.find('Amount').text
            
            print(f"Xử lý GD: {trans_id} - ${amount}")
            counter += 1
            
            # QUAN TRỌNG NHẤT: Giải phóng Element Tree khỏi Node mẹ (Root)
            # Khởi thuỷ vòng đời làm sạch RAM
            root.clear()
            
    print(f"Kéo thả hoàn tất {counter} đơn hàng mà ko trượt 1 byte RAM oom.")
    
# Cú chốt phỏng vấn: "Cách hay nhất của XML size lớn là hãy convert file qua JSON hoặc 
# Parquet luôn trước khi phân tích chuyên sâu".
```

---

## 🔗 Chặng Cuối

- [Data Structures for Data Engineers](07_Data_Structures_for_DE.md)
- [Quay lại Trang Chủ Interview](../README.md)

---

*Biên soạn: DE Master Reviewer Team - Shopee / Tech Giants Level (2026)*
