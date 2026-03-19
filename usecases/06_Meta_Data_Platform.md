# Meta/Facebook Data Platform Architecture

## Kiến Trúc Data Platform Của Meta - The Social Network Giant

---

## 🏢 TỔNG QUAN CÔNG TY

- **Quy mô:** 3+ tỷ monthly active users (Facebook, Instagram, WhatsApp)
- **Data scale:** Exabytes of data, largest data warehouse in the world
- **Innovation:** Pioneers of many data technologies
- **Open source contributions:** Presto, Spark improvements, RocksDB, Velox, PyTorch

---

## 🏗️ TỔNG QUAN KIẾN TRÚC

```mermaid
graph TB
    subgraph Sources[" "]
        Sources_title["📱 DATA SOURCES"]
        style Sources_title fill:none,stroke:none,color:#333,font-weight:bold
        S1["Posts / Likes"]
        S2["Photos / Videos"]
        S3["Messages Events"]
        S4["Ads Events"]
        S5["Instagram / WhatsApp"]
    end

    subgraph Ingestion[" "]
        Ingestion_title["📥 INGESTION LAYER"]
        style Ingestion_title fill:none,stroke:none,color:#333,font-weight:bold
        Scribe["Scribe<br/>Distributed Log Aggregation"]
        StreamProc["Stream Processing<br/>Real-time joins & features"]
    end

    subgraph Storage[" "]
        Storage_title["💾 STORAGE LAYER"]
        style Storage_title fill:none,stroke:none,color:#333,font-weight:bold
        DWH["Data Warehouse<br/>Hive/Spark - Exabytes"]
        FS["Feature Store<br/>Feature Platform"]
        RT["Real-time Store<br/>TAO Social Graph<br/>ZippyDB KV Store"]
    end

    subgraph Query[" "]
        Query_title["🔍 QUERY LAYER"]
        style Query_title fill:none,stroke:none,color:#333,font-weight:bold
        Presto["Presto<br/>Interactive SQL"]
        SparkSQL["Spark SQL<br/>ETL / ML"]
        Scuba["Scuba<br/>Real-time Analytics"]
    end

    subgraph MLPlatform[" "]
        MLPlatform_title["🧠 ML PLATFORM"]
        style MLPlatform_title fill:none,stroke:none,color:#333,font-weight:bold
        PyTorch[PyTorch]
        FBLearner[FBLearner Flow]
        MLFeature[Feature Store]
        ModelReg[Model Registry]
        Inference[Inference Platform]
    end

    subgraph Products[" "]
        Products_title["🚀 DATA PRODUCTS"]
        style Products_title fill:none,stroke:none,color:#333,font-weight:bold
        P1[News Feed Ranking]
        P2[Ads Ranking]
        P3[Content Recommend]
        P4[Search Ranking]
        P5[Integrity Detection]
    end

    S1 & S2 & S3 & S4 & S5 --> Scribe
    Scribe --> StreamProc
    StreamProc --> DWH & FS & RT
    DWH & FS & RT --> Presto & SparkSQL & Scuba
    Presto & SparkSQL & Scuba --> PyTorch & FBLearner & MLFeature & ModelReg & Inference
    PyTorch & FBLearner --> P1 & P2 & P3 & P4 & P5
```

---

## 🔧 TECH STACK CHI TIẾT

### 1. Presto (Meta Created)

**Origin:** Created by Facebook in 2012, now Trino (fork) and PrestoDB

```
```mermaid
flowchart TD
    subgraph PRESTO [" "]
        direction TB
        P_TITLE["PRESTO<br>(Distributed SQL Query Engine)"]
        style P_TITLE fill:none,stroke:none,font-weight:bold,color:#333
        
        C["Coordinator<br>- Query parsing<br>- Query planning<br>- Query scheduling"]
        
        W1["Worker 1<br>- Task execution<br>- Data processing"]
        WN["Worker N<br>- Task execution<br>- Data processing"]
        
        C --> W1
        C --> WN
    end
```

> **Connectors:** Hive (HDFS/S3), MySQL, Kafka, Cassandra, Custom connectors
> 
> **PRESTO AT META:**
> 
> * **Scale:** 1000s of queries/second, 300+ PB scanned/day, 10,000s of users
> * **Use cases:** Interactive analytics (seconds), A/B test analysis, Ad-hoc exploration, Dashboard backend
```

### 2. Spark at Meta Scale

