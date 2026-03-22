# Stream Processing Foundational Papers

## Những Paper Nền Tảng Cho Xử Lý Luồng Dữ Liệu Real-time

---

## 📋 Mục Lục

1. [Kafka](#1-kafka---2011)
2. [Dataflow Model](#2-dataflow-model---2015)
3. [Flink Snapshots](#3-flink-lightweight-asynchronous-snapshots---2015)
4. [MillWheel](#4-millwheel---2013)
5. [Storm](#5-storm---2014)
6. [Spark Streaming](#6-spark-streaming---2013)
7. [Samza](#7-samza---2017)
8. [Kafka Streams](#8-kafka-streams---2016)
9. [One SQL to Rule Them All](#9-one-sql-to-rule-them-all---2019)
10. [Tổng Kết](#10-tổng-kết--evolution)

---

## 1. KAFKA - 2011

### Paper Info
- **Title:** Kafka: a Distributed Messaging System for Log Processing
- **Authors:** Jay Kreps, Neha Narkhede, Jun Rao
- **Conference:** NetDB Workshop 2011
- **Link:** https://www.microsoft.com/en-us/research/wp-content/uploads/2017/09/Kafka.pdf
- **PDF:** http://notes.stephenholiday.com/Kafka.pdf

### Key Contributions
- Distributed commit log
- High-throughput message system
- Consumer groups for scaling
- Log compaction

### Architecture

```mermaid
graph TB
    subgraph Producers[" "]
        Producers_title["📤 Producers"]
        style Producers_title fill:none,stroke:none,color:#333,font-weight:bold
        P1[Producer 1]
        P2[Producer 2]
    end

    subgraph Cluster[" "]
        Cluster_title["Kafka Cluster"]
        style Cluster_title fill:none,stroke:none,color:#333,font-weight:bold
        subgraph B1[" "]
            B1_title["Broker 1"]
            style B1_title fill:none,stroke:none,color:#333,font-weight:bold
            T1P0["Topic A<br/>Partition 0<br/>(Leader)"]
            T1P1["Topic A<br/>Partition 1<br/>(Follower)"]
        end
        subgraph B2[" "]
            B2_title["Broker 2"]
            style B2_title fill:none,stroke:none,color:#333,font-weight:bold
            T2P0["Topic A<br/>Partition 0<br/>(Follower)"]
            T2P1["Topic A<br/>Partition 1<br/>(Leader)"]
        end
        subgraph B3[" "]
            B3_title["Broker 3"]
            style B3_title fill:none,stroke:none,color:#333,font-weight:bold
            T3P0["Topic A<br/>Partition 0<br/>(Follower)"]
            T3P2["Topic A<br/>Partition 2<br/>(Leader)"]
        end
    end

    subgraph ConsumerGroup[" "]
        ConsumerGroup_title["📥 Consumer Group"]
        style ConsumerGroup_title fill:none,stroke:none,color:#333,font-weight:bold
        C1["Consumer 1<br/>← Partition 0"]
        C2["Consumer 2<br/>← Partition 1"]
        C3["Consumer 3<br/>← Partition 2"]
    end

    P1 --> T1P0
    P2 --> T2P1
    T1P0 --> C1
    T2P1 --> C2
    T3P2 --> C3
```

### Log Structure & Offset

```mermaid
graph LR
    subgraph Partition[" "]
        Partition_title["Partition 0 (Append-only Log)"]
        style Partition_title fill:none,stroke:none,color:#333,font-weight:bold
        direction LR
        O0["Offset 0<br/>msg A"]
        O1["Offset 1<br/>msg B"]
        O2["Offset 2<br/>msg C"]
        O3["Offset 3<br/>msg D"]
        O4["Offset 4<br/>msg E"]
        O5["Offset 5<br/>msg F"]
        O6["... →<br/>New writes"]
    end

    subgraph Consumers[" "]
        Consumers_title["Consumer Positions"]
        style Consumers_title fill:none,stroke:none,color:#333,font-weight:bold
        CG1["Consumer Group 1<br/>offset = 2 (reading C)"]
        CG2["Consumer Group 2<br/>offset = 5 (reading F)"]
    end
```

### Key Design Decisions

| Decision | Rationale |
|----------|-----------|
| **Sequential disk I/O** | Faster than random RAM access (page cache) |
| **sendfile() zero-copy** | Kernel sends directly from page cache → NIC |
| **Batching** | Amortize network overhead |
| **Pull-based consumers** | Consumer controls pace (backpressure) |
| **Simple broker** | No per-message state; offset managed by consumer |
| **Partition = parallelism** | More partitions = more consumer parallelism |

### Delivery Guarantees

```mermaid
graph TD
    subgraph Guarantees[" "]
        Guarantees_title["Delivery Semantics"]
        style Guarantees_title fill:none,stroke:none,color:#333,font-weight:bold
        AtMost["At-most-once<br/>Read → Process → Commit offset<br/>If crash after process: message lost"]
        AtLeast["At-least-once<br/>Read → Process → Commit offset<br/>If crash before commit: reprocess"]
        Exactly["Exactly-once (Kafka 0.11+)<br/>Idempotent producer +<br/>Transactional consumer<br/>→ No duplicates"]
    end
```

### Impact on Modern Tools
- **Apache Kafka** — De facto standard for event streaming
- **Apache Pulsar** — Next-gen with tiered storage
- **Amazon Kinesis** — AWS managed streaming
- **Azure Event Hubs** — Azure's Kafka-compatible service
- **Redpanda** — Kafka-compatible, C++ implementation
- **Confluent** — Commercial Kafka platform

### Limitations & Evolution (Sự thật phũ phàng)
- Kafka **không phải stream processor hoàn chỉnh**: cần thêm engine để xử lý stateful/window phức tạp.
- Rebalance + partition skew có thể làm p99 latency tăng mạnh.
- **Evolution:** Kafka Streams, Flink, Pulsar Functions và ksqlDB để lấp khoảng trống processing layer.

### War Stories & Troubleshooting
- Lỗi phổ biến: **consumer lag tăng không hồi**, thường do downstream chậm hoặc key skew.
- Fix nhanh: scale consumer group theo partition, tăng `fetch.min.bytes`/batch hợp lý, tách hot key bằng re-key/bucketing.

### Metrics & Order of Magnitude
- End-to-end pipeline Kafka thường mục tiêu p99 ở mức **10ms đến vài trăm ms** tùy processing phía sau.
- Compression (`lz4`/`zstd`) thường giảm network + storage đáng kể (thường 2-5x với log text).
- Partition count là đòn bẩy throughput chính nhưng tăng quá mức sẽ tăng metadata/control overhead.

### Micro-Lab
```bash
# 1) Tạo topic lab
kafka-topics.sh --bootstrap-server localhost:9092 --create --topic lag-lab --partitions 3 --replication-factor 1
# 2) Theo dõi lag theo consumer group
kafka-consumer-groups.sh --bootstrap-server localhost:9092 --group demo-g --describe
# 3) Produce burst nhỏ rồi quan sát lag tăng/giảm
kafka-console-producer.sh --bootstrap-server localhost:9092 --topic lag-lab
```
---

> 💡 **Gemini Feedback**
> **Góc nhìn Thực chiến (Senior to Junior)**
1. **Limitations & Evolution (Sự thật phũ phàng):** Bản chất Kafka chỉ là một cái "ống nước" (Dumb broker, Smart consumer) chuyên ghi tuần tự ra đĩa, chứ không có năng lực tính toán (Map/Reduce). Sai lầm lớn nhất của Junior là coi Kafka như một Database để query data cũ. Sự tiến hóa sau này là KSQL và Kafka Streams ra đời để đắp thêm não (Compute) cho cái ống nước vô tri này.
    
2. **War Stories & Troubleshooting:** Ác mộng kinh hoàng nhất với Kafka là **"Consumer Rebalance Storm"**. Khi một node app của em bị đơ (CPU spike) và không gửi `heartbeat` về cho Kafka kịp, Kafka tưởng node đó chết nên thu hồi Partition và chia lại cho các node khác. Cả quá trình này (Rebalance) làm toàn bộ consumer group bị "đứng hình" không xử lý được message nào, gây lag nghẽn hệ thống hàng chục phút. Cách fix: Tách riêng thread xử lý logic và thread gửi heartbeat, tăng `session.timeout.ms`.
    
3. **Metrics & Order of Magnitude:** Đừng sợ Kafka ghi ra ổ cứng. Do nó dùng cơ chế OS PageCache và Sequential I/O, tốc độ ghi disk của Kafka có thể đạt hàng trăm MB/s, tức là xử lý hàng triệu message mỗi giây trên một node bình thường.
    
4. **Micro-Lab:** Chạy Kafka local và tự tay trải nghiệm việc gửi/nhận message qua terminal để hiểu khái niệm topic: `docker run -p 9092:9092 apache/kafka:3.7.0` (Sau đó dùng `kafka-console-producer.sh` và `kafka-console-consumer.sh`)
---

## 2. DATAFLOW MODEL - 2015

### Paper Info
- **Title:** The Dataflow Model: A Practical Approach to Balancing Correctness, Latency, and Cost in Massive-Scale, Unbounded, Out-of-Order Data Processing
- **Authors:** Tyler Akidau, Robert Bradshaw, et al.
- **Conference:** VLDB 2015
- **Link:** https://research.google/pubs/pub43864/
- **PDF:** https://static.googleusercontent.com/media/research.google.com/en//pubs/archive/43864.pdf

### Key Contributions
- Unified batch and streaming model
- Event time vs processing time
- Windowing semantics (fixed, sliding, session)
- Triggers and watermarks
- Accumulation modes

### The Four Questions

```mermaid
graph TB
    subgraph Questions[" "]
        Questions_title["The 4 Questions of Dataflow"]
        style Questions_title fill:none,stroke:none,color:#333,font-weight:bold
        Q1["1. WHAT results?<br/>Transformations<br/>(ParDo, GroupByKey,<br/>Combine, Flatten)"]
        Q2["2. WHERE in event time?<br/>Windowing<br/>(Fixed, Sliding, Session,<br/>Global)"]
        Q3["3. WHEN to emit?<br/>Triggers + Watermarks<br/>(early, on-time, late<br/>firings)"]
        Q4["4. HOW do refinements relate?<br/>Accumulation<br/>(Discarding, Accumulating,<br/>Retracting)"]
    end
    
    Q1 --> Q2 --> Q3 --> Q4
```

### Windowing Types

```mermaid
graph TB
    subgraph Fixed[" "]
        Fixed_title["Fixed (Tumbling) Windows"]
        style Fixed_title fill:none,stroke:none,color:#333,font-weight:bold
        F1["Window 1<br/>00:00-01:00"]
        F2["Window 2<br/>01:00-02:00"]
        F3["Window 3<br/>02:00-03:00"]
    end

    subgraph Sliding[" "]
        Sliding_title["Sliding (Hopping) Windows<br/>size=60min, slide=30min"]
        style Sliding_title fill:none,stroke:none,color:#333,font-weight:bold
        S1["Window A<br/>00:00-01:00"]
        S2["Window B<br/>00:30-01:30"]
        S3["Window C<br/>01:00-02:00"]
    end

    subgraph Session[" "]
        Session_title["Session Windows<br/>gap=30min"]
        style Session_title fill:none,stroke:none,color:#333,font-weight:bold
        SE1["User X<br/>|--events--|  gap  |--events--|"]
        SE2["User Y<br/>|--events--|"]
    end
```

### Watermarks & Late Data

```mermaid
graph LR
    subgraph Watermark[" "]
        Watermark_title["Watermark Concept"]
        style Watermark_title fill:none,stroke:none,color:#333,font-weight:bold
        direction TB
        Ideal["Ideal: Event time = Processing time<br/>(no late data)"]
        Real["Reality: Events arrive out of order<br/>Watermark = heuristic estimate of<br/>'all events before time T have arrived'"]
        Late["Late events: arrive after watermark<br/>→ Side output or update result"]
    end
```

### Triggers & Accumulation

```mermaid
sequenceDiagram
    participant W as Window [12:00-13:00]
    participant R as Result

    Note over W: Trigger: Early every 1 min
    W->>R: Early result: count=5 (12:01)
    W->>R: Early result: count=12 (12:02)
    
    Note over W: Watermark passes 13:00
    W->>R: On-time result: count=45 (13:01)
    
    Note over W: Late event arrives
    W->>R: Late result: count=46 (13:15)
    
    Note over R: Accumulation modes:
    Note over R: Discarding: 5, 7, 33, 1
    Note over R: Accumulating: 5, 12, 45, 46
    Note over R: Retracting: 5, -5+12, -12+45, -45+46
```

### Beam Code Example

```python
import apache_beam as beam
from apache_beam.transforms.window import FixedWindows
from apache_beam.transforms.trigger import AfterWatermark, AfterCount, AccumulationMode

(
    pipeline
    | "Read" >> beam.io.ReadFromPubSub(topic="events")
    | "Parse" >> beam.Map(parse_event)
    | "Window" >> beam.WindowInto(
        FixedWindows(60),  # 60-second windows
        trigger=AfterWatermark(
            early=AfterCount(10),      # Emit after 10 elements
            late=AfterCount(1)         # Emit per late element
        ),
        accumulation_mode=AccumulationMode.ACCUMULATING,
        allowed_lateness=3600  # Accept 1 hour late
    )
    | "Count" >> beam.CombinePerKey(sum)
    | "Write" >> beam.io.WriteToBigQuery("output_table")
)
```

### Impact on Modern Tools
- **Apache Beam** — Direct implementation of Dataflow model
- **Google Cloud Dataflow** — Managed Beam service
- **Apache Flink** — Adopted many concepts
- **Apache Spark Structured Streaming** — Influenced by Dataflow
- **Kafka Streams** — Window semantics from Dataflow

### Limitations & Evolution (Sự thật phũ phàng)
- Event-time correctness rất mạnh nhưng **mental model khó** cho team mới (trigger + lateness + accumulation).
- Cấu hình sai watermark/allowed lateness dễ tạo kết quả "đúng lý thuyết nhưng sai nghiệp vụ".
- **Evolution:** runner/tooling hiện đại thêm observability cho watermark, late data và state growth.

### War Stories & Troubleshooting
- Lỗi phổ biến: **late data bị drop** vì watermark quá aggressive.
- Fix nhanh: tăng `allowed_lateness`, phát side output cho late events, audit clock skew ở nguồn event.

### Metrics & Order of Magnitude
- Watermark lag thực tế thường từ **vài giây đến vài phút** tùy nguồn dữ liệu.
- Trigger early giúp latency xuống sub-minute nhưng tăng số lần emit/state update.
- Chi phí compute tăng theo số lần firing và độ trễ chấp nhận cho late data.

### Micro-Lab
```sql
-- Kiểm tra tỷ lệ late events theo phút
SELECT
    window_start,
    COUNTIF(is_late) / COUNT(*) AS late_ratio,
    COUNT(*) AS total_events
FROM stream_metrics
GROUP BY window_start
ORDER BY window_start DESC;
```

---

## 3. FLINK (LIGHTWEIGHT ASYNCHRONOUS SNAPSHOTS) - 2015

### Paper Info
- **Title:** Lightweight Asynchronous Snapshots for Distributed Dataflows
- **Authors:** Paris Carbone, Gyula Fóra, Stephan Ewen, et al.
- **Conference:** arXiv 2015
- **Link:** https://arxiv.org/abs/1506.08603
- **PDF:** https://arxiv.org/pdf/1506.08603.pdf

### Key Contributions
- Asynchronous barrier snapshotting (ABS)
- Exactly-once semantics via checkpointing
- Low-overhead distributed snapshots
- Based on Chandy-Lamport algorithm

### Chandy-Lamport vs Flink ABS

```mermaid
graph TB
    subgraph ChandyLamport[" "]
        ChandyLamport_title["Chandy-Lamport (1985)"]
        style ChandyLamport_title fill:none,stroke:none,color:#333,font-weight:bold
        CL1["1. Initiator records state"]
        CL2["2. Send marker on all outputs"]
        CL3["3. On first marker: record state,<br/>start recording channel"]
        CL4["4. On second marker: save<br/>recorded messages as<br/>channel state"]
        CL1 --> CL2 --> CL3 --> CL4
    end

    subgraph FlinkABS[" "]
        FlinkABS_title["Flink ABS (2015)"]
        style FlinkABS_title fill:none,stroke:none,color:#333,font-weight:bold
        F1["1. JobManager injects barriers"]
        F2["2. Barriers flow with data"]
        F3["3. On barrier: checkpoint state<br/>(async, non-blocking)"]
        F4["4. Barrier alignment:<br/>buffer fast inputs"]
        F5["5. No channel state needed<br/>(blocked by alignment)"]
        F1 --> F2 --> F3 --> F4 --> F5
    end
```

### Barrier Alignment

```mermaid
sequenceDiagram
    participant S1 as Source 1
    participant S2 as Source 2
    participant Op as Operator
    participant SM as State Manager

    S1->>Op: data, data, data
    S1->>Op: ── barrier n ──
    Note over Op: Barrier from S1 received
    Note over Op: Buffer S1 data, wait for S2
    
    S2->>Op: data, data
    S2->>Op: ── barrier n ──
    Note over Op: Both barriers received!
    
    Op->>SM: Async snapshot of state
    Note over Op: Continue processing
    Note over Op: (release buffered data)
    
    Op->>Op: Forward barrier n downstream
```

### Unaligned Checkpoints (Flink 1.11+)

```mermaid
graph LR
    subgraph Aligned[" "]
        Aligned_title["Aligned Checkpoints"]
        style Aligned_title fill:none,stroke:none,color:#333,font-weight:bold
        A1["Buffer data from<br/>fast input channels"]
        A2["Wait for slow barriers"]
        A3["Higher latency during<br/>checkpoint"]
        A1 --> A2 --> A3
    end

    subgraph Unaligned[" "]
        Unaligned_title["Unaligned Checkpoints"]
        style Unaligned_title fill:none,stroke:none,color:#333,font-weight:bold
        U1["Don't wait for alignment"]
        U2["Include in-flight data<br/>in checkpoint"]
        U3["Lower latency, but<br/>larger checkpoint size"]
        U1 --> U2 --> U3
    end
```

### Recovery Process

```mermaid
graph TD
    Failure["❌ Operator Failure"] --> Detect["JobManager detects failure"]
    Detect --> Restart["Restart all operators"]
    Restart --> Restore["Restore from latest<br/>successful checkpoint"]
    Restore --> Replay["Sources replay from<br/>checkpoint offset"]
    Replay --> Resume["Processing resumes<br/>Exactly-once guaranteed"]
```

### Impact on Modern Tools
- **Apache Flink** — Core checkpointing mechanism
- **Spark Structured Streaming** — Influenced checkpoint design
- **Standard** — For exactly-once stream processing
- **Flink CDC** — Change data capture using same engine

### Limitations & Evolution (Sự thật phũ phàng)
- Aligned checkpoint có thể gây **checkpoint stalls** khi backpressure nặng.
- State lớn làm checkpoint duration phình to và recovery chậm.
- **Evolution:** unaligned checkpoint, incremental checkpoint, disaggregated state backends.

### War Stories & Troubleshooting
- Lỗi phổ biến: **checkpoint timeout** và job restart loop.
- Fix nhanh: tăng timeout + min pause, giảm state TTL/size, chuyển RocksDB incremental + tune I/O storage.

### Metrics & Order of Magnitude
- Checkpoint interval thường ở **10s-5m** tùy SLA và cost.
- State backend lớn có thể đẩy recovery từ giây lên phút nếu thiếu incremental snapshot.
- Backpressure kéo dài làm alignment time tăng theo bậc.

### Micro-Lab
```bash
# Kiểm tra checkpoint metrics (Flink REST)
curl -s http://localhost:8081/jobs/<job_id>/checkpoints | jq '.latest'
# Xem thêm trạng thái backpressure để correlate với checkpoint timeout
curl -s http://localhost:8081/jobs/<job_id>/vertices/<vertex_id>/backpressure | jq
```
---
> 💡 **Gemini Feedback**
> **Góc nhìn Thực chiến (Senior to Junior)**
1. **Limitations & Evolution (Sự thật phũ phàng):** Thuật toán Chandy-Lamport giúp Flink có Exactly-Once. Nhưng điểm yếu chí mạng là **State Bloat (Phình to trạng thái)**. Nếu em dùng Flink để JOIN 2 luồng data khổng lồ mà quên không cấu hình TTL (Time To Live), Flink sẽ lưu toàn bộ lịch sử data vào RocksDB (ổ cứng) mãi mãi cho đến khi sập ổ đĩa.
    
2. **War Stories & Troubleshooting:** **"Checkpoint Timeout"** là lỗi Junior hay khóc thét nhất. Khi Job Flink có một Task bị Data Skew (nghiêng data), Task đó sẽ bận đến mức không kịp nhận cái thẻ "Barrier" của thuật toán Chandy-Lamport để chụp hình (snapshot). Kết quả là Checkpoint bị quá giờ (timeout) liên tục, hệ thống mất khả năng chịu lỗi. Khi Flink chết, nó phải đọc lại data từ rất xa trong quá khứ, tạo ra một vòng lặp chết chóc (Restart Loop).
    
3. **Metrics & Order of Magnitude:** Một Checkpoint của Flink có thể nặng từ vài chục MB đến hàng Terabyte. Nếu Checkpoint size > 1GB, bắt buộc phải xài Incremental Checkpoint (chỉ lưu phần thay đổi) với RocksDB StateBackend.

---
## 4. MILLWHEEL - 2013

### Paper Info
- **Title:** MillWheel: Fault-Tolerant Stream Processing at Internet Scale
- **Authors:** Tyler Akidau, Alex Balikov, et al.
- **Conference:** VLDB 2013
- **Link:** https://research.google/pubs/pub41378/
- **PDF:** https://static.googleusercontent.com/media/research.google.com/en//pubs/archive/41378.pdf

### Key Contributions
- Exactly-once delivery in streaming
- Low watermarks for completeness tracking
- Persistent per-key state
- Timer-based processing

### Architecture

```mermaid
graph TB
    subgraph MillWheel[" "]
        MillWheel_title["MillWheel System"]
        style MillWheel_title fill:none,stroke:none,color:#333,font-weight:bold
        subgraph Computation[" "]
            Computation_title["Computation DAG"]
            style Computation_title fill:none,stroke:none,color:#333,font-weight:bold
            C1["Computation A<br/>(parse events)"]
            C2["Computation B<br/>(window counts)"]
            C3["Computation C<br/>(anomaly detect)"]
            C1 --> C2
            C2 --> C3
        end

        subgraph Runtime[" "]
            Runtime_title["Per-Computation Runtime"]
            style Runtime_title fill:none,stroke:none,color:#333,font-weight:bold
            Dedup["Dedup Module<br/>(filter duplicates)"]
            State["State Storage<br/>(Spanner/Bigtable)"]
            Timer["Timer Manager<br/>(delayed processing)"]
            WM["Watermark Tracker<br/>(oldest unprocessed)"]
        end
    end
```

### Exactly-Once Delivery

```mermaid
sequenceDiagram
    participant U as Upstream
    participant C as Computation
    participant S as State (Spanner)
    participant D as Downstream

    U->>C: Record (with unique ID)
    C->>S: Check: seen this ID before?
    
    alt Already processed
        S->>C: Yes → skip (deduplicate)
    else New record
        S->>C: No → process
        Note over C,S: Single atomic operation:
        C->>S: 1. Save new state
        C->>S: 2. Save dedup ID
        C->>S: 3. Save pending outputs
        C->>D: 4. Send output downstream
        C->>U: 5. ACK upstream
    end
```

### Low Watermarks

```mermaid
graph TB
    subgraph WatermarkPropagation[" "]
        WatermarkPropagation_title["Watermark Propagation"]
        style WatermarkPropagation_title fill:none,stroke:none,color:#333,font-weight:bold
        Source["Source<br/>WM = min(unprocessed<br/>input timestamps)"]
        CompA["Computation A<br/>WM = min(A's oldest<br/>unprocessed, Source WM)"]
        CompB["Computation B<br/>WM = min(B's oldest<br/>unprocessed, CompA WM)"]
        
        Source --> CompA --> CompB
    end
    
    subgraph Usage[" "]
        Usage_title["Watermark Usage"]
        style Usage_title fill:none,stroke:none,color:#333,font-weight:bold
        Trigger["Window completion:<br/>'All data before time T<br/>has been processed'"]
        GC["State garbage collection:<br/>'Safe to delete state<br/>for times < WM'"]
    end
```

### Use Cases at Google
- **Zeitgeist** — Trending queries detection
- **Billing** — Ad serving revenue computation
- **Abuse detection** — Real-time spam/fraud detection
- **Recommendations** — Real-time personalization

### Impact on Modern Tools
- **Google Cloud Dataflow** — Successor to MillWheel
- **Apache Flink** — Many similar concepts (watermarks, timers)
- **Watermark concept** — Now standard in all streaming systems

### Limitations & Evolution (Sự thật phũ phàng)
- Kiến trúc phụ thuộc strongly-consistent state store nên **ops complexity cao**.
- Exactly-once mạnh nhưng đổi lại latency/cost cho transactional state.
- **Evolution:** managed streaming services tối giản vận hành state + checkpoint.

### War Stories & Troubleshooting
- Lỗi phổ biến: **timer explosion** (quá nhiều timer per key) gây OOM.
- Fix nhanh: coarsen timer granularity, TTL state, gộp key và giới hạn cardinality upstream.

### Metrics & Order of Magnitude
- Cardinality key tăng 10x thường kéo state size gần tuyến tính nếu không TTL.
- Exactly-once pipeline thường có overhead đáng kể so với at-least-once.
- Watermark health là leading indicator cho freshness SLA.

### Micro-Lab
```python
# Ước lượng state footprint thô
num_keys, bytes_per_key = 5_000_000, 200
print(f"state ~ {num_keys*bytes_per_key/1024/1024:.1f} MB")
# Thử thêm replication/checkpoint overhead đơn giản
overhead_factor = 1.5
print(f"effective_storage ~ {num_keys*bytes_per_key*overhead_factor/1024/1024:.1f} MB")
```
---

> 💡 **Gemini Feedback**
> **Góc nhìn Thực chiến (Senior to Junior)**
> *Lưu ý : Hai paper này là linh hồn của Apache Beam và Google Cloud Dataflow, em có thể gộp chung góc nhìn*

1. **Limitations & Evolution (Sự thật phũ phàng):** Dataflow Model đẻ ra khái niệm **Watermark** để xử lý Late Data (dữ liệu đến trễ). Nhưng trên thực tế, cấu hình Watermark cực kỳ trừu tượng và khó debug. Rất nhiều team từ bỏ Beam vì code pipeline quá cồng kềnh và khó viết unit test so với Spark.
    
2. **War Stories & Troubleshooting:** Lỗi **"Watermark Hold"**. Hệ thống của em đang chạy ngon 100.000 msg/s, tự nhiên output ngưng bặt, không ra một dòng data nào dù CPU vẫn chạy. Check log mới thấy có MỘT thiết bị IoT ở vùng sâu vùng xa bị mất mạng, giờ nó gửi bù data của 3 ngày trước. Cả hệ thống Windowing phải "nín thở" giữ state trên RAM để chờ thằng đó chốt sổ, dẫn đến tràn RAM (OOM). Cách fix: Cấu hình `allowedLateness` chuẩn và thiết lập Drop Late Data cứng rắn.
    
3. **Metrics & Order of Magnitude:** Trễ (Latency) trong Dataflow phụ thuộc vào Window size. Nếu em mở Fixed Window 5 phút, data sẽ bị om đúng 5 phút mới nhả ra, trừ khi em xài cơ chế Early Triggers (nhả data mồi liên tục).

---

## 5. STORM - 2014

### Paper Info
- **Title:** Storm @Twitter
- **Authors:** Ankit Toshniwal, Siddarth Taneja, et al.
- **Conference:** SIGMOD 2014
- **Link:** https://dl.acm.org/doi/10.1145/2588555.2595641
- **PDF:** https://cs.brown.edu/courses/cs227/archives/2015/papers/ss-twitter.pdf

### Key Contributions
- First widely-adopted open-source stream processor
- Topology abstraction (spouts/bolts)
- At-least-once processing guarantee
- Nimbus/Supervisor architecture

### Topology Model

```mermaid
graph LR
    subgraph Topology[" "]
        Topology_title["Storm Topology"]
        style Topology_title fill:none,stroke:none,color:#333,font-weight:bold
        Spout1["Spout<br/>(Kafka Reader)"]
        Spout2["Spout<br/>(Twitter API)"]
        
        Bolt1["Bolt: Parse<br/>(extract fields)"]
        Bolt2["Bolt: Filter<br/>(remove noise)"]
        Bolt3["Bolt: Count<br/>(word count)"]
        Bolt4["Bolt: Aggregate<br/>(top-N)"]
        Bolt5["Bolt: Store<br/>(write to DB)"]
        
        Spout1 -->|shuffle| Bolt1
        Spout2 -->|shuffle| Bolt1
        Bolt1 -->|"fields(word)"| Bolt3
        Bolt1 -->|shuffle| Bolt2
        Bolt2 -->|shuffle| Bolt4
        Bolt3 -->|"fields(word)"| Bolt4
        Bolt4 -->|global| Bolt5
    end
    style Spout1 fill:#fff9c4,stroke:#fbc02d
style Bolt1 fill:#e1f5fe,stroke:#0288d1
```

### Stream Groupings

| Grouping | Description | Use Case |
|----------|-------------|----------|
| **Shuffle** | Random distribution | Stateless processing |
| **Fields** | Hash by field value | Stateful (count per key) |
| **All** | Broadcast to all bolts | Config updates |
| **Global** | Single bolt receives all | Final aggregation |
| **Direct** | Sender chooses target | Custom routing |
| **Local/Shuffle** | Prefer same worker | Reduce network |

### Architecture

```mermaid
graph TB
    subgraph Master[" "]
        Master_title["Master Node"]
        style Master_title fill:none,stroke:none,color:#333,font-weight:bold
        Nimbus["Nimbus<br/>• Distribute topology<br/>• Monitor workers<br/>• Reassign on failure"]
    end

    subgraph ZK[" "]
        ZK_title["ZooKeeper"]
        style ZK_title fill:none,stroke:none,color:#333,font-weight:bold
        Coord["Coordination<br/>• Worker heartbeats<br/>• Topology state"]
    end

    subgraph Workers[" "]
        Workers_title["Worker Nodes"]
        style Workers_title fill:none,stroke:none,color:#333,font-weight:bold
        Sup1["Supervisor 1"]
        W1["Worker JVM<br/>Executors → Tasks"]
        Sup2["Supervisor 2"]
        W2["Worker JVM"]
    end

    Nimbus <--> ZK
    ZK <--> Sup1
    ZK <--> Sup2
    Sup1 --> W1
    Sup2 --> W2
```

### Impact on Modern Tools
- **Apache Storm** — Original implementation (now maintenance mode)
- **Twitter Heron** — Storm successor (better performance)
- Pioneered real-time processing for industry
- Largely replaced by Flink and Spark Structured Streaming

### Limitations & Evolution (Sự thật phũ phàng)
- At-least-once + ack tree khiến debug semantics phức tạp ở topology lớn.
- Ecosystem/state management kém linh hoạt hơn thế hệ mới.
- **Evolution:** Heron, Flink và Structured Streaming với model state/checkpoint tốt hơn.

### War Stories & Troubleshooting
- Lỗi phổ biến: **topology backpressure** nhưng không rõ bolt nào nghẽn.
- Fix nhanh: tăng parallelism đúng bolt, đổi grouping phù hợp key distribution, giảm per-tuple processing time.

### Metrics & Order of Magnitude
- Per-record latency thấp nhưng tail latency nhạy với skew và external sink.
- Ack timeout sai dễ gây replay storm.
- Throughput thường scale theo số executors cho tới khi chạm bottleneck network/sink.

### Micro-Lab
```bash
# Kiểm tra topology đang chạy
storm list
# Lấy thông tin chi tiết 1 topology để tìm bolt nghẽn
storm topology <topology-name>
```

---
> 💡 **Gemini Feedback**
> **Góc nhìn Thực chiến (Senior to Junior)**
1. **Limitations & Evolution (Sự thật phũ phàng):** Storm là ông tổ của Streaming nhưng hiện tại **ĐÃ CHẾT**. Nó xử lý từng event một (Tuple-at-a-time) nên latency cực thấp (dưới 10ms), nhưng throughput thê thảm và KHÔNG hỗ trợ Exactly-once state management natively (Trident quá phức tạp). Hiện nay, Flink đã hoàn toàn thay thế Storm.
    
2. **War Stories & Troubleshooting:** Ngày xưa dùng Storm, hễ Worker bị sập là y như rằng data bị tính đúp (duplicate) vào Database (At-least-once). Developer phải tự code phần logic chống trùng lặp (Idempotent) ở phía Database cực kỳ khổ sở. Thấy chữ Storm trong CV bây giờ thì chỉ mang tính chất hoài niệm lịch sử.
---

## 6. SPARK STREAMING - 2013

### Paper Info
- **Title:** Discretized Streams: Fault-Tolerant Streaming Computation at Scale
- **Authors:** Matei Zaharia, Tathagata Das, et al.
- **Conference:** SOSP 2013
- **Link:** https://www.usenix.org/conference/nsdi12/technical-sessions/presentation/zaharia
- **PDF:** https://people.csail.mit.edu/matei/papers/2013/sosp_spark_streaming.pdf

### Key Contributions
- Micro-batch streaming model (D-Streams)
- RDD lineage for fault tolerance
- Unified batch and streaming API
- Stateful operators with checkpointing

### Micro-Batch Model

```mermaid
graph LR
    subgraph Stream[" "]
        Stream_title["Continuous Event Stream"]
        style Stream_title fill:none,stroke:none,color:#333,font-weight:bold
        E["...events flowing continuously..."]
    end

    subgraph DStreams[" "]
        DStreams_title["Discretized Streams"]
        style DStreams_title fill:none,stroke:none,color:#333,font-weight:bold
        MB1["Micro-batch 1<br/>(RDD @ t=0)"]
        MB2["Micro-batch 2<br/>(RDD @ t=1)"]
        MB3["Micro-batch 3<br/>(RDD @ t=2)"]
        MB4["Micro-batch 4<br/>(RDD @ t=3)"]
    end

    Stream -->|"Discretize<br/>every Δt"| DStreams
```

### Fault Tolerance via Lineage

```mermaid
graph TB
    subgraph Lineage[" "]
        Lineage_title["RDD Lineage Graph"]
        style Lineage_title fill:none,stroke:none,color:#333,font-weight:bold
        Input1["Input RDD (t=0)<br/>from Kafka"]
        Input2["Input RDD (t=1)<br/>from Kafka"]
        
        Map1["Map RDD (t=0)"]
        Map2["Map RDD (t=1)"]
        
        State0["State RDD (t=0)"]
        State1["State RDD (t=1)<br/>updateStateByKey"]
        
        Input1 --> Map1
        Input2 --> Map2
        Map1 --> State0
        State0 --> State1
        Map2 --> State1
    end

    Failure["❌ Node failure<br/>State1 lost"]
    Recovery["Recompute from lineage:<br/>1. Replay Input2 from Kafka<br/>2. Re-derive Map2<br/>3. Read State0 (checkpoint)<br/>4. Recompute State1"]
    
    Failure --> Recovery
```

### Trade-offs: Micro-batch vs True Streaming

| Aspect | Micro-batch (Spark) | True Streaming (Flink) |
|--------|-------------------|---------------------|
| **Latency** | 100ms-seconds | Milliseconds |
| **Throughput** | Very high (batching) | High |
| **Fault tolerance** | Simple (RDD lineage) | Complex (checkpoints) |
| **API** | Same as batch Spark | Separate stream API |
| **Exactly-once** | Easy | Harder |
| **State management** | External | Built-in |

### Evolution: DStreams → Structured Streaming

```mermaid
graph LR
    DS["DStreams (2013)<br/>• RDD-based<br/>• Low-level API<br/>• Manual state"]
    SS["Structured Streaming (2016)<br/>• DataFrame-based<br/>• SQL support<br/>• Built-in state<br/>• Continuous mode"]
    
    DS -->|"Evolution"| SS
```

### Impact on Modern Tools
- **Spark Streaming (DStreams)** — Original micro-batch API (legacy)
- **Spark Structured Streaming** — SQL-based evolution (active)
- Micro-batch model: simple but higher latency trade-off

### Limitations & Evolution (Sự thật phũ phàng)
- Micro-batch tạo floor latency, khó đạt ultra-low-latency use case.
- State và trigger semantics thế hệ DStreams khó maintain.
- **Evolution:** Structured Streaming + AQE + better state store internals.

### War Stories & Troubleshooting
- Lỗi phổ biến: **batch backlog tăng dần** (processing time > batch interval).
- Fix nhanh: tăng batch interval, optimize stateful ops, autoscale executors và giảm wide shuffles.

### Metrics & Order of Magnitude
- Batch interval thường từ **100ms đến vài giây** tùy SLA.
- Khi input rate vượt process rate liên tục, latency tăng tuyến tính theo backlog depth.
- Checkpoint interval quá ngắn làm tăng I/O overhead đáng kể.

### Micro-Lab
```python
# Ước lượng backlog growth đơn giản
in_rate, proc_rate = 120000, 100000
print("lag/s:", in_rate - proc_rate)
# Ước lượng lag sau 10 phút nếu không scale
seconds = 600
print("lag_after_10m:", (in_rate - proc_rate) * seconds)
```

---

> 💡 **Gemini Feedback**
> **Góc nhìn Thực chiến (Senior to Junior)**
1. **Limitations & Evolution (Sự thật phũ phàng):** Spark Streaming (DStream) là **"Hàng giả mạo" (Micro-batch)**. Nó không thực sự xử lý real-time từng event, mà nó cắt data thành từng cục nhỏ (ví dụ 1 giây 1 cục) rồi xử lý như batch. Do đó, em vĩnh viễn không bao giờ đạt được độ trễ dưới 100ms với Spark. Sau này Databricks phải đẻ ra Structured Streaming và Continuous Processing để gỡ gạc nhưng vẫn không mượt bằng kiến trúc thuần stream của Flink.
    
2. **War Stories & Troubleshooting:** Lỗi kinh điển: `Processing Time > Batch Interval`. Nếu em cấu hình gom data mỗi 2 giây, nhưng logic tính toán của em tốn 3 giây để hoàn thành. Các cục batch phía sau sẽ bị xếp hàng chờ (Queuing), tích tụ dần dần cho đến khi vỡ nợ (OOM - Out of Memory) toàn bộ cụm Spark. Cách fix: Tối ưu lại logic hoặc tăng Batch Interval lên.
    
3. **Metrics & Order of Magnitude:** Latency an toàn của Spark Streaming thường ở mức 500ms - 2s. Tuyệt đối không dùng Spark Streaming cho các bài toán High-Frequency Trading (giao dịch chứng khoán tính bằng micro-second).

---
## 7. SAMZA - 2017

### Paper Info
- **Title:** Samza: Stateful Scalable Stream Processing at LinkedIn
- **Authors:** Shadi A. Noghabi, Kartik Paramasivam, et al.
- **Conference:** VLDB 2017
- **Link:** https://www.vldb.org/pvldb/vol10/p1634-noghabi.pdf
- **PDF:** https://www.vldb.org/pvldb/vol10/p1634-noghabi.pdf

### Key Contributions
- Kafka-native stream processing
- Local state with RocksDB
- Changelog-based fault tolerance
- Host affinity for state locality

### Architecture

```mermaid
graph LR
    subgraph Input[" "]
        Input_title["Input"]
        style Input_title fill:none,stroke:none,color:#333,font-weight:bold
        KI["Kafka Input Topic"]
    end

    subgraph SamzaJob[" "]
        SamzaJob_title["Samza Job (YARN Container)"]
        style SamzaJob_title fill:none,stroke:none,color:#333,font-weight:bold
        subgraph Task1[" "]
            Task1_title["Task 1 (Partition 0)"]
            style Task1_title fill:none,stroke:none,color:#333,font-weight:bold
            P1["Process<br/>Messages"]
            R1["RocksDB<br/>Local State"]
        end
        subgraph Task2[" "]
            Task2_title["Task 2 (Partition 1)"]
            style Task2_title fill:none,stroke:none,color:#333,font-weight:bold
            P2["Process"]
            R2["RocksDB"]
        end
    end

    subgraph Output[" "]
        Output_title["Output"]
        style Output_title fill:none,stroke:none,color:#333,font-weight:bold
        KO["Kafka Output Topic"]
        CL["Kafka Changelog Topic<br/>(state backup)"]
    end

    KI --> Task1
    KI --> Task2
    Task1 --> KO
    Task2 --> KO
    R1 -->|"async"| CL
    R2 -->|"async"| CL
```

### State Recovery

```mermaid
sequenceDiagram
    participant T as Task (Failed)
    participant CL as Changelog Topic
    participant NT as New Task Instance

    Note over T: Task crashes!
    Note over NT: New task started (preferably same host)
    
    alt Same Host (Host Affinity)
        NT->>NT: RocksDB still on disk
        NT->>CL: Replay only recent changelog
        Note over NT: Fast recovery (~seconds)
    else Different Host
        NT->>CL: Replay full changelog
        NT->>NT: Rebuild RocksDB from scratch
        Note over NT: Slower recovery (~minutes)
    end
    
    NT->>NT: Resume processing
```

### Impact on Modern Tools
- **Apache Samza** — LinkedIn's stream processor
- **Kafka Streams** — Adopted changelog pattern
- Influenced stateful streaming designs

### Limitations & Evolution (Sự thật phũ phàng)
- Gắn chặt Kafka/YARN ecosystem nên portability hạn chế.
- Host affinity tốt cho recovery nhưng gây khó autoscaling linh hoạt.
- **Evolution:** Kafka Streams/Flink với runtime linh hoạt hơn trên Kubernetes.

### War Stories & Troubleshooting
- Lỗi phổ biến: **recovery rất chậm** khi task chuyển host (replay full changelog).
- Fix nhanh: giữ host affinity, giảm changelog noise (compaction), snapshot state định kỳ.

### Metrics & Order of Magnitude
- Same-host recovery thường nhanh hơn khác host theo bậc nhiều lần.
- Changelog topic growth là chỉ số sớm cho chi phí recovery tương lai.
- RocksDB local state giúp read latency ổn định ở mức thấp.

### Micro-Lab
```bash
# Quan sát tốc độ tăng changelog topic
kafka-run-class.sh kafka.tools.GetOffsetShell --broker-list localhost:9092 --topic app-changelog
# Chạy lại sau 1-2 phút để so sánh delta offsets
kafka-run-class.sh kafka.tools.GetOffsetShell --broker-list localhost:9092 --topic app-changelog
```


---

## 8. KAFKA STREAMS - 2016

### Paper Info
- **Title:** Kafka Streams (Confluent Documentation & Design)
- **Authors:** Confluent Engineering
- **Source:** Confluent Blog & Documentation
- **Link:** https://www.confluent.io/blog/introducing-kafka-streams-stream-processing-made-simple/
- **Design Docs:** https://cwiki.apache.org/confluence/display/KAFKA/Kafka+Streams

### Key Contributions
- Library-based stream processing (no separate cluster)
- Kafka-native (input, output, state all in Kafka)
- Exactly-once with Kafka transactions
- KStream and KTable abstractions

### KStream vs KTable

```mermaid
graph TB
    subgraph KStream[" "]
        KStream_title["KStream (Event Stream)"]
        style KStream_title fill:none,stroke:none,color:#333,font-weight:bold
        direction LR
        KS1["(key=A, val=1)"]
        KS2["(key=B, val=2)"]
        KS3["(key=A, val=3)"]
        KS4["(key=A, val=5)"]
    end
    
    subgraph KTable[" "]
        KTable_title["KTable (Changelog → latest state)"]
        style KTable_title fill:none,stroke:none,color:#333,font-weight:bold
        KT["Key | Value<br/>----|------<br/>A   | 5  (latest)<br/>B   | 2"]
    end

    KStream -->|"Aggregate/<br/>reduce"| KTable
    KTable -->|"toStream()"| KStream
```

### Architecture: Library, Not Cluster

```mermaid
graph TB
    subgraph App1[" "]
        App1_title["Application Instance 1"]
        style App1_title fill:none,stroke:none,color:#333,font-weight:bold
        KS1["Kafka Streams Library<br/>Tasks: P0, P1"]
        RS1["RocksDB State Store"]
    end

    subgraph App2[" "]
        App2_title["Application Instance 2"]
        style App2_title fill:none,stroke:none,color:#333,font-weight:bold
        KS2["Kafka Streams Library<br/>Tasks: P2, P3"]
        RS2["RocksDB State Store"]
    end

    subgraph Kafka[" "]
        Kafka_title["Kafka Cluster"]
        style Kafka_title fill:none,stroke:none,color:#333,font-weight:bold
        Input["Input Topic<br/>(4 partitions)"]
        Output["Output Topic"]
        CL["Changelog Topic<br/>(state backup)"]
    end

    Input -->|"P0, P1"| KS1
    Input -->|"P2, P3"| KS2
    KS1 --> Output
    KS2 --> Output
    RS1 -->|"async"| CL
    RS2 -->|"async"| CL
```

### Exactly-Once Semantics

```mermaid
sequenceDiagram
    participant KS as Kafka Streams Task
    participant KB as Kafka Broker

    KS->>KB: init_transactions()
    
    loop For each batch
        KS->>KB: begin_transaction()
        KS->>KB: produce(output_records)
        KS->>KB: produce(changelog_records)
        KS->>KB: send_offsets_to_transaction(consumer_offsets)
        KS->>KB: commit_transaction()
        Note over KS,KB: All or nothing:<br/>output + state + offsets<br/>atomically committed
    end
```

### Processor Topology

```java
StreamsBuilder builder = new StreamsBuilder();

// KStream: event stream
KStream<String, String> source = builder.stream("input-topic");

// Processing pipeline
source
    .filter((key, value) -> value != null)
    .mapValues(value -> value.toUpperCase())
    .groupByKey()
    .windowedBy(TimeWindows.ofSizeWithNoGrace(Duration.ofMinutes(5)))
    .count()
    .toStream()
    .to("output-topic");
```

### Impact on Modern Tools
- **Kafka Streams** — Embedded stream processing in any JVM app
- **ksqlDB** — SQL layer on Kafka Streams
- Pattern: stream processing as library (no separate cluster)

### Limitations & Evolution (Sự thật phũ phàng)
- Library model đơn giản nhưng **ops phân tán** theo từng app instance.
- Rebalance và state restore có thể làm startup/redeploy chậm.
- **Evolution:** ksqlDB cho SQL-first ops, cooperative rebalancing giảm disruption.

### War Stories & Troubleshooting
- Lỗi phổ biến: **rebalance storm** khi deploy rolling sai cách.
- Fix nhanh: cooperative sticky assignor, graceful shutdown, warm-up state store trước cutover.

### Metrics & Order of Magnitude
- State restore time tỉ lệ mạnh với kích thước changelog.
- EOS transaction overhead thường đổi lấy correctness ở workload tài chính/ordering-critical.
- p99 processing latency phụ thuộc nhiều vào RocksDB compaction health.

### Micro-Lab
```java
// Bật exactly-once-v2
props.put(StreamsConfig.PROCESSING_GUARANTEE_CONFIG, StreamsConfig.EXACTLY_ONCE_V2);
props.put(StreamsConfig.NUM_STREAM_THREADS_CONFIG, "2");
props.put(StreamsConfig.COMMIT_INTERVAL_MS_CONFIG, "100");
// Chạy app và verify output topic không bị duplicate khi restart
```


---

> 💡 **Gemini Feedback**
> **Góc nhìn Thực chiến (Senior to Junior)**
1. **Limitations & Evolution (Sự thật phũ phàng):** Kafka Streams không phải là một Cluster to nạc như Spark/Flink, nó chỉ là một cái **Java Library (Thư viện)** nhúng thẳng vào file `.jar` chạy app của em. Rất dễ deploy, nhưng nhược điểm là nó "trói chặt" mạng sống vào Kafka. Em không thể dùng Kafka Streams để đọc data từ RabbitMQ hay ghi thẳng ra S3 một cách mượt mà được.
    
2. **War Stories & Troubleshooting:** Kafka Streams lưu trạng thái (State) ở ổ cứng local bằng RocksDB và backup lên Kafka qua một topic ẩn gọi là `changelog`. Khi app của em bị sập đĩa và khởi động lại ở một node mới, nó phải kéo toàn bộ data từ topic `changelog` về để khôi phục RocksDB. Quá trình này có thể tốn vài tiếng đồng hồ cho các state vài chục GB, làm gián đoạn dịch vụ cực lâu.

---

## 9. ONE SQL TO RULE THEM ALL - 2019

### Paper Info
- **Title:** One SQL to Rule Them All (Apache Calcite)
- **Authors:** Edmon Begoli, Jesús Camacho-Rodríguez, et al.
- **Conference:** SIGMOD 2019
- **Link:** https://dl.acm.org/doi/10.1145/3299869.3314040
- **PDF:** https://arxiv.org/pdf/1905.12133.pdf

### Key Contributions
- Streaming SQL extensions
- Time-varying relations
- Stream-table duality
- Unified query semantics for batch + streaming

### Time-Varying Relations

```mermaid
graph TB
    subgraph TVR[" "]
        TVR_title["Time-Varying Relation"]
        style TVR_title fill:none,stroke:none,color:#333,font-weight:bold
        T1["t=10: {(1,'a'), (2,'b')}"]
        T2["t=20: {(1,'a'), (2,'b'), (3,'c')} ← INSERT"]
        T3["t=30: {(1,'a'), (2,'x'), (3,'c')} ← UPDATE"]
        T4["t=40: {(1,'a'), (3,'c')} ← DELETE"]
        
        T1 --> T2 --> T3 --> T4
    end

    subgraph Duality[" "]
        Duality_title["Stream ↔ Table Duality"]
        style Duality_title fill:none,stroke:none,color:#333,font-weight:bold
        Stream["Stream<br/>(append-only changes)"]
        Table["Table<br/>(point-in-time snapshot)"]
        
        Stream -->|"Aggregate<br/>over time"| Table
        Table -->|"Emit<br/>changes"| Stream
    end
```

### Streaming SQL Syntax

```sql
-- Fixed (tumbling) window
SELECT
    user_id,
    TUMBLE_START(event_time, INTERVAL '1' HOUR) AS window_start,
    COUNT(*) AS click_count
FROM clicks
GROUP BY
    user_id,
    TUMBLE(event_time, INTERVAL '1' HOUR);

-- Sliding (hopping) window
SELECT
    user_id,
    HOP_START(event_time, INTERVAL '5' MINUTE, INTERVAL '1' HOUR) AS window_start,
    AVG(duration) AS avg_duration
FROM sessions
GROUP BY
    user_id,
    HOP(event_time, INTERVAL '5' MINUTE, INTERVAL '1' HOUR);

-- Session window
SELECT
    user_id,
    SESSION_START(event_time, INTERVAL '30' MINUTE) AS session_start,
    COUNT(*) AS event_count
FROM events
GROUP BY
    user_id,
    SESSION(event_time, INTERVAL '30' MINUTE);

-- Stream-table join
SELECT
    e.user_id,
    e.event_type,
    u.name,
    u.tier
FROM events e
JOIN users_table FOR SYSTEM_TIME AS OF e.event_time u
    ON e.user_id = u.user_id;
```

### Impact on Modern Tools
- **Apache Calcite** — Query planning framework (used by many)
- **Apache Flink SQL** — Streaming SQL implementation
- **ksqlDB** — Kafka-native streaming SQL
- **Spark Structured Streaming SQL** — Spark's implementation
- Standard for streaming SQL syntax

### Limitations & Evolution (Sự thật phũ phàng)
- Unified SQL semantics mạnh nhưng **khác biệt engine runtime** vẫn tồn tại.
- SQL che bớt complexity nhưng không xóa vấn đề state/watermark/backpressure.
- **Evolution:** chuẩn hóa planner (Calcite) + engine-specific optimizer/adaptive runtime.

### War Stories & Troubleshooting
- Lỗi phổ biến: cùng SQL nhưng output lệch giữa engines do timezone/watermark defaults.
- Fix nhanh: chuẩn hóa session configs (timezone, lateness, null semantics), thêm regression test cross-engine.

### Metrics & Order of Magnitude
- SQL abstraction tăng velocity đội Data/Analytics nhưng cần guardrail cho cost/perf.
- Windowed join thường là điểm nóng CPU/state; cardinality tăng làm cost tăng phi tuyến.
- Planner quality quyết định lớn tới bytes shuffled và latency.

### Micro-Lab
```sql
-- Sanity check semantic: event-time watermark và window count
SELECT
    TUMBLE_START(ts, INTERVAL '1' MINUTE) AS w,
    COUNT(*) AS c
FROM s
GROUP BY TUMBLE(ts, INTERVAL '1' MINUTE)
ORDER BY w;
```


---
> 💡 **Gemini Feedback**
> **Góc nhìn Thực chiến (Senior to Junior)**
1. **Limitations & Evolution (Sự thật phũ phàng):** Ý tưởng dùng chung một cú pháp SQL cho cả Batch (data tĩnh) và Stream (data chảy liên tục) là giấc mơ đẹp của Flink. Nhưng thực tế, Streaming SQL cực kỳ khó debug. Khi em `JOIN` hai luồng stream với nhau, nếu kết quả ra sai, em gần như không thể dùng `println` để xem data bên trong nó đang chạy thế nào vì mọi thứ bị giấu sau lớp abstraction của Engine.
    
2. **War Stories & Troubleshooting:** Junior viết Flink SQL rất hay quên khái niệm **"Retraction" (Thu hồi)**. Stream SQL không chỉ tạo ra data mới (INSERT), mà khi update, nó bắn ra lệnh thu hồi data cũ (-UPDATE) và phát ra data mới (+UPDATE). Nếu cái Sink đầu ra (ví dụ Kafka) không hiểu lệnh thu hồi này, dữ liệu cuối cùng hiển thị trên Dashboard sẽ bị sai lệch hoàn toàn.
    
3. **Micro-Lab:** Để hiểu Streaming SQL, hãy tải Flink SQL Client về, tạo một bảng mô phỏng luồng click chuột từ `datagen` (dữ liệu rác tự sinh) và gõ lệnh `SELECT count(*), window_start FROM table GROUP BY TUMBLE(time, INTERVAL '10' SECONDS)` để thấy kết quả nháy liên tục trên màn hình.

---
## 10. TỔNG KẾT & EVOLUTION

### Timeline

```mermaid
timeline
    title Stream Processing Papers Evolution
    2011 : Kafka (LinkedIn)
         : Distributed commit log
    2013 : MillWheel (Google)
         : Exactly-once streaming
         : Spark Streaming (Berkeley)
         : Micro-batch model
    2014 : Storm @Twitter
         : First open-source stream processor
    2015 : Dataflow Model (Google)
         : Unified batch+streaming
         : Flink ABS Snapshots
         : Lightweight checkpointing
    2016 : Kafka Streams (Confluent)
         : Library-based processing
    2017 : Samza (LinkedIn)
         : Kafka-native stateful
    2019 : Streaming SQL (Calcite)
         : One SQL to Rule Them All
```

### Evolution of Processing Guarantees

```mermaid
graph LR
    AtMost["At-most-once<br/>(Storm, early Kafka)"]
    AtLeast["At-least-once<br/>(Storm, Samza)"]
    Exactly["Exactly-once<br/>(Flink, Kafka 0.11+,<br/>Dataflow, Spark)"]
    
    AtMost -->|"2011-2013"| AtLeast
    AtLeast -->|"2013-2016"| Exactly
```

### Comparison of All Systems

| System | Model | Latency | Guarantee | State | API |
|--------|-------|---------|-----------|-------|-----|
| **Kafka** | Message bus | ~1ms | Exactly-once (0.11+) | — | Producer/Consumer |
| **Storm** | Record-by-record | Low | At-least-once | Bolt state | Spout/Bolt |
| **Spark Streaming** | Micro-batch | 100ms+ | Exactly-once | RDD state | DStream/SQL |
| **MillWheel** | Record-by-record | Low | Exactly-once | Spanner | Computation |
| **Flink** | Record-by-record | Low | Exactly-once | RocksDB | DataStream/SQL |
| **Samza** | Record-by-record | Low | At-least-once | RocksDB | Task |
| **Kafka Streams** | Record-by-record | Low | Exactly-once | RocksDB | KStream/KTable |
| **Beam/Dataflow** | Unified | Varies | Exactly-once | Runner | PCollection |

### Key Concepts Introduced by Each Paper

```mermaid
graph TB
    subgraph Concepts[" "]
        Concepts_title["Lasting Contributions"]
        style Concepts_title fill:none,stroke:none,color:#333,font-weight:bold
        Kafka["Kafka: Commit log<br/>as universal data backbone"]
        Mill["MillWheel: Watermarks<br/>and exactly-once"]
        DF["Dataflow: The 4 Questions<br/>What/Where/When/How"]
        Flink["Flink: ABS checkpointing<br/>for fault tolerance"]
        KS["Kafka Streams: Stream<br/>processing as a library"]
        SQL["Streaming SQL: Unified<br/>batch + stream SQL"]
    end
```

---

## 📦 Verified Resources

| Resource | Link | Note |
|----------|------|------|
| Streaming Systems Book | [oreilly.com](https://www.oreilly.com/library/view/streaming-systems/9781491983867/) | Tyler Akidau et al. |
| Kafka: The Definitive Guide | [confluent.io](https://www.confluent.io/resources/kafka-the-definitive-guide-v2/) | Free ebook |
| Flink Documentation | [flink.apache.org](https://flink.apache.org/docs/) | Official docs |
| Beam Programming Guide | [beam.apache.org](https://beam.apache.org/documentation/programming-guide/) | Dataflow implementation |
| Papers We Love | [papers-we-love/papers-we-love](https://github.com/papers-we-love/papers-we-love) | 90k⭐ Paper discussions |

---
<mark style="background: #BBFABBA6;">💡 **Gemini Message**</mark>
Đúng là từ sau năm 2019 (với paper _One SQL to Rule Them All_ của Flink), mảng Stream Processing dường như không có thêm một "Framework" cốt lõi nào mang tính lật đổ như cách Spark/Flink từng làm.

Nhưng không có nghĩa là công nghệ này dậm chân tại chỗ. Từ 2019 đến 2026, cuộc chơi Streaming đã chuyển sang một "hình thái" hoàn toàn khác. Thay vì đẻ thêm Framework tính toán, giới kỹ thuật tập trung vào **Streaming Databases**, **Tích hợp Data Lake** và **Trải nghiệm Developer (DX)**.

Dưới đây là bức tranh tiến hóa của Stream Processing từ 2019 - 2026 mà em có thể note lại, nó sẽ cực kỳ hữu ích khi em thiết kế kiến trúc cho các dự án tự build như Data-Keeper:

**(1) Kỷ nguyên của Streaming Databases (2020 - nay)**

- **Sự thật phũ phàng:** Flink hay Kafka Streams tính toán rất giỏi, nhưng chúng KHÔNG PHẢI LÀ DATABASE. Em không thể cắm trực tiếp một cái BI Dashboard hay API vào Flink để query được. Phải đẩy data kết quả ra một hệ thống thứ 3 (như Postgres hay Redis) cực kỳ cồng kềnh.

- **Kẻ thay đổi cuộc chơi:** Sự bùng nổ của **Materialize (2020)** và **RisingWave (2022)**. Chúng là các cơ sở dữ liệu sinh ra cho streaming. Em đẩy thẳng data từ Kafka vào, gõ SQL tạo `MATERIALIZED VIEW`, và database sẽ tự động update view đó real-time ở dưới nền tảng (dùng Incremental Computation). Sau đó em cắm thẳng API vào đọc bảng view đó. Nhanh, gọn, lẹ.


**(2) Real-time OLAP "Xưng vương" (2021 - nay)**

- Khi phần cứng (như các dòng máy trạm HP Z440 với CPU nhiều nhân) ngày càng rẻ và SSD NVMe ngày càng nhanh, việc dùng sức mạnh "cơ bắp" để quét dữ liệu thay vì phải maintain luồng stream phức tạp trở nên khả thi.

- **Kẻ thay đổi cuộc chơi:** **ClickHouse**, **Apache Pinot**, **Apache Druid**. Thay vì hì hục code Flink để tính tổng số sự kiện trong 5 phút, em cứ xả raw data thẳng vào ClickHouse. Với khả năng Vectorized Execution siêu việt, nó quét hàng tỷ dòng trong vài chục millisecond. Kiến trúc lúc này siêu tối giản: `Kafka -> ClickHouse -> Dashboard`, bỏ qua luôn lớp Flink ở giữa cho các bài toán Aggregation cơ bản.


**(3) Streaming gặp gỡ Data Lakehouse (2022 - 2026)**

- **Sự thật phũ phàng:** Ghi data liên tục (streaming) vào S3/MinIO bằng Parquet là một thảm họa vật lý vì nó sinh ra hàng vạn file dung lượng vài KB (Small File Problem), làm sập NameNode hoặc tốn chi phí API call khổng lồ.

- **Kẻ thay đổi cuộc chơi:** **Apache Paimon (2023)** (được nhắc ở file 04) ra đời chuyên trị bài toán "Streaming Data Lake". Nó tích hợp cực sâu với Flink, cho phép ghi data real-time thẳng xuống Object Storage với kiến trúc LSM-Tree mà không sợ nát file metadata. Các format khác như Iceberg v2/v3 (với Deletion Vectors) hay Delta Live Tables cũng lao vào giải quyết triệt để nỗi đau này.


**(4) Real-time AI & RAG (2024 - 2026)**

- Khi AI bùng nổ, việc có data sạch và mới nhất là yếu tố sống còn cho các hệ thống Agent. Nếu data bị trễ 1 ngày, con AI sẽ lấy thông tin cũ để trả lời (Hallucination).

- **Kẻ thay đổi cuộc chơi:** Các luồng streaming hiện tại được dùng để làm **Real-time RAG**. Các công cụ streaming native bằng Python (như Bytewax, Quix, hoặc Flink Python API) được ưa chuộng. Cứ có một tài liệu hay log mới sinh ra, pipeline sẽ tự động chạy real-time để chia nhỏ (chunk), biến thành vector (embed) và cập nhật thẳng vào Vector Database, giúp AI có "ký ức" được update theo từng giây.


**Tóm lại:** Nếu 2011-2019 là kỷ nguyên **"Xây dựng nhà máy nước"** (tạo ra các đường ống Kafka, máy bơm Flink to nạc), thì 2019-2026 là kỷ nguyên **"Sản xuất nước đóng chai"** (đóng gói mọi sức mạnh đó vào Streaming DBs, Cloud Serverless, hoặc giấu nhẹm đi bằng SQL).

Do đó, giới học thuật sẽ không viết paper về việc tạo ra một cái ống nước mới nữa, mà họ chuyển sang viết về cách làm sao để tích hợp dòng nước đó thẳng vào Database, Data Lake và AI một cách vô hình nhất!


---
## 🔗 Liên Kết Nội Bộ

- [[01_Distributed_Systems_Papers|Distributed Systems Papers]] — Foundation papers
- [[../tools/05_Apache_Kafka_Complete_Guide|Apache Kafka]] — Kafka deep dive
- [[../tools/04_Apache_Flink_Complete_Guide|Apache Flink]] — Flink deep dive
- [[../fundamentals/07_Batch_vs_Streaming|Batch vs Streaming]] — Processing patterns
- [[../tools/06_Apache_Spark_Complete_Guide|Apache Spark]] — Spark Streaming

---

*Document Version: 2.0*
*Last Updated: February 2026*
*Coverage: Kafka, Dataflow, Flink ABS, MillWheel, Storm, Spark Streaming, Samza, Kafka Streams, Streaming SQL*
