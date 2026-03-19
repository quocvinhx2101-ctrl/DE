# LinkedIn Data Platform Architecture

## Kiến Trúc Data Platform Của LinkedIn - The Professional Network Giant

---

## 🏢 TỔNG QUAN CÔNG TY

- **Quy mô:** 900+ triệu members, 200+ countries
- **Data volume:** Trillions of events/day
- **Historical significance:** Birthplace of Apache Kafka
- **Open source contributions:** Kafka, Samza, Pinot, Gobblin, Datahub

---

## 🏗️ TỔNG QUAN KIẾN TRÚC

```mermaid
graph TB
    subgraph Sources[" "]
        Sources_title["📊 DATA SOURCES"]
        style Sources_title fill:none,stroke:none,color:#333,font-weight:bold
        S1[Profile Updates]
        S2[Feed Activity]
        S3[Jobs Posts]
        S4[Messaging Events]
        S5[Ads Impressions]
    end

    subgraph Streaming[" "]
        Streaming_title["🔄 STREAMING LAYER"]
        style Streaming_title fill:none,stroke:none,color:#333,font-weight:bold
        Kafka["Apache Kafka<br/>LinkedIn Created<br/>7T messages/day, 7PB/day"]
        Samza[Samza<br/>Stream Processing]
        Flink[Flink<br/>Stream Processing]
        Brooklin[Brooklin<br/>Mirror/Replication]
    end

    subgraph Storage[" "]
        Storage_title["💾 STORAGE LAYER"]
        style Storage_title fill:none,stroke:none,color:#333,font-weight:bold
        HDFS["Data Lake<br/>HDFS - Petabytes"]
        Pinot["Apache Pinot<br/>Real-time OLAP"]
        Venice["Venice<br/>Derived Data Store<br/>Feature Serving"]
    end

    subgraph Compute[" "]
        Compute_title["⚙️ COMPUTE LAYER"]
        style Compute_title fill:none,stroke:none,color:#333,font-weight:bold
        Spark["Spark<br/>ETL"]
        Presto["Presto<br/>Interactive SQL"]
        ProML["Pro-ML Platform<br/>Feathr + Training"]
    end

    subgraph Products[" "]
        Products_title["🚀 DATA PRODUCTS"]
        style Products_title fill:none,stroke:none,color:#333,font-weight:bold
        P1[Feed Ranking]
        P2[People You Know]
        P3[Job Matching]
        P4[Ads Targeting]
        P5[Sales Navigator]
    end

    S1 & S2 & S3 & S4 & S5 --> Kafka
    Kafka --> Samza & Flink & Brooklin
    Samza & Flink --> HDFS & Pinot & Venice
    HDFS & Pinot & Venice --> Spark & Presto & ProML
    Spark & Presto & ProML --> P1 & P2 & P3 & P4 & P5
```

---

## 🔧 TECH STACK CHI TIẾT

### 1. Apache Kafka (LinkedIn Created)

**Origin:** Created by LinkedIn in 2010, open-sourced 2011, Apache 2012

```
```mermaid
flowchart TD
    subgraph KAFKA [" "]
        direction TB
        K_TITLE["KAFKA ECOSYSTEM"]
        style K_TITLE fill:none,stroke:none,font-weight:bold,color:#333
        
        subgraph CLUSTERS ["Clusters"]
            direction LR
            TC["Tracking<br>Cluster"]
            MC["Metrics<br>Cluster"]
            QC["Queuing<br>Cluster"]
            CC["Change<br>Capture"]
        end
    end
```

> **KAFKA AT LINKEDIN:**
> 
> * **Scale (2024):** 7+ trillion messages/day, 7+ PB/day, 100K+ topics. 1000s of producers/consumers.
> * **Key Innovations:**
>   * Log compaction (for derived data)
>   * Exactly-once semantics
>   * Kafka Streams
>   * Kafka Connect
> 
> * **KAFKA USE CASES:**
>   1. **Activity Tracking:** Page views, clicks, searches (Analytics, ML)
>   2. **Metrics Pipeline:** Operational metrics, Business metrics
>   3. **Data Integration:** Change data capture, Database replication
>   4. **Commit Log:** Event sourcing, Derived data
> 
> * **WHY LINKEDIN CREATED KAFKA:**
>   * **Problem (2009):** Many data pipelines, Point-to-point connections, Inconsistent data, Scaling issues
>   * **Solution (Kafka):** Central commit log, Publish-subscribe, Horizontal scaling, Durability + replay
```