```
> **SPARK AT META:**
> 
> * **Scale:**
>   * 10,000s of jobs/day
>   * 1,000s of TB processed/day
>   * Multi-exabyte data lake
> 
> * **Optimizations by Meta:**
>   1. **Shuffle Optimization:** Custom shuffle service, Disaggregated shuffle storage
>   2. **Adaptive Query Execution:** Runtime re-optimization, Dynamic partition coalescing
>   3. **Resource Management:** Custom YARN scheduler, Preemption for priority jobs
>   4. **Caching:** Distributed cache (Alluxio-like), Hot data acceleration
> 
> * **Use cases:**
>   * ETL pipelines
>   * ML training data preparation
>   * Data quality checks
>   * Privacy compliance (data deletion)
```

### 3. TAO (The Associations and Objects)

```
```mermaid
flowchart TD
    subgraph TAO [" "]
        direction TB
        T_TITLE["TAO<br>(Distributed Social Graph Store)"]
        style T_TITLE fill:none,stroke:none,font-weight:bold,color:#333
        
        DM["Data Model:<br>Objects: Users, Posts, Photos, Pages<br>Associations: Friendships, Likes, Comments<br><br>User(123) --[friend]--> User(456)<br>User(123) --[authored]--> Post(789)<br>User(456) --[liked]--> Post(789)"]
        style DM fill:none,stroke:none,text-align:left
        
        TC["TAO Clients (App servers)"]
        TL["TAO Leaders (Caching tier)<br>- Cache coherence<br>- Write-through"]
        TF["TAO Followers (Read replicas)<br>- Read-only replicas<br>- Geographic distribution"]
        DB["MySQL (Persistent storage)<br>- Sharded by object ID"]
        
        TC --> TL
        TL --> TF
        TF --> DB
    end
```

> **TAO Scale:**
> - Billions of objects
> - Trillions of associations
> - 100B+ queries/day
> - 99.9999% cache hit rate
```

### 4. Scuba (Real-time Analytics)

```
```mermaid
flowchart TD
    subgraph SCUBA [" "]
        direction TB
        S_TITLE["SCUBA<br>(Real-time in-memory analytics)"]
        style S_TITLE fill:none,stroke:none,font-weight:bold,color:#333
        
        UC["Use Case: Real-time operational analytics<br>- Site performance monitoring<br>- Product metrics (real-time)<br>- Error tracking<br>- Ad hoc investigation"]
        
        ARCH["Events (Scribe) --> Scuba Servers (In-memory) --> Query Results<br><br>Key features:<br>- In-memory columnar storage<br>- Automatic sampling for speed<br>- Time-based retention<br>- Sub-second queries"]
        
        QRY["Query:<br>SELECT country, COUNT(*)<br>FROM app_errors<br>WHERE timestamp > now() - interval '5 minutes'<br>GROUP BY country<br><br>Result in < 1 second"]
        
        UC --> ARCH
        ARCH --> QRY
    end
```
```

### 5. Velox (Execution Engine)

```
```mermaid
flowchart TD
    subgraph VELOX [" "]
        direction TB
        V_TITLE["VELOX<br>(Unified Execution Engine)"]
        style V_TITLE fill:none,stroke:none,font-weight:bold,color:#333
        
        GOAL["Goal: Common execution engine for Presto, Spark, etc."]
        style GOAL fill:none,stroke:none
        
        subgraph F ["Query Frontends"]
            direction LR
            P["Presto"]
            S["Spark"]
            C["Custom"]
        end
        
        VE["Velox Engine<br><br>Key Features:<br>- Vectorized execution (SIMD)<br>- Adaptive execution<br>- Efficient memory management<br>- Arrow-compatible<br><br>Components:<br>- Type system, Functions library<br>- Expression evaluation<br>- Operators (scan, filter, join, agg)<br>- Memory pools"]
        
        P --> VE
        S --> VE
        C --> VE
    end
```

> **Open sourced:** 2022
> 
> **Used by:** Presto, potentially Spark, custom engines
```

### 6. PyTorch (Deep Learning)

```
> **PYTORCH AT META:**
> 
> * **Created:** 2016 by Facebook AI Research (FAIR)
> * **Status:** Most popular research framework
> 
> * **Use at Meta:**
>   * News Feed ranking
>   * Ads prediction
>   * Content understanding (CV, NLP)
>   * Integrity/safety detection
>   * Recommendations (Reels, Stories)
>   * AR/VR (Reality Labs)
>   * Large Language Models (LLaMA)
> 
> * **Scale:**
>   * 1000s of models in production
>   * 100s of billions of inferences/day
>   * Custom hardware (training + inference)
>   * Largest GPU clusters in the world
```

