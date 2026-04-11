# ♟️ Data Structures & Algorithms cho Data Engineering (Masterclass)

> Bản Masterclass Thượng Thừa (1.5k+ dòng): File này KHÔNG luyện giải thi thố thuật toán LeetCode mẹo mực. Trọng tâm của bài là Cấu trúc dữ liệu và Thuật toán (DSA) ĐƯỢC ỨNG DỤNG THỰC TẾ TRONG BIG DATA. Một Data Engineer tier-1 cần thấu hiểu sâu sắc *tại sao* thuật toán nền tảng này nắm vai trò sống còn trong việc design các công cụ xử lý Dữ liệu lớn (như Flink, Kafka, Airflow, Graph Lineage, RocksDB).

---

## 📚 Mục Lục Toàn Tập Cuốn Bí Kíp

### Phần 1: Stream Processing & Advanced Array Memory
1. [Sliding Window - Bài toán dãy dữ liệu trong Streaming](#task-1-bài-toán-dãy-ngày-tăng-trưởng-liên-tiếp-tối-đa-sliding-window)
2. [Bloom Filters - Deduplicate Event tiền tỷ không tốn RAM](#task-5-bloom-filters-trong-data-engineering-deduplication)
3. [Consistent Hashing - Chia partition Kafka đều tăm tắp](#task-6-vòng-băm-chống-dồn-tải-consistent-hashing)

### Phần 2: Trees & Data Organization
4. [Trie (Cây Tiền Tố) - IP Routing & Elasticsearch Suggestion](#task-7-prefix-tree-trie---ip-routing-và-phân-tích-log)
5. [Cán mỏng Deep JSON không đệ quy bằng Stack (DFS)](#task-3-flatten-nested-data-siêu-sâu-tránh-recursionerror)
6. [LSM-Trees (Log-Structured Merge-Tree) - Trái tim của NoSQL](#task-10-lsm-trees-trái-tim-của-cassandra--rocksdb)
7. [Heaps (Priority Queue) - External K-way Merge Sort file lớn](#task-8-k-way-merge-sort-với-heap-xử-lý-chập-nhiều-file-khổng-lồ)

### Phần 3: Graphs, Caching & Advanced Analytics
8. [Topological Sort - Trái tim của Airflow DAG](#task-2-giả-lập-airflow-scheduler-phân-tích-trình-tự--nhận-báo-vòng-lặp)
9. [DFS Data Lineage - Phát hiện thảm họa Downstream](#task-4-cỗ-máy-dò-tìm-tác-động-dòng-chảy-hậu-duệ-downstream-lineage)
10. [LRU Cache - Giảm tải Database Lookup Cost](#task-9-lru-cache---tối-ưu-bộ-nhớ-tạm-trên-spark-executor)
11. [Roaring Bitmaps (Bitmap Index) - Đếm siêu tốc ở ClickHouse](#task-11-roaring-bitmaps-chìa-khoá-của-olap-database)
12. [Union-Find - Gộp Entitity (User Deduplication)](#task-12-union-find-disjoint-set---hợp-nhất-định-danh-khách-hàng)

---

## 🌊 Phần 1: Stream Processing & Advanced Array Memory

**TẠI SAO PHẢI THẤU HIỂU NGUYÊN LÝ NÀY?**
Khi dữ liệu truyền vào vĩnh viễn theo thời gian thực (real-time streaming infinite bounds) qua hệ thống như Apache Flink, Kafka Streams hay Spark Structured Streaming, chúng ta không thể lưu trữ được tất cả event trọn đời vào RAM để tính toán (`GROUP BY`). Hệ thống giải quyết bằng các "Khung thời gian" (Window) đẩy cuộn dần. Quản lý pointer để gom cục các nhóm Metric theo State (Memory local cục bộ) là cốt lõi của bài toán này. Những hệ thống này cũng đòi hỏi quản trị Memory Fingerprint siêu gắt gao.

### Task 1: Bài toán Dãy Ngày Tăng Trưởng Liên Tiếp Tối Đa (Sliding Window)

**Problem:**
Bạn nhận được một batch stream doanh thu hằng ngày trong mảng. Tìm chuỗi ngày liên tiếp cực đại có doanh thu tăng liên tục ngày hôm sau nhỉnh hơn hôm trước.

**Solution:**
Ta sẽ dùng kĩ thuật Variable Pointer kết hợp Sliding Data để tính toán, chỉ tốn $O(1)$ memory state overhead. Hệ thống sẽ càn quét dòng lũ data đúng 1 lần (Single Pass Iteration).
```python
def find_longest_growth_streak(revenue_stream: list[float]) -> int:
    """
    Giả lập logic cập nhật State (Stateful checking) trong Stream data.
    - Time Complexity: O(N) - Chạy thông list data 1 mạch (Linear Scan).
    - Space/Memory Complexity: O(1) - Chỉ lưu đúng 2 con trỏ state nguyên thủy. Rất an toàn memory.
    """
    if not revenue_stream:
        return 0
        
    maximum_streak = 1
    current_active_streak = 1
    
    # Checkpoint từ t+1 so sánh t. 
    for i in range(1, len(revenue_stream)):
        if revenue_stream[i] > revenue_stream[i-1]:
            # Biến tích lũy state (Accumulated event metric)
            current_active_streak += 1
            maximum_streak = max(maximum_streak, current_active_streak)
        else:
            # Ngắt cầu tiêu huỷ window chốt lại - Reset the state pointer
            current_active_streak = 1
            
    return maximum_streak

# 👉 System Focus: Trong Streaming Engines Flink, code tương đương việc định nghĩa 
# một ProcessWindowFunction mà mỗi tín hiệu event trigger hàm update giá trị ValueState() trên TaskManager.
```

---

### Task 5: Bloom Filters trong Data Engineering (Deduplication)

**Problem:**
Crawler của công ty bạn thu thập hàng TỶ URLs mỗi ngày vào trong Data Lake. Bạn muốn viết 1 Streaming Filter để cản không xử lý các URL TRÙNG LẶP đã từng đi qua. Giả sử 1 URL dài 100 Bytes. 1 Tỷ URL nhét vào HashSet bằng Python/Java ngốn tưng bừng tới 100GB Của RAM. Làm sao để chặn trùng lặp mà tốn chỉ tốn vài chục Megabytes?

**Analytical Thinking (Tư Duy Thuật Toán):**
Bloom Filter sử dụng sức mạnh của Hashing và Binary Arrays (Mảng Bit 0 và 1). 
Thay vì lưu nguyên cái tên URL, gõ cái tên URL vào Hash function -> Nhận được một con số. Nhảy tới vị trí (Index) số đó trong Mảng Dài của Bloom, bật công tắc số này từ 0 thành 1.
Chấp nhận tỷ lệ False Positive (Rủi ro rất nhỏ đụng hàng độ băm, nhận vơ URL mới là quen). Bloom Filters không có chối bỏ False Positive, nhưng nó đảm bảo "No False Negatives" (Nếu nó nói KHÔNG quen, thì chắc chắn 100% URL là mới hoàn toàn). Đây hoàn toàn có thể bỏ qua được trong Crawler Analytics.

**Solution:**
```python
import hashlib
import math

class ProbabilisticBloomFilter:
    """
    Triển khai cấu trúc Bloom Filter chặn trùng lặp Big Data (Deduplication filter).
    Ứng dụng thực tế:
    - Cassandra/RocksDB check xem SSTable có chứa record không trước khi đọc IO đĩa.
    - Kafka/Flink exactly-once delivery check trùng log messages.
    """
    def __init__(self, expected_items: int, false_positive_rate: float):
        # Công thức toán học (Math formulation): 
        # m (bit array size) = -(n * ln(p)) / (ln(2)^2)
        # k (hash functions) = (m / n) * ln(2)
        
        self.size = self._get_size(expected_items, false_positive_rate)
        self.hash_count = self._get_hash_count(self.size, expected_items)
        
        # Mảng bit sử dụng bitwise operation để siêu tiết kiệm memory
        # Python list tốn cỡ 8 byte/phần tử. Chúng ta xài bytearray tiết kiệm gấp tỉ lần.
        self.bit_array = bytearray((self.size + 7) // 8)
        
    def _get_size(self, n, p):
        m = -(n * math.log(p)) / (math.log(2) ** 2)
        return int(m)
        
    def _get_hash_count(self, m, n):
        k = (m / n) * math.log(2)
        return max(1, int(k))
        
    def _create_hashes(self, item: str):
        # Dùng nhiều hàm hash (ảo) bằng cách cấy biến thể seed trên 1 hàm hash MD5
        base_hash = hashlib.md5(item.encode('utf-8'))
        digest = int(base_hash.hexdigest(), 16)
        
        hashes = []
        for i in range(self.hash_count):
            h = (digest + i * i) % self.size
            hashes.append(h)
        return hashes
        
    def add(self, item: str):
        """
        Nhét Event Key mới (URL, Traces ID) vô bộ lọc.
        O(K) thao tác bật Bit = 1 cấp tốc.
        """
        hashes = self._create_hashes(item)
        for h in hashes:
            byte_index = h // 8
            bit_index = h % 8
            # Nạp Bit 1 bằng cổng OR (`|`)
            self.bit_array[byte_index] |= (1 << bit_index)
            
    def contains(self, item: str) -> bool:
        """
        Scan Event.
        O(K) check, nếu dính dù chỉ một bit = 0. Tức là SURE KÈO CHƯA TỪNG TINH TƯ. Hàng mới đét!
        Nếu bit toàn màu cờ đỏ = 1. -> Xác xuất cao (tuỳ FP Rate) là bị SPAM trùng lặp -> Né.
        """
        hashes = self._create_hashes(item)
        for h in hashes:
            byte_index = h // 8
            bit_index = h % 8
            # So cổng AND (`&`)
            if not (self.bit_array[byte_index] & (1 << bit_index)):
                return False
        return True

# Phỏng Vấn Question: Lỡ Memory tui dư nhiều thì xài Hash Set bình thường được không?
# Trả lời: Trong Streaming/Real-time ingestion, Garbage Collection (GC) của JVM/Python sẽ đóng băng 
# hệ thống khi quét Dọn một HashTable có 1 tỉ Object String. Bloom Filter mảng Byte thô sơ tránh 
# dập RAM và ko gây đứt quãng độ trễ mạng tẹo nào.
```

---

### Task 6: Vòng Băm Chống Dồn Tải (Consistent Hashing)

**Problem:**
Bạn cấu hình hệ thống với 5 node Kafka / Redis để gánh phân tán Cache User Carts (Giỏ hàng). Để chia tải, bạn dùng công thức Cổ Khảo `node_index = hash(user_id) % 5`. Quá trơn tru mượt mà! 
Nhưng năm nay cty ra chiến dịch bão Sale Shopee, Server cháy, Sếp lệnh bổ sung vào thêm 2 Node (Tổng lên 7 nodes).
Cú `hash(user_id) % 7` này phá tan cmn hoang cấu trúc cũ. 95% Cache của hệ thống đột ngột bị miss (Trượt kết quả) và phải đi chọc lại Database. Database chịu không nổi nghìn tỷ con trỏ vào gọi -> Crash cty. Làm thế nào để giải quyết scale server không bị miss cache?

**Analytical Thinking (Tư Duy Cấu Trúc Đồ Thị / Mảng):**
Dùng Consistent Hashing - Tưởng tượng Node Sever không phải mảng tuyến tính mà nằm trên 1 "Vòng tròn". Giống cái mâm bàn quay (Hash Ring). Node nằm ở góc 12h, 3h, 6h, 9h. Giá trị `user_id` cũng là 1 con số nằm trên mâm, nó sẽ lấy Data từ Node xuất hiện theo chiều kim đồng hồ ngay cạnh gần nhất.
Khi thêm 1 Node vô góc 4h. Nó chỉ chia lại miếng bánh từ Node 6h lấy Data, và KHÔNG HỀ đụng chạm hay phá cấu trúc Của Node 12h và 9h. Đỡ thảm hoạ Scale-up rực rỡ nhất!

**Solution:**
```python
import hashlib
import bisect

class ConsistentHashingStreamPartitioner:
    """
    Trái tim định tuyến chia Node lưu trữ của Cassandra Ring và DynamoDB.
    """
    def __init__(self, nodes: list, virtual_replicas: int = 100):
        self.virtual_replicas = virtual_replicas
        self.hash_ring = [] # Sorted Array 
        self.node_mapper = {} # Lưu vết Hash_Key -> Server Name
        
        for node in nodes:
            self.add_node(node)
            
    def _hash(self, key: str) -> int:
        return int(hashlib.md5(key.encode('utf-8')).hexdigest(), 16)
        
    def add_node(self, node: str):
        """
        Kỹ thuật Virtual Nodes: Tránh trường hợp chia mâm lồi lõm rải rác trên Vòng Tròn.
        Node A sẽ dc sinh ra tự động 100 phiên bản Clone trên Cây, rải tăm vãi trấu tứ phía.
        O(R log N) Time Complexity chèn vào Mảng Binary Sort.
        """
        for i in range(self.virtual_replicas):
            virtual_key = f"{node}_replica_{i}"
            ring_hash_value = self._hash(virtual_key)
            
            # Insort là chèn nhét Binary Search giữ List luôn được Sort mà không xào tốn N
            bisect.insort(self.hash_ring, ring_hash_value)
            self.node_mapper[ring_hash_value] = node
            
    def remove_node(self, node: str):
        for i in range(self.virtual_replicas):
            virtual_key = f"{node}_replica_{i}"
            ring_hash_value = self._hash(virtual_key)
            self.hash_ring.remove(ring_hash_value)
            del self.node_mapper[ring_hash_value]
            
    def get_assigned_node(self, stream_key: str) -> str:
        """
        Quyết định xem event này chảy vô Node Máy Chủ Nào.
        O(Log N). Binary Search mượt.
        """
        if not self.hash_ring:
            return None
            
        data_hash = self._hash(stream_key)
        
        # Tìm idx vòng quay theo kim đồng hồ gần nhất
        # Binary search (Bisect_Right) chặt nhị phân độ sát góc
        idx = bisect.bisect_right(self.hash_ring, data_hash)
        
        # Nếu Event rớt ra ngoài biên của Node ở Vĩ tuyến cuối, vòng quy ngược kim đồng hồ
        # trả về Node xuất phát đỉnh chóp vòng xoay
        if idx == len(self.hash_ring):
            idx = 0
            
        server_hash_key = self.hash_ring[idx]
        return self.node_mapper[server_hash_key]

# 💡 Kết quả lúc Phỏng Vấn: Nhờ kỹ thuật này, khi bổ sung server, 
# ta chỉ mất k / n số liệu dịch chuyển Cache. (N là số node mới, k là slot data).
# Nghĩa là thêm Node thứ 7, hệ thống chỉ miss cache tái phân rã 1/7 lượng Data, chừa lại 85% Cache
# vô thương. Không bao giờ DB bị dập Overload thui chột.
```

---

## 🌲 Phần 2: Trees & Data Organization

### Task 7: Prefix Tree (Trie) - IP Routing và Phân tích Log

**Problem:**
Trong hệ thống Log Aggregation 100K logs/sec, bạn cần map địa chỉ IPv4 thô sang dạng Geographic Location (Quốc gia, Thành phố), hoặc Autocomplete (Gợi ý lệnh truy vấn SQL Search Index cho Kibana).
Nếu bạn lưu một Hash Map có 4 Tỷ cái IPv4, RAM của bạn sẽ vỡ nát ngay lập tức (Hash Collisions cực bự và String size tốn Memory). Hãy design một cấu trúc tìm kiếm tiền tố siêu việt.

**Analytical Thinking:**
Triển khai Cây Tiền Tố (Trie/ Radix Tree). Quá trình di chuyển tìm IP hay chuỗi Keyword đi theo mảng cắt vụn Characters. Tra cứu string có length M thì tốn đúng Time Complexity $O(M)$ không phụ thuộc tỷ lượng String kho chứa N records. 
Đối lập với Regex scan mất $O(N)$ càn quét. Trie là kiến trúc vua của Fast String Pattern.

**Solution:**
```python
class TrieNode:
    def __init__(self):
        self.children = {}
        self.is_end_of_ip_block = False
        self.geo_metadata = None

class IPTrieRouter:
    """
    Trie (Prefix Tree) thiết kế tối ưu hoá cho IP Routing Table và Geo Map.
    Memory Footprint chia sẻ cấu hình chung tiền tố: Mạng "192.168" dùng chung một Rễ cây.
    Thay vì 1 triệu IP bắt đầu = "192" tốn 1 triệu bản sao chuỗi trên Object Heap.
    """
    def __init__(self):
        self.root = TrieNode()
        
    def insert_subnet(self, ip_prefix: str, geo_data: str):
        """ Time: O(L) với L là độ dài string phân mục IP Subnet. Space: Tiết kiệm tối đa Prefix chia sẻ """
        current = self.root
        for char in ip_prefix:
            if char not in current.children:
                current.children[char] = TrieNode()
            current = current.children[char]
            
        current.is_end_of_ip_block = True
        current.geo_metadata = geo_data
        
    def resolve_ip_location(self, ip_address: str) -> str:
        """
        Tìm chuỗi tiền tố Subnet Block dài nhất khớp với IP Request Event.
        Cực kì hữu dụng chống Spoofing Spam Rate Limiting Rules.
        """
        current = self.root
        longest_matching_geo = "UNKNOWN_OR_UNALLOCATED"
        
        for char in ip_address:
            if char in current.children:
                current = current.children[char]
                if current.is_end_of_ip_block:
                    longest_matching_geo = current.geo_metadata
            else:
                break # Chặt nhánh thoát hiểm.
                
        return longest_matching_geo

# Phỏng vấn: Elasticsearch cấu hình Edge N-Gram Autocomplete cũng dùng kiến trúc vương giả (FST - Finite State Transducer) gần gũi với Trie để search trong O(1).
```

---

### Task 3: Flatten Nested Data siêu sâu tránh RecursionError

**Problem:**
Bóc tách đập phẳng dữ liệu thô JSON lồng ghép nhiều tầng nấc trả về một chiều bảng Schema SQL Phẳng (Flat Key-Value pairs).

**Analytical Thinking:**
"Cây" (Trees) là cấu trúc của Data Đa Mức Mảng / Cấu Trúc Bán Cấu Trúc (Semi-Structured Data), rành rọt nhất là dạng raw Mongo/NoSQL/JSON Document nested vô cùng sâu không rõ điểm khựng.
Flatten chúng bằng các vòng đệ quy Call Stack sẽ bị Stack Overflow Limits. Do Python/JVM ấn định Limit (Thường 1000). DFS (với Stack heap memory thủ công) giải quách được JSON Unnest Array thành Cây bẹt. Mọi rẽ nhánh đều Push vào Stack đệm ảo.

**Solution (Iterative DFS Stack Pattern):**
```python
import json

def flatten_bottomless_json(nested_source: dict) -> dict:
    """
    Sử dụng Stack trong heap memory phá vỡ giới hạn Deep Recursion.
    - Time Complexity: O(N) dạo đúng lượng cặp key-value tổng cộng file raw.
    - Space/Memory Level: O(D) lưu footprint chiều nhành sâu tối đa của Cây vào Stack.
    """
    flattened_schema = {}
    
    # Stack ghim cấu trúc Tuple tracker (Tiền tố Đường dẫn Field Prefix, Cục Node)
    # Ví dụ ("user_profile", {"age": 20})
    iteration_stack = [("", nested_source)]
    
    while iteration_stack:
        current_path_prefix, node = iteration_stack.pop()
        
        if isinstance(node, dict):
            for child_key, child_val in node.items():
                new_concat_path = f"{current_path_prefix}_{child_key}" if current_path_prefix else child_key
                # Spread nón rể nhánh cây Push vùi vào LIFO Stack.
                iteration_stack.append((new_concat_path, child_val))
                
        elif isinstance(node, list):
            # Với cấu trúc Array Data Warehouse BigQuery/Snowflake chuộng cast ra VARCHAR ARRAY JSON.
            flattened_schema[current_path_prefix] = json.dumps(node)
            
        else:
            # Lõi mỏ Scalar đơn tuyến Leaf
            flattened_schema[current_path_prefix] = node
            
    return flattened_schema
```

---

### Task 10: LSM-Trees (Trái tim của Cassandra & RocksDB)

**Problem:**
Bạn muốn build một hệ thống Write-Heavy Ingestion (Event Tracking) đập vô hàng Triệu request/s. Tại sao nhét thẳng vô RDBMS MySQL cùi bắp hay PostgreSQL dùng Cấu trúc B-Tree lại bị thắt cổ chai đĩa (Disk Thrashing) chậm kinh hoàng?

**Analytical Thinking:**
B-Tree Của Database cổ điển là "In-place update", khi sửa Data, ổ đĩa sẽ phải dịch con trỏ Seek từ rãnh Random đĩa cứng này trượt sột soạt sang Track rãnh kia (Random I/O Writes - Chậm nhất thế giới).
LSM-Tree (Log-Structured Merge-Tree) thay đổi hoàn toàn khái niệm Lưu Trữ. Nó biến Mọi thao tác Ghi Thành Sequential I/O (Ghi đằng tút đuôi dây băng tịnh tiến, siêu cấp vũ trụ lẹ O(1) appending).

**Giảng giải tư duy Data Architecture:**
1. **MemTable**: Khi có luồng Insert, đổ mẹ vô RAM Memory. Nhào trộn Sort cây Nhị phân nhẹ tựa lông hồng.
2. **SSTable / Flushing**: Khi RAM béo phì (Full), Đổ bê tông MemTable đóng đông trên đĩa Hard Drive (Được tệp SSTable bất biến - Không một vị thánh nào có quyền sửa file này).
3. **Compaction**: Sau 1 tháng, ta có 1 Đống File SSTable nát bấy hầm bà lằng. Server ngầm lúc rảnh rỗi sẽ dùng thuật toán `K-Way Merge Sort Algorithm` gộp quét Mấy File Phẳng Lầm Lì đó quy hồi về 1 Khối Bê Tông to bành (Dệt đi đống rác Cũ Delete/Update ghi đè).

```python
# 👉 NOTE FOR DE INTERVIEW: Bạn không cần phải code hàm LSM Tree từ số 0.
# Yêu cầu System Insight: Vượt qua hệ thống Kafka, Flink Checkpoints, 
# ClickHouse MergeTree, InfluxDB time-series engines điều được nhào nặn 
# chìm bởi LSM-Trees.
# B-Tree: Rất tốt cho Read-Heavy (Đọc nhiều râu ria do tree balance O(log N)).
# LSM-Tree: Thánh nổ của Big Data Streaming vì O(1) appends Write-Intensive.
```

---

### Task 8: K-Way Merge Sort với Heap (Xử lý chập nhiều File Khổng lồ)

**Problem:**
Nền hệ điều hành chỉ cấp cho bạn 500 MB RAM máy. Bạn có 100 File logs Server, mỗi file nặng 10 GB đã trót được Sort Sơ Cấp bằng ID Tăng Dần. Bạn muốn gộp mập nối 100 File này thành Độc Nhất 1 File Cụ Tổ (1.000GB) hoàn hảo Sắp xấp Tăng dần Toàn Cục.

**Analytical Thinking:**
Luật của Big Data: Không Mở 1000 GB Nhét Vô RAM.
Luật của External Sort: Load Nét Cạnh Biên Vào Bằng Cấu trúc Minimum Priority Queue (Min-Heap).

**Solution:**
Sử dụng Heap. Đưa Đỉnh đầu dòng tiên phong rẻ nhất của mỗi File vào Mâm Thi Đấu (Heap). Bốc Thằng Thấp Nhất Ném Xuống Ổ Đĩa Mới. Nó thuộc file nào, ta bóc tiếp dòng kế cận nhồi vô Mới Mâm. Cứ cào như vậy, Memory RAM không bao giờ trút cao hơn Mâm 100 thằng Hàng Đại Diện O(K).

```python
import heapq

def k_way_external_file_merging(sorted_files_paths: list[str], output_path: str):
    """
    Min-Heap P-Queue Merging. Trái tim của MapReduce (Giai đoạn Reduce/Sort Shuffle phase).
    Cũng là thuật toán Compaction gộp lèn Rác SS-Tables của Cassandra/LSM-Trees phía trên.
    Time Complexity: O(N log K) với N dòng dữ liệu tổng, K là số lượng files Mâm Đấu (Lõi logK bốc ra vô heap).
    Space Complexity: O(K) con trỏ Pointer đệm Stream - Siêu Nhẹn Cứu dỗi RAM Server nhỏ lẻ.
    """
    
    # Kẹp mảng mở files trỏ đuôi lướt (Iterator File Handlers)
    # Rất ngốn File Descriptor (Cẩn thận Lệnh Ulimit mốc 1024 ở OS Linux Mặc Định)
    file_handlers = [open(path, 'r') for path in sorted_files_paths]
    output_f = open(output_path, 'w')
    
    # Priority Queue Heap Cấu Tạo 
    min_heap = []
    
    # Bước 1: Kéo Lần lượt Mạng Bọc Dòng Đầu Tiên Lên Thi Đấu
    for idx, fh in enumerate(file_handlers):
        first_line = fh.readline()
        if first_line:
            # Nhét Tuple Sorting Criteria (Chuỗi Data Text, Bản sắc Căn Cước của thằng Nào / File Index)
            # Tuple đánh số theo [0] element bốc trước
            heapq.heappush(min_heap, (first_line, idx))
            
    # Bước 2: Vòng xoáy Cát Trắng Hút Min
    while min_heap:
        smallest_val, owner_val_file_idx = heapq.heappop(min_heap)
        
        # Bắn nhả Lượng Đáy Dải Đất xuống Đĩa mới
        output_f.write(smallest_val)
        
        # Thác Đổ - Đi tìm Rút Ruột Nhập Hàng Tế Thế
        source_file_fh = file_handlers[owner_val_file_idx]
        next_line = source_file_fh.readline()
        
        if next_line:
            heapq.heappush(min_heap, (next_line, owner_val_file_idx))
            
    # Hậu kiểm Cleanup Cháy Vườn Đuổi Chim
    for fh in file_handlers:
        fh.close()
    output_f.close()
```

---

## 🕸️ Phần 3: Graphs, Caching & Advanced Analytics

### Task 2: Cổ Máy Xếp Lịch Bất Khả Bại (Topological Sort trong Airflow DAG)

**Problem:**
Bạn được yêu cầu code hệ thống cốt lõi (Core Engine) cho một Job Scheduler tuân theo cấu trúc DAG (Directed Acyclic Graph - Đồ thị có hướng không tuần hoàn) rặt như Apache Airflow hay dbt.
Hệ thống cho bạn một list các Công việc (Tasks) và Khoá Luồng Ràng Buộc Phụ Thuộc (Dependencies). Ví dụ `Task_B` chạy sau `Task_A`. `Task_E` chạy sau cả `Task_C` và `Task_D`.
Hai điểm mấu chốt bạn phải giải quyết cho Phỏng vấn viên:
1. Thứ tự chạy chuẩn xác cho ThreadPool Engine bốc đúng mâm?
2. Bịt lỗ hổng Trí Mạng: Kiểm tra xem User định nghĩa DAG có bị "Ngáo Cần" (Vòng lặp bất tận - Cycle Dependency, vd A -> B -> C -> A) không?

**Analytical Thinking (Phân Tích Giải Thuật):**
Giải pháp tối thượng cho mọi bài toán Dependency là Thuật toán Khoá Phân Cấp Kahn (Kahn's Algorithm for Topological Sorting).
Ý tưởng của Kahn cực ngầu: Mọi Task đều có In-Degree (Số Tên Phả Hệ đứng đè đầu cưỡi cổ chờ mình).
- Bước 1: Gắp TẤT CẢ các Task có `In-Degree == 0` (Bậc Không Cấm Kỵ 100% tự do) nhét vào Queue khởi điểm.
- Bước 2: Bốc 1 đứa Tự do ra khỏi Queue để Executor OS chạy code.
- Bước 3: Đứa đó chạy xong, nó Cắt đứt Dây Phả Hệ Trói Xuống đám con (Giảm `In-Degree` của bọn Con đi 1).
- Bước 4: Thằng con nào mà `In-Degree == 0` thì lập tức giác ngộ Vô Queue Tự Do chờ chạy.
Cuối cùng: Nếu đếm được số lượng task Chạy thành công mà Mắc Hụt so với Tổng đống DAG Ban đầu -> Hệ thống bị nguyền rủa Cycle Mắc Cạn Vòng Lặp Trầm Luân! (Airflow sẽ raise `DagCycleException`).

**Solution:**
```python
from collections import deque, defaultdict

def compile_and_run_dag_scheduler(tasks: list[str], dependencies: list[tuple[str, str]]) -> list[str]:
    """
    Kahn's Topological Sort.
    - Time Complexity: O(V + E) đỉnh + Nét Đứt Cạnh. Dạo vòng quanh mâm cỗ đúng 1 lần.
    - Space: O(V + E) Cho mảng băm chứa Hash Map Adjacency.
    """
    # Xây cất kiến trúc móng đồ thị
    adj_graph = defaultdict(list)
    in_degree = {task: 0 for task in tasks}
    
    # dependencies quy ước: (Tiền nhân u, Hậu bối v) - u phải chạy xong trước v
    for u, v in dependencies:
        adj_graph[u].append(v)
        in_degree[v] += 1
        
    # Chuông Báo Gọi Trận
    independent_queue = deque([t for t in tasks if in_degree[t] == 0])
    
    execution_order = []
    
    while independent_queue:
        current_node = independent_queue.popleft()
        
        # Trigger execution_worker.submit(current_node)
        execution_order.append(current_node)
        
        # Mở cổng Trói dây
        for child_task in adj_graph[current_node]:
            in_degree[child_task] -= 1
            if in_degree[child_task] == 0:
                independent_queue.append(child_task)
                
    # Tử huyệt kiểm tra Vòng Lặp Vô Song
    if len(execution_order) != len(tasks):
        raise ValueError("Phát hiện DAG Cycle: Ảo đảo Bế Tắc Vô Tận. Review lại phụ thuộc Job.")
        
    return execution_order
```

---

### Task 4: Cỗ Máy Dò Tìm Dòng Chảy (Downstream Lineage) với DFS Graph

**Problem:**
Bảng gốc nguồn `source_sap_erp` bất chợt đổ bể chứa Cột Doanh Thu rác âm. Lệnh trên Giám Đốc đập xuống: "Ngay lập tức truy luân xem Bảng này có rây cứt bẩn vào những bảng con bảng cháu dbt Data Warehouse nào đang lấp liếm ngoài Frontend Tableau Dashboard không?".
Cấu trúc Data Warehouse Lineage tồn tại dưới dạng Đồ thị hướng. 

**Analytical Thinking (Phân Tích Giải Thuật):**
DFS (Depth First Search - Tìm kiếm Lật móng rễ sâu tới đáy Bùn). Trái lại với BFS (Tìm Mạng Lưới Nhỏ Lòng Mạch Nông). Đi tìm phả hệ đổ tội, bạn phải sục sôi ngọn nguồn tới Bảng Chó Ngáp (Tận cùng Dashboard), do đó DFS ăn tiền 100%.

**Solution:**
```python
import collections

def track_downstream_impacts_recursive(lineage_graph: dict[str, list], start_table: str) -> list[str]:
    """
    Tiến hành rải thuốc nhuộm (Tracking) tất cả các Bảng Cháu Chắt bị Ô Nhiễm.
    Sử dụng Set để tránh vòng lẩn quẩn View đan xen (Graph Traversal có Loop back).
    Time Complexity: O(V + E) Vét màng toàn cọp.
    """
    polluted_tables = set()
    
    def dfs_paint_poison(current_table):
        # Base mark (Vết chân đếm qua)
        polluted_tables.add(current_table)
        
        # Nếu chưa leo lên ngọn (Chưa ra Tableau), Lùng Sục Đi Chặn Con Cháu
        if current_table in lineage_graph:
            for child_dependent_table in lineage_graph[current_table]:
                if child_dependent_table not in polluted_tables:
                    dfs_paint_poison(child_dependent_table)
                    
    # Triệu Hồi Độc Tố Ngọn Nguồn
    dfs_paint_poison(start_table)
    return list(polluted_tables)
```

---

### Task 9: LRU Cache - Tối ưu Bộ nhớ tạm trên Spark Executor/Application

**Problem:**
Luồng xử lý (Data Flow) kéo lên phải liên tục Convert "Mã Khách Hàng (Customer_UUID)" thành "Tên Chuyên Nghiệp Khách Hàng". Nếu gọi Postgres DB 10Tỉ dòng gọi hoài thì sập Cụ Postgres chết đứng Database.
Tuy nhiên, có luật Pareto: 20% Customers Mua tấp nập chiếm 80% Tra cứu Log. Bạn thiết kế 1 Local Cache Memory ở Client bằng Python lưu 10.000 dòng.
Luật LRU (Least Recently Used): Hễ Đứa Nào Xưa Cổ không xài ngán chỗ Cút Xuống Đáy xả rác cho Đứa Xài Nhiều nạp vào.

**Analytical Thinking:**
HashMap Dictionary thuần của Python chỉ tốn O(1) Fetch/Add. Nhưng Không lưu lại vết thời gian xài của Cấu kiện.
Nếu xài Mảng Array lưu Vết xoá mảng Tức là O(N) cho thao tác Delete Shifting chèn phứa. Đám Big Data Không khoan nhượng Nào Chịu Chờ O(N) trơ tráo.
Gộp Hash Map + Dây Chuyền Kép Liên Kết (Doubly Linked List). Add O(1) Tìm Ra. Xoá O(1) cắt nốt dây. Lắp Đít / Rời Đầu O(1). Hoàn hảo Tuyệt Đối Luyện Công Nghệ O(1) Constant Time.

**Solution:**
```python
class NodeDList:
    def __init__(self, key, value):
        self.key = key
        self.value = value
        self.prev = None
        self.next = None

class LRUCacheDict:
    """
    Design Pattern Của Redis Internal & Postgres Buffer Pool.
    Bằng sự trợ giúp Python Doubly Linked List, Các Thao tác Nhạt Phèo nhất Đều ăn O(1).
    Phỏng vấn OOD (Object Oriented Design) Data Engineer không bao giờ chạy thoát Bài Này.
    """
    def __init__(self, capacity: int):
        self.capacity = capacity
        self.cache_mapper = {}
        
        # Guard Rails Dummy (Lính gác xẹt cửa không mang data bảo vệ viền đê)
        self.ancient_tail = NodeDList(0, 0)
        self.recent_head = NodeDList(0, 0)
        
        self.recent_head.next = self.ancient_tail
        self.ancient_tail.prev = self.recent_head
        
    def _kick_out_node(self, node: NodeDList):
        """ Thủ thuật vá màng: Rút nó ra và Cắm lại 2 Đầu dây Bẹn nhau """
        prev_node = node.prev
        next_node = node.next
        prev_node.next = next_node
        next_node.prev = prev_node
        
    def _shove_node_to_latest_head(self, node: NodeDList):
        """ Kẹp cái Node nạp Nhanh Lú lẫn Trọng Yêu Nhất Vào Ngay Sau Gáy Guard Head """
        node.prev = self.recent_head
        node.next = self.recent_head.next
        
        self.recent_head.next.prev = node
        self.recent_head.next = node
        
    def fetch_record(self, key: int) -> int:
        if key in self.cache_mapper:
            node = self.cache_mapper[key]
            # Mới lướt tay Đụng Vào => Hot Data Nhét Chui Cấp Bách lên Đỉnh Dây
            self._kick_out_node(node)
            self._shove_node_to_latest_head(node)
            return node.value
        return -1
        
    def cache_record(self, key: int, value: int):
        if key in self.cache_mapper:
            node = self.cache_mapper[key]
            self._kick_out_node(node)
            node.value = value
            self._shove_node_to_latest_head(node)
        else:
            if len(self.cache_mapper) >= self.capacity:
                # Xả Khát nước ngấm nát Vứt Rác Chặn Cửa Cũ
                lru_rotting_node = self.ancient_tail.prev
                self._kick_out_node(lru_rotting_node)
                del self.cache_mapper[lru_rotting_node.key]
                
            new_chad_node = NodeDList(key, value)
            self.cache_mapper[key] = new_chad_node
            self._shove_node_to_latest_head(new_chad_node)
```

---

### Task 11: Roaring Bitmaps (Chìa khoá của OLAP Database)

**Problem:**
Trong ElasticSearch hoặc Clickhouse, Query đếm số Khách (COUNT DISTINCT User_ID) Mua hàng hôm qua và cả Mua hàng Tuần trước (Intersection Giao Tập) trên Tổng Dân Cư Sinh sống 30 Triệu User. Nhanh nhạy Mốc Chóp không độ Trễ tính trên Milli Giây.
Nếu Nhét Array Giao Nhau (Set Intersection), Duyệt List cực đắt O(N + M). 

**Analytical Thinking (Cấu Trúc Tệp Toán Học Bitmap):**
Đừng Lưu Dấu ID Tự Bự String. Gán Mỗi User Một Mã Int Số Nguyên tăng Tịnh từ 0 đến N.
Tạo một Mảng Bits Bitmap Trắng phớ. Hôm Qua Thằng Mã số 5, 9, 31 mua Hàng -> Bật Bit vị trí 5, 9, 31 lên = 1.
Chốt Hôm Qua: `[0, 0, 0, 0, 0, 1, 0, 0, 0, 1 ...]`
Tuần Trước:  `[0, 0, 0, 0, 1, 1, 0, 0, 0, 1 ...]`
Tìm Số Khách Thơm 2 Lần Cả Tròn Cặp: Lôi Toán AND Nhị Phân Gõ Chồng Nhau `Bit_Yesterday & Bit_LastWeek`.
CPU Xử Lí AND Nhị Phân Trên Lực Tập Băng Chuyền Xử lí Song song Nhanh gấp 100 Lần Phếp Toán Thường Tình Toán Ngôn Ngữ Bậc Cao. Không Cần Loop Tìm O(N).

**Solution (Mindset Explanation):**
```python
# 👉 NOTE GHI CHÚ GHI NHỚ INTERVIEW:
# Roaring Bitmaps (RB) là Bitmap nén Gọn Đảo Chiều Không Lề Mép Mảng BIT Thường.
# Do Sparse Data (Data rỗng cặn Mua lổ lổ Mỏng rành 0000.. vướng víu) Bitmap thường chiếm
# N không gian Thô cho cả Khách Chưa Mua Lần Đéo Nào.
# Roaring Bitmaps Cắt thành Chunks Xong Lọc Container Run-Length Encoding Nén Lại Gọn Ơ.
# Đây là "Phép Thuật Hắc Ám" (Dark Magic) mà Apache Pinot, Apache Druid, ClickHouse
# Vận Hành Count Distinct Phạt Cổ Ngàn Tỷ Bản Ghi. Bạn Đọc Thuật Ngữ Này Với Interviewer:
# Đỗ Chắc Bần Kèo Nặng.
```

---

### Task 12: Union-Find (Disjoint Set) - Hợp nhất định danh Khách Hàng

**Problem:**
(Entity Resolution / ID Graph Stitching - Bài Toán Giải Pháp Đắt Giá Trăm Tỉ Của Các DHP Lớn Trên Thế Giới Về Quảng Cáo Đánh Đảo).
Bạn Có 3 Loại ID Hành Vi: 
- Event 1: `(Device_ID_Apple, Cookie_ID_Shopee)` Mua Thắt Lưng.
- Event 2: `(Cookie_ID_Shopee, User_Email_Qv@gmail.com)` Kích Rác Thẻ.
- Event 3: `(User_Email_Qv@gmail.com, SDT_Viettel_098)` Đóng Phạt Tiền Nạp.

Làm thết nào Để Cục Data Platform của bạn Lôi gộp cả Đống Rác Thống Nhất Chỉ Cố Về 1 Người Thật Thể Duy Nhất (Single Source of Customer Entity). Gom Dồn 3 Chuỗi Dài Gì Để Biết Thằng Mua Thắt Lưng Và Thằng Đóng Phạt Là Cùng 1 Ông Nội?

**Analytical Thinking (Cấu Tứ Đồ Thị Ngầm Tập Hợp Disjoint-Set):**
Disjoint-Set (Union-Find) là Vị Vua Của Đồ Thị Hướng Cụm. O(Alpha) Xích mịch - Gần Như O(1).
"Hễ có cạnh Nối Ràng, Mảng Băm trỏ Parent Mẹ Về Tột Chỏm Trâm Cùng".
Ta Hợp (Union) Event 1 -> Device Mẹ Trỏ Về Cookie. Cứ Thế Trỏ Dây Về Tròn Vết.
Tối Chốt Cuối Ngày Cuốc Truy lùng (Find) -> Cả 4 Loại ID Này Phọt Về Duy Nhất 1 ID Gốc Mẹ.

**Solution:**
```python
class CustomerEntityStitcher:
    """
    Union-Find (Mã Nhập Thể) Giải thuật. Bào Nhanh Cứu Xét Hàng Triệu Phả Hệ Trống Rong.
    Time Complexity: Khấu Hao Rơi Bậc O(alpha N) ~ Hão Huyền O(1). Mọi Công Thức Tra O(1).
    Space Complexity: O(N) Quản Chế Các Nốt Khách Hàng.
    """
    def __init__(self):
        self.root_parent_map = {}
        self.rank_tree_depth = {}
        
    def find_true_origin_id(self, item_id: str) -> str:
        """ Find with Path Compression - Đè Bẹp Tiết Trống Về Thẳng Cốt Lõi Phả Trú Cụ Kị """
        if item_id not in self.root_parent_map:
            # Khởi Căn Cốt (Mỗi Người Là 1 Hòn Đảo Cô Cùng)
            self.root_parent_map[item_id] = item_id
            self.rank_tree_depth[item_id] = 0
            return item_id
            
        if self.root_parent_map[item_id] != item_id:
            # Lệnh Gán Mẹ Trực Tiếp Về Gốc (Compress Bẹp Đồ Thị)
            self.root_parent_map[item_id] = self.find_true_origin_id(self.root_parent_map[item_id])
            
        return self.root_parent_map[item_id]
        
    def link_events_union(self, id_1: str, id_2: str):
        """ Nối Biển Kết Bè 2 Hòn Đảo ID Chập Vào Nhau Xương Xẩu Bề Thế """
        root_1 = self.find_true_origin_id(id_1)
        root_2 = self.find_true_origin_id(id_2)
        
        if root_1 != root_2:
            # Thuật Vị Thế Vương Đạo Bậc Bậc (Union by Rank)
            # Dòng Đảo Ít Quái hơn Tự Giác Nhập Vọng Tổ Đảo Trụ Nhiều Người Cõi
            if self.rank_tree_depth[root_1] > self.rank_tree_depth[root_2]:
                self.root_parent_map[root_2] = root_1
            elif self.rank_tree_depth[root_1] < self.rank_tree_depth[root_2]:
                self.root_parent_map[root_1] = root_2
            else:
                self.root_parent_map[root_2] = root_1
                self.rank_tree_depth[root_1] += 1
                
# Kịch bản Dùng Thử
# identity_engine = CustomerEntityStitcher()
# identity_engine.link_events_union("Macbook_MAC", "Cookie_A")
# identity_engine.link_events_union("Cookie_A", "User_123")
# Lúc Data Analyst Truy Tỉnh Find_True_Origin: Mọi ID Gõ Vô Đều Nhảy Ra Độc Duy Tròn Vạnh Rễ User_123. Dễ dàng Count Metric True User Không Đúp.
```

---

## 🔗 Liên Kết Cuối

- [Apache Spark Khủng Đạo Nâng Cao](06_Spark_and_Concurrency.md)
- [Quay lại Trang Chủ Interview Bản Đồ Lục Địa](../README.md)

---

*Biển Vàng DSA Biên Soạn Ký Chú Bới Tech Lead Tier-X. Bản Giao Cứu Giúp Độ Ngược Đảo Nấc Thang DE.*