### 2. Apache Samza (LinkedIn Created)

```
```mermaid
flowchart TD
    subgraph SAMZA [" "]
        direction TB
        S_TITLE["SAMZA<br>(Stateful Stream Processing)"]
        style S_TITLE fill:none,stroke:none,font-weight:bold,color:#333
        
        IN["Input<br>(Kafka)"]
        TASK["Task<br>Process + State (RocksDB)"]
        OUT["Output<br>(Kafka)"]
        
        IN --> TASK
        TASK --> OUT
    end
```

> **Key Features:**
> - Local state (RocksDB)
> - State replication via Kafka
> - Exactly-once processing
> - Easy recovery
> 
> **SAMZA USE CASES:**
> 1. Standardization: Raw events -> standardized events, Schema validation
> 2. Aggregation: Near-real-time metrics, Session aggregation
> 3. Derived Data: Compute features, Update Venice
```

### 3. Apache Pinot (LinkedIn Created)

```
```mermaid
flowchart TD
    subgraph PINOT [" "]
        direction TB
        P_TITLE["PINOT<br>(Real-time OLAP)"]
        style P_TITLE fill:none,stroke:none,font-weight:bold,color:#333
        
        QB["Query Broker<br>- Query routing<br>- Result merging"]
        RS["Real-time Server<br>(Kafka ingestion)"]
        OS["Offline Server<br>(HDFS segments)"]
        
        QB --> RS
        QB --> OS
    end
```

> **PINOT AT LINKEDIN:**
> 
> * **Use Cases:** Who Viewed My Profile (real-time), Campaign analytics, A/B test results, Ads performance
> * **Scale:** 100K+ queries/second, Sub-second latency (p99 < 100ms), 100s of tables
```

### 4. Venice (Derived Data Store)

```
```mermaid
flowchart TD
    subgraph VENICE [" "]
        direction TB
        V_TITLE["VENICE<br>(Read-after-write derived data)"]
        style V_TITLE fill:none,stroke:none,font-weight:bold,color:#333
        
        BATCH["Batch (Spark)"]
        STREAM["Stream (Samza)"]
        FP["Full push"]
        RT["RT update"]
        VS["Venice Server (RocksDB-based)<br>- Key-value<br>- Versioned"]
        
        BATCH --> FP
        STREAM --> RT
        FP --> VS
        RT --> VS
    end
```

> **VENICE CHARACTERISTICS:**
> 
> * **Use Cases:** Feature serving (ML), Derived data for applications, Cache bypass
> * **Properties:** Eventually consistent, High read throughput, Batch + streaming writes
```

### 5. Datahub (Metadata Platform)

```
```mermaid
flowchart TD
    subgraph DATAHUB [" "]
        direction TB
        D_TITLE["DATAHUB<br>(Unified Metadata Platform)"]
        style D_TITLE fill:none,stroke:none,font-weight:bold,color:#333
        
        subgraph SOURCES ["Metadata Sources"]
            direction LR
            HT["Hive Tables"]
            KT["Kafka Topics"]
            SJ["Spark Jobs"]
            AD["Airflow DAGs"]
        end
        style SOURCES fill:none,stroke:none
        
        INGEST["Metadata Ingestion<br>- Crawlers<br>- Push APIs<br>- Kafka events"]
        STORE["Metadata Store<br>- Graph DB (relationships)<br>- Search index (Elasticsearch)<br>- Kafka (change log)"]
        UI["UI & APIs<br>- Search & discovery<br>- Lineage visualization<br>- Data quality scores<br>- Ownership management"]
        
        SOURCES --> INGEST
        INGEST --> STORE
        STORE --> UI
    end
```
```

### 6. Feathr (Feature Store)