---

## 🎯 KEY DATA PRODUCTS

### 1. News Feed Ranking

**WHAT - Mục tiêu:**
- Personalized feed for 3B+ users
- Maximize meaningful engagement
- Balance content types (friends, pages, ads)
- Reduce harmful content exposure

**HOW - Implementation:**

```
```mermaid
flowchart TD
    subgraph FEED [" "]
        direction TB
        F_TITLE["NEWS FEED RANKING"]
        style F_TITLE fill:none,stroke:none,font-weight:bold,color:#333
        
        S1["Step 1: Inventory<br>- Friends' posts<br>- Pages/Groups content<br>- Ads<br>- Suggested content<br>= 1000s of candidates"]
        
        S2["Step 2: Signals (1000s of features)<br>User features: Past engagement patterns, Friend affinity scores, Content type preferences<br>Content features: Post age, Author engagement history, Content type, Engagement velocity<br>Context features: Time of day, Device type, Connection quality"]
        
        S3["Step 3: Prediction (Multiple models)<br>P(like) = model_like(features)<br>P(comment) = model_comment(features)<br>P(share) = model_share(features)<br>P(hide) = model_hide(features)<br>P(meaningful_interaction) = ..."]
        
        S4["Step 4: Ranking Score<br>Score = w1*P(like) + w2*P(comment) + w3*P(share)<br>- w4*P(hide) + w5*P(meaningful)<br>+ integrity_adjustment<br>+ diversity_boost"]
        
        S5["Step 5: Final Ordering<br>- Sort by score<br>- Apply business rules<br>- Insert ads at optimal positions<br>- Ensure diversity"]
        
        S1 --> S2
        S2 --> S3
        S3 --> S4
        S4 --> S5
    end
```
```

**WHY - Lý do & Impact:**
- Core product driving daily engagement
- Higher relevance = longer session times
- Critical for user retention
- Enables advertising business model

---

### 2. Ads System

**WHAT - Mục tiêu:**
- $100B+/year advertising revenue
- Match ads với relevant users
- Maximize ROI for advertisers
- Maintain good user experience

**HOW - Implementation:**

```
```mermaid
flowchart TD
    subgraph ADS [" "]
        direction TB
        A_TITLE["ADS RANKING<br>Objective: Maximize value for users, advertisers, and Meta"]
        style A_TITLE fill:none,stroke:none,font-weight:bold,color:#333
        
        AS["Ad Selection:<br>1. Advertiser bids on target audience<br>2. User profile matched against targeting<br>3. Eligible ads retrieved"]
        
        AR["Ad Ranking:<br>Total Value = Bid × P(Action) × Estimated Action Rate<br>+ User Value<br>- Quality Penalty<br><br>Where:<br>- P(Action) = probability of desired action (click/conv)<br>- User Value = relevance to user<br>- Quality = ad quality score"]
        
        ML["ML Models:<br>- Click prediction (CTR)<br>- Conversion prediction (CVR)<br>- Quality prediction<br>- User value prediction<br><br>Training:<br>- Billions of examples/day<br>- Real-time feature updates<br>- Continuous retraining"]
        
        AS --> AR
        AR --> ML
    end
```

> **Revenue:** $100B+/year from ads
```

**WHY - Lý do & Impact:**
- Primary revenue source
- Better targeting = higher advertiser ROI
- Relevant ads = better user experience
- Self-serve platform = massive scalability

---

### 3. Integrity & Safety

**WHAT - Mục tiêu:**
- Protect 3B+ users from harmful content
- Remove hate speech, misinformation, spam
- Detect fake accounts và coordinated behavior
- Maintain platform trust

**HOW - Implementation:**

```
```mermaid
flowchart TD
    subgraph INTEGRITY [" "]
        direction TB
        I_TITLE["INTEGRITY PLATFORM"]
        style I_TITLE fill:none,stroke:none,font-weight:bold,color:#333
        
        DT["Detection Types:<br>- Hate speech<br>- Misinformation<br>- Spam<br>- Fake accounts<br>- Coordinated inauthentic behavior<br>- Harmful content<br>- Bullying/harassment"]
        
        CP["Content Posted"]
        
        RC["Real-time Classifiers<br>- Text (NLP)<br>- Image (CV)<br>- Video (CV+Audio)"]
        
        HC["High Confidence<br>-> Remove"]
        BL["Borderline<br>-> Review (40,000+ humans)"]
        
        CP --> RC
        RC --> HC
        RC --> BL
    end
