# ⚡ Apache Flink - Complete Guide

> **"Stateful Computations over Data Streams"**

---

## 📑 Mục Lục

1. [Giới Thiệu & Lịch Sử](#-giới-thiệu--lịch-sử)
2. [Kiến Trúc Chi Tiết](#-kiến-trúc-chi-tiết)
3. [Core Concepts](#-core-concepts)
4. [Programming APIs](#-programming-apis)
5. [State Management](#-state-management)
6. [Windowing](#-windowing)
7. [Hands-on Code Examples](#-hands-on-code-examples)
8. [Use Cases Thực Tế](#-use-cases-thực-tế)
9. [Best Practices](#-best-practices)
10. [Production Deployment](#-production-deployment)

---

## 🌟 Giới Thiệu & Lịch Sử

### Flink là gì?

Apache Flink là một **distributed stream processing framework** và **batch processing engine** được thiết kế cho high-throughput, low-latency data processing. Flink xử lý dữ liệu như **unbounded streams** (continuous) hoặc **bounded streams** (batch), với exactly-once semantics và stateful computations.

### Lịch Sử Phát Triển

**2010** - Bắt đầu như research project "Stratosphere" tại TU Berlin

**2014** - Donated cho Apache Software Foundation
- Renamed to Apache Flink (Flink = "agile" in German)

**2015** - Graduated thành Top-Level Apache Project

**2016** - Version 1.0 release
- Production-ready with stateful streaming

**2017** - Alibaba adopts và contributes massively
- Blink merge begins

**2019** - Version 1.9 - Blink SQL engine merged
- Major performance improvements

**2020** - Version 1.11-1.12 - PyFlink matures

**2021** - Version 1.13-1.14 - Unified batch/stream API

**2022** - Version 1.15-1.16 - Improved Kubernetes support

**2023** - Version 1.17-1.18 - Better SQL, state improvements

**2024** - Version 1.19-2.0 - Major version jump

**2025** - Version 2.2.0 (December) - AI integration, improved Iceberg support

### Tại sao chọn Flink?

**Flink vs Spark Streaming:**
- True streaming (not micro-batch)
- Lower latency (milliseconds vs seconds)
- Better stateful processing
- Event-time processing built-in

**Flink vs Kafka Streams:**
- Cluster management included
- Better for complex topologies
- More processing capabilities

### Key Contributors

**Stephan Ewen** - Co-creator, CTO Ververica (nay Confluent)

**Kostas Tzoumas** - Co-creator, CEO Ververica

**Robert Metzger** - PMC Chair

**Alibaba** - Major contributor (Blink)

**Companies Using Flink:**
- Alibaba (largest deployment: 10,000+ jobs)
- Netflix
- Uber
- Pinterest
- Lyft
- ING Bank
- Booking.com

---

## 🏗️ Kiến Trúc Chi Tiết

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                         Flink Cluster                                │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  ┌────────────────────────────────────────────────────────────────┐ │
│  │                      Job Manager                                │ │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │ │
│  │  │  Dispatcher  │  │ResourceMgr  │  │  JobMaster   │          │ │
│  │  │  (REST API)  │  │(allocations)│  │ (per job)    │          │ │
│  │  └──────────────┘  └──────────────┘  └──────────────┘          │ │
│  │                                                                 │ │
│  │  Responsibilities:                                              │ │
│  │  • Coordinate distributed execution                            │ │
│  │  • Schedule tasks to Task Managers                             │ │
│  │  • Coordinate checkpoints                                      │ │
│  │  • Handle recovery                                             │ │
│  └────────────────────────────────────────────────────────────────┘ │
│                              │                                       │
│                              ▼                                       │
│  ┌────────────────────────────────────────────────────────────────┐ │
│  │                    Task Managers (Workers)                      │ │
│  │                                                                 │ │
│  │  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐ │ │
│  │  │  Task Manager 1 │  │  Task Manager 2 │  │  Task Manager N │ │ │
│  │  │                 │  │                 │  │                 │ │ │
│  │  │  ┌───────────┐  │  │  ┌───────────┐  │  │  ┌───────────┐  │ │ │
│  │  │  │  Task 1   │  │  │  │  Task 3   │  │  │  │  Task 5   │  │ │ │
│  │  │  │ (Slot 1)  │  │  │  │ (Slot 1)  │  │  │  │ (Slot 1)  │  │ │ │
│  │  │  └───────────┘  │  │  └───────────┘  │  │  └───────────┘  │ │ │
│  │  │  ┌───────────┐  │  │  ┌───────────┐  │  │  ┌───────────┐  │ │ │
│  │  │  │  Task 2   │  │  │  │  Task 4   │  │  │  │  Task 6   │  │ │ │
│  │  │  │ (Slot 2)  │  │  │  │ (Slot 2)  │  │  │  │ (Slot 2)  │  │ │ │
│  │  │  └───────────┘  │  │  └───────────┘  │  │  └───────────┘  │ │ │
│  │  │                 │  │                 │  │                 │ │ │
│  │  │  [State Store] │  │  [State Store] │  │  [State Store] │ │ │
│  │  │  (RocksDB)     │  │  (RocksDB)     │  │  (RocksDB)     │ │ │
│  │  └─────────────────┘  └─────────────────┘  └─────────────────┘ │ │
│  └────────────────────────────────────────────────────────────────┘ │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    Checkpoint Storage                                │
│                 (S3 / HDFS / GCS / Azure Blob)                       │
└─────────────────────────────────────────────────────────────────────┘
```

### Job Execution Flow

```
┌─────────────────────────────────────────────────────────────────────┐
│                      Job Submission Flow                             │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│   User Code                                                          │
│      │                                                               │
│      ▼                                                               │
│   ┌──────────────┐                                                   │
│   │  StreamGraph │  ─► Logical representation of program             │
│   │  (logical)   │     Operators and their connections               │
│   └──────┬───────┘                                                   │
│          │                                                           │
│          ▼                                                           │
│   ┌──────────────┐                                                   │
│   │   JobGraph   │  ─► Optimized with operator chaining              │
│   │  (optimized) │     Operator chains = tasks                       │
│   └──────┬───────┘                                                   │
│          │                                                           │
│          ▼                                                           │
│   ┌──────────────────┐                                               │
│   │ ExecutionGraph   │  ─► Parallelism applied                       │
│   │   (parallel)     │     Tasks split into subtasks                 │
│   └──────────────────┘                                               │
│          │                                                           │
│          ▼                                                           │
│   Deployed to Task Managers                                          │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

### Operator Chaining

```
Before Chaining:
┌────────┐   ┌────────┐   ┌────────┐   ┌────────┐
│ Source │──►│ Filter │──►│  Map   │──►│  Sink  │
└────────┘   └────────┘   └────────┘   └────────┘
  Task 1       Task 2       Task 3       Task 4

After Chaining:
┌──────────────────────────────────────┐   ┌────────┐
│  Source ──► Filter ──► Map           │──►│  Sink  │
│          (chained operators)          │   └────────┘
└──────────────────────────────────────┘
              Task 1                        Task 2

Benefits:
✅ Reduced serialization overhead
✅ Lower latency
✅ Better resource utilization
```

---

## 📚 Core Concepts

### 1. Streams vs Bounded/Unbounded

```
Unbounded Streams (typical streaming):
─────────────────────────────────────────────────►
Events arrive continuously, no end

Bounded Streams (batch):
─────────────────────────────────────────┤
Dataset with known beginning and end

Flink treats everything as streams:
• Unbounded → DataStream API
• Bounded → DataStream API or Table API (batch mode)
```

### 2. Event Time vs Processing Time

**Processing Time:**
- Time when event is processed by Flink
- Simplest, but non-deterministic
- Use when: Order doesn't matter

**Event Time:**
- Time embedded in the event itself
- Deterministic, handles late data
- Use when: Order matters, analytics

**Ingestion Time:**
- Time when event enters Flink
- Middle ground

```
Event Timeline:
                                                    
Event Created    Network Delay    Enters Flink    Processed
     │                               │                │
     ▼                               ▼                ▼
   ─────────────────────────────────────────────────────►
     │                               │                │
   Event Time                  Ingestion Time   Processing Time
```

### 3. Watermarks

Watermarks tell Flink "all events up to this time have arrived."

```
Event Stream with Watermarks:
                                                    
──[e1:t=1]──[e2:t=3]──[e5:t=5]──[W:4]──[e4:t=4]──[e6:t=6]──[W:6]──►
                                  │                        │
                      Watermark t=4              Watermark t=6
                      (events ≤4 complete)       (events ≤6 complete)

Late event e4 (t=4) arrives after watermark t=4
→ Can be handled by "allowed lateness"
```

**Watermark Strategies:**

```java
// Bounded out-of-orderness (most common)
WatermarkStrategy
    .<Event>forBoundedOutOfOrderness(Duration.ofSeconds(5))
    .withTimestampAssigner((event, timestamp) -> event.getTimestamp());

// Monotonously increasing (perfect ordering)
WatermarkStrategy
    .forMonotonousTimestamps();

// Custom
WatermarkStrategy
    .forGenerator(ctx -> new MyWatermarkGenerator());
```

### 4. Checkpointing

Flink's mechanism for fault tolerance:

```
Checkpoint Process:
┌─────────────────────────────────────────────────────────────────┐
│                                                                  │
│  1. JobManager triggers checkpoint                              │
│     │                                                            │
│     ▼                                                            │
│  2. Checkpoint barriers injected into data stream              │
│     ────[data]────[barrier]────[data]────►                      │
│     │                                                            │
│     ▼                                                            │
│  3. Operators snapshot state when barrier arrives               │
│     State → State Backend → Checkpoint Storage                  │
│     │                                                            │
│     ▼                                                            │
│  4. All operators acknowledge → Checkpoint complete             │
│                                                                  │
│  Recovery:                                                       │
│  • Restart from last successful checkpoint                      │
│  • Restore state                                                │
│  • Replay from checkpoint position in source                    │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

**Checkpoint Configuration:**

```java
env.enableCheckpointing(60000);  // Every 60 seconds
env.getCheckpointConfig().setCheckpointingMode(CheckpointingMode.EXACTLY_ONCE);
env.getCheckpointConfig().setMinPauseBetweenCheckpoints(30000);
env.getCheckpointConfig().setCheckpointTimeout(600000);
env.getCheckpointConfig().setMaxConcurrentCheckpoints(1);
env.getCheckpointConfig().setExternalizedCheckpointCleanup(
    ExternalizedCheckpointCleanup.RETAIN_ON_CANCELLATION);
```

---

## 🔧 Programming APIs

### API Layers

```
┌─────────────────────────────────────────────────────────────────┐
│                         High-Level                               │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │                    Table API / SQL                          │ │
│  │         Declarative, SQL-like, unified batch/stream         │ │
│  └────────────────────────────────────────────────────────────┘ │
│                              │                                   │
│                              ▼                                   │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │                    DataStream API                           │ │
│  │       Functional transformations on data streams            │ │
│  └────────────────────────────────────────────────────────────┘ │
│                              │                                   │
│                              ▼                                   │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │                   ProcessFunction API                       │ │
│  │         Low-level: timers, state, side outputs              │ │
│  └────────────────────────────────────────────────────────────┘ │
│                          Low-Level                               │
└─────────────────────────────────────────────────────────────────┘
```

### DataStream API

```java
// Basic transformations
DataStream<Event> events = env.addSource(new FlinkKafkaConsumer<>(...));

events
    .filter(e -> e.getType().equals("click"))
    .map(e -> new ClickEvent(e.getUserId(), e.getTimestamp()))
    .keyBy(e -> e.getUserId())
    .window(TumblingEventTimeWindows.of(Time.minutes(5)))
    .reduce((a, b) -> new ClickEvent(a.getUserId(), a.getCount() + b.getCount()))
    .addSink(new FlinkKafkaProducer<>(...));
```

### Table API / SQL

```java
// Table API
TableEnvironment tableEnv = TableEnvironment.create(settings);

Table events = tableEnv.from("kafka_events");
Table result = events
    .filter($("type").isEqual("click"))
    .groupBy($("user_id"), $("window_start"))
    .select($("user_id"), $("window_start"), $("event_id").count().as("click_count"));

tableEnv.executeSql("CREATE TABLE output_table ...").await();
result.executeInsert("output_table");
```

```sql
-- Pure SQL
CREATE TABLE events (
    event_id STRING,
    user_id STRING,
    event_time TIMESTAMP(3),
    WATERMARK FOR event_time AS event_time - INTERVAL '5' SECOND
) WITH (
    'connector' = 'kafka',
    'topic' = 'events',
    'properties.bootstrap.servers' = 'localhost:9092',
    'format' = 'json'
);

SELECT 
    user_id,
    TUMBLE_START(event_time, INTERVAL '5' MINUTE) AS window_start,
    COUNT(*) AS event_count
FROM events
GROUP BY 
    user_id,
    TUMBLE(event_time, INTERVAL '5' MINUTE);
```

---

## 💾 State Management

### State Types

**Keyed State** (per key)

```
KeyedState Types:
┌─────────────────────────────────────────────────────────────────┐
│                                                                  │
│  ValueState<T>      - Single value per key                      │
│  ListState<T>       - List of values per key                    │
│  MapState<K,V>      - Map of key-values per key                 │
│  ReducingState<T>   - Aggregated value per key                  │
│  AggregatingState   - Custom aggregation per key                │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

**Operator State** (per operator instance)

```
OperatorState Types:
┌─────────────────────────────────────────────────────────────────┐
│                                                                  │
│  ListState<T>                 - Union redistribution            │
│  BroadcastState<K,V>          - Broadcast patterns              │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### State Backends

**HashMapStateBackend (Default)**
- State stored in JVM heap
- Fast for small state
- Limited by memory

**EmbeddedRocksDBStateBackend**
- State stored in RocksDB (disk)
- Scales to TBs of state
- Slightly slower but very large state support

```java
// Configure RocksDB backend
env.setStateBackend(new EmbeddedRocksDBStateBackend(true));
env.getCheckpointConfig().setCheckpointStorage("s3://bucket/checkpoints");
```

### Using State

```java
public class StatefulFunction extends KeyedProcessFunction<String, Event, Result> {
    
    // Declare state
    private ValueState<Long> countState;
    private ValueState<Long> lastTimestampState;
    
    @Override
    public void open(Configuration parameters) {
        // Initialize state
        ValueStateDescriptor<Long> countDesc = 
            new ValueStateDescriptor<>("count", Long.class);
        countState = getRuntimeContext().getState(countDesc);
        
        ValueStateDescriptor<Long> tsDesc = 
            new ValueStateDescriptor<>("lastTs", Long.class);
        lastTimestampState = getRuntimeContext().getState(tsDesc);
    }
    
    @Override
    public void processElement(Event event, Context ctx, Collector<Result> out) {
        // Read state
        Long count = countState.value();
        if (count == null) count = 0L;
        
        // Update state
        count++;
        countState.update(count);
        lastTimestampState.update(event.getTimestamp());
        
        // Register timer
        ctx.timerService().registerEventTimeTimer(
            event.getTimestamp() + Duration.ofMinutes(5).toMillis()
        );
        
        out.collect(new Result(event.getKey(), count));
    }
    
    @Override
    public void onTimer(long timestamp, OnTimerContext ctx, Collector<Result> out) {
        // Timer fired - emit result or clean up
        Long count = countState.value();
        out.collect(new Result(ctx.getCurrentKey(), count));
        
        // Clear state if needed
        countState.clear();
    }
}
```

---

## 🪟 Windowing

### Window Types

```
1. Tumbling Windows (non-overlapping, fixed size)
┌──────────┐┌──────────┐┌──────────┐┌──────────┐
│ Window 1 ││ Window 2 ││ Window 3 ││ Window 4 │
│  0-5min  ││  5-10min ││ 10-15min ││ 15-20min │
└──────────┘└──────────┘└──────────┘└──────────┘
───────────────────────────────────────────────────►

2. Sliding Windows (overlapping)
┌──────────────────┐
│     Window 1     │  (0-10min)
└──────────────────┘
      ┌──────────────────┐
      │     Window 2     │  (5-15min)
      └──────────────────┘
            ┌──────────────────┐
            │     Window 3     │  (10-20min)
            └──────────────────┘
───────────────────────────────────────────────────►

3. Session Windows (activity-based gaps)
┌─────────┐          ┌──────────────┐       ┌───┐
│Session 1│          │   Session 2  │       │S3 │
└─────────┘          └──────────────┘       └───┘
   │ gap │              │   gap   │
───────────────────────────────────────────────────►

4. Global Windows (all elements in one window)
┌─────────────────────────────────────────────────┐
│                  Global Window                   │
│              (with custom trigger)               │
└─────────────────────────────────────────────────┘
───────────────────────────────────────────────────►
```

### Window Operations

```java
// Tumbling window
events
    .keyBy(e -> e.getUserId())
    .window(TumblingEventTimeWindows.of(Time.minutes(5)))
    .reduce((a, b) -> a.merge(b));

// Sliding window
events
    .keyBy(e -> e.getUserId())
    .window(SlidingEventTimeWindows.of(Time.minutes(10), Time.minutes(5)))
    .aggregate(new MyAggregateFunction());

// Session window
events
    .keyBy(e -> e.getUserId())
    .window(EventTimeSessionWindows.withGap(Time.minutes(30)))
    .process(new SessionProcessFunction());

// With late data handling
events
    .keyBy(e -> e.getUserId())
    .window(TumblingEventTimeWindows.of(Time.minutes(5)))
    .allowedLateness(Time.minutes(1))
    .sideOutputLateData(lateOutputTag)
    .reduce((a, b) -> a.merge(b));
```

---

## 💻 Hands-on Code Examples

### PyFlink Setup

```python
from pyflink.datastream import StreamExecutionEnvironment
from pyflink.table import StreamTableEnvironment, EnvironmentSettings

# Create environment
env = StreamExecutionEnvironment.get_execution_environment()
env.set_parallelism(4)
env.enable_checkpointing(60000)

# Table environment
settings = EnvironmentSettings.new_instance().in_streaming_mode().build()
table_env = StreamTableEnvironment.create(env, settings)
```

### Kafka to Iceberg Pipeline

```python
# Define Kafka source
table_env.execute_sql("""
    CREATE TABLE kafka_events (
        event_id STRING,
        user_id STRING,
        event_type STRING,
        event_time TIMESTAMP(3),
        properties MAP<STRING, STRING>,
        WATERMARK FOR event_time AS event_time - INTERVAL '5' SECOND
    ) WITH (
        'connector' = 'kafka',
        'topic' = 'events',
        'properties.bootstrap.servers' = 'localhost:9092',
        'properties.group.id' = 'flink-consumer',
        'scan.startup.mode' = 'latest-offset',
        'format' = 'json'
    )
""")

# Define Iceberg sink
table_env.execute_sql("""
    CREATE TABLE iceberg_events (
        event_id STRING,
        user_id STRING,
        event_type STRING,
        event_time TIMESTAMP(3),
        event_date STRING
    ) WITH (
        'connector' = 'iceberg',
        'catalog-name' = 'iceberg_catalog',
        'catalog-type' = 'hive',
        'warehouse' = 's3://my-bucket/warehouse'
    )
""")

# Streaming insert
table_env.execute_sql("""
    INSERT INTO iceberg_events
    SELECT 
        event_id,
        user_id,
        event_type,
        event_time,
        DATE_FORMAT(event_time, 'yyyy-MM-dd') AS event_date
    FROM kafka_events
""")
```

### Windowed Aggregation

```python
# Tumbling window aggregation
table_env.execute_sql("""
    CREATE VIEW hourly_stats AS
    SELECT 
        user_id,
        TUMBLE_START(event_time, INTERVAL '1' HOUR) AS window_start,
        TUMBLE_END(event_time, INTERVAL '1' HOUR) AS window_end,
        COUNT(*) AS event_count,
        COUNT(DISTINCT event_type) AS unique_events
    FROM kafka_events
    GROUP BY 
        user_id,
        TUMBLE(event_time, INTERVAL '1' HOUR)
""")

# Write to sink
table_env.execute_sql("""
    INSERT INTO analytics_output
    SELECT * FROM hourly_stats
""")
```

### DataStream API Example (Java)

```java
import org.apache.flink.streaming.api.environment.StreamExecutionEnvironment;
import org.apache.flink.streaming.api.datastream.DataStream;
import org.apache.flink.streaming.api.windowing.time.Time;

public class FlinkExample {
    public static void main(String[] args) throws Exception {
        StreamExecutionEnvironment env = 
            StreamExecutionEnvironment.getExecutionEnvironment();
        
        // Configure checkpointing
        env.enableCheckpointing(60000);
        env.getCheckpointConfig().setMinPauseBetweenCheckpoints(30000);
        
        // Source
        DataStream<Event> events = env
            .addSource(new FlinkKafkaConsumer<>(
                "events",
                new EventDeserializationSchema(),
                kafkaProps
            ))
            .assignTimestampsAndWatermarks(
                WatermarkStrategy
                    .<Event>forBoundedOutOfOrderness(Duration.ofSeconds(5))
                    .withTimestampAssigner((e, t) -> e.getTimestamp())
            );
        
        // Processing
        DataStream<Result> results = events
            .filter(e -> e.getType().equals("click"))
            .keyBy(Event::getUserId)
            .window(TumblingEventTimeWindows.of(Time.minutes(5)))
            .aggregate(new ClickCountAggregator());
        
        // Sink
        results.addSink(new FlinkKafkaProducer<>(
            "results",
            new ResultSerializationSchema(),
            kafkaProps
        ));
        
        env.execute("Click Analytics Job");
    }
}
```

### Stateful Processing Example

```java
public class FraudDetector extends KeyedProcessFunction<Long, Transaction, Alert> {
    
    private static final double SMALL_AMOUNT = 1.00;
    private static final double LARGE_AMOUNT = 500.00;
    private static final long ONE_MINUTE = 60 * 1000;
    
    private transient ValueState<Boolean> flagState;
    private transient ValueState<Long> timerState;
    
    @Override
    public void open(Configuration parameters) {
        flagState = getRuntimeContext().getState(
            new ValueStateDescriptor<>("flag", Boolean.class));
        timerState = getRuntimeContext().getState(
            new ValueStateDescriptor<>("timer", Long.class));
    }
    
    @Override
    public void processElement(Transaction tx, Context ctx, Collector<Alert> out) 
            throws Exception {
        
        Boolean lastTransactionWasSmall = flagState.value();
        
        if (lastTransactionWasSmall != null && lastTransactionWasSmall) {
            if (tx.getAmount() > LARGE_AMOUNT) {
                // Fraud pattern detected!
                out.collect(new Alert(tx.getAccountId()));
            }
            // Clear the flag
            cleanUp(ctx);
        }
        
        if (tx.getAmount() < SMALL_AMOUNT) {
            // Set flag and timer
            flagState.update(true);
            
            long timer = ctx.timerService().currentProcessingTime() + ONE_MINUTE;
            ctx.timerService().registerProcessingTimeTimer(timer);
            timerState.update(timer);
        }
    }
    
    @Override
    public void onTimer(long timestamp, OnTimerContext ctx, Collector<Alert> out) {
        // Clear flag after timeout
        timerState.clear();
        flagState.clear();
    }
    
    private void cleanUp(Context ctx) throws Exception {
        Long timer = timerState.value();
        if (timer != null) {
            ctx.timerService().deleteProcessingTimeTimer(timer);
        }
        timerState.clear();
        flagState.clear();
    }
}
```

### CDC with Flink SQL

```sql
-- MySQL CDC Source
CREATE TABLE mysql_orders (
    order_id BIGINT,
    user_id BIGINT,
    amount DECIMAL(10, 2),
    status STRING,
    created_at TIMESTAMP(3),
    PRIMARY KEY (order_id) NOT ENFORCED
) WITH (
    'connector' = 'mysql-cdc',
    'hostname' = 'mysql-host',
    'port' = '3306',
    'username' = 'flink',
    'password' = 'password',
    'database-name' = 'orders_db',
    'table-name' = 'orders'
);

-- Iceberg Sink with Upsert
CREATE TABLE iceberg_orders (
    order_id BIGINT,
    user_id BIGINT,
    amount DECIMAL(10, 2),
    status STRING,
    created_at TIMESTAMP(3),
    PRIMARY KEY (order_id) NOT ENFORCED
) WITH (
    'connector' = 'iceberg',
    'catalog-name' = 'iceberg_catalog',
    'database-name' = 'orders',
    'table-name' = 'orders',
    'write.upsert.enabled' = 'true'
);

-- Stream changes to Iceberg
INSERT INTO iceberg_orders
SELECT * FROM mysql_orders;
```

---

## 🎯 Use Cases Thực Tế

### 1. Alibaba - Double 11 (Singles Day)

```
┌─────────────────────────────────────────────────────────────────┐
│                  Alibaba Double 11 Architecture                  │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│   Scale:                                                         │
│   • 583,000 orders per second peak                              │
│   • 10,000+ Flink jobs                                          │
│   • Petabytes of data processed                                 │
│                                                                  │
│   Use Cases:                                                     │
│   • Real-time GMV dashboard                                     │
│   • Fraud detection                                             │
│   • Recommendation updates                                      │
│   • Inventory management                                        │
│                                                                  │
│   Architecture:                                                  │
│   Mobile Apps ──► API Gateway ──► Kafka ──► Flink               │
│                                              │                   │
│                            ┌─────────────────┼─────────────────┐ │
│                            ▼                 ▼                 ▼ │
│                     Real-time          Analytics          ML     │
│                     Dashboard          (Hudi/Iceberg)    Models  │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### 2. Fraud Detection Pipeline

```
┌─────────────────────────────────────────────────────────────────┐
│                    Fraud Detection Pipeline                      │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│   Transactions ──► Kafka ──► Flink                              │
│                               │                                  │
│                   ┌───────────┴───────────┐                     │
│                   ▼                       ▼                     │
│           ┌─────────────┐         ┌─────────────┐               │
│           │   Pattern   │         │     ML      │               │
│           │  Detection  │         │   Scoring   │               │
│           │  (rules)    │         │  (model)    │               │
│           └──────┬──────┘         └──────┬──────┘               │
│                  │                       │                      │
│                  └───────────┬───────────┘                      │
│                              ▼                                   │
│                      ┌─────────────┐                            │
│                      │   Combine   │                            │
│                      │   Results   │                            │
│                      └──────┬──────┘                            │
│                             │                                    │
│               ┌─────────────┴─────────────┐                     │
│               ▼                           ▼                     │
│        ┌───────────┐               ┌───────────┐                │
│        │   Block   │               │   Alert   │                │
│        │Transaction│               │   Team    │                │
│        └───────────┘               └───────────┘                │
│                                                                  │
│   Features:                                                      │
│   • Sub-100ms latency                                           │
│   • Exactly-once processing                                     │
│   • Stateful pattern matching                                   │
│   • ML model inference                                          │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### 3. Real-time ETL to Lakehouse

```python
# Complete ETL pipeline: Kafka → Flink → Iceberg

# Source: Kafka with CDC events
table_env.execute_sql("""
    CREATE TABLE cdc_events (
        `before` ROW<id BIGINT, name STRING, amount DECIMAL(10,2)>,
        `after` ROW<id BIGINT, name STRING, amount DECIMAL(10,2)>,
        `op` STRING,
        `ts_ms` BIGINT,
        proc_time AS PROCTIME()
    ) WITH (
        'connector' = 'kafka',
        'topic' = 'postgres.public.orders',
        'properties.bootstrap.servers' = 'kafka:9092',
        'format' = 'debezium-json'
    )
""")

# Transform and write to Iceberg
table_env.execute_sql("""
    INSERT INTO iceberg_catalog.db.orders
    SELECT 
        COALESCE(`after`.id, `before`.id) AS id,
        `after`.name AS name,
        `after`.amount AS amount,
        CASE `op`
            WHEN 'c' THEN 'INSERT'
            WHEN 'u' THEN 'UPDATE'
            WHEN 'd' THEN 'DELETE'
            ELSE 'UNKNOWN'
        END AS operation,
        TO_TIMESTAMP(FROM_UNIXTIME(`ts_ms` / 1000)) AS event_time
    FROM cdc_events
""")
```

---

## ✅ Best Practices

### 1. Checkpointing

**Configuration:**
```java
// Enable checkpointing
env.enableCheckpointing(60000);  // 60 seconds

// Exactly-once mode
env.getCheckpointConfig().setCheckpointingMode(CheckpointingMode.EXACTLY_ONCE);

// Minimum pause between checkpoints
env.getCheckpointConfig().setMinPauseBetweenCheckpoints(30000);

// Checkpoint timeout
env.getCheckpointConfig().setCheckpointTimeout(600000);

// Retain checkpoints on cancellation
env.getCheckpointConfig().setExternalizedCheckpointCleanup(
    ExternalizedCheckpointCleanup.RETAIN_ON_CANCELLATION);

// Use incremental checkpoints with RocksDB
env.setStateBackend(new EmbeddedRocksDBStateBackend(true));
```

### 2. Parallelism Tuning

**Guidelines:**
- Start with parallelism = number of Kafka partitions
- Monitor backpressure
- Scale based on throughput needs

```java
// Global parallelism
env.setParallelism(16);

// Operator-specific parallelism
events
    .filter(e -> e.isValid())
    .setParallelism(8)  // Lower parallelism for light operations
    .keyBy(e -> e.getKey())
    .window(TumblingEventTimeWindows.of(Time.minutes(5)))
    .aggregate(new HeavyAggregation())
    .setParallelism(32);  // Higher for heavy operations
```

### 3. Memory Configuration

```yaml
# flink-conf.yaml
taskmanager.memory.process.size: 4096m
taskmanager.memory.managed.fraction: 0.4
taskmanager.memory.network.fraction: 0.1
taskmanager.memory.jvm-overhead.fraction: 0.1

# For RocksDB
state.backend.rocksdb.memory.managed: true
state.backend.rocksdb.memory.fixed-per-slot: 256mb
```

### 4. Handling Late Data

```java
events
    .keyBy(e -> e.getUserId())
    .window(TumblingEventTimeWindows.of(Time.minutes(5)))
    .allowedLateness(Time.minutes(1))
    .sideOutputLateData(lateDataTag)
    .process(new MyWindowFunction());

// Handle late data separately
DataStream<Event> lateData = result.getSideOutput(lateDataTag);
lateData.addSink(new LateDataSink());
```

### 5. Watermark Strategy

```java
// For well-ordered data
WatermarkStrategy.forMonotonousTimestamps();

// For out-of-order data (most common)
WatermarkStrategy
    .<Event>forBoundedOutOfOrderness(Duration.ofSeconds(10))
    .withTimestampAssigner((event, timestamp) -> event.getEventTime())
    .withIdleness(Duration.ofMinutes(1));  // Handle idle partitions
```

---

## 🏭 Production Deployment

### Kubernetes Deployment

```yaml
# Flink Kubernetes Operator deployment
apiVersion: flink.apache.org/v1beta1
kind: FlinkDeployment
metadata:
  name: my-flink-job
spec:
  image: flink:1.18
  flinkVersion: v1_18
  flinkConfiguration:
    taskmanager.numberOfTaskSlots: "2"
    state.backend: rocksdb
    state.checkpoints.dir: s3://bucket/checkpoints
  serviceAccount: flink
  jobManager:
    resource:
      memory: "2048m"
      cpu: 1
  taskManager:
    resource:
      memory: "4096m"
      cpu: 2
    replicas: 3
  job:
    jarURI: s3://bucket/jobs/my-job.jar
    parallelism: 6
    upgradeMode: savepoint
```

### Monitoring

**Key Metrics:**
- `numRecordsIn/Out` - Throughput
- `numRecordsInPerSecond` - Input rate
- `currentInputWatermark` - Watermark progress
- `lastCheckpointDuration` - Checkpoint health
- `lastCheckpointSize` - State size

**Backpressure Monitoring:**
- Check isBackPressured metric
- Look at busy/idle ratio
- Identify bottleneck operators

---

## 📚 Resources

### Official
- Apache Flink Website: https://flink.apache.org/
- GitHub: https://github.com/apache/flink
- Documentation: https://nightlies.apache.org/flink/flink-docs-stable/

### Learning
- Flink Training: https://github.com/apache/flink-training
- Ververica Blog: https://www.ververica.com/blog

### Community
- Mailing Lists: https://flink.apache.org/community.html
- Slack: https://apache-flink.slack.com/

---

> **Document Version**: 1.0  
> **Last Updated**: December 31, 2025  
> **Flink Version**: 2.2.0