```
```mermaid
flowchart TD
    subgraph FEATHR [" "]
        direction TB
        F_TITLE["FEATHR<br>(Enterprise Feature Store)"]
        style F_TITLE fill:none,stroke:none,font-weight:bold,color:#333
        
        FD["Feature Definition (Python)<br>anchor = FeatureAnchor(<br>  name='member_features',<br>  source=HdfsSource('/data/members'),<br>  features=[<br>    Feature(name='connections_count', transform='connections', type=INT32),<br>    Feature(name='profile_views_7d', transform=WindowAgg('views', 7, 'count'))<br>  ]<br>)"]
        
        OS1["Offline (Spark)<br>- Training data<br>- Backfill"]
        OS2["Online (Redis)<br>- Serving<br>- Low latency"]
        
        FD --> OS1
        FD --> OS2
    end
```
```

---

## 🎯 KEY DATA PRODUCTS

### 1. Feed Ranking

**WHAT - Mục tiêu:**
- Show relevant content to 900M+ members
- Maximize engagement và value
- Balance creator và consumer interests
- Integrate organic và sponsored content

**HOW - Implementation:**

```
```mermaid
flowchart TD
    subgraph FEED [" "]
        direction TB
        F_TITLE["FEED RANKING SYSTEM"]
        style F_TITLE fill:none,stroke:none,font-weight:bold,color:#333
        
        USER["Member opens LinkedIn"]
        CG["Candidate Generation<br>- Posts from connections<br>- Posts from followed companies<br>- Recommended content<br>- Ads candidates"]
        FF["Feature Fetch (Venice + Pinot)<br>- Member features<br>- Author features<br>- Content features<br>- Context features"]
        RM["Ranking Models<br>- First pass: lightweight model<br>- Second pass: deep neural network<br>- Objectives: engagement + relevance"]
        BD["Blending & Diversity<br>- Mix organic + sponsored<br>- Ensure diversity<br>- Apply business rules"]
        RES["Personalized Feed"]
        
        USER --> CG
        CG --> FF
        FF --> RM
        RM --> BD
        BD --> RES
    end
```
```

**WHY - Lý do & Impact:**
- Core engagement driver for platform
- Higher feed relevance = longer session times
- Better content distribution for creators
- Foundation for advertising revenue

---

### 2. People You May Know (PYMK)

**WHAT - Mục tiêu:**
- Grow member networks
- Connect professionals với relevant people
- Increase platform stickiness
- Create network effects

**HOW - Implementation:**

```
```mermaid
flowchart TD
    subgraph PYMK [" "]
        direction TB
        P_TITLE["PEOPLE YOU MAY KNOW"]
        style P_TITLE fill:none,stroke:none,font-weight:bold,color:#333
        
        GA["Graph Analysis:<br>LinkedIn Social Graph (900M+ nodes, billions of edges)<br>You -> A -> B (2nd degree)<br>         -> C (3rd degree)"]
        style GA fill:none,stroke:none,text-align:left
        
        CS["Candidate Sources:<br>- 2nd degree connections<br>- Same company/school alumni<br>- Profile viewers<br>- Imported contacts"]
        style CS fill:none,stroke:none,text-align:left
        
        RS["Ranking Signals:<br>- Connection strength (mutual connections)<br>- Profile similarity (industry, skills)<br>- Interaction history (profile views, searches)<br>- Recency"]
        style RS fill:none,stroke:none,text-align:left
        
        GA --> CS
        CS --> RS
    end
```
```

**WHY - Lý do & Impact:**
- #1 driver of new connections
- Larger networks = more engaged members
- Critical for platform growth
- Network effects = competitive moat

---

### 3. Job Recommendations

**WHAT - Mục tiêu:**
- Match members với relevant jobs
- Help recruiters find candidates
- Drive Premium subscriptions
- Enable career growth

**HOW - Implementation:**

```
```mermaid
flowchart TD
    subgraph JOB [" "]
        direction TB
        J_TITLE["JOB RECOMMENDATIONS"]
        style J_TITLE fill:none,stroke:none,font-weight:bold,color:#333
        
        MP["Member Profile<br>- Title<br>- Skills<br>- Experience<br>- Location<br>- Preferences"]
        JP["Job Posting<br>- Title<br>- Required<br>- Preferred<br>- Location<br>- Company"]
        
        MM["Matching Model<br>- Semantic matching<br>- Skill graph embedding<br>- Location preference<br>- Career trajectory"]
        RANK["Ranking<br>- Relevance score<br>- Apply likelihood<br>- Quality indicators"]
        
        MP --> MM
        JP --> MM
        MM --> RANK
    end