```

> **Scale:**
> - Billions of content pieces/day reviewed
> - 100s of languages
> - Milliseconds latency
> - 40,000+ human reviewers for edge cases

**WHY - Lý do & Impact:**
- Critical for platform trust
- Billions of harmful content removed/year
- Regulatory compliance required
- User safety = platform longevity
```

---

## 🛠️ META OPEN SOURCE CONTRIBUTIONS

```
> **META OSS ECOSYSTEM:**
> 
> * **Data Engineering:**
>   * Presto - Distributed SQL (now Trino fork too)
>   * RocksDB - Embedded key-value store
>   * Velox - Unified execution engine
>   * Scribe - Distributed log aggregation
> 
> * **ML/AI:**
>   * PyTorch - Deep learning framework
>   * FAISS - Similarity search
>   * LLaMA - Large language model
>   * Detectron2 - Object detection
>   * fairseq - Sequence modeling
> 
> * **Infrastructure:**
>   * React - UI framework
>   * GraphQL - Query language
>   * Cassandra - Distributed database (co-creator)
>   * Open Compute - Hardware designs
>   * Katran - Load balancer
> 
> * **Mobile:**
>   * React Native - Mobile development
>   * Hermes - JavaScript engine
>   * Litho - UI framework
```

---

## 📊 SCALE & NUMBERS

```
> **META BY THE NUMBERS:**
> 
> * **Users:**
>   * 3.1B daily active users (family of apps)
>   * 3.9B monthly active users
>   * 100+ billion messages/day (WhatsApp + Messenger)
> 
> * **Data:**
>   * Exabytes of data in warehouse
>   * 300+ PB scanned daily by Presto
>   * 100+ trillion edges in social graph
>   * Millions of ML model inferences/second
> 
> * **Infrastructure:**
>   * 100s of thousands of servers
>   * Custom data centers worldwide
>   * Custom hardware (training chips, inference)
>   * One of largest AI compute installations
```

---

## 🔑 KEY LESSONS

### 1. Build for Massive Scale
- Everything designed for billions of users
- Horizontal scaling everywhere
- Caching is critical (TAO)

### 2. Unified Platforms
- Single query engine (Presto)
- Single ML framework (PyTorch)
- Single execution engine (Velox)
- Reduces complexity, improves efficiency

### 3. Open Source Strategy
- Open source core infrastructure
- Community improves products
- Industry standardization benefits everyone

### 4. Real-time is Essential
- Scuba for operational analytics
- Streaming for features
- Sub-second integrity decisions

### 5. ML at the Core
- Every product uses ML
- Custom hardware for scale
- Continuous model improvement

---

## 🔗 OPEN-SOURCE REPOS (Verified)

Meta (Facebook) đóng góp nhiều infrastructure tools trở thành industry standard:

| Repo | Stars | Mô Tả |
|------|-------|--------|
| [prestodb/presto](https://github.com/prestodb/presto) | 16k⭐ | Distributed SQL query engine — **Facebook tạo ra**. Nhánh chính thức. |
| [trinodb/trino](https://github.com/trinodb/trino) | 10k⭐ | Fork của Presto bởi original creators (Martin Traverso, Dain Sundstrom, David Phillips). |
| [pytorch/pytorch](https://github.com/pytorch/pytorch) | 87k⭐ | ML framework — **Meta tạo ra**. Nền tảng cho ML platform của Meta. |
| [facebookincubator/velox](https://github.com/facebookincubator/velox) | 3.4k⭐ | Unified execution engine — **Meta tạo ra**. C++ vectorized execution. |

> 💡 **Lưu ý:** Presto có 2 forks — `prestodb/presto` (Meta maintain) và `trinodb/trino` (original creators). Trino có community active hơn.

---

## 📚 REFERENCES

**Engineering Blog:**
- Meta Engineering: https://engineering.fb.com/

**Key Articles:**
- Presto: https://prestodb.io/
- TAO: https://engineering.fb.com/2013/06/25/core-infra/tao-the-power-of-the-graph/
- Velox: https://velox-lib.io/

**Papers:**
- Presto: SQL on Everything (ICDE 2019)
- TAO: Facebook's Distributed Data Store (USENIX ATC 2013)
- Scuba: Diving into Data at Facebook (VLDB 2013)

---

*Document Version: 1.1*
*Last Updated: February 2026*