```
```

**WHY - Lý do & Impact:**
- Major revenue driver (Talent Solutions)
- Higher match quality = more hires
- Competitive advantage in job market
- Drives Premium member acquisition

---

## 🛠️ LINKEDIN OPEN SOURCE CONTRIBUTIONS

```
> **LINKEDIN OSS ECOSYSTEM:**
> 
> * **Data Infrastructure:**
>   * Apache Kafka (Distributed streaming)
>   * Apache Samza (Stream processing)
>   * Apache Pinot (Real-time OLAP)
>   * Apache Gobblin (Data ingestion)
>   * Venice (Derived data store)
>   * Datahub (Metadata platform - now Acryl)
>   * Feathr (Feature store)
>   * Brooklin (Kafka mirroring)
> 
> * **ML/AI:**
>   * Photon-ML (ML library)
>   * li-apache-kafka-clients (Enhanced Kafka client)
> 
> * **Infrastructure:**
>   * Ambry (Blob store)
>   * Rest.li (REST framework)
>   * Helix (Cluster management)
```

---

## 📊 SCALE & NUMBERS

```
> **LINKEDIN BY THE NUMBERS:**
> 
> * **Kafka:**
>   * 7+ trillion messages/day
>   * 7+ PB throughput/day
>   * 100K+ topics
>   * 4000+ Kafka brokers
> 
> * **Data Infrastructure:**
>   * Exabytes in HDFS
>   * 100+ Pinot clusters
>   * 1000s of Spark jobs/day
>   * 10,000s of streaming jobs
> 
> * **Platform:**
>   * 900M+ members
>   * 60M+ companies
>   * 40M+ job postings
>   * Billions of API calls/day
```

---

## 🔑 KEY LESSONS

### 1. Build for Scale from Day One
- Kafka designed for LinkedIn's needs
- Became universal infrastructure
- Horizontal scaling essential

### 2. Unified Streaming Architecture
- Kafka as central nervous system
- All data flows through Kafka
- Real-time and batch from same source

### 3. Invest in Metadata
- Datahub for discovery
- Critical at scale
- Enables self-service

### 4. Derived Data is Key
- Venice for serving features
- Pre-computed for low latency
- Eventual consistency OK

### 5. Open Source Strategy
- Build internally, open source
- Community improves product
- Attracts talent

---

## 🔗 OPEN-SOURCE REPOS (Verified)

LinkedIn là nguồn gốc của Kafka — nền tảng event streaming phổ biến nhất thế giới:

| Repo | Stars | Mô Tả |
|------|-------|--------|
| [apache/kafka](https://github.com/apache/kafka) | 29k⭐ | Distributed event streaming — **LinkedIn tạo ra** (Jay Kreps, Jun Rao, Neha Narkhede). |
| [datahub-project/datahub](https://github.com/datahub-project/datahub) | 11.5k⭐ | Data catalog & discovery — **LinkedIn tạo ra**. Có `docker/` dir cho Docker Compose quickstart. |
| [apache/pinot](https://github.com/apache/pinot) | 5.5k⭐ | Real-time OLAP datastore — **LinkedIn tạo ra**. |

> 💡 **Hands-on:** `datahub-project/datahub` có Docker Compose quickstart hoàn chỉnh và Helm charts cho K8s tại `datahub-kubernetes/`.

---

## 📚 REFERENCES

**Engineering Blog:**
- LinkedIn Engineering: https://engineering.linkedin.com/blog

**Key Articles:**
- Kafka at LinkedIn: https://engineering.linkedin.com/kafka
- Pinot: https://pinot.apache.org/
- Datahub: https://datahubproject.io/

**Papers:**
- Kafka paper: VLDB 2011
- Building LinkedIn's Real-time Activity Data Pipeline

---

*Document Version: 1.1*
*Last Updated: February 2026*
